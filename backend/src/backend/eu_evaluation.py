"""Measure selected CTIS references through the app's European search endpoint."""

import argparse
import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import httpx
from pydantic import BaseModel, Field, StrictBool, ValidationError

from backend.main import app
from backend.registry import get_registry

TRIAL_PATTERN = r"^[0-9]{4}-[0-9]{6}-[0-9]{2}-[0-9]{2}$"


class Reference(BaseModel):
    id: str = Field(pattern=TRIAL_PATTERN)
    title: str = Field(min_length=1)
    condition: str = Field(min_length=1)
    source_url: str
    reason: str = Field(min_length=1)


class Case(BaseModel):
    id: str = Field(min_length=1)
    query: str = Field(min_length=1, max_length=120)
    relevant_id: str = Field(pattern=TRIAL_PATTERN)
    mismatch_ids: list[str] = []


class Dataset(BaseModel):
    description: str
    references: list[Reference] = Field(min_length=1)
    cases: list[Case] = Field(min_length=1)


class SourceCondition(BaseModel):
    medicalCondition: str


class SourceConditions(BaseModel):
    partIMedicalConditions: list[SourceCondition]


class SourceInformation(BaseModel):
    medicalCondition: SourceConditions


class SourceIdentifiers(BaseModel):
    publicTitle: str


class SourceDetails(BaseModel):
    clinicalTrialIdentifiers: SourceIdentifiers
    trialInformation: SourceInformation


class SourcePart(BaseModel):
    trialDetails: SourceDetails


class SourceCountry(BaseModel):
    mscName: str


class SourceApplication(BaseModel):
    memberStatesConcerned: list[SourceCountry]
    authorizedPartI: SourcePart


class SourceRecord(BaseModel):
    ctNumber: str
    authorizedApplication: SourceApplication


class ResultStudy(BaseModel):
    id: str = Field(pattern=TRIAL_PATTERN)


class ResultPage(BaseModel):
    studies: list[ResultStudy]
    page: int = Field(strict=True, ge=1)
    total: int = Field(strict=True, ge=0)
    more_results: StrictBool


def check_reference(
    reference: Reference, status_code: int, payload: object
) -> Literal["current", "changed", "error"]:
    if status_code != 200:
        return "error"
    try:
        record = SourceRecord.model_validate(payload)
    except ValidationError:
        return "error"
    application = record.authorizedApplication
    details = application.authorizedPartI.trialDetails
    conditions = [
        item.medicalCondition
        for item in details.trialInformation.medicalCondition.partIMedicalConditions
    ]
    if (
        record.ctNumber != reference.id
        or reference.source_url
        != f"https://euclinicaltrials.eu/ctis-public/view/{reference.id}"
        or details.clinicalTrialIdentifiers.publicTitle != reference.title
        or conditions != [reference.condition]
        or not any(
            state.mscName == "Greece" for state in application.memberStatesConcerned
        )
    ):
        return "changed"
    return "current"


async def search_across_pages(
    client: httpx.AsyncClient, case: Case, max_pages: int
) -> dict:
    ids: list[str] = []
    pages_checked = 0
    first_page_outcome = None
    status_code = None
    more_results = None
    for page_number in range(1, max_pages + 1):
        try:
            response = await client.post(
                "/api/eu-studies/search",
                json={"condition": case.query, "page": page_number},
            )
            status_code = response.status_code
            if status_code != 200:
                raise ValueError("Search failed")
            page = ResultPage.model_validate(response.json())
            if page.page != page_number:
                raise ValueError("Unexpected page number")
        except httpx.HTTPError, ValidationError, ValueError:
            return {
                "outcome": "error",
                "http_status": status_code,
                "pages_checked": pages_checked,
                "first_page_outcome": first_page_outcome,
                "returned_ids": ids,
                "more_results": None,
                "known_mismatches_shown": [
                    item for item in case.mismatch_ids if item in ids
                ],
            }
        pages_checked += 1
        page_ids = [study.id for study in page.studies]
        if first_page_outcome is None:
            first_page_outcome = "found" if case.relevant_id in page_ids else "missed"
        for trial_id in page_ids:
            if trial_id not in ids:
                ids.append(trial_id)
        more_results = page.more_results
        if not more_results:
            break
    return {
        "outcome": "found" if case.relevant_id in ids else "missed",
        "http_status": status_code,
        "pages_checked": pages_checked,
        "first_page_outcome": first_page_outcome,
        "returned_ids": ids,
        "more_results": more_results,
        "known_mismatches_shown": [item for item in case.mismatch_ids if item in ids],
    }


def summarize(results: list[dict]) -> dict:
    found = sum(item["outcome"] == "found" for item in results)
    missed = sum(item["outcome"] == "missed" for item in results)
    return {
        "found": found,
        "missed": missed,
        "errors": sum(item["outcome"] == "error" for item in results),
        "references_changed": sum(
            item["outcome"] == "reference_changed" for item in results
        ),
        "target_hit_rate": found / (found + missed) if found + missed else None,
        "cases_showing_known_mismatch": sum(
            bool(item["known_mismatches_shown"]) for item in results
        ),
    }


async def evaluate(dataset: Dataset, dataset_hash: str, max_pages: int) -> dict:
    references = {reference.id: reference for reference in dataset.references}
    if len(references) != len(dataset.references) or len(
        {case.id for case in dataset.cases}
    ) != len(dataset.cases):
        raise ValueError("Reference IDs and case IDs must be unique")
    for case in dataset.cases:
        if case.relevant_id not in references or any(
            item not in references for item in case.mismatch_ids
        ):
            raise ValueError("Each case must reference known records")
        if case.relevant_id in case.mismatch_ids or len(set(case.mismatch_ids)) != len(
            case.mismatch_ids
        ):
            raise ValueError("A mismatch must differ from the target and be unique")
    checked_at = datetime.now(UTC).isoformat()
    reference_status = {}
    async with httpx.AsyncClient(timeout=15) as registry:
        for reference in dataset.references:
            try:
                response = await get_registry(
                    registry,
                    f"https://euclinicaltrials.eu/ctis-public-api/retrieve/{reference.id}",
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
            statuses = [
                reference_status[item]
                for item in [case.relevant_id, *case.mismatch_ids]
            ]
            if any(status != "current" for status in statuses):
                scored = {
                    "outcome": "error" if "error" in statuses else "reference_changed",
                    "http_status": None,
                    "pages_checked": 0,
                    "first_page_outcome": None,
                    "returned_ids": [],
                    "more_results": None,
                    "known_mismatches_shown": [],
                }
            else:
                scored = await search_across_pages(client, case, max_pages)
            results.append({**case.model_dump(), **scored})
    return {
        "checked_at_utc": checked_at,
        "dataset_sha256": dataset_hash,
        "max_pages": max_pages,
        "summary": summarize(results),
        "reference_status": reference_status,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Measure selected European reference records in search results."
    )
    parser.add_argument("--cases", type=Path, default=Path("evaluation/eu-cases.json"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-pages", type=int, choices=range(1, 11), default=1)
    args = parser.parse_args()
    case_bytes = args.cases.read_bytes()
    dataset = Dataset.model_validate_json(case_bytes)
    report = asyncio.run(
        evaluate(dataset, hashlib.sha256(case_bytes).hexdigest(), args.max_pages)
    )
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(output, end="")
    if args.output:
        args.output.write_text(output)
    if report["summary"]["errors"] or report["summary"]["references_changed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
