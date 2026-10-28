import requests
import json
from datetime import date

BASE_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"


def fetch_page(offset, limit, year):
    params = {
        "$where": f"merk='VOLKSWAGEN' AND handelsbenaming in ('UP!', 'UP') AND date_extract_y(datum_eerste_toelating_dt) = {year}",
        "$limit": limit,
        "$order": "kenteken",
        "$offset": offset,
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def fetch_count(year):
    params = {
        "$where": f"merk='VOLKSWAGEN' AND handelsbenaming in ('UP!', 'UP') AND date_extract_y(datum_eerste_toelating_dt) = {year}",
        "$select": "count(*) AS count",
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
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

    records = fetch_all(2015)
    kentekens = [r["kenteken"] for r in records]

    path = save_raw(records, 2015)
    print("opgeslagen:", path)

    print("verwacht:", fetch_count(2015))
    print("opgehaald:", len(records))
    print("uniek:", len(set(kentekens)))
