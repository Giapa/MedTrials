from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError

from backend.eu_search import router as eu_search_router
from backend.eu_study import router as eu_study_router
from backend.registry import RegistryStudy, get_registry, registry_client
from backend.search import router as search_router

app = FastAPI()
app.include_router(search_router)
app.include_router(eu_study_router)
app.include_router(eu_search_router)
EXAMPLE_ID = "NCT02798055"


@app.get("/api/example-study")
async def example_study(client: Annotated[httpx.AsyncClient, Depends(registry_client)]):
    try:
        response = await get_registry(
            client, f"https://clinicaltrials.gov/api/v2/studies/{EXAMPLE_ID}"
        )
        if response.status_code == 429:
            raise HTTPException(status_code=429, detail="Registry connection is busy")
        response.raise_for_status()
        study = RegistryStudy.model_validate(response.json()).protocolSection
        if study.identificationModule.nctId != EXAMPLE_ID:
            raise ValueError("Unexpected study identifier")
    except (httpx.HTTPError, ValidationError, ValueError) as error:
        raise HTTPException(
            status_code=502, detail="Registry unavailable or invalid"
        ) from error

    update = study.statusModule.lastUpdatePostDateStruct
    return {
        "id": study.identificationModule.nctId,
        "title": study.identificationModule.briefTitle,
        "summary": study.descriptionModule.briefSummary,
        "eligibility": study.eligibilityModule.model_dump(),
        "status": study.statusModule.overallStatus,
        "last_updated": update.date if update else None,
        "locations": [
            {"facility": location.facility, "city": location.city}
            for location in study.contactsLocationsModule.locations
            if location.country == "Greece"
        ],
        "source_url": f"https://clinicaltrials.gov/study/{EXAMPLE_ID}",
    }
