from rdw_pipeline.extract import fetch_count, fetch_all, save_raw
from rdw_pipeline.transform import raw_to_parquet
from rdw_pipeline.load import upload

YEAR = 2015

def main():
    before = fetch_count(YEAR)
    records = fetch_all(YEAR)
    after = fetch_count(YEAR)

    fetched = len(records)
    unique = len(set(r["kenteken"] for r in records))

    raw_path = save_raw(records, YEAR)
    print("ruw opgeslagen:", raw_path)

    if before != after:
        print(f"WAARSCHUWING: bron veranderd tijdens ophalen (voor: {before}, na: {after})")
    elif before == fetched == unique:
        print(f"compleet: {fetched} records")
    else:
        raise SystemExit(f"FOUT: voor={before}, opgehaald={fetched}, uniek={unique}")

    parquet_path, rows = raw_to_parquet(raw_path)
    print("parquet geschreven:", parquet_path, f"({rows} rijen)")

    gcs_uri = upload(parquet_path)
    print("geüpload naar:", gcs_uri)

if __name__ == "__main__":
    main()
