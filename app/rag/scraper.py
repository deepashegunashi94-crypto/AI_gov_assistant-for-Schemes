import requests
import json
import time
from pathlib import Path


API_URL = "https://www.myscheme.gov.in/api/apisetu/search/schemes"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*"
}


# Number of schemes we want from each category
CATEGORY_LIMITS = {
    "Education & Learning": 200,
    "Social welfare & Empowerment": 200,
    "Agriculture,Rural & Environment": 200,
    "Business & Entrepreneurship": 150,
    "Banking,Financial Services and Insurance": 150,
    "Women and Child": 150,
    "Skills & Employment": 150,
    "Health & Wellness": 100,
    "Science, IT & Communications": 100,
    "Sports & Culture": 50,
    "Housing & Shelter": 50,
    "Other": 100
}


OUTPUT_FILE = Path("data/schemes/balanced_schemes.json")


def fetch_category(category, limit):

    print("\n" + "=" * 60)
    print(f"Fetching category: {category}")
    print(f"Target: {limit} schemes")
    print("=" * 60)

    schemes = []
    start = 0
    batch_size = 10

    while len(schemes) < limit:

        params = {
            "lang": "en",
            "q": json.dumps([
                {
                    "identifier": "schemeCategory",
                    "value": category
                }
            ]),
            "keyword": "",
            "sort": "",
            "from": start,
            "size": batch_size
        }

        response = requests.get(
            API_URL,
            params=params,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code != 200:
            print(
                f"API error: {response.status_code}"
            )
            break

        data = response.json()

        items = data.get(
            "data",
            {}
        ).get(
            "hits",
            {}
        ).get(
            "items",
            []
        )

        if not items:
            print("No more schemes available.")
            break

        for item in items:

            fields = item.get("fields", {})

            scheme = {
                "id": item.get("id"),
                "schemeName": fields.get("schemeName"),
                "schemeShortTitle": fields.get(
                    "schemeShortTitle"
                ),
                "slug": fields.get("slug"),
                "briefDescription": fields.get(
                    "briefDescription"
                ),
                "beneficiaryState": fields.get(
                    "beneficiaryState", []
                ),
                "level": fields.get("level"),
                "schemeCategory": fields.get(
                    "schemeCategory", []
                ),
                "nodalMinistryName": fields.get(
                    "nodalMinistryName"
                ),
                "schemeFor": fields.get("schemeFor"),
                "tags": fields.get("tags", []),
                "schemeCloseDate": fields.get(
                    "schemeCloseDate"
                )
            }

            schemes.append(scheme)

            if len(schemes) >= limit:
                break

        print(
            f"Collected {len(schemes)} / {limit}"
        )

        start += batch_size

        time.sleep(0.3)

    return schemes


def main():

    all_schemes = []

    for category, limit in CATEGORY_LIMITS.items():

        if category == "Other":
            continue

        schemes = fetch_category(
            category,
            limit
        )

        all_schemes.extend(schemes)

    # Remove duplicate schemes using ID
    unique_schemes = {}

    for scheme in all_schemes:

        scheme_id = scheme.get("id")

        if scheme_id:
            unique_schemes[scheme_id] = scheme

    all_schemes = list(unique_schemes.values())

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_schemes,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)
    print("SCRAPING COMPLETED")
    print("=" * 60)

    print(
        f"Total unique schemes: {len(all_schemes)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()