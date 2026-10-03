import ast
import html
import json
import re
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INDEX_PATH = BASE_DIR / "vectorstore" / "schemes.index"
METADATA_PATH = BASE_DIR / "vectorstore" / "metadata.json"
ENRICHED_PATH = BASE_DIR / "data" / "schemes" / "enriched_schemes.json"


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


# ============================================================
# LOAD FAISS INDEX
# ============================================================

index = faiss.read_index(
    str(INDEX_PATH)
)


# ============================================================
# LOAD METADATA
# ============================================================

with open(
    METADATA_PATH,
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)


# ============================================================
# LOAD ENRICHED DATA
# ============================================================

with open(
    ENRICHED_PATH,
    "r",
    encoding="utf-8"
) as f:

    enriched = json.load(f)


if isinstance(enriched, dict):

    enriched_records = (
        enriched.get("schemes")
        or enriched.get("data")
        or enriched.get("results")
        or []
    )

else:

    enriched_records = enriched


ENRICHED_BY_SLUG = {}

for item in enriched_records:

    if not isinstance(item, dict):
        continue

    slug = str(
        item.get("slug", "")
    ).strip()

    if slug:

        ENRICHED_BY_SLUG[slug] = item


# ============================================================
# RICH TEXT CLEANING
# ============================================================

STRUCTURAL_KEYS = {
    "id",
    "type",
    "label",
    "align",
    "class",
    "className",
    "bold",
    "italic",
    "underline",
    "style",
    "format",
    "level",
    "key",
    "nodeType",
    "entityRanges",
    "data"
}


IMPORTANT_KEYS = [
    "text",
    "children",
    "brief",
    "description",
    "description_md",
    "process",
    "process_md",
    "benefits",
    "benefits_md",
    "eligibility",
    "eligibilityDescription",
    "eligibilityDescription_md",
    "documents",
    "documentsRequired"
]


def parse_serialized_value(value):

    if not isinstance(value, str):

        return value

    text = value.strip()

    if not text:
        return ""

    # Only try parsing strings that look like
    # Python/JSON structures.

    if not (
        (
            text.startswith("{")
            and text.endswith("}")
        )
        or
        (
            text.startswith("[")
            and text.endswith("]")
        )
    ):

        return value

    try:

        return ast.literal_eval(
            text
        )

    except Exception:

        try:

            return json.loads(
                text
            )

        except Exception:

            return value


def flatten_rich_value(value):

    value = parse_serialized_value(
        value
    )


    # --------------------------------------------------------
    # EMPTY / BOOLEAN
    # --------------------------------------------------------

    if value is None:

        return ""


    if isinstance(value, bool):

        return ""


    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    if isinstance(value, str):

        parsed = parse_serialized_value(
            value
        )

        if parsed is not value:

            return flatten_rich_value(
                parsed
            )

        return value


    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    if isinstance(value, list):

        parts = []

        for item in value:

            cleaned = flatten_rich_value(
                item
            )

            if cleaned:

                parts.append(
                    cleaned
                )

        return " ".join(parts)


    # --------------------------------------------------------
    # DICTIONARY
    # --------------------------------------------------------

    if isinstance(value, dict):

        parts = []

        # First prefer meaningful fields
        # in a predictable order.

        for key in IMPORTANT_KEYS:

            if key in value:

                cleaned = flatten_rich_value(
                    value[key]
                )

                if cleaned:

                    parts.append(
                        cleaned
                    )


        # If no important fields were found,
        # inspect remaining fields.

        if not parts:

            for key, item in value.items():

                if key in STRUCTURAL_KEYS:
                    continue

                cleaned = flatten_rich_value(
                    item
                )

                if cleaned:

                    parts.append(
                        cleaned
                    )


        return " ".join(parts)


    return str(value)


# ============================================================
# GENERAL TEXT CLEANING
# ============================================================

