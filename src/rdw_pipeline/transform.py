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
