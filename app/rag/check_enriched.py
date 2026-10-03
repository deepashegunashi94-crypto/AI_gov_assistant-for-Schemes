import json
from pathlib import Path


FILE = Path("data/schemes/enriched_schemes.json")


with open(FILE, "r", encoding="utf-8") as f:
    schemes = json.load(f)


total = len(schemes)

eligibility_count = 0
benefits_count = 0
application_count = 0
description_count = 0


for scheme in schemes:

    details = scheme.get("details", {})

    eligibility = details.get("eligibility", {})
    benefits = details.get("benefits", {})
    description = details.get("description", {})
    application = details.get("applicationProcess", [])


    if eligibility:
        eligibility_count += 1

    if benefits.get("benefits") or benefits.get("benefits_md"):
        benefits_count += 1

    if application:
        application_count += 1

    if (
        description.get("brief")
        or description.get("detailed")
        or description.get("detailed_md")
    ):
        description_count += 1


print("=" * 50)
print("ENRICHED DATA QUALITY CHECK")
print("=" * 50)

print(f"Total schemes:        {total}")
print(f"Eligibility present:  {eligibility_count}")
print(f"Benefits present:     {benefits_count}")
print(f"Application present:  {application_count}")
print(f"Description present:  {description_count}")

print("=" * 50)