def clean_text(value):

    if value is None:

        return ""


    text = flatten_rich_value(
        value
    )


    if not text:

        return ""


    text = html.unescape(
        str(text)
    )


    # Remove HTML tags

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )


    # Markdown links:
    # [Google](https://google.com)
    # becomes:
    # Google

    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )


    # Remove markdown emphasis

    text = re.sub(
        r"\*\*([^*]+)\*\*",
        r"\1",
        text
    )

    text = re.sub(
        r"__([^_]+)__",
        r"\1",
        text
    )


    text = text.replace(
        "```",
        ""
    )


    # Remove common structural tokens

    structural_tokens = [
        "children",
        "blockquote",
        "superscript",
        "subscript",
        "bold",
        "italic",
        "underline",
        "type",
        "className",
        "nodeType"
    ]


    for token in structural_tokens:

        text = re.sub(
            rf"\b{re.escape(token)}\b",
            " ",
            text,
            flags=re.IGNORECASE
        )


    # Remove literal boolean artifacts

    text = re.sub(
        r"\b(True|False|None)\b",
        " ",
        text
    )


    # Remove leftover braces/brackets

    text = text.replace(
        "{",
        " "
    )

    text = text.replace(
        "}",
        " "
    )


    # Remove repeated punctuation

    text = re.sub(
        r"\s+",
        " ",
        text
    )


    text = re.sub(
        r"\s+([,.;:])",
        r"\1",
        text
    )


    return text.strip()


# ============================================================
# FIELD CLEANING
# ============================================================

def clean_field(
    item,
    possible_keys
):

    for key in possible_keys:

        if key not in item:
            continue

        value = clean_text(
            item.get(key)
        )

        if value:

            return value


    return ""


# ============================================================
# NORMALIZE STATE
# ============================================================

STATE_ALIASES = {

    "karntaka": "Karnataka",
    "karnatak": "Karnataka",
    "karnataka": "Karnataka",

    "tamilnadu": "Tamil Nadu",
    "tamil nadu": "Tamil Nadu",

    "andhrapradesh": "Andhra Pradesh",
    "andhra pradesh": "Andhra Pradesh",

    "uttarpradesh": "Uttar Pradesh",
    "uttar pradesh": "Uttar Pradesh",

    "westbengal": "West Bengal",
    "west bengal": "West Bengal"

}


def normalize_state(value):

    if not value:

        return ""


    text = clean_text(
        value
    ).strip()


    key = re.sub(
        r"[^a-z]",
        "",
        text.lower()
    )


    return STATE_ALIASES.get(
        key,
        text
    )


# ============================================================
# NORMALIZE PROFILE
# ============================================================

def normalize_profile(profile):

    if not profile:

        return {}


    normalized = {}


    for key, value in profile.items():

        if value is None:
            continue


        value = clean_text(
            value
        ).strip()


        if not value:
            continue


        if key == "state":

            value = normalize_state(
                value
            )


        elif key == "category":

            value = value.strip()


        elif key == "education":

            value = value.strip()


        elif key == "occupation":

            value = value.strip()


        normalized[key] = value


    return normalized


# ============================================================
# NORMALIZE SEARCH TEXT
# ============================================================

def normalize_search_text(text):

    text = clean_text(
        text
    ).lower()


    text = re.sub(
        r"[^a-z0-9₹\s]",
        " ",
        text
    )


    text = re.sub(
        r"\s+",
        " ",
        text
    )


    return text.strip()


# ============================================================
# PROFILE KEYWORD GROUPS
# ============================================================

GROUP_KEYWORDS = {

    "SC": [
        "sc",
        "scheduled caste",
        "scheduled castes"
    ],

    "ST": [
        "st",
        "scheduled tribe",
        "scheduled tribes"
    ],

    "OBC": [
        "obc",
        "other backward class",
        "other backward classes"
    ],

    "Minority": [
        "minority",
        "minorities"
    ],

    "Women": [
        "women",
        "woman",
        "girl",
        "girls",
        "female",
        "mother"
    ],

    "Disability": [
        "disabled",
        "disability",
        "pwd",
        "persons with disabilities"
    ],

    "Senior": [
        "senior citizen",
        "senior citizens",
        "elderly",
        "old age"
    ]

}


# ============================================================
# CHECK EXCLUSIVE GROUP
# ============================================================

def contains_group(
    text,
    group
):

    text = normalize_search_text(
        text
    )


    keywords = GROUP_KEYWORDS.get(
        group,
        []
    )


    for keyword in keywords:

        if keyword in text:

            return True


    return False


