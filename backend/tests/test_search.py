from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import httpx
from fastapi.testclient import TestClient

from backend import registry
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
        "next_page_token": "more",
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
    assert response.json() == {
        "studies": [],
        "more_results": False,
        "next_page_token": None,
    }


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


def test_next_page_uses_the_original_search_and_registry_token():
    def reply(request):
        assert request.url.params["query.cond"] == "breast cancer"
        assert request.url.params["filter.advanced"] == "AREA[LocationCountry]Greece"
        assert (
            request.url.params["filter.overallStatus"]
            == "RECRUITING,NOT_YET_RECRUITING"
        )
        assert request.url.params["pageToken"] == "next-page"
        return httpx.Response(200, json={"studies": []})

    async def mock_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search",
            json={
                "condition": "breast cancer",
                "open_studies_only": True,
                "page_token": "next-page",
            },
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["next_page_token"] is None


def test_rate_limit_without_retry_header_recovers_after_one_pause(monkeypatch):
    attempts = 0
    waits = []

    def reply(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429)
        return httpx.Response(200, json={"studies": []})

    async def fake_wait(seconds):
        waits.append(seconds)

    async def mock_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            yield client

    monkeypatch.setattr(registry.asyncio, "sleep", fake_wait)
    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search", json={"condition": "diabetes"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert attempts == 2
    assert waits == [10]


def test_persistent_rate_limit_is_reported_without_unbounded_retries(monkeypatch):
    attempts = 0
    waits = []

    def reply(request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(429, headers={"Retry-After": "0"})

    async def fake_wait(seconds):
        waits.append(seconds)

    async def mock_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            yield client

    monkeypatch.setattr(registry.asyncio, "sleep", fake_wait)
    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search", json={"condition": "diabetes"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 429
    assert attempts == 2
    assert waits == [0]


def test_long_retry_after_is_not_shortened(monkeypatch):
    attempts = 0

    def reply(request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(429, headers={"Retry-After": "120"})

    async def fake_wait(seconds):
        raise AssertionError("Should not retry before requested delay")

    async def mock_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            yield client

    monkeypatch.setattr(registry.asyncio, "sleep", fake_wait)
    app.dependency_overrides[registry_client] = mock_client
    try:
        response = TestClient(app).post(
            "/api/studies/search", json={"condition": "diabetes"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 429
    assert attempts == 1


def test_retry_after_date_and_malformed_values_are_handled_safely():
    now = datetime(2026, 11, 12, 12, 0, tzinfo=UTC)
    assert registry.retry_delay(None, now) == 10
    assert registry.retry_delay("0", now) == 0
    assert (
        registry.retry_delay(
            format_datetime(now + timedelta(seconds=5), usegmt=True), now
        )
        == 5
    )
    assert (
        registry.retry_delay(
            format_datetime(now + timedelta(seconds=15), usegmt=True), now
        )
        is None
    )
    assert registry.retry_delay("not-a-date", now) is None
