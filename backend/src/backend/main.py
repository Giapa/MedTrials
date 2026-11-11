from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

app = FastAPI()
EXAMPLE_ID = "NCT02798055"


class RegistryLocation(BaseModel):
    facility: str | None = None
    city: str | None = None
    country: str | None = None


class Identification(BaseModel):
    nctId: str
    briefTitle: str


class DateValue(BaseModel):
    date: str


class Status(BaseModel):
    overallStatus: str | None = None
    lastUpdatePostDateStruct: DateValue | None = None


class Description(BaseModel):
    briefSummary: str | None = None


class ContactsAndLocations(BaseModel):
    locations: list[RegistryLocation] = []


class Protocol(BaseModel):
    identificationModule: Identification
    statusModule: Status = Status()
    descriptionModule: Description = Description()
    contactsLocationsModule: ContactsAndLocations = ContactsAndLocations()


class RegistryStudy(BaseModel):
    protocolSection: Protocol


async def registry_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=10) as client:
        yield client


@app.get("/api/example-study")
async def example_study(client: Annotated[httpx.AsyncClient, Depends(registry_client)]):
    try:
        response = await client.get(
            f"https://clinicaltrials.gov/api/v2/studies/{EXAMPLE_ID}"
        )
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
        "status": study.statusModule.overallStatus,
        "last_updated": update.date if update else None,
        "locations": [
            {"facility": location.facility, "city": location.city}
            for location in study.contactsLocationsModule.locations
            if location.country == "Greece"
        ],
        "source_url": f"https://clinicaltrials.gov/study/{EXAMPLE_ID}",
    }