def exclusive_group_mismatch(
    scheme_text,
    profile_category
):

    scheme_text = normalize_search_text(
        scheme_text
    )


    category = normalize_search_text(
        profile_category
    )


    # --------------------------------------------------------
    # GENERAL CATEGORY
    # --------------------------------------------------------

    if category == "general":

        exclusive_groups = [
            "SC",
            "ST",
            "OBC",
            "Minority",
            "Disability"
        ]


        for group in exclusive_groups:

            if contains_group(
                scheme_text,
                group
            ):

                return True


    # --------------------------------------------------------
    # SC
    # --------------------------------------------------------

    if category == "sc":

        if (
            contains_group(
                scheme_text,
                "ST"
            )
            and
            not contains_group(
                scheme_text,
                "SC"
            )
        ):

            return True


    # --------------------------------------------------------
    # ST
    # --------------------------------------------------------

    if category == "st":

        if (
            contains_group(
                scheme_text,
                "SC"
            )
            and
            not contains_group(
                scheme_text,
                "ST"
            )
        ):

            return True


    # --------------------------------------------------------
    # OBC
    # --------------------------------------------------------

    if category == "obc":

        if (
            contains_group(
                scheme_text,
                "SC"
            )
            or
            contains_group(
                scheme_text,
                "ST"
            )
        ):

            return True


    return False


# ============================================================
# EDUCATION MATCHING
# ============================================================

def education_score(
    scheme_text,
    education
):

    text = normalize_search_text(
        scheme_text
    )

    education = normalize_search_text(
        education
    )


    score = 0


    if not education:

        return 0


    # B.E / engineering

    if (
        "b.e" in education
        or "be" == education
        or "btech" in education
        or "b.tech" in education
        or "engineering" in education
    ):

        strong_terms = [
            "engineering",
            "b.tech",
            "btech",
            "b.e",
            "professional course",
            "technical course",
            "undergraduate",
            "graduation",
            "college",
            "university",
            "degree"
        ]


        for term in strong_terms:

            if term in text:

                score += 8


        # Strong negative for school-only
        school_terms = [
            "primary school",
            "class 1",
            "class 2",
            "class 3",
            "class 4",
            "class 5",
            "class 6",
            "class 7",
            "class 8",
            "class 9",
            "class 10",
            "pre matric"
        ]


        for term in school_terms:

            if term in text:

                score -= 10


    # 12th

    elif "12" in education:

        if (
            "class 12"
            in text
            or "12th"
            in text
            or "higher secondary"
            in text
        ):

            score += 8


    # 10th

    elif "10" in education:

        if (
            "class 10"
            in text
            or "10th"
            in text
            or "secondary"
            in text
        ):

            score += 8


    return score


# ============================================================
# OCCUPATION MATCHING
# ============================================================

def occupation_score(
    scheme_text,
    occupation
):

    text = normalize_search_text(
        scheme_text
    )

    occupation = normalize_search_text(
        occupation
    )


    score = 0


    if not occupation:

        return score


    groups = {

        "student": [
            "student",
            "scholarship",
            "education",
            "college",
            "university",
            "internship",
            "fellowship"
        ],

        "farmer": [
            "farmer",
            "farming",
            "agriculture",
            "agricultural",
            "crop",
            "cultivation",
            "kisan",
            "livestock",
            "horticulture"
        ],

        "teacher": [
            "teacher",
            "teaching",
            "education"
        ],

        "engineer": [
            "engineering",
            "technical",
            "technology"
        ],

        "unemployed": [
            "unemployed",
            "employment",
            "job",
            "skill",
            "training",
            "placement"
        ],

        "entrepreneur": [
            "entrepreneur",
            "startup",
            "business",
            "msme",
            "enterprise"
        ],

        "business": [
            "business",
            "msme",
            "enterprise",
            "entrepreneur"
        ],

        "woman": [
            "women",
            "woman",
            "girl",
            "female"
        ],

        "women": [
            "women",
            "woman",
            "girl",
            "female"
        ]

    }


    keywords = groups.get(
        occupation,
        []
    )


    for keyword in keywords:

        if keyword in text:

            score += 7


    return score


# ============================================================
# PURPOSE DETECTION
# ============================================================

