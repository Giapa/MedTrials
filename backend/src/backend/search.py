from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, StrictBool, StringConstraints, ValidationError

from backend.registry import RegistryStudy, registry_client

router = APIRouter()


class SearchRequest(BaseModel):
    condition: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
    ]
    open_studies_only: StrictBool = False


class RegistryResults(BaseModel):
    studies: list[RegistryStudy]
    nextPageToken: str | None = None


@router.post("/api/studies/search")
async def search_studies(
    query: SearchRequest,
    client: Annotated[httpx.AsyncClient, Depends(registry_client)],
):
    try:
        params = {
            "query.cond": query.condition,
            "filter.advanced": "AREA[LocationCountry]Greece",
            "pageSize": "10",
            "format": "json",
        }
        if query.open_studies_only:
            params["filter.overallStatus"] = "RECRUITING,NOT_YET_RECRUITING"
        response = await client.get(
            "https://clinicaltrials.gov/api/v2/studies", params=params
        )
        response.raise_for_status()
        registry_results = RegistryResults.model_validate(response.json())
        studies = []
        for record in registry_results.studies:
            study = record.protocolSection
            study_id = study.identificationModule.nctId
            if (
                len(study_id) != 11
                or not study_id.startswith("NCT")
                or not study_id[3:].isascii()
                or not study_id[3:].isdigit()
            ):
                raise ValueError("Invalid study identifier")
            locations = [
                {"facility": loc.facility, "city": loc.city, "status": loc.status}
                for loc in study.contactsLocationsModule.locations
                if loc.country == "Greece"
            ]
            if not locations:
                continue
            update = study.statusModule.lastUpdatePostDateStruct
            studies.append(
                {
                    "id": study_id,
                    "title": study.identificationModule.briefTitle,
                    "summary": study.descriptionModule.briefSummary,
                    "eligibility": study.eligibilityModule.model_dump(),
                    "status": study.statusModule.overallStatus,
                    "last_updated": update.date if update else None,
                    "locations": locations,
                    "source_url": f"https://clinicaltrials.gov/study/{study_id}",
                }
            )
    except (httpx.HTTPError, ValidationError, ValueError) as error:
        raise HTTPException(
            status_code=502, detail="Registry unavailable or invalid"
        ) from error
    return {
        "studies": studies,
        "more_results": registry_results.nextPageToken is not None,
    }
