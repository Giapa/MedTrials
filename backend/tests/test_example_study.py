import httpx
from fastapi.testclient import TestClient

from backend.main import app, registry_client


def test_example_shows_record_and_greek_location():
    record = {
        "protocolSection": {
            "identificationModule": {
                "nctId": "NCT02798055",
                "briefTitle": "A registry study",
            },
            "statusModule": {
                "overallStatus": "COMPLETED",
                "lastUpdatePostDateStruct": {"date": "2019-07-05"},
            },
            "descriptionModule": {"briefSummary": "A study description."},
            "eligibilityModule": {
                "eligibilityCriteria": "Inclusion Criteria:\n\n* Must be an adult.\n\nExclusion Criteria:\n\n* Prior condition.",
                "minimumAge": "18 Years",
                "sex": "ALL",
                "healthyVolunteers": False,
            },
            "contactsLocationsModule": {
                "locations": [
                    {
                        "facility": "Athens Hospital",
                        "city": "Athens",
                        "country": "Greece",
                    },
                    {
                        "facility": "Other hospital",
                        "city": "Paris",
                        "country": "France",
                    },
                ]
            },
        }
    }

    async def mock_client():
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json=record)
        )
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).get("/api/example-study")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": "NCT02798055",
        "title": "A registry study",
        "summary": "A study description.",
        "eligibility": {
            "criteria": "Inclusion Criteria:\n\n* Must be an adult.\n\nExclusion Criteria:\n\n* Prior condition.",
            "minimum_age": "18 Years",
            "maximum_age": None,
            "sex": "ALL",
            "healthy_volunteers": False,
            "gender_based": None,
            "gender_description": None,
        },
        "status": "COMPLETED",
        "last_updated": "2019-07-05",
        "locations": [{"facility": "Athens Hospital", "city": "Athens"}],
        "source_url": "https://clinicaltrials.gov/study/NCT02798055",
    }


def test_invalid_registry_record_is_not_displayed():
    async def mock_client():
        transport = httpx.MockTransport(lambda request: httpx.Response(200, json={}))
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).get("/api/example-study")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502


def test_example_reports_registry_rate_limit():
    async def mock_client():
        transport = httpx.MockTransport(
            lambda request: httpx.Response(429, headers={"Retry-After": "120"})
        )
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).get("/api/example-study")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 429
