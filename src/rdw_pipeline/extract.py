import requests

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

if __name__ == "__main__":
    print(fetch_count(2015))

    a = fetch_page(0, 3, 2015)
    b = fetch_page(3, 3, 2015)
    c = fetch_page(0, 6, 2015)

    print([r["kenteken"] for r in a])
    print([r["kenteken"] for r in b])
    print([r["kenteken"] for r in c])
