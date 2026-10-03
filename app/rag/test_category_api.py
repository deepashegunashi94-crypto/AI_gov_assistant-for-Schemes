import requests

url = "https://www.myscheme.gov.in/api/apisetu/search/schemes"

params = {
    "lang": "en",
    "q": '[{"identifier":"schemeCategory","value":"Education & Learning"}]',
    "keyword": "",
    "sort": "",
    "from": 0,
    "size": 10
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*"
}

response = requests.get(url, params=params, headers=headers)

print("Status:", response.status_code)

data = response.json()

items = data["data"]["hits"]["items"]

print("\nEducation & Learning schemes:\n")

for i, item in enumerate(items, start=1):

    fields = item["fields"]

    print(
        f"{i}. {fields.get('schemeName')}"
    )

print("\nTotal:", len(items))