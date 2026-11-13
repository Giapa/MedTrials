import httpx
from fastapi.testclient import TestClient

from backend.main import app, registry_client

TRIAL_ID = "2025-522873-12-00"


def record():
    return {
        "ctNumber": TRIAL_ID,
        "authorizedApplication": {
            "memberStatesConcerned": [{"mscName": "Greece"}, {"mscName": "France"}],
            "authorizedPartI": {
                "trialDetails": {
                    "clinicalTrialIdentifiers": {
                        "publicTitle": "A public title",
                        "publicTitleTranslations": [
                            {
                                "languageDescription": "Greek (Greece)",
                                "attributeTranslation": "Δημόσιος τίτλος",
                            }
                        ],
                    },
                    "trialInformation": {
                        "trialObjective": {
                            "mainObjective": "Compare the two treatments.",
                            "mainObjectiveTranslations": [
                                {
                                    "languageDescription": "Greek (Greece)",
                                    "attributeTranslation": "Σύγκριση των δύο θεραπειών.",
                                }
                            ],
                        },
                        "eligibilityCriteria": {
                            "principalInclusionCriteria": [
                                {
                                    "principalInclusionCriteria": "Adult participants",
                                    "principalInclusionCriteriaTranslations": [
                                        {
                                            "languageDescription": "Greek (Greece)",
                                            "attributeTranslation": "Ενήλικες συμμετέχοντες",
                                        }
                                    ],
                                }
                            ],
                            "principalExclusionCriteria": [
                                {
                                    "principalExclusionCriteria": "Prior treatment",
                                    "principalExclusionCriteriaTranslations": [],
                                }
                            ],
                        },
                    },
                }
            },
        },
    }


def call_lookup(payload, trial_id=TRIAL_ID, status=200):
    async def mock_client():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    status, json=payload, headers={"Retry-After": "120"}
                )
            )
        ) as client:
            yield client

    app.dependency_overrides[registry_client] = mock_client
    try:
        return TestClient(app).get(f"/api/eu-studies/{trial_id}")
    finally:
        app.dependency_overrides.clear()


def test_returns_greek_translations_and_original_criteria_with_source():
    response = call_lookup(record())
    assert response.status_code == 200
    assert response.json() == {
        "id": TRIAL_ID,
        "title": {"english": "A public title", "greek": "Δημόσιος τίτλος"},
        "objective": {
            "english": "Compare the two treatments.",
            "greek": "Σύγκριση των δύο θεραπειών.",
        },
        "inclusion": [
            {"english": "Adult participants", "greek": "Ενήλικες συμμετέχοντες"}
        ],
        "exclusion": [{"english": "Prior treatment", "greek": None}],
        "source_url": f"https://euclinicaltrials.eu/ctis-public/view/{TRIAL_ID}",
    }


def test_does_not_show_record_when_greece_is_not_listed():
    data = record()
    data["authorizedApplication"]["memberStatesConcerned"] = [{"mscName": "France"}]
    assert call_lookup(data).status_code == 404


def test_refuses_mismatched_or_malformed_source_records():
    data = record()
    data["ctNumber"] = "2024-111111-11-11"
    assert call_lookup(data).status_code == 502
    assert call_lookup({}).status_code == 502
    data = record()
    del data["authorizedApplication"]["memberStatesConcerned"]
    assert call_lookup(data).status_code == 502


def test_missing_criteria_are_not_presented_as_rules():
    data = record()
    del data["authorizedApplication"]["authorizedPartI"]["trialDetails"][
        "trialInformation"
    ]
    response = call_lookup(data)
    assert response.status_code == 200
    assert response.json()["inclusion"] == []
    assert response.json()["exclusion"] == []
    assert response.json()["objective"] is None


def test_preserves_missing_and_greek_only_objectives():
    data = record()
    objective = data["authorizedApplication"]["authorizedPartI"]["trialDetails"][
        "trialInformation"
    ]["trialObjective"]
    objective["mainObjectiveTranslations"] = []
    assert call_lookup(data).json()["objective"] == {
        "english": "Compare the two treatments.",
        "greek": None,
    }
    objective["mainObjective"] = None
    objective["mainObjectiveTranslations"] = [
        {
            "languageDescription": "Greek (Greece)",
            "attributeTranslation": "Σύγκριση θεραπειών.",
        }
    ]
    assert call_lookup(data).json()["objective"] == {
        "english": None,
        "greek": "Σύγκριση θεραπειών.",
    }
    objective["mainObjectiveTranslations"] = []
    assert call_lookup(data).json()["objective"] is None
    objective["mainObjective"] = "   "
    objective["mainObjectiveTranslations"] = [
        {
            "languageDescription": "French (France)",
            "attributeTranslation": "Texte français",
        }
    ]
    assert call_lookup(data).json()["objective"] is None


def test_reports_source_failure_and_invalid_id():
    assert call_lookup({}, status=503).status_code == 502
    assert call_lookup({}, status=429).status_code == 429
    assert call_lookup({}, status=404).status_code == 404
    assert call_lookup({}, trial_id="not-an-id").status_code == 422