def detect_purpose(
    query,
    user_message=""
):

    text = normalize_search_text(
        f"{query} {user_message}"
    )


    scholarship_words = [
        "scholarship",
        "scholarships",
        "stipend",
        "fellowship",
        "education assistance"
    ]


    job_words = [
        "job",
        "jobs",
        "employment",
        "recruitment",
        "vacancy",
        "career",
        "apprenticeship"
    ]


    farmer_words = [
        "farmer",
        "farming",
        "agriculture",
        "crop",
        "kisan"
    ]


    loan_words = [
        "loan",
        "credit",
        "interest subsidy"
    ]


    if any(
        word in text
        for word in scholarship_words
    ):

        return "scholarship"


    if any(
        word in text
        for word in job_words
    ):

        return "job"


    if any(
        word in text
        for word in farmer_words
    ):

        return "farmer"


    if any(
        word in text
        for word in loan_words
    ):

        return "loan"


    return "general"


# ============================================================
# PURPOSE SCORE
# ============================================================

def purpose_score(
    scheme_text,
    purpose
):

    text = normalize_search_text(
        scheme_text
    )


    score = 0


    if purpose == "scholarship":

        positive = [
            "scholarship",
            "stipend",
            "fellowship",
            "education",
            "student"
        ]

        negative = [
            "loan",
            "credit",
            "interest subsidy"
        ]


    elif purpose == "job":

        positive = [
            "job",
            "employment",
            "recruitment",
            "vacancy",
            "apprentice",
            "apprenticeship",
            "career",
            "skill"
        ]

        negative = [
            "pension"
        ]


    elif purpose == "farmer":

        positive = [
            "farmer",
            "agriculture",
            "farming",
            "crop",
            "kisan",
            "livestock",
            "horticulture"
        ]

        negative = [
            "scholarship",
            "student"
        ]


    elif purpose == "loan":

        positive = [
            "loan",
            "credit",
            "interest subsidy",
            "financial assistance"
        ]

        negative = []


    else:

        positive = [
            "government",
            "assistance",
            "benefit",
            "scheme",
            "support"
        ]

        negative = []


    for word in positive:

        if word in text:

            score += 5


    for word in negative:

        if word in text:

            score -= 6


    return score


# ============================================================
# AGE SCORE
# ============================================================

def age_score(
    scheme_text,
    age
):

    if not age:

        return 0


    try:

        age = int(
            str(age)
        )

    except Exception:

        return 0


    text = normalize_search_text(
        scheme_text
    )


    score = 0


    senior_terms = [
        "senior citizen",
        "senior citizens",
        "old age",
        "elderly",
        "pension"
    ]


    young_terms = [
        "student",
        "scholarship",
        "school",
        "college",
        "youth"
    ]


    if age < 30:

        for term in senior_terms:

            if term in text:

                score -= 15


        for term in young_terms:

            if term in text:

                score += 4


    elif age >= 60:

        for term in senior_terms:

            if term in text:

                score += 10


    return score


# ============================================================
# STATE SCORE
# ============================================================

def state_score(
    scheme_state,
    user_state
):

    if not user_state:

        return 0


    scheme_state = normalize_state(
        scheme_state
    )

    user_state = normalize_state(
        user_state
    )


    if not scheme_state:

        return 0


    scheme_lower = scheme_state.lower()
    user_lower = user_state.lower()


    # Central / All India

    if scheme_lower in [
        "all",
        "central",
        "india",
        "all india"
    ]:

        return 5


    if scheme_lower == user_lower:

        return 15


    # Clearly different state

    return -20


# ============================================================
# BUILD CLEAN RECORD
# ============================================================

