# MedTrials

An early portfolio project for finding clinical study information relevant to people in Greece. It searches ClinicalTrials.gov for a condition and shows records with a listed location in Greece. It also displays one example record.

The interface is available in Greek and English. Search currently works best with English condition terms; it does not yet interpret Greek descriptions or assess a person's eligibility. Study titles, summaries and the participation criteria text are shown as recorded by the registry, usually in English. The app also shows basic participation fields when reported and links to the original record. These fields may differ from the written criteria, and the registry text may not include all requirements. The app does not yet provide plain-language explanations of the criteria. Search results are not recommendations. The example was completed. Registry records can change, and a study's overall status does not tell you whether a particular location is recruiting. This tool provides information, not medical advice; discuss any study with a doctor and the study team.

The search checks at most the first 10 records returned by the registry, and excludes records without a listed Greek location. The optional recruitment filter uses the overall study status; it does not guarantee that a Greek site is recruiting. The app says when the registry reports more results; those additional records cannot yet be opened in the app. ClinicalTrials.gov does not include every study in Greece. An empty result is not proof that no relevant study exists.

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

These checks do not measure search quality or medical accuracy. A reviewed set of examples and quality measures will be added in a later stage. Cypress is not configured.
