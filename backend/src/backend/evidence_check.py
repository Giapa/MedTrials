"""Check exact quotation locations in published CTIS records; not claim truth."""

import argparse
import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal, Self

import httpx
from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

from backend.main import app

TrialNumber = Annotated[
    str, StringConstraints(pattern=r"^[0-9]{4}-[0-9]{6}-[0-9]{2}-[0-9]{2}$")
]


class Candidate(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    trial_id: TrialNumber
    source_url: str = Field(min_length=1, max_length=300)
    field: Literal["objective", "inclusion", "exclusion"]
    index: int | None = Field(strict=True, ge=0, le=1000)
    language: Literal["english", "greek"]
    quote: str = Field(min_length=1, max_length=2000)
    claim: str = Field(min_length=1, max_length=2000)

    @field_validator("quote", "claim")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text must not be blank")
        return value

    @model_validator(mode="after")
    def check_index(self) -> Self:
        if (self.field == "objective") != (self.index is None):
            raise ValueError("Objective has no index; criteria require an index")
        return self


class CandidateSet(BaseModel):
    description: str
    candidates: list[Candidate] = Field(min_length=1)


class SourceText(BaseModel):
    english: str | None
    greek: str | None


class SourceRecord(BaseModel):
    id: TrialNumber
    source_url: str
    objective: SourceText | None
    inclusion: list[SourceText]
    exclusion: list[SourceText]


def check_quote(
    candidate: Candidate, status_code: int | None, payload: object
) -> Literal["quote_found", "quote_not_found", "field_unavailable", "source_error"]:
    if status_code != 200:
        return "source_error"
    try:
        source = SourceRecord.model_validate(payload)
    except ValidationError:
        return "source_error"
    expected_url = f"https://euclinicaltrials.eu/ctis-public/view/{candidate.trial_id}"
    if (
        source.id != candidate.trial_id
        or source.source_url != expected_url
        or candidate.source_url != expected_url
    ):
        return "source_error"
    if candidate.field == "objective":
        text = source.objective
    else:
        entries = (
            source.inclusion if candidate.field == "inclusion" else source.exclusion
        )
        if candidate.index is None or candidate.index >= len(entries):
            return "field_unavailable"
        text = entries[candidate.index]
    if text is None:
        return "field_unavailable"
    field_text = text.english if candidate.language == "english" else text.greek
    if field_text is None:
        return "field_unavailable"
    return "quote_found" if candidate.quote in field_text else "quote_not_found"


async def check_candidates(dataset: CandidateSet, dataset_hash: str) -> dict:
    if len({candidate.id for candidate in dataset.candidates}) != len(
        dataset.candidates
    ):
        raise ValueError("Candidate IDs must be unique")
    sources = {}
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://medtrials.local"
    ) as client:
        for candidate in dataset.candidates:
            if candidate.trial_id in sources:
                continue
            try:
                response = await client.get(f"/api/eu-studies/{candidate.trial_id}")
                sources[candidate.trial_id] = (response.status_code, response.json())
            except httpx.HTTPError, ValueError:
                sources[candidate.trial_id] = (None, None)
    results = []
    for candidate in dataset.candidates:
        status, payload = sources[candidate.trial_id]
        results.append(
            {
                **candidate.model_dump(),
                "outcome": check_quote(candidate, status, payload),
            }
        )
    return {
        "notice": "Only exact quotation locations are checked. This does not check whether any claim is true, complete, safe, or medically appropriate.",
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "dataset_sha256": dataset_hash,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check exact quotations against published CTIS records; does not check medical claims."
    )
    parser.add_argument(
        "--cases", type=Path, default=Path("evaluation/quote-cases.json")
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    case_bytes = args.cases.read_bytes()
    dataset = CandidateSet.model_validate_json(case_bytes)
    report = asyncio.run(
        check_candidates(dataset, hashlib.sha256(case_bytes).hexdigest())
    )
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(output, end="")
    if args.output:
        args.output.write_text(output)
    if any(result["outcome"] != "quote_found" for result in report["results"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
