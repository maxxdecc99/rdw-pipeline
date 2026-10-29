# RDW Vehicle Data Pipeline

A Python data pipeline that extracts vehicle registration data from the Dutch RDW open data API, verifies the transfer is complete, converts it to Parquet and uploads it to Google Cloud Storage.

It is built to handle the problems real data transfers run into: unreliable connections, source data that changes during the transfer, and fields that are missing or inconsistent.

## What it does

```
RDW API ──► extract ──► data/raw/*.json ──► transform ──► data/processed/*.parquet ──► load ──► GCS bucket
               │
               └── completeness check (stops the pipeline on failure)
```

1. **Extract** – fetches all Volkswagen up! records for a given year, page by page, and saves the raw response as JSON.
2. **Check** – counts records at the source before and after the transfer, and compares them with the number fetched and the number of unique license plates.
3. **Transform** – keeps a fixed set of fields and writes them to Parquet.
4. **Load** – uploads the Parquet file to a private Google Cloud Storage bucket.

## Problems I ran into and how I solved them

**Filter too broad.** A pattern filter (`like '%UP%'`) also matched LUPO, POLO COUPE and TRANSPORTER PICK-UP. I switched to an exact match on the two spellings the up! is registered under (`UP!` and `UP`).

**Unstable pagination.** The same request returned records in a different order each time. With offset-based paging, that can silently duplicate some records and skip others. Fixed by sorting on license plate (`kenteken`), which is unique per vehicle, and verified by checking that two half-pages equal one full page.

**The source changed during the transfer.** My completeness check caught a vehicle being added between fetching and counting (11,952 → 11,953). The pipeline now counts before *and* after: if the source changed it warns, and if the counts don't match it stops with exit code 1, so no incomplete data is delivered.

**A field that looked like text but wasn't.** `datum_eerste_toelating` arrives as a string in the JSON (`"20150312"`), but the API rejected a text pattern match on it with a 400 error, so it isn't stored as text. I filtered on the proper date field instead (`date_extract_y(datum_eerste_toelating_dt)`). Lesson: the format data arrives in doesn't tell you its real type.

**Missing fields.** The API leaves out empty fields instead of returning `null`, so records have different keys. The transform step uses a fixed schema, so the output always has the same columns.

**Unreliable connections.** Timeouts, connection errors and temporary server errors (429, 5xx) are retried with exponential backoff (2s, 4s). Permanent errors such as 400 are not retried, because repeating a bad request won't fix it.

## Results

For vehicles first registered in 2015:

| | |
|---|---|
| Records | 11,953 |
| Raw JSON (all ~50 fields + API links) | 23 MB |
| Parquet (10 selected fields) | 154 KB |

Most of the size reduction comes from dropping fields; the rest from Parquet's columnar storage and compression.

## Security

- The bucket is in `europe-west4` (Netherlands), with public access prevention enforced and uniform bucket-level access.
- No credentials in the code: the pipeline uses Application Default Credentials, stored outside the repository.
- Raw and processed data are excluded from Git via `.gitignore`.
- Raw data is kept locally so the transform step can be re-run without calling the API again.

## How to run

Requirements: Python 3.13, the `gcloud` CLI, and a Google Cloud project with a storage bucket.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

gcloud auth application-default login
```

Set your own project and bucket in `src/rdw_pipeline/load.py`, then run:

```bash
PYTHONPATH=src python -m rdw_pipeline.main
```

## Project structure

```
src/rdw_pipeline/
├── extract.py     # API calls, pagination, retries, saving raw data
├── transform.py   # raw JSON → Parquet with a fixed schema
├── load.py        # upload to Google Cloud Storage
└── main.py        # runs the pipeline and the completeness check
```

## Limitations and next steps

- **Validation and type conversion.** All values are still strings, and placeholder values such as `"Niet geregistreerd"` are not yet treated as missing.
- **Tests.** The pagination and completeness checks were tested by hand; they should become pytest tests.
- **Configuration.** Year, model, project and bucket are hardcoded; they should come from command-line arguments or environment variables.
- **Scheduling.** The pipeline runs locally; a next step is running it on a schedule, for example as a Cloud Run job.

## Data source

[RDW Open Data](https://opendata.rdw.nl/) – registered vehicles dataset.
