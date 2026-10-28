import json
from pathlib import Path

import pandas as pd

FIELDS = [
    "kenteken",
    "merk",
    "handelsbenaming",
    "datum_eerste_toelating_dt",
    "vervaldatum_apk_dt",
    "eerste_kleur",
    "catalogusprijs",
    "massa_ledig_voertuig",
    "aantal_zitplaatsen",
    "tellerstandoordeel",
]

def raw_to_parquet(raw_path):
    with open(raw_path) as f:
        records = json.load(f)

    df = pd.DataFrame(records)

    df = df.reindex(columns=FIELDS)

    out_path = f"data/processed/{Path(raw_path).stem}.parquet"
    df.to_parquet(out_path, index=False)

    return out_path, len(df)

if __name__ == "__main__":
    out_path, rows = raw_to_parquet("data/raw/up_2015_2026-10-28.json")
    print("geschreven:", out_path)
    print("rijen:", rows)
