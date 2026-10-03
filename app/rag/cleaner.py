import json
from pathlib import Path


INPUT_FILE = Path("data/schemes/all_schemes.json")
OUTPUT_FILE = Path("data/schemes/cleaned_schemes.json")


def clean_text(text):
    if not text:
        return ""

    unwanted = [
        "Enter scheme name to search...",
        "Sign In",
        "English",
        "Back",
        "Details",
        "Benefits",
        "Eligibility",
        "Application Process",
        "Documents Required",
        "Frequently Asked Questions",
        "Sources And References",
        "Feedback",
        "Check Eligibility",
        "Was this helpful?",
        "News and Updates",
        "No new news and updates available",
        "Share",
        "Quick Links",
        "Useful Links",
        "Get in touch",
    ]

    for item in unwanted:
        text = text.replace(item, " ")

    return " ".join(text.split())


def clean_scheme(scheme):

    return {
        "name": clean_text(scheme.get("name")),
        "description": clean_text(
            scheme.get("description")
        ),
        "eligibility": clean_text(
            scheme.get("eligibility")
        ),
        "benefits": clean_text(
            scheme.get("benefits")
        ),
        "documents": clean_text(
            scheme.get("documents")
        ),
        "application_process": clean_text(
            scheme.get("application_process")
        ),
        "official_url": scheme.get(
            "official_url",
            ""
        ),
        "source": scheme.get(
            "source",
            "myScheme"
        )
    }


def main():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        schemes = json.load(file)

    cleaned = []

    for scheme in schemes:

        item = clean_scheme(scheme)

        if item["name"]:
            cleaned.append(item)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            cleaned,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("=" * 60)
    print("CLEANING COMPLETED")
    print("=" * 60)
    print("Original schemes:", len(schemes))
    print("Cleaned schemes:", len(cleaned))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()