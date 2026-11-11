import httpx
from fastapi.testclient import TestClient

from backend.main import app, registry_client


def test_search_returns_only_greek_locations_and_source_links():
    record = {
        "protocolSection": {
            "identificationModule": {
                "nctId": "NCT12345678",
                "briefTitle": "Study title",
            },
            "statusModule": {"overallStatus": "RECRUITING"},
            "contactsLocationsModule": {
                "locations": [
                    {
                        "facility": "Athens Hospital",
                        "city": "Athens",
                        "country": "Greece",
                        "status": "NOT_YET_RECRUITING",
                    },
                    {
                        "facility": "Paris Hospital",
                        "country": "France",
                        "status": "RECRUITING",
                    },
                ]
            },
        }
    }

    def reply(request):
        assert request.url.params["query.cond"] == "breast cancer"
        assert request.url.params["filter.advanced"] == "AREA[LocationCountry]Greece"
        return httpx.Response(200, json={"studies": [record], "nextPageToken": "more"})

    async def mock_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search", json={"condition": "breast cancer"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "studies": [
            {
                "id": "NCT12345678",
                "title": "Study title",
                "summary": None,
                "eligibility": {
                    "criteria": None,
                    "minimum_age": None,
                    "maximum_age": None,
                    "sex": None,
                    "healthy_volunteers": None,
                    "gender_based": None,
                    "gender_description": None,
                },
                "status": "RECRUITING",
                "last_updated": None,
                "locations": [
                    {
                        "facility": "Athens Hospital",
                        "city": "Athens",
                        "status": "NOT_YET_RECRUITING",
                    }
                ],
                "source_url": "https://clinicaltrials.gov/study/NCT12345678",
            }
        ],
        "more_results": True,
    }


def test_search_rejects_empty_condition():
    response = TestClient(app).post("/api/studies/search", json={"condition": "  "})
    assert response.status_code == 422


def test_search_reports_registry_failure():
    async def mock_client():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(503))
        ) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search", json={"condition": "diabetes"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 502


def test_search_omits_studies_without_a_greek_location():
    record = {
        "protocolSection": {
            "identificationModule": {"nctId": "NCT12345678", "briefTitle": "Study"},
            "contactsLocationsModule": {"locations": [{"country": "France"}]},
        }
    }

    async def mock_client():
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json={"studies": [record]})
        )
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search", json={"condition": "diabetes"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.json() == {"studies": [], "more_results": False}


def test_search_does_not_treat_invalid_registry_data_as_no_results():
    async def mock_client():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))
        ) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search", json={"condition": "diabetes"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 502


def test_search_rejects_invalid_health_volunteer_value():
    record = {
        "protocolSection": {
            "identificationModule": {"nctId": "NCT12345678", "briefTitle": "Study"},
            "eligibilityModule": {"healthyVolunteers": "false"},
            "contactsLocationsModule": {"locations": [{"country": "Greece"}]},
        }
    }

    async def mock_client():
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json={"studies": [record]})
        )
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search", json={"condition": "diabetes"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 502


def test_optional_recruitment_filter_is_sent_to_the_registry():
    def reply(request):
        assert (
            request.url.params["filter.overallStatus"]
            == "RECRUITING,NOT_YET_RECRUITING"
        )
        return httpx.Response(200, json={"studies": []})

    async def mock_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search",
            json={"condition": "diabetes", "open_studies_only": True},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
