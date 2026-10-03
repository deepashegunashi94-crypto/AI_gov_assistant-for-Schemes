import requests


API_URL = (
    "https://www.myscheme.gov.in/"
    "api/apisetu/search/schemes"
)


def get_schemes(start, size):

    params = {
        "lang": "en",
        "q": "[]",
        "keyword": "",
        "sort": "",
        "from": start,
        "size": size
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=30
    )

    print("Status:", response.status_code)
    print("URL:", response.url)

    response.raise_for_status()

    return response.json()


print("=" * 60)
print("TESTING MYScheme API")
print("=" * 60)


data1 = get_schemes(
    start=0,
    size=10
)

print()
print("FIRST RESPONSE TYPE:")
print(type(data1))

print()
print("FIRST RESPONSE:")
print(data1)


data2 = get_schemes(
    start=10,
    size=10
)

print()
print("=" * 60)
print("SECOND PAGE")
print("=" * 60)

print(data2)