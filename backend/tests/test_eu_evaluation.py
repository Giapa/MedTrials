import asyncio
import json
import sys

import httpx
import pytest

from backend import eu_evaluation
from backend.eu_evaluation import (
    Case,
    Dataset,
    Reference,
    check_reference,
    search_across_pages,
)


def example_reference():
    return Reference(
        id="2025-522985-60-00",
        title="Trial title",
        condition="Non-small cell lung cancer",
        source_url="https://euclinicaltrials.eu/ctis-public/view/2025-522985-60-00",
        reason="Published condition and Greece listing.",
    )


def example_record():
    return {
        "ctNumber": "2025-522985-60-00",
        "authorizedApplication": {
            "memberStatesConcerned": [{"mscName": "Greece"}],
            "authorizedPartI": {
                "trialDetails": {
                    "clinicalTrialIdentifiers": {"publicTitle": "Trial title"},
                    "trialInformation": {
                        "medicalCondition": {
                            "partIMedicalConditions": [
                                {"medicalCondition": "Non-small cell lung cancer"}
                            ]
                        }
                    },
                }
            },
        },
    }


def test_reference_checks_country_title_condition_and_source():
    ref = example_reference()
    record = example_record()
    assert check_reference(ref, 200, record) == "current"
    record["authorizedApplication"]["memberStatesConcerned"] = [{"mscName": "France"}]
    assert check_reference(ref, 200, record) == "changed"
    record = example_record()
    record["authorizedApplication"]["authorizedPartI"]["trialDetails"][
        "trialInformation"
    ]["medicalCondition"]["partIMedicalConditions"][0][
        "medicalCondition"
    ] = "Small cell lung cancer"
    assert check_reference(ref, 200, record) == "changed"
    assert check_reference(ref, 200, {}) == "error"
    assert check_reference(ref, 503, {}) == "error"


def test_search_checks_all_pages_for_target_and_known_mismatch():
    requests = []

    def reply(request):
        body = json.loads(request.content)
        requests.append(body)
        if body["page"] == 1:
            return httpx.Response(
                200,
                json={
                    "page": 1,
                    "total": 2,
                    "more_results": True,
                    "studies": [{"id": "2025-525026-35-00"}],
                },
            )
        return httpx.Response(
            200,
            json={
                "page": 2,
                "total": 2,
                "more_results": False,
                "studies": [{"id": "2025-522985-60-00"}],
            },
        )

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(reply), base_url="http://local"
        ) as client:
            case = Case(
                id="lung",
                query="small cell lung cancer",
                relevant_id="2025-525026-35-00",
                mismatch_ids=["2025-522985-60-00"],
            )
            return await search_across_pages(client, case, 2)

    result = asyncio.run(run())
    assert result["outcome"] == "found"
    assert result["first_page_outcome"] == "found"
    assert result["pages_checked"] == 2
    assert result["known_mismatches_shown"] == ["2025-522985-60-00"]
    assert requests == [
        {"condition": "small cell lung cancer", "page": 1},
        {"condition": "small cell lung cancer", "page": 2},
    ]


def test_failure_on_later_page_is_not_scored_as_complete():
    def reply(request):
        body = json.loads(request.content)
        if body["page"] == 1:
            return httpx.Response(
                200,
                json={
                    "page": 1,
                    "total": 2,
                    "more_results": True,
                    "studies": [{"id": "2025-525026-35-00"}],
                },
            )
        return httpx.Response(429, json={"detail": "busy"})

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(reply), base_url="http://local"
        ) as client:
            case = Case(
                id="lung",
                query="small cell lung cancer",
                relevant_id="2025-525026-35-00",
                mismatch_ids=[],
            )
            return await search_across_pages(client, case, 2)

    result = asyncio.run(run())
    assert result["outcome"] == "error"
    assert result["first_page_outcome"] == "found"
    assert result["pages_checked"] == 1
    assert result["http_status"] == 429


def test_dataset_rejects_unknown_or_conflicting_references_before_search():
    dataset = Dataset(
        description="Examples",
        references=[example_reference()],
        cases=[Case(id="one", query="asthma", relevant_id="2025-525026-35-00")],
    )
    with pytest.raises(ValueError, match="known records"):
        asyncio.run(eu_evaluation.evaluate(dataset, "hash", 1))
    dataset.cases[0].relevant_id = "2025-522985-60-00"
    dataset.cases[0].mismatch_ids = ["2025-522985-60-00"]
    with pytest.raises(ValueError, match="differ"):
        asyncio.run(eu_evaluation.evaluate(dataset, "hash", 1))


def test_cli_exits_with_error_if_results_could_not_be_measured(tmp_path, monkeypatch):
    case_file = tmp_path / "cases.json"
    report_file = tmp_path / "report.json"
    dataset = Dataset(
        description="Examples",
        references=[example_reference()],
        cases=[Case(id="one", query="asthma", relevant_id="2025-522985-60-00")],
    )
    case_file.write_text(dataset.model_dump_json())

    async def fake_evaluation(_dataset, _hash, _max_pages):
        return {"summary": {"errors": 1, "references_changed": 0}}

    monkeypatch.setattr(eu_evaluation, "evaluate", fake_evaluation)
    monkeypatch.setattr(
        sys,
        "argv",
        ["evaluate", "--cases", str(case_file), "--output", str(report_file)],
    )
    with pytest.raises(SystemExit) as result:
        eu_evaluation.main()
    assert result.value.code == 1
    assert json.loads(report_file.read_text())["summary"]["errors"] == 1
