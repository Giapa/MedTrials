# MedTrials

An early portfolio project for finding clinical study information relevant to people in Greece. It searches ClinicalTrials.gov for a condition and shows records with a listed location in Greece. It also displays one example record.

The interface is available in Greek and English. Search uses English condition terms; for eight specific Greek condition names and some simple phrases beginning with “έχω”, the app suggests a source-linked English term that the user may choose to use. It does not interpret general Greek descriptions or assess a person's eligibility. Study titles, summaries and the participation criteria text are shown as recorded by the registry, usually in English. The app also shows basic participation fields when reported and links each group of information to the relevant part of the original record. These fields may differ from the written criteria, and the registry text may not include all requirements. The app does not yet provide plain-language explanations of the criteria. Search results are not recommendations. The example was completed. Registry records can change, and a study's overall status does not tell you whether a particular location is recruiting. This tool provides information, not medical advice; discuss any study with a doctor and the study team.

The search displays registry records in pages of up to 10 and excludes records without a listed Greek location. When more records are available, select “Load more studies” to request the next page. The optional recruitment filter uses the overall study status; it does not guarantee that a Greek site is recruiting. ClinicalTrials.gov does not include every study in Greece. An empty result is not proof that no relevant study exists.

Greek suggestions work only for a small list of condition names and simple “έχω” phrases. They allow certain spelling variants and differences in case, accents, spacing, and a final full stop. They do not interpret general descriptions, negatives, or extra medical details. The app asks the user to choose a suggestion before searching and does not send the Greek text to a translation service. Unsupported Greek text cannot be submitted; use an English term or open the linked EMA trial map separately. The map searches a different source; its results are not integrated into this app. Check what information you share on any external site.

## Run locally

You need Python 3.14, [uv](https://docs.astral.sh/uv/), Node.js 22.22.2 or newer in the Node 22 line (or 24.15.0 or newer), and npm 11. An internet connection is needed to install dependencies and load the study. The commands below use two terminals.

In the first terminal:

```sh
cd backend
uv sync --locked
uv run uvicorn backend.main:app --reload
```

In the second terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite. The backend fetches the example directly from ClinicalTrials.gov on each load. A search sends the entered condition to ClinicalTrials.gov; do not enter names, contact details, or other identifying information. The app does not save searches. If the registry cannot be reached or returns invalid data, the page shows an error instead of claiming there are no results.

If the registry connection responds that it is receiving too many requests, the app retries once. It waits ten seconds when no retry time is supplied; if a valid retry time is supplied, it waits for that time only when it is at most ten seconds. Otherwise it does not retry automatically. If the limit persists, the page says the connection is busy. Previously loaded results stay visible. This does not guarantee availability when traffic is high.

## Checks

In `backend/`:

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

In `frontend/`:

```sh
npm run test:unit
npm run build
npm run lint
npm run format:check
```

The [search evaluation](backend/evaluation/README.md) contains a small set of fictional searches and linked reference records, plus a command to measure whether the app shows each selected record. The [Greek suggestion evaluation](frontend/evaluation/README.md) separately checks the search form against fictional examples, including cases where it should not suggest a term. Some examples informed development, so neither set is independent evidence of search quality. Neither the suggestions nor the evaluations have been reviewed by a clinician. Cypress is not configured.
