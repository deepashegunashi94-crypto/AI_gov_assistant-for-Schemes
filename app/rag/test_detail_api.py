import requests
import json

url = "https://www.myscheme.gov.in/api/apisetu/schemes"

params = {
    "slug": "rtif",
    "lang": "en"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.myscheme.gov.in/schemes/rtif"
}

response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=30
)

print("Status:", response.status_code)
print("URL:", response.url)

try:
    data = response.json()

    print("\nJSON RESPONSE:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

except Exception:
    print("\nRaw response:")
    print(response.text[:10000])