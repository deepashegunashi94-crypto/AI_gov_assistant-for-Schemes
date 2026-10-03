import json
from pathlib import Path


INPUT_FILE = Path(
    "data/schemes/enriched_schemes.json"
)

OUTPUT_FILE = Path(
    "data/schemes/rag_documents.json"
)


def clean(value):

    if value is None:
        return ""

    if isinstance(value, list):
        return ", ".join(
            str(x) for x in value
        )

    if isinstance(value, dict):
        return json.dumps(
            value,
            ensure_ascii=False
        )

    return str(value)


def main():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        schemes = json.load(f)


    documents = []


    for scheme in schemes:

        details = scheme.get(
            "details",
            {}
        )

        basic = details.get(
            "basicDetails",
            {}
        )

        eligibility = details.get(
            "eligibility",
            {}
        )

        benefits = details.get(
            "benefits",
            {}
        )

        description = details.get(
            "description",
            {}
        )

        application = details.get(
            "applicationProcess",
            [] 
        )

        document = f"""
SCHEME NAME:
{clean(scheme.get("schemeName"))}

SHORT TITLE:
{clean(scheme.get("schemeShortTitle"))}

CATEGORY:
{clean(scheme.get("schemeCategory"))}

LEVEL:
{clean(scheme.get("level"))}

BENEFICIARY STATE:
{clean(scheme.get("beneficiaryState"))}

MINISTRY:
{clean(scheme.get("nodalMinistryName"))}

SCHEME FOR:
{clean(scheme.get("schemeFor"))}

TAGS:
{clean(scheme.get("tags"))}

DESCRIPTION:
{clean(description.get("brief"))}

DETAILED DESCRIPTION:
{clean(description.get("detailed"))}

ELIGIBILITY:
{clean(
    eligibility.get("eligibilityDescription")
)}

BENEFITS:
{clean(benefits.get("benefits"))}

BENEFIT TYPES:
{clean(benefits.get("benefitTypes"))}

APPLICATION PROCESS:
{clean(application)}

EXCLUSIONS:
{clean(details.get("exclusions"))}

REFERENCES:
{clean(details.get("references"))}

SLUG:
{clean(scheme.get("slug"))}
""".strip()


        documents.append({
            "id": scheme.get("id"),
            "schemeName": scheme.get(
                "schemeName"
            ),
            "slug": scheme.get("slug"),
            "category": scheme.get(
                "schemeCategory"
            ),
            "state": scheme.get(
                "beneficiaryState"
            ),
            "text": document
        })


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            documents,
            f,
            indent=2,
            ensure_ascii=False
        )


    print("=" * 60)
    print("RAG DOCUMENT PREPARATION COMPLETED")
    print("=" * 60)

    print(
        f"Documents created: {len(documents)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()