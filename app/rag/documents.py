import json
from pathlib import Path


INPUT_FILE = Path(
    "data/schemes/cleaned_schemes.json"
)


def load_schemes():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def create_documents():

    schemes = load_schemes()

    documents = []

    for scheme in schemes:

        text = f"""
Scheme Name:
{scheme.get("name", "")}

Description:
{scheme.get("description", "")}

Eligibility:
{scheme.get("eligibility", "")}

Benefits:
{scheme.get("benefits", "")}

Documents Required:
{scheme.get("documents", "")}

Application Process:
{scheme.get("application_process", "")}

Official URL:
{scheme.get("official_url", "")}
"""

        documents.append({
            "text": text.strip(),
            "metadata": {
                "name": scheme.get("name", ""),
                "official_url": scheme.get(
                    "official_url",
                    ""
                ),
                "source": scheme.get(
                    "source",
                    "myScheme"
                )
            }
        })

    return documents