from collections.abc import AsyncIterator

import httpx
from pydantic import BaseModel, Field, StrictBool


class RegistryLocation(BaseModel):
    facility: str | None = None
    city: str | None = None
    country: str | None = None
    status: str | None = None


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


class Eligibility(BaseModel):
    criteria: str | None = Field(default=None, validation_alias="eligibilityCriteria")
    minimum_age: str | None = Field(default=None, validation_alias="minimumAge")
    maximum_age: str | None = Field(default=None, validation_alias="maximumAge")
    sex: str | None = None
    healthy_volunteers: StrictBool | None = Field(
        default=None, validation_alias="healthyVolunteers"
    )
    gender_based: StrictBool | None = Field(
        default=None, validation_alias="genderBased"
    )
    gender_description: str | None = Field(
        default=None, validation_alias="genderDescription"
    )


class Protocol(BaseModel):
    identificationModule: Identification
    statusModule: Status = Status()
    descriptionModule: Description = Description()
    eligibilityModule: Eligibility = Eligibility()
    contactsLocationsModule: ContactsAndLocations = ContactsAndLocations()


class RegistryStudy(BaseModel):
    protocolSection: Protocol


async def registry_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=10) as client:
        yield client
