import requests

BASE_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"


def fetch_sample(limit=5):
    params = {
        "$where": "merk='VOLKSWAGEN' AND handelsbenaming in ('UP!', 'UP')",
        "$limit": limit,
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    records = fetch_sample()
    print(len(records))
    print(records[0])
