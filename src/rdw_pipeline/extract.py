import requests

BASE_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"


def fetch_page(offset, limit):
    params = {
        "$where": "merk='VOLKSWAGEN' AND handelsbenaming in ('UP!', 'UP')",
        "$limit": limit,
        "$order": "kenteken",
        "$offset": offset,
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def fetch_count():
    params = {
        "$where": "merk='VOLKSWAGEN' AND handelsbenaming in ('UP!', 'UP')",
        "$select": "count(*) AS count"
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    first = data[0]
    count = first["count"]
    return int(count)

if __name__ == "__main__":
    print(fetch_count())

    a = fetch_page(0, 3)
    b = fetch_page(3, 3)
    c = fetch_page(0, 6)

    print([r["kenteken"] for r in a])
    print([r["kenteken"] for r in b])
    print([r["kenteken"] for r in c])
