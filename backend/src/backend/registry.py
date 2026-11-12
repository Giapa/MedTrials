import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

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


def retry_delay(header: str | None, now: datetime) -> float | None:
    if header is None:
        return 10
    if len(header) > 128:
        return None
    value = header.strip()
    if value.isascii() and value.isdigit():
        delay = float(int(value))
    else:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=UTC)
            delay = max(0.0, (retry_at - now).total_seconds())
        except TypeError, ValueError, OverflowError:
            return None
    return delay if delay <= 10 else None


async def get_registry(
    client: httpx.AsyncClient, url: str, *, params: dict[str, str] | None = None
) -> httpx.Response:
    response = await client.get(url, params=params)
    if response.status_code != 429:
        return response
    delay = retry_delay(response.headers.get("Retry-After"), datetime.now(UTC))
    if delay is None:
        return response
    await asyncio.sleep(delay)
    return await client.get(url, params=params)


async def registry_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=10) as client:
        yield client
