import asyncio
import json
import sys

import httpx
import pytest
from pydantic import ValidationError

from backend import evidence_check
from backend.evidence_check import (
    Candidate,
    CandidateSet,
    check_candidates,
    check_quote,
)
from backend.main import app, registry_client

TRIAL = "2025-522873-12-00"
URL = f"https://euclinicaltrials.eu/ctis-public/view/{TRIAL}"


def source():
    return {
        "id": TRIAL,
        "source_url": URL,
        "objective": {
            "english": "Compare the two treatments.",
            "greek": "Σύγκριση θεραπειών.",
        },
        "inclusion": [
            {"english": "Adult participants.", "greek": "Ενήλικες συμμετέχοντες."}
        ],
        "exclusion": [{"english": "Prior treatment.", "greek": None}],
    }


def candidate(**changes):
    data = {
        "id": "one",
        "trial_id": TRIAL,
        "source_url": URL,
        "field": "inclusion",
        "index": 0,
        "language": "english",
        "quote": "Adult participants.",
        "claim": "All adults can join.",
    }
    data.update(changes)
    return Candidate.model_validate(data)


def test_exact_quote_does_not_claim_medical_correctness():
    assert check_quote(candidate(), 200, source()) == "quote_found"
    assert (
        check_quote(candidate(claim="The trial accepts no adults."), 200, source())
        == "quote_found"
    )
    assert (
        check_quote(
            candidate(language="greek", quote="Ενήλικες συμμετέχοντες."), 200, source()
        )
        == "quote_found"
    )


def test_made_up_or_wrong_field_quotes_are_not_found():
    assert (
        check_quote(candidate(quote="All adults can join."), 200, source())
        == "quote_not_found"
    )
    assert (
        check_quote(
            candidate(field="exclusion", quote="Adult participants."), 200, source()
        )
        == "quote_not_found"
    )


def test_missing_text_and_source_failure_are_distinct():
    assert (
        check_quote(candidate(field="exclusion", language="greek"), 200, source())
        == "field_unavailable"
    )
    assert check_quote(candidate(index=9), 200, source()) == "field_unavailable"
    assert check_quote(candidate(), 503, {}) == "source_error"


def test_rejects_mismatched_source_url_or_trial_id():
    assert (
        check_quote(candidate(source_url="https://example.com/"), 200, source())
        == "source_error"
    )
    changed = source()
    changed["id"] = "2025-111111-11-11"
    assert check_quote(candidate(), 200, changed) == "source_error"


def test_rejects_invalid_field_locations_and_blank_quotes():
    with pytest.raises(ValidationError):
        candidate(field="objective", index=0)
    with pytest.raises(ValidationError):
        candidate(index=None)
    with pytest.raises(ValidationError):
        candidate(quote="   ")


def test_checks_candidates_through_the_real_lookup_and_reports_its_limits():
    requests = []
    record = {
        "ctNumber": TRIAL,
        "authorizedApplication": {
            "memberStatesConcerned": [{"mscName": "Greece"}],
            "authorizedPartI": {
                "trialDetails": {
                    "clinicalTrialIdentifiers": {"publicTitle": "Title"},
                    "trialInformation": {
                        "eligibilityCriteria": {
                            "principalInclusionCriteria": [
                                {"principalInclusionCriteria": "Adult participants."}
                            ],
                        }
                    },
                }
            },
        },
    }

    def reply(request):
        requests.append(request.url.path)
        return httpx.Response(200, json=record)

    async def mock_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            yield client

    dataset = CandidateSet(
        description="Examples",
        candidates=[
            candidate(id="found"),
            candidate(id="missing", quote="Made up."),
        ],
    )
    app.dependency_overrides[registry_client] = mock_client
    try:
        report = asyncio.run(check_candidates(dataset, "test-hash"))
    finally:
        app.dependency_overrides.clear()
    assert [item["outcome"] for item in report["results"]] == [
        "quote_found",
        "quote_not_found",
    ]
    assert "does not check whether any claim is true" in report["notice"]
    assert len(requests) == 1


def test_cli_reports_nonmatching_quotes_and_returns_failure(
    tmp_path, monkeypatch, capsys
):
    dataset = CandidateSet(description="Examples", candidates=[candidate()])
    cases = tmp_path / "cases.json"
    cases.write_text(dataset.model_dump_json())

    async def fake_check(_dataset, _hash):
        return {
            "notice": "Not a correctness check",
            "results": [{"outcome": "quote_not_found"}],
        }

    monkeypatch.setattr(evidence_check, "check_candidates", fake_check)
    monkeypatch.setattr(sys, "argv", ["check", "--cases", str(cases)])
    with pytest.raises(SystemExit) as result:
        evidence_check.main()
    assert result.value.code == 1
    assert (
        json.loads(capsys.readouterr().out)["results"][0]["outcome"]
        == "quote_not_found"
    )
