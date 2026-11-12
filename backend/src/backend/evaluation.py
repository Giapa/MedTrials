"""Evaluate known reference records against the current search endpoint."""

import argparse
import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, Self

import httpx
from pydantic import BaseModel, Field, StrictBool, ValidationError, model_validator

from backend.main import app
from backend.registry import RegistryStudy, get_registry


class Reference(BaseModel):
    id: str = Field(pattern=r"^NCT[0-9]{8}$")
    title: str = Field(min_length=1)
    source_url: str
    record_updated: str
    reason: str = Field(min_length=1)


class Case(BaseModel):
    id: str = Field(min_length=1)
    language: str = Field(min_length=1)
    query: str = Field(min_length=1, max_length=120)
    expected_id: str = Field(pattern=r"^NCT[0-9]{8}$")


class Cases(BaseModel):
    description: str
    references: list[Reference] = Field(min_length=1)
    cases: list[Case] = Field(min_length=1)


class ReturnedStudy(BaseModel):
    id: str = Field(pattern=r"^NCT[0-9]{8}$")


class SearchResponse(BaseModel):
    studies: list[ReturnedStudy]
    more_results: StrictBool
    next_page_token: str | None = Field(min_length=1, max_length=2048)

    @model_validator(mode="after")
    def validate_token(self) -> Self:
        if self.more_results != bool(self.next_page_token):
            raise ValueError("Page token does not match more-results flag")
        return self


def score_result(expected_id: str, status_code: int, payload: object) -> dict:
    if status_code != 200:
        return {
            "outcome": "error",
            "returned_ids": [],
            "more_results": None,
            "http_status": status_code,
        }
    try:
        response = SearchResponse.model_validate(payload)
    except ValidationError:
        return {
            "outcome": "error",
            "returned_ids": [],
            "more_results": None,
            "http_status": status_code,
        }
    returned_ids = [study.id for study in response.studies]
    return {
        "outcome": "found" if expected_id in returned_ids else "missed",
        "returned_ids": returned_ids,
        "more_results": response.more_results,
        "http_status": status_code,
    }


def summarize_results(results: list[dict]) -> dict:
    found = sum(result["outcome"] == "found" for result in results)
    missed = sum(result["outcome"] == "missed" for result in results)
    return {
        "found": found,
        "missed": missed,
        "errors": sum(result["outcome"] == "error" for result in results),
        "references_changed": sum(
            result["outcome"] == "reference_changed" for result in results
        ),
        "target_hit_rate": found / (found + missed) if found + missed else None,
    }


async def search_across_pages(
    client: httpx.AsyncClient, case: Case, max_pages: int
) -> dict:
    ids: list[str] = []
    seen_tokens: set[str] = set()
    token: str | None = None
    first_page_outcome: str | None = None
    pages_checked = 0
    for _ in range(max_pages):
        request_body = {"condition": case.query, "open_studies_only": False}
        if token is not None:
            request_body["page_token"] = token
        try:
            response = await client.post("/api/studies/search", json=request_body)
            data = response.json()
            scored = score_result(case.expected_id, response.status_code, data)
        except httpx.HTTPError, ValueError:
            scored = {
                "outcome": "error",
                "returned_ids": [],
                "more_results": None,
                "http_status": None,
            }
        if scored["outcome"] == "error":
            return {
                **scored,
                "returned_ids": ids,
                "pages_checked": pages_checked,
                "first_page_outcome": first_page_outcome,
            }
        page = SearchResponse.model_validate(data)
        pages_checked += 1
        if first_page_outcome is None:
            first_page_outcome = scored["outcome"]
        for study_id in scored["returned_ids"]:
            if study_id not in ids:
                ids.append(study_id)
        if scored["outcome"] == "found" or page.next_page_token is None:
            return {
                **scored,
                "returned_ids": ids,
                "pages_checked": pages_checked,
                "first_page_outcome": first_page_outcome,
            }
        if page.next_page_token in seen_tokens:
            return {
                "outcome": "error",
                "returned_ids": ids,
                "more_results": None,
                "http_status": response.status_code,
                "pages_checked": pages_checked,
                "first_page_outcome": first_page_outcome,
            }
        seen_tokens.add(page.next_page_token)
        token = page.next_page_token
    return {
        **scored,
        "returned_ids": ids,
        "pages_checked": pages_checked,
        "first_page_outcome": first_page_outcome,
    }


def check_reference(
    reference: Reference, status_code: int, payload: object
) -> Literal["current", "changed", "error"]:
    if status_code != 200:
        return "error"
    try:
        study = RegistryStudy.model_validate(payload).protocolSection
    except ValidationError:
        return "error"
    update = study.statusModule.lastUpdatePostDateStruct
    if (
        reference.source_url != f"https://clinicaltrials.gov/study/{reference.id}"
        or study.identificationModule.nctId != reference.id
        or study.identificationModule.briefTitle != reference.title
        or update is None
        or update.date != reference.record_updated
        or not any(
            loc.country == "Greece" for loc in study.contactsLocationsModule.locations
        )
    ):
        return "changed"
    return "current"


async def evaluate(dataset: Cases, dataset_sha256: str, max_pages: int = 1) -> dict:
    references = {reference.id: reference for reference in dataset.references}
    if len(references) != len(dataset.references) or len(
        {case.id for case in dataset.cases}
    ) != len(dataset.cases):
        raise ValueError("Reference IDs and case IDs must be unique")
    if any(case.expected_id not in references for case in dataset.cases):
        raise ValueError("Each case must have an existing reference")

    checked_at = datetime.now(UTC).isoformat()
    async with httpx.AsyncClient(timeout=15) as registry:
        reference_status = {}
        for reference in dataset.references:
            try:
                response = await get_registry(
                    registry,
                    f"https://clinicaltrials.gov/api/v2/studies/{reference.id}",
                )
                reference_status[reference.id] = check_reference(
                    reference, response.status_code, response.json()
                )
            except httpx.HTTPError, ValueError:
                reference_status[reference.id] = "error"

    results = []
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://medtrials.local"
    ) as client:
        for case in dataset.cases:
            reference_state = reference_status[case.expected_id]
            if reference_state != "current":
                scored = {
                    "outcome": "reference_changed"
                    if reference_state == "changed"
                    else "error",
                    "returned_ids": [],
                    "more_results": None,
                    "http_status": None,
                    "pages_checked": 0,
                    "first_page_outcome": None,
                }
            else:
                scored = await search_across_pages(client, case, max_pages)
            results.append({**case.model_dump(), **scored})

    return {
        "checked_at_utc": checked_at,
        "dataset_sha256": dataset_sha256,
        "max_pages": max_pages,
        "summary": summarize_results(results),
        "first_page_summary": summarize_results(
            [
                {"outcome": result["first_page_outcome"] or result["outcome"]}
                for result in results
            ]
        ),
        "reference_status": reference_status,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Measure whether search results contain known reference records."
    )
    parser.add_argument("--cases", type=Path, default=Path("evaluation/cases.json"))
    parser.add_argument("--output", type=Path, help="Save the report as JSON")
    parser.add_argument(
        "--max-pages",
        type=int,
        choices=range(1, 11),
        default=1,
        help="Maximum registry pages per case (1–10)",
    )
    args = parser.parse_args()
    case_bytes = args.cases.read_bytes()
    dataset = Cases.model_validate_json(case_bytes)
    report = asyncio.run(
        evaluate(dataset, hashlib.sha256(case_bytes).hexdigest(), args.max_pages)
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    if report["summary"]["errors"] or report["summary"]["references_changed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
