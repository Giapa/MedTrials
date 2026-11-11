from collections.abc import AsyncIterator

import httpx
from pydantic import BaseModel


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
