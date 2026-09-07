# Happy Hours Kraków

FastAPI service and data pipeline for discovering current promotions in Kraków bars and cafés.

## Current architecture

- `main.py` — FastAPI application
- `api/routes/` — health, venue, deal, and HTML preview endpoints
- `services/` — database reads and active-deal logic
- `scraper/` — source fetching, parsing, validation, and enrichment
- `run_pipeline.py` — scrape → parse → validate → idempotent upsert
- `seed_data.py` — initial venue and deal data
- `database/migrations/` — database schema

## Local setup

Python 3.11 or newer is required for direct execution. If Python is not
installed, use the Docker setup below instead.

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in `SUPABASE_URL` and `SUPABASE_KEY` in `.env`. Apply
`database/migrations/001_initial_schema.sql` in the Supabase SQL editor, then
seed the database:

```powershell
python seed_data.py
```

Start the API:

```powershell
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is
at `/docs`, and the human-readable preview is at `/deals/preview`.

## Pipeline

Run the scraper locally:

```powershell
python run_pipeline.py
```

Without `ANTHROPIC_API_KEY`, the pipeline uses the deterministic mock parser and
still writes its parsed output to `scraper/pipeline_output.json`. With the key
configured, it uses Anthropic extraction. Pipeline writes use a deterministic
`dedupe_key`, so rerunning the job updates existing deals instead of inserting
duplicates.

Sources and their database venue names are maintained in
`scraper/scraper_config.py`. Add a source there only when the venue exists in
Supabase.

## Tests

The project uses the Python standard library test runner:

```powershell
python -m unittest discover -s tests -v
```

## Docker

Docker is the recommended setup when Python is unavailable. Docker Desktop
must be running, and `.env` must contain the Supabase credentials.

Build the application image:

```powershell
docker compose build
```

The image is built once and reused by the seed, pipeline, and API services.
The Docker build intentionally uses binary wheels where available, so the
first build may take a few minutes while dependencies download.

Seed the restored Supabase project:

```powershell
docker compose --profile tools run --rm seed
```

Run the scraper and upsert current source data:

```powershell
docker compose --profile tools run --rm pipeline
```

Start the API:

```powershell
docker compose up -d api
```

Stop the API:

```powershell
docker compose down
```

The API is then available at `http://127.0.0.1:8000`.

The equivalent single-container command is:

```powershell
docker build -t happy-hours-krakow .
docker run --env-file .env -p 8000:8000 happy-hours-krakow
```

## API examples

```text
GET /health
GET /venues/
GET /deals/
GET /deals/?active_now=true
GET /deals/preview
```

The public read policies in the migration allow the API to read venues and
deals using a Supabase anon key. Keep service-role keys out of source control.
