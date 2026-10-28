from enum import UNIQUE

import requests
import json
from datetime import date
import time

BASE_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
RETRY_STATUS = {429, 500, 502, 503, 504}

def get_with_retry(params, max_attempts=3, timeout=30):
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(BASE_URL, params=params, timeout=timeout)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt == max_attempts:
                raise
            wait = 2 ** attempt
            print(f"poging {attempt} mislukt ({type(e).__name__}), opnieuw over {wait}s")
            time.sleep(wait)
            continue

        if response.status_code in RETRY_STATUS and attempt < max_attempts:
            wait = 2 ** attempt
            print(f"poging {attempt} kreeg {response.status_code}, opnieuw over {wait}s")
            time.sleep(wait)
            continue

        response.raise_for_status()
        return response.json()

def fetch_page(offset, limit, year):
    params = {
        "$where": f"merk='VOLKSWAGEN' AND handelsbenaming in ('UP!', 'UP') AND date_extract_y(datum_eerste_toelating_dt) = {year}",
        "$limit": limit,
        "$order": "kenteken",
        "$offset": offset,
    }
    return get_with_retry(params)

def fetch_count(year):
    params = {
        "$where": f"merk='VOLKSWAGEN' AND handelsbenaming in ('UP!', 'UP') AND date_extract_y(datum_eerste_toelating_dt) = {year}",
        "$select": "count(*) AS count",
    }
    data = get_with_retry(params)
    first = data[0]
    count = first["count"]
    return int(count)

def fetch_all(year, page_size=1000):
    page_list = []
    offset = 0
    while True:
        page = fetch_page(offset, page_size, year)

        if not page:
            break

        page_list.extend(page)
        offset += page_size

    return page_list

def make_raw_path(year):
    today = date.today()
    return f"data/raw/up_{year}_{today}.json"

def save_raw(records, year):
    path = make_raw_path(year)
    with open(path, "w") as f:
        json.dump(records, f)
    return path


if __name__ == "__main__":
    before = fetch_count(2015)
    records = fetch_all(2015)
    after = fetch_count(2015)

    fetched = len(records)
    unique = len(set([r["kenteken"] for r in records]))

    path = save_raw(records, 2015)
    print("opgeslagen:", path)

    if before != after:
        print(f"WAARSCHUWING: bron veranderd tijdens ophalen (voor: {before}, na: {after})")
    elif before == unique == fetched:
        print(f"compleet: {fetched} records")
    else:
        print(f"FOUT: voor={before}, opgehaald={fetched}, uniek={unique}")
