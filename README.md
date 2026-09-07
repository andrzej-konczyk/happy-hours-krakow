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

## Windows setup

Python 3.11 or newer is required. The setup script uses an existing Python
installation or installs Python 3.13 through Windows `winget`.

```powershell
.\setup.ps1
```

Fill in `SUPABASE_URL` and `SUPABASE_KEY` in `.env`. Apply
`database/migrations/001_initial_schema.sql` in the Supabase SQL editor, then
seed the database:

```powershell
.\.venv\Scripts\python.exe seed_data.py
```

Start the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is
at `/docs`, and the human-readable preview is at `/deals/preview`.

## Pipeline

Run the scraper locally:

```powershell
.\.venv\Scripts\python.exe run_pipeline.py
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
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
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