def build_record(
    metadata_item
):

    if not isinstance(
        metadata_item,
        dict
    ):

        return None


    slug = str(
        metadata_item.get(
            "slug",
            ""
        )
    ).strip()


    enriched_item = (
        ENRICHED_BY_SLUG.get(
            slug,
            {}
        )
    )


    if not isinstance(
        enriched_item,
        dict
    ):

        enriched_item = {}


    # Merge metadata + enriched data

    combined = {}

    combined.update(
        metadata_item
    )

    combined.update(
        enriched_item
    )


    scheme_name = clean_field(
        combined,
        [
            "schemeName",
            "scheme_name",
            "name",
            "title"
        ]
    )


    state = clean_field(
        combined,
        [
            "state",
            "schemeState"
        ]
    )


    category = clean_field(
        combined,
        [
            "category",
            "categories"
        ]
    )


    description = clean_field(
        combined,
        [
            "description",
            "description_md",
            "brief"
        ]
    )


    eligibility = clean_field(
        combined,
        [
            "eligibility",
            "eligibilityDescription",
            "eligibilityDescription_md"
        ]
    )


    benefits = clean_field(
        combined,
        [
            "benefits",
            "benefits_md"
        ]
    )


    application = clean_field(
        combined,
        [
            "application",
            "process",
            "process_md"
        ]
    )


    documents = clean_field(
        combined,
        [
            "documents",
            "documentsRequired",
            "documents_required"
        ]
    )


    tags = clean_field(
        combined,
        [
            "tags",
            "keywords",
            "searchTags"
        ]
    )


    # If description is empty,
    # build one from useful information.

    if not description:

        description = clean_text(
            combined.get(
                "descriptionText",
                ""
            )
        )


    # --------------------------------------------------------
    # Official URL
    # --------------------------------------------------------

    official_link = clean_field(
        combined,
        [
            "official_link",
            "officialLink",
            "url",
            "schemeUrl"
        ]
    )


    if (
        not official_link
        or
        "myscheme.gov.in" not in official_link
    ):

        if slug:

            official_link = (
                "https://www.myscheme.gov.in/"
                f"schemes/{slug}"
            )

        else:

            official_link = (
                "https://www.myscheme.gov.in/"
            )


    return {

        "schemeName":
            scheme_name
            or "Government Scheme",

        "state":
            state
            or "All",

        "category":
            category
            or "Government Scheme",

        "description":
            description,

        "eligibility":
            eligibility,

        "benefits":
            benefits,

        "application":
            application,

        "documents":
            documents,

        "official_link":
            official_link,

        "slug":
            slug,

        "tags":
            tags

    }


# ============================================================
# SEARCH
# ============================================================

