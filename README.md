# MedTrials

An early portfolio project for finding clinical study information relevant to people in Greece. This first stage displays one real example record from ClinicalTrials.gov. It is not yet a trial search tool.

The interface is available in Greek and English. The study title and summary are shown in the original English from the registry. The example was completed and is not a recommendation. The registry record can change, and a study's overall status does not tell you whether a particular location is recruiting. This tool provides information, not medical advice; discuss any study with a doctor and the study team.

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

Open the local URL printed by Vite. The backend fetches the example directly from ClinicalTrials.gov on each load; it does not store searches. This stage does not ask for personal information. If the registry cannot be reached or returns invalid data, the page shows an error and lets you retry.

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

These checks do not measure search quality or medical accuracy. A reviewed set of examples and quality measures will be added when search and explanations exist. Cypress is not configured.
