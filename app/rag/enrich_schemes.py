import requests
import json
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path(
    "data/schemes/balanced_schemes.json"
)

OUTPUT_FILE = Path(
    "data/schemes/enriched_schemes.json"
)


# ============================================================
# API
# ============================================================

API_URL = (
    "https://www.myscheme.gov.in/api/apisetu/schemes"
)

SCHEME_PAGE_URL = (
    "https://www.myscheme.gov.in/schemes/"
)


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.myscheme.gov.in/"
}


HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.myscheme.gov.in/"
}


# ============================================================
# FETCH API DETAILS
# ============================================================

def fetch_details(slug):

    params = {
        "slug": slug,
        "lang": "en"
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code != 200:

            print(
                f"API error for {slug}: "
                f"{response.status_code}"
            )

            return None

        data = response.json()

        return data.get(
            "data",
            {}
        )

    except Exception as e:

        print(
            f"Error fetching API details "
            f"for {slug}: {e}"
        )

        return None


# ============================================================
# FETCH PUBLIC SCHEME PAGE
# ============================================================

def fetch_scheme_page(slug):

    url = (
        SCHEME_PAGE_URL
        + str(slug)
    )

    try:

        response = requests.get(
            url,
            headers=HTML_HEADERS,
            timeout=30
        )

        if response.status_code != 200:

            print(
                f"Page error for {slug}: "
                f"{response.status_code}"
            )

            return None

        return response.text

    except Exception as e:

        print(
            f"Error fetching page "
            f"for {slug}: {e}"
        )

        return None


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if not text:

        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# CLEAN DOCUMENT
# ============================================================

def clean_document(text):

    text = clean_text(
        text
    )

    # Remove common numbering
    text = re.sub(
        r"^\s*\d+[\.\)]\s*",
        "",
        text
    )

    # Remove bullets
    text = re.sub(
        r"^[•●▪◦\-]+\s*",
        "",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT DOCUMENTS FROM PUBLIC PAGE
# ============================================================

def extract_documents_from_page(
    html
):

    if not html:

        return []

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    documents = []

    # ========================================================
    # METHOD 1
    # Search for heading containing
    # "Documents Required"
    # ========================================================

    headings = soup.find_all(
        [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "div",
            "span",
            "p"
        ]
    )

    document_heading = None

    for element in headings:

        text = clean_text(
            element.get_text(
                " ",
                strip=True
            )
        )

        normalized = (
            text
            .lower()
            .replace(":", "")
        )

        if normalized in [
            "documents required",
            "documents required."
        ]:

            document_heading = element

            break

    # ========================================================
    # If heading found, collect following list items
    # ========================================================

    if document_heading:

        # First look for the nearest parent section
        parent = (
            document_heading.parent
        )

        if parent:

            list_items = parent.find_all(
                "li"
            )

            for li in list_items:

                document = clean_document(
                    li.get_text(
                        " ",
                        strip=True
                    )
                )

                if (
                    document
                    and len(document) > 2
                    and document not in documents
                ):

                    documents.append(
                        document
                    )

        # If parent did not contain them,
        # inspect following siblings.
        if not documents:

            current = (
                document_heading
            )

            for _ in range(15):

                current = (
                    current.find_next_sibling()
                )

                if current is None:

                    break

                text = clean_text(
                    current.get_text(
                        " ",
                        strip=True
                    )
                )

                if (
                    text
                    .lower()
                    .startswith(
                        "frequently asked"
                    )
                ):

                    break

                for li in current.find_all(
                    "li"
                ):

                    document = clean_document(
                        li.get_text(
                            " ",
                            strip=True
                        )
                    )

                    if (
                        document
                        and document not in documents
                    ):

                        documents.append(
                            document
                        )

    # ========================================================
    # METHOD 2
    # Search raw text around Documents Required
    # ========================================================

    if not documents:

        full_text = soup.get_text(
            "\n",
            strip=True
        )

        lines = [
            clean_text(line)
            for line in full_text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        start_index = None

        for i, line in enumerate(lines):

            normalized = (
                line
                .lower()
                .replace(":", "")
            )

            if normalized in [
                "documents required",
                "documents required."
            ]:

                start_index = i

                break

        if start_index is not None:

            for line in lines[
                start_index + 1:
            ]:

                normalized = (
                    line.lower()
                )

                # Stop at next major section
                if any(
                    section in normalized
                    for section in [
                        "frequently asked questions",
                        "faq",
                        "contact",
                        "references",
                        "scheme image"
                    ]
                ):

                    break

                document = clean_document(
                    line
                )

                if (
                    document
                    and len(document) > 2
                    and document not in documents
                ):

                    documents.append(
                        document
                    )

    # ========================================================
    # Remove obviously incorrect values
    # ========================================================

    cleaned = []

    for document in documents:

        lower = (
            document.lower()
        )

        if lower in [
            "documents required",
            "application process",
            "online",
            "offline"
        ]:

            continue

        if (
            len(document) < 3
        ):

            continue

        if document not in cleaned:

            cleaned.append(
                document
            )

    return cleaned


# ============================================================
# FIND DOCUMENT FIELDS IN API
# ============================================================

def find_document_fields(
    obj,
    found=None
):

    if found is None:

        found = []

    if isinstance(
        obj,
        dict
    ):

        for key, value in obj.items():

            key_lower = (
                str(key).lower()
            )

            if (
                "document" in key_lower
                or "required_document" in key_lower
                or "documents_required" in key_lower
            ):

                if value not in [
                    None,
                    "",
                    [],
                    {}
                ]:

                    found.append(
                        {
                            "field": key,
                            "value": value
                        }
                    )

            find_document_fields(
                value,
                found
            )

    elif isinstance(
        obj,
        list
    ):

        for item in obj:

            find_document_fields(
                item,
                found
            )

    return found


# ============================================================
# EXTRACT API DOCUMENTS
# ============================================================

def extract_documents_from_api(
    english
):

    documents = []

    fields = find_document_fields(
        english
    )

    for field in fields:

        value = field.get(
            "value"
        )

        if isinstance(
            value,
            str
        ):

            document = clean_document(
                value
            )

            if document:

                documents.append(
                    document
                )

        elif isinstance(
            value,
            list
        ):

            for item in value:

                if isinstance(
                    item,
                    str
                ):

                    document = clean_document(
                        item
                    )

                    if document:

                        documents.append(
                            document
                        )

                elif isinstance(
                    item,
                    dict
                ):

                    for key in [
                        "name",
                        "title",
                        "document",
                        "documentName",
                        "description",
                        "label"
                    ]:

                        if item.get(
                            key
                        ):

                            document = clean_document(
                                item.get(key)
                            )

                            if document:

                                documents.append(
                                    document
                                )

                            break

    # Remove duplicates
    final_documents = []

    for document in documents:

        if document not in final_documents:

            final_documents.append(
                document
            )

    return final_documents


# ============================================================
# EXTRACT DETAILS
# ============================================================

def extract_details(
    data
):

    english = data.get(
        "en",
        {}
    )

    basic = english.get(
        "basicDetails",
        {}
    )

    eligibility = english.get(
        "eligibilityCriteria",
        {}
    )

    content = english.get(
        "schemeContent",
        {}
    )

    application = english.get(
        "applicationProcess",
        []
    )

    # --------------------------------------------------------
    # Documents from API
    # --------------------------------------------------------

    documents = (
        extract_documents_from_api(
            english
        )
    )

    # --------------------------------------------------------
    # Application URLs
    # --------------------------------------------------------

    application_urls = []

    if isinstance(
        application,
        list
    ):

        for step in application:

            if not isinstance(
                step,
                dict
            ):

                continue

            url = step.get(
                "url"
            )

            if url:

                url = str(
                    url
                ).strip()

                if (
                    url
                    and url not in application_urls
                ):

                    application_urls.append(
                        url
                    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "basicDetails": basic,

        "eligibility": eligibility,

        "benefits": {

            "benefitTypes": content.get(
                "benefitTypes",
                []
            ),

            "benefits": content.get(
                "benefits",
                ""
            ),

            "benefits_md": content.get(
                "benefits_md",
                ""
            )
        },

        "description": {

            "brief": content.get(
                "briefDescription",
                ""
            ),

            "detailed": content.get(
                "detailedDescription",
                ""
            ),

            "detailed_md": content.get(
                "detailedDescription_md",
                ""
            )
        },

        "documents": documents,

        "exclusions": content.get(
            "exclusions",
            ""
        ),

        "references": content.get(
            "references",
            []
        ),

        "applicationProcess": application,

        "applicationUrls": application_urls,

        "schemeImageUrl": content.get(
            "schemeImageUrl"
        )
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Loading schemes..."
    )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        schemes = json.load(
            f
        )

    print(
        f"Total schemes: "
        f"{len(schemes)}"
    )

    enriched = []

    api_documents_count = 0
    page_documents_count = 0
    total_documents_count = 0

    # ========================================================
    # PROCESS
    # ========================================================

    for index, scheme in enumerate(
        schemes,
        start=1
    ):

        slug = scheme.get(
            "slug"
        )

        scheme_name = scheme.get(
            "schemeName",
            "Unknown Scheme"
        )

        print(
            f"\n[{index}/{len(schemes)}] "
            f"{scheme_name}"
        )

        if not slug:

            print(
                "No slug - skipping"
            )

            continue

        # ====================================================
        # API DETAILS
        # ====================================================

        details = fetch_details(
            slug
        )

        if details:

            extracted = extract_details(
                details
            )

            print(
                "✓ API details fetched"
            )

        else:

            extracted = {}

            print(
                "✗ API details unavailable"
            )

        # ====================================================
        # DOCUMENTS FROM API
        # ====================================================

        api_documents = (
            extracted.get(
                "documents",
                []
            )
        )

        if api_documents:

            api_documents_count += 1

            print(
                f"  API documents: "
                f"{len(api_documents)}"
            )

        # ====================================================
        # PUBLIC PAGE
        # ====================================================

        page_html = fetch_scheme_page(
            slug
        )

        page_documents = []

        if page_html:

            page_documents = (
                extract_documents_from_page(
                    page_html
                )
            )

        if page_documents:

            page_documents_count += 1

            print(
                f"  Page documents: "
                f"{len(page_documents)}"
            )

        # ====================================================
        # COMBINE DOCUMENTS
        # ====================================================

        combined_documents = []

        for document in (
            api_documents
            + page_documents
        ):

            if (
                document
                and document not in combined_documents
            ):

                combined_documents.append(
                    document
                )

        extracted[
            "documents"
        ] = combined_documents

        total_documents_count += (
            len(combined_documents)
        )

        # ====================================================
        # APPLICATION PAGE
        # ====================================================

        extracted[
            "schemePageUrl"
        ] = (
            SCHEME_PAGE_URL
            + str(slug)
        )

        # ====================================================
        # SAVE
        # ====================================================

        scheme[
            "details"
        ] = extracted

        enriched.append(
            scheme
        )

        # Small delay
        time.sleep(
            0.5
        )

    # ========================================================
    # SAVE FILE
    # ========================================================

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
            enriched,
            f,
            indent=2,
            ensure_ascii=False
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 65
    )

    print(
        "ENRICHMENT COMPLETED"
    )

    print(
        "=" * 65
    )

    print(
        f"Total enriched records: "
        f"{len(enriched)}"
    )

    print(
        f"Schemes with API documents: "
        f"{api_documents_count}"
    )

    print(
        f"Schemes with page documents: "
        f"{page_documents_count}"
    )

    print(
        f"Total document entries: "
        f"{total_documents_count}"
    )

    print(
        f"Saved to: "
        f"{OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()