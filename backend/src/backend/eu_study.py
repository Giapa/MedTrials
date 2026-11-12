from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, ValidationError

from backend.registry import get_registry, registry_client

router = APIRouter()
TrialNumber = Annotated[str, Path(pattern=r"^[0-9]{4}-[0-9]{6}-[0-9]{2}-[0-9]{2}$")]


class Translation(BaseModel):
    languageDescription: str | None = None
    attributeTranslation: str | None = None


class Identifiers(BaseModel):
    publicTitle: str | None = None
    fullTitle: str | None = None
    publicTitleTranslations: list[Translation] = []
    fullTitleTranslations: list[Translation] = []


class Inclusion(BaseModel):
    principalInclusionCriteria: str | None = None
    principalInclusionCriteriaTranslations: list[Translation] = []


class Exclusion(BaseModel):
    principalExclusionCriteria: str | None = None
    principalExclusionCriteriaTranslations: list[Translation] = []


class Eligibility(BaseModel):
    principalInclusionCriteria: list[Inclusion] = []
    principalExclusionCriteria: list[Exclusion] = []


class TrialInformation(BaseModel):
    eligibilityCriteria: Eligibility = Eligibility()


class TrialDetails(BaseModel):
    clinicalTrialIdentifiers: Identifiers
    trialInformation: TrialInformation = TrialInformation()


class PartI(BaseModel):
    trialDetails: TrialDetails


class MemberState(BaseModel):
    mscName: str


class Application(BaseModel):
    memberStatesConcerned: list[MemberState]
    authorizedPartI: PartI


class EuropeanRecord(BaseModel):
    ctNumber: str
    authorizedApplication: Application


def greek_translation(translations: list[Translation]) -> str | None:
    for translation in translations:
        if (
            translation.languageDescription in ("Greek", "Greek (Greece)")
            and translation.attributeTranslation
            and translation.attributeTranslation.strip()
        ):
            return translation.attributeTranslation
    return None


def text_pair(
    english: str | None, translations: list[Translation]
) -> dict[str, str | None]:
    greek = greek_translation(translations)
    if not english or not english.strip():
        raise ValueError("Missing original text")
    return {"english": english, "greek": greek}


@router.get("/api/eu-studies/{trial_id}")
async def get_eu_study(
    trial_id: TrialNumber,
    client: Annotated[httpx.AsyncClient, Depends(registry_client)],
):
    try:
        response = await get_registry(
            client, f"https://euclinicaltrials.eu/ctis-public-api/retrieve/{trial_id}"
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Trial not found")
        if response.status_code == 429:
            raise HTTPException(status_code=429, detail="Registry connection is busy")
        response.raise_for_status()
        record = EuropeanRecord.model_validate(response.json())
        if record.ctNumber != trial_id:
            raise ValueError("Unexpected trial number")
        application = record.authorizedApplication
        if not any(
            state.mscName == "Greece" for state in application.memberStatesConcerned
        ):
            raise HTTPException(
                status_code=404, detail="Greece is not listed in the record"
            )
        details = application.authorizedPartI.trialDetails
        identifiers = details.clinicalTrialIdentifiers
        if identifiers.publicTitle and identifiers.publicTitle.strip():
            title = text_pair(
                identifiers.publicTitle, identifiers.publicTitleTranslations
            )
        else:
            title = text_pair(identifiers.fullTitle, identifiers.fullTitleTranslations)
        criteria = details.trialInformation.eligibilityCriteria
        inclusion = [
            text_pair(
                item.principalInclusionCriteria,
                item.principalInclusionCriteriaTranslations,
            )
            for item in criteria.principalInclusionCriteria
        ]
        exclusion = [
            text_pair(
                item.principalExclusionCriteria,
                item.principalExclusionCriteriaTranslations,
            )
            for item in criteria.principalExclusionCriteria
        ]
    except (httpx.HTTPError, ValidationError, ValueError) as error:
        raise HTTPException(
            status_code=502, detail="European registry unavailable or invalid"
        ) from error
    return {
        "id": trial_id,
        "title": title,
        "inclusion": inclusion,
        "exclusion": exclusion,
        "source_url": f"https://euclinicaltrials.eu/ctis-public/view/{trial_id}",
    }
