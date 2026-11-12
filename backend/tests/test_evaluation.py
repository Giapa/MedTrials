import asyncio
import json
import sys

import httpx
import pytest

from backend import evaluation
from backend.evaluation import (
    Case,
    Reference,
    check_reference,
    score_result,
    search_across_pages,
    summarize_results,
)


def test_expected_record_is_found_among_returned_results():
    result = score_result(
        "NCT12345678",
        200,
        {
            "studies": [{"id": "NCT87654321"}, {"id": "NCT12345678"}],
            "more_results": True,
            "next_page_token": "next",
        },
    )
    assert result == {
        "outcome": "found",
        "returned_ids": ["NCT87654321", "NCT12345678"],
        "more_results": True,
        "http_status": 200,
    }


def test_valid_empty_results_are_a_miss():
    assert score_result(
        "NCT12345678",
        200,
        {"studies": [], "more_results": False, "next_page_token": None},
    ) == {
        "outcome": "missed",
        "returned_ids": [],
        "more_results": False,
        "http_status": 200,
    }


def test_service_failure_is_not_counted_as_a_miss():
    assert score_result("NCT12345678", 502, {"detail": "unavailable"}) == {
        "outcome": "error",
        "returned_ids": [],
        "more_results": None,
        "http_status": 502,
    }


def test_malformed_result_is_not_counted_as_a_miss():
    assert score_result("NCT12345678", 200, {"studies": [{}]}) == {
        "outcome": "error",
        "returned_ids": [],
        "more_results": None,
        "http_status": 200,
    }
    assert (
        score_result(
            "NCT12345678",
            200,
            {"studies": [], "more_results": False, "next_page_token": ""},
        )["outcome"]
        == "error"
    )


def test_hit_rate_excludes_errors_and_changed_references():
    results = [
        {"outcome": "found"},
        {"outcome": "missed"},
        {"outcome": "error"},
        {"outcome": "reference_changed"},
    ]
    assert summarize_results(results) == {
        "found": 1,
        "missed": 1,
        "errors": 1,
        "references_changed": 1,
        "target_hit_rate": 0.5,
    }
    assert summarize_results([{"outcome": "error"}])["target_hit_rate"] is None


def test_evaluation_checks_later_pages_and_keeps_the_same_search():
    requests = []

    def reply(request):
        body = json.loads(request.content)
        requests.append(body)
        if "page_token" not in body:
            return httpx.Response(
                200,
                json={
                    "studies": [{"id": "NCT87654321"}],
                    "more_results": True,
                    "next_page_token": "next",
                },
            )
        return httpx.Response(
            200,
            json={
                "studies": [{"id": "NCT12345678"}],
                "more_results": False,
                "next_page_token": None,
            },
        )

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(reply), base_url="http://local"
        ) as client:
            case = Case(
                id="one",
                language="English",
                query="condition",
                expected_id="NCT12345678",
            )
            return await search_across_pages(client, case, 2)

    result = asyncio.run(run())
    assert result["outcome"] == "found"
    assert result["first_page_outcome"] == "missed"
    assert result["pages_checked"] == 2
    assert result["returned_ids"] == ["NCT87654321", "NCT12345678"]
    assert requests[1] == {
        "condition": "condition",
        "open_studies_only": False,
        "page_token": "next",
    }


def test_failed_later_page_is_not_a_miss():
    def reply(request):
        body = json.loads(request.content)
        if "page_token" not in body:
            return httpx.Response(
                200,
                json={"studies": [], "more_results": True, "next_page_token": "next"},
            )
        return httpx.Response(502, json={"detail": "unavailable"})

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(reply), base_url="http://local"
        ) as client:
            case = Case(
                id="one",
                language="English",
                query="condition",
                expected_id="NCT12345678",
            )
            return await search_across_pages(client, case, 2)

    result = asyncio.run(run())
    assert result["outcome"] == "error"
    assert result["first_page_outcome"] == "missed"
    assert result["pages_checked"] == 1
    assert result["http_status"] == 502


def test_changed_reference_is_not_treated_as_a_current_answer():
    reference = Reference(
        id="NCT12345678",
        title="Study",
        source_url="https://clinicaltrials.gov/study/NCT12345678",
        record_updated="2024-01-01",
        reason="Condition and location checked",
    )
    record = {
        "protocolSection": {
            "identificationModule": {"nctId": "NCT12345678", "briefTitle": "Study"},
            "statusModule": {"lastUpdatePostDateStruct": {"date": "2024-01-01"}},
            "contactsLocationsModule": {"locations": [{"country": "Greece"}]},
        }
    }
    assert check_reference(reference, 200, record) == "current"
    record["protocolSection"]["statusModule"]["lastUpdatePostDateStruct"]["date"] = (
        "2025-01-01"
    )
    assert check_reference(reference, 200, record) == "changed"
    assert check_reference(reference, 503, {}) == "error"


def test_cli_fails_if_searches_could_not_be_measured(tmp_path, monkeypatch):
    case_file = tmp_path / "cases.json"
    report_file = tmp_path / "report.json"
    case_file.write_text(
        json.dumps(
            {
                "description": "Example cases",
                "references": [
                    {
                        "id": "NCT12345678",
                        "title": "Study",
                        "source_url": "https://clinicaltrials.gov/study/NCT12345678",
                        "record_updated": "2024-01-01",
                        "reason": "Checked",
                    }
                ],
                "cases": [
                    {
                        "id": "one",
                        "language": "English",
                        "query": "condition",
                        "expected_id": "NCT12345678",
                    }
                ],
            }
        )
    )

    async def fake_evaluate(dataset, dataset_sha256, max_pages):
        return {"summary": {"errors": 1, "references_changed": 0}}

    monkeypatch.setattr(evaluation, "evaluate", fake_evaluate)
    monkeypatch.setattr(
        sys,
        "argv",
        ["evaluation", "--cases", str(case_file), "--output", str(report_file)],
    )
    with pytest.raises(SystemExit) as error:
        evaluation.main()
    assert error.value.code == 1
    assert json.loads(report_file.read_text())["summary"]["errors"] == 1
