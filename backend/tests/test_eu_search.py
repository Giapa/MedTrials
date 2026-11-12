import json

import httpx
from fastapi.testclient import TestClient

from backend.main import app, registry_client


def source_response():
    return {
        "pagination": {
            "totalRecords": 11,
            "currentPage": 1,
            "totalPages": 2,
            "nextPage": True,
        },
        "data": [
            {
                "ctNumber": "2025-522873-12-00",
                "ctTitle": "Breast cancer trial",
                "conditions": "Advanced breast cancer",
                "trialCountries": ["Greece:4", "France:4"],
            }
        ],
    }


def perform_search(payload, response_data=None, response_status=200):
    requests = []

    def reply(request):
        requests.append(request)
        return httpx.Response(response_status, json=response_data)

    async def mock_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post("/api/eu-studies/search", json=payload)
    finally:
        app.dependency_overrides.clear()
    return response, requests


def test_search_uses_greece_filter_and_returns_source_link():
    response, requests = perform_search(
        {"condition": "breast cancer"}, source_response()
    )
    assert response.status_code == 200
    sent = json.loads(requests[0].content)
    assert sent["searchCriteria"] == {"medicalCondition": "breast cancer", "msc": [300]}
    assert sent["pagination"] == {"page": 1, "size": 10}
    assert response.json() == {
        "studies": [
            {
                "id": "2025-522873-12-00",
                "title": "Breast cancer trial",
                "condition": "Advanced breast cancer",
                "source_url": "https://euclinicaltrials.eu/ctis-public/view/2025-522873-12-00",
            }
        ],
        "total": 11,
        "page": 1,
        "more_results": True,
    }


def test_rejects_records_without_greece_or_valid_identifiers():
    data = source_response()
    data["data"][0]["trialCountries"] = ["France:4"]
    assert perform_search({"condition": "breast cancer"}, data)[0].status_code == 502
    data = source_response()
    data["data"][0]["ctNumber"] = "bad-id"
    assert perform_search({"condition": "breast cancer"}, data)[0].status_code == 502
    data = source_response()
    data["data"][0]["trialCountries"] = ["Greece:"]
    assert perform_search({"condition": "breast cancer"}, data)[0].status_code == 502


def test_missing_or_inconsistent_pagination_is_an_error():
    data = source_response()
    del data["pagination"]
    assert perform_search({"condition": "breast cancer"}, data)[0].status_code == 502
    data = source_response()
    data["pagination"]["currentPage"] = 2
    assert perform_search({"condition": "breast cancer"}, data)[0].status_code == 502


def test_requests_next_page_and_keeps_null_condition_missing():
    data = source_response()
    data["pagination"]["currentPage"] = 2
    data["pagination"]["nextPage"] = False
    data["data"][0]["conditions"] = None
    response, requests = perform_search({"condition": "breast cancer", "page": 2}, data)
    assert response.status_code == 200
    assert json.loads(requests[0].content)["pagination"]["page"] == 2
    assert response.json()["studies"][0]["condition"] is None
    assert response.json()["more_results"] is False


def test_search_reports_source_errors_and_rejects_invalid_inputs():
    assert perform_search({"condition": "asthma"}, {}, 429)[0].status_code == 429
    assert perform_search({"condition": "asthma"}, {}, 503)[0].status_code == 502
    assert perform_search({"condition": "  "})[0].status_code == 422
    assert perform_search({"condition": "asthma", "page": 0})[0].status_code == 422
