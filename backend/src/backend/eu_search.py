import re
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, StrictBool, StringConstraints, ValidationError

from backend.registry import registry_client

router = APIRouter()


class SearchRequest(BaseModel):
    condition: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
    ]
    page: Annotated[int, Field(strict=True, ge=1, le=10000)] = 1


class Trial(BaseModel):
    ctNumber: Annotated[
        str, StringConstraints(pattern=r"^[0-9]{4}-[0-9]{6}-[0-9]{2}-[0-9]{2}$")
    ]
    ctTitle: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    conditions: str | None = None
    trialCountries: list[str]


class Pagination(BaseModel):
    totalRecords: Annotated[int, Field(strict=True, ge=0)]
    currentPage: Annotated[int, Field(strict=True, ge=1)]
    totalPages: Annotated[int, Field(strict=True, ge=0)]
    nextPage: StrictBool


class SearchResults(BaseModel):
    data: Annotated[list[Trial], Field(max_length=10)]
    pagination: Pagination


@router.post("/api/eu-studies/search")
async def search_european_studies(
    query: SearchRequest,
    client: Annotated[httpx.AsyncClient, Depends(registry_client)],
):
    try:
        response = await client.post(
            "https://euclinicaltrials.eu/ctis-public-api/search",
            json={
                "pagination": {"page": query.page, "size": 10},
                "sort": {"property": "decisionDate", "direction": "DESC"},
                "searchCriteria": {"medicalCondition": query.condition, "msc": [300]},
            },
        )
        if response.status_code == 429:
            raise HTTPException(
                status_code=429, detail="European registry connection is busy"
            )
        response.raise_for_status()
        results = SearchResults.model_validate(response.json())
        pagination = results.pagination
        if pagination.currentPage != query.page or pagination.nextPage != (
            query.page < pagination.totalPages
        ):
            raise ValueError("Inconsistent registry pagination")
        if any(
            not any(
                re.fullmatch(r"Greece:[0-9]+", country)
                for country in trial.trialCountries
            )
            for trial in results.data
        ):
            raise ValueError("Registry result does not list Greece")
    except (httpx.HTTPError, ValidationError, ValueError) as error:
        raise HTTPException(
            status_code=502, detail="European registry unavailable or invalid"
        ) from error
    return {
        "studies": [
            {
                "id": trial.ctNumber,
                "title": trial.ctTitle,
                "condition": trial.conditions,
                "source_url": f"https://euclinicaltrials.eu/ctis-public/view/{trial.ctNumber}",
            }
            for trial in results.data
        ],
        "total": pagination.totalRecords,
        "page": pagination.currentPage,
        "more_results": pagination.nextPage,
    }