def search_schemes(
    query,
    top_k=8,
    user_profile=None,
    user_state=None,
    user_message=None
):

    # --------------------------------------------------------
    # NORMALIZE PROFILE
    # --------------------------------------------------------

    profile = normalize_profile(
        user_profile
    )


    if user_state:

        profile["state"] = normalize_state(
            user_state
        )


    # --------------------------------------------------------
    # QUERY
    # --------------------------------------------------------

    query = str(
        query or ""
    ).strip()


    if not query:

        query = (
            "government schemes "
            "scholarships jobs welfare "
            "financial assistance"
        )


    # --------------------------------------------------------
    # EMBEDDING
    # --------------------------------------------------------

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )


    # --------------------------------------------------------
    # RETRIEVE MANY CANDIDATES
    # --------------------------------------------------------

    candidate_count = min(
        max(
            100,
            top_k * 15
        ),
        index.ntotal
    )


    scores, indices = index.search(
        query_embedding,
        candidate_count
    )


    candidates = []


    for similarity, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx < 0:
            continue


        if idx >= len(metadata):
            continue


        raw_item = metadata[idx]


        record = build_record(
            raw_item
        )


        if not record:
            continue


        record["_similarity"] = float(
            similarity
        )


        candidates.append(
            record
        )


    # --------------------------------------------------------
    # PURPOSE
    # --------------------------------------------------------

    purpose = detect_purpose(
        query,
        user_message or ""
    )


    # --------------------------------------------------------
    # RERANK
    # --------------------------------------------------------

    ranked = []


    for record in candidates:

        combined_text = " ".join(
            [
                record.get(
                    "schemeName",
                    ""
                ),

                record.get(
                    "category",
                    ""
                ),

                record.get(
                    "description",
                    ""
                ),

                record.get(
                    "eligibility",
                    ""
                ),

                record.get(
                    "benefits",
                    ""
                ),

                record.get(
                    "tags",
                    ""
                )

            ]
        )


        similarity = record.get(
            "_similarity",
            0
        )


        final_score = (
            similarity * 20
        )


        # State

        final_score += state_score(
            record.get(
                "state",
                ""
            ),
            profile.get(
                "state",
                ""
            )
        )


        # Category mismatch

        if profile.get(
            "category"
        ):

            if exclusive_group_mismatch(
                combined_text,
                profile[
                    "category"
                ]
            ):

                final_score -= 40


        # Education

        final_score += education_score(
            combined_text,
            profile.get(
                "education",
                ""
            )
        )


        # Occupation

        final_score += occupation_score(
            combined_text,
            profile.get(
                "occupation",
                ""
            )
        )


        # Age

        final_score += age_score(
            combined_text,
            profile.get(
                "age",
                ""
            )
        )


        # Purpose

        final_score += purpose_score(
            combined_text,
            purpose
        )


        # ----------------------------------------------------
        # SPECIAL PENALTIES
        # ----------------------------------------------------

        text_lower = normalize_search_text(
            combined_text
        )


        # General category:
        # reduce group-specific schemes

        if (
            profile.get(
                "category",
                ""
            ).lower()
            == "general"
        ):

            restricted_terms = [
                "sc only",
                "scheduled caste only",
                "st only",
                "scheduled tribe only",
                "obc only",
                "minority only"
            ]


            for term in restricted_terms:

                if term in text_lower:

                    final_score -= 30


        # Young user:
        # strongly penalize obvious pension schemes

        try:

            age_value = int(
                profile.get(
                    "age",
                    0
                )
            )

        except Exception:

            age_value = 0


        if (
            age_value
            and age_value < 40
        ):

            if (
                "senior citizen"
                in text_lower
                or
                "old age pension"
                in text_lower
            ):

                final_score -= 35


        # Engineering student:
        # penalize school-only schemes

        education = normalize_search_text(
            profile.get(
                "education",
                ""
            )
        )


        if (
            "engineering"
            in education
            or
            "b.e"
            in education
            or
            "btech"
            in education
        ):

            school_terms = [
                "primary school",
                "class 1",
                "class 2",
                "class 3",
                "class 4",
                "class 5",
                "class 6",
                "class 7",
                "class 8",
                "class 9",
                "class 10"
            ]


            if any(
                term in text_lower
                for term in school_terms
            ):

                final_score -= 20


        ranked.append(
            (
                final_score,
                record
            )
        )


    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    ranked.sort(
        key=lambda x: x[0],
        reverse=True
    )


    # --------------------------------------------------------
    # FILTER OBVIOUS MISMATCHES
    # --------------------------------------------------------

    selected = []


    for score, record in ranked:

        text = " ".join(
            [
                record.get(
                    "schemeName",
                    ""
                ),
                record.get(
                    "category",
                    ""
                ),
                record.get(
                    "description",
                    ""
                ),
                record.get(
                    "eligibility",
                    ""
                )
            ]
        )


        # ----------------------------------------------------
        # Different state
        # ----------------------------------------------------

        requested_state = profile.get(
            "state"
        )


        if requested_state:

            scheme_state = normalize_state(
                record.get(
                    "state",
                    ""
                )
            )


            if (
                scheme_state
                and
                scheme_state.lower()
                not in [
                    "all",
                    "central",
                    "india",
                    "all india",
                    requested_state.lower()
                ]
            ):

                # Do not immediately remove it,
                # but only allow it if we don't
                # have enough good results.

                if len(selected) >= top_k:

                    continue


        # ----------------------------------------------------
        # General mismatch
        # ----------------------------------------------------

        category = profile.get(
            "category"
        )


        if (
            category
            and
            exclusive_group_mismatch(
                text,
                category
            )
        ):

            continue


        # ----------------------------------------------------
        # Age mismatch
        # ----------------------------------------------------

        try:

            age_value = int(
                profile.get(
                    "age",
                    0
                )
            )

        except Exception:

            age_value = 0


        if age_value < 40:

            lower_text = normalize_search_text(
                text
            )


            if (
                "senior citizen"
                in lower_text
                or
                "old age pension"
                in lower_text
            ):

                continue


        selected.append(
            record
        )


        if len(selected) >= top_k:

            break


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if len(selected) < top_k:

        selected_slugs = {
            item.get(
                "slug"
            )
            for item in selected
        }


        for score, record in ranked:

            slug = record.get(
                "slug"
            )


            if slug in selected_slugs:

                continue


            selected.append(
                record
            )


            selected_slugs.add(
                slug
            )


            if len(selected) >= top_k:

                break


    # --------------------------------------------------------
    # REMOVE INTERNAL FIELDS
    # --------------------------------------------------------

    final_results = []


    seen = set()


    for record in selected:

        slug = record.get(
            "slug"
        )


        if slug in seen:

            continue


        seen.add(
            slug
        )


        record.pop(
            "_similarity",
            None
        )


        record.pop(
            "slug",
            None
        )


        record.pop(
            "tags",
            None
        )


        final_results.append(
            record
        )


    return final_results