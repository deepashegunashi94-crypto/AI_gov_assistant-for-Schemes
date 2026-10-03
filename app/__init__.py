import os
import re
import json

from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
from groq import Groq

from .rag.search import search_schemes


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

groq_client = None


if GROQ_API_KEY:
    try:
        groq_client = Groq(
            api_key=GROQ_API_KEY
        )

    except Exception as e:
        print(
            "Groq initialization failed:",
            e
        )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_reply(text):

    if not text:
        return ""

    text = str(text)

    # Remove HTML
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # Convert markdown links to their label
    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )

    # Remove markdown formatting
    text = text.replace(
        "**",
        ""
    )

    text = text.replace(
        "__",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    # Remove table-like lines
    lines = []

    for line in text.splitlines():

        if "|" in line:
            continue

        if re.fullmatch(
            r"\s*:?-+:?\s*",
            line
        ):
            continue

        if line.strip():
            lines.append(
                line.strip()
            )

    text = " ".join(lines)

    # Normalize spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# PROFILE EXTRACTION FROM CHAT
# ============================================================

def extract_profile_from_message(message):

    message_lower = message.lower()

    profile = {}


    # --------------------------------------------------------
    # AGE
    # --------------------------------------------------------

    age_match = re.search(
        r"\b(?:age|aged)\s*(?:is|of)?\s*(\d{1,3})\b",
        message_lower
    )

    if age_match:
        profile["age"] = age_match.group(1)


    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category_patterns = {

        "SC": [
            r"\bsc\b",
            r"\bscheduled caste\b"
        ],

        "ST": [
            r"\bst\b",
            r"\bscheduled tribe\b"
        ],

        "OBC": [
            r"\bobc\b",
            r"\bother backward class\b"
        ],

        "General": [
            r"\bgeneral category\b",
            r"\bgeneral\b"
        ],

        "Minority": [
            r"\bminority\b"
        ]

    }


    for category, patterns in category_patterns.items():

        for pattern in patterns:

            if re.search(
                pattern,
                message_lower
            ):

                profile["category"] = category
                break

        if "category" in profile:
            break


    # --------------------------------------------------------
    # OCCUPATION
    # --------------------------------------------------------

    occupation_keywords = [

        "student",
        "farmer",
        "teacher",
        "engineer",
        "employee",
        "worker",
        "business",
        "entrepreneur",
        "unemployed",
        "job seeker",
        "senior citizen",
        "housewife",
        "woman",
        "women"

    ]


    for keyword in occupation_keywords:

        if keyword in message_lower:

            profile["occupation"] = keyword
            break


    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    education_patterns = [

        (
            "B.E",
            [
                "b.e",
                "be student",
                "engineering student",
                "engineering"
            ]
        ),

        (
            "B.Tech",
            [
                "b.tech",
                "btech"
            ]
        ),

        (
            "M.Tech",
            [
                "m.tech",
                "mtech"
            ]
        ),

        (
            "MBA",
            [
                "mba"
            ]
        ),

        (
            "12th",
            [
                "12th",
                "12th standard",
                "class 12"
            ]
        ),

        (
            "10th",
            [
                "10th",
                "10th standard",
                "class 10"
            ]
        )

    ]


    for education, keywords in education_patterns:

        for keyword in keywords:

            if keyword in message_lower:

                profile["education"] = education
                break

        if "education" in profile:
            break


    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    states = [

        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal"

    ]


    for state in states:

        if state.lower() in message_lower:

            profile["state"] = state
            break


    return profile


# ============================================================
# BUILD SEARCH QUERY
# ============================================================

def build_retrieval_query(
    message,
    profile=None
):

    parts = []


    if message:

        parts.append(
            message
        )


    if profile:

        for key, value in profile.items():

            if value:

                parts.append(
                    f"{key}: {value}"
                )


    query = " ".join(parts)


    if not query:

        query = (
            "government schemes "
            "scholarships jobs welfare "
            "benefits"
        )


    return query


# ============================================================
# LOCAL FALLBACK RESPONSE
# ============================================================

def local_response(
    items,
    purpose="chat"
):

    count = len(items)


    if count == 0:

        if purpose == "find":

            return (
                "I could not find sufficiently "
                "relevant schemes for the details "
                "you entered. Try adding your state, "
                "education, occupation, age, or "
                "category."
            )


        return (
            "I could not find sufficiently relevant "
            "schemes for your request. Try using "
            "more specific details such as your "
            "state, occupation, education, or "
            "requirement."
        )


    if purpose == "find":

        return (
            f"I found {count} scheme"
            f"{'s' if count != 1 else ''} "
            "that may be relevant to the details "
            "you entered. Please review the "
            "eligibility and official application "
            "information for each scheme before applying."
        )


    return (
        f"I found {count} government scheme"
        f"{'s' if count != 1 else ''} "
        "related to your request. Check the "
        "scheme details below and verify the "
        "latest eligibility and application "
        "requirements on the official website."
    )


# ============================================================
# GROQ RESPONSE
# ============================================================

def generate_groq_response(
    items,
    profile=None,
    user_message="",
    purpose="chat"
):

    fallback = local_response(
        items,
        purpose
    )


    if not groq_client:
        return fallback


    if not items:
        return fallback


    context = []


    for item in items[:5]:

        context.append({

            "scheme_name":
                item.get(
                    "schemeName",
                    ""
                ),

            "state":
                item.get(
                    "state",
                    ""
                ),

            "category":
                item.get(
                    "category",
                    ""
                ),

            "description":
                item.get(
                    "description",
                    ""
                ),

            "eligibility":
                item.get(
                    "eligibility",
                    ""
                ),

            "benefits":
                item.get(
                    "benefits",
                    ""
                )

        })


    profile_text = ""


    if profile:

        profile_text = json.dumps(
            profile,
            ensure_ascii=False
        )


    prompt = f"""
You are a helpful government scheme assistant.

The user asked:

{user_message}

User profile:

{profile_text}

Below are government scheme results retrieved
from the database:

{json.dumps(context, ensure_ascii=False, indent=2)}

Give a short natural-language response.

Rules:

1. Use only the information provided above.
2. Do not create or invent schemes.
3. Do not claim that the user is definitely eligible.
4. Say that schemes may be relevant when appropriate.
5. Do not output a markdown table.
6. Do not output HTML.
7. Do not output JSON.
8. Do not output URLs.
9. Do not repeat all scheme details.
10. Keep the response to 2-4 sentences.
11. Mention that the user should verify the latest eligibility and application requirements on the official government website.
"""


    try:

        completion = (
            groq_client
            .chat
            .completions
            .create(
                model=GROQ_MODEL,

                messages=[
                    {
                        "role": "system",
                        "content":
                            "You are a concise "
                            "government information "
                            "assistant."
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.2,

                max_tokens=250
            )
        )


        response = (
            completion
            .choices[0]
            .message
            .content
        )


        response = clean_reply(
            response
        )


        if not response:
            return fallback


        return response


    except Exception as e:

        print(
            "Groq response error:",
            e
        )

        return fallback


# ============================================================
# BUILD CLEAN API ITEMS
# ============================================================

def build_api_items(results):

    items = []


    for result in results:

        item = {

            "schemeName":
                result.get(
                    "schemeName",
                    "Government Scheme"
                ),

            "state":
                result.get(
                    "state",
                    "All"
                ),

            "category":
                result.get(
                    "category",
                    "Government Scheme"
                ),

            "description":
                result.get(
                    "description",
                    ""
                ),

            "eligibility":
                result.get(
                    "eligibility",
                    ""
                ),

            "benefits":
                result.get(
                    "benefits",
                    ""
                ),

            "application":
                result.get(
                    "application",
                    ""
                ),

            "documents":
                result.get(
                    "documents",
                    ""
                ),

            "official_link":
                result.get(
                    "official_link",
                    "https://www.myscheme.gov.in/"
                )

        }


        items.append(item)


    return items


# ============================================================
# CREATE FLASK APP
# ============================================================

def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )


    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY",
        "change-this-secret-key"
    )


    # ========================================================
    # HOME PAGE
    # ========================================================

    @app.route("/")
    def home():

        return render_template(
            "index.html"
        )


    # ========================================================
    # CHAT
    # ========================================================

    @app.route(
        "/chat",
        methods=["POST"]
    )
    def chat():

        data = (
            request.get_json(
                silent=True
            ) or {}
        )


        message = str(
            data.get(
                "message",
                ""
            )
        ).strip()


        if not message:

            return jsonify({
                "reply":
                    "Please enter a question.",
                "items": []
            }), 400


        # Profile is OPTIONAL for chat

        profile = extract_profile_from_message(
            message
        )


        query = build_retrieval_query(
            message,
            profile
        )


        try:

            results = search_schemes(
                query,
                top_k=5,
                user_profile=profile,
                user_message=message
            )


        except Exception as e:

            print(
                "RAG search error:",
                e
            )

            results = []


        items = build_api_items(
            results
        )


        reply = generate_groq_response(
            items,
            profile=profile,
            user_message=message,
            purpose="chat"
        )


        return jsonify({
            "reply": reply,
            "items": items
        })


    # ========================================================
    # FIND SCHEMES FOR ME
    # ========================================================

    @app.route(
        "/find-schemes",
        methods=["POST"]
    )
    def find_schemes():

        data = (
            request.get_json(
                silent=True
            ) or {}
        )


        profile = {}


        # Only use fields actually entered
        # by the user

        fields = [

            "state",
            "education",
            "occupation",
            "category",
            "income",
            "age"

        ]


        for field in fields:

            value = data.get(
                field,
                ""
            )


            if value is None:
                continue


            value = str(
                value
            ).strip()


            if value:

                profile[field] = value


        # Require at least one field

        if not profile:

            return jsonify({

                "reply":
                    "Please enter at least one detail so I can search for relevant government schemes.",

                "items": []

            }), 400


        # Build dynamic query

        query = build_retrieval_query(
            "government schemes for me",
            profile
        )


        print(
            "\nFind Schemes Profile:"
        )

        print(profile)

        print(
            "Search Query:",
            query
        )


        # RAG SEARCH

        try:

            results = search_schemes(
                query,
                top_k=5,
                user_profile=profile,
                user_message=query
            )


        except Exception as e:

            print(
                "Find schemes RAG error:",
                e
            )

            results = []


        items = build_api_items(
            results
        )


        # Generate response

        reply = generate_groq_response(
            items,
            profile=profile,
            user_message=query,
            purpose="find"
        )


        return jsonify({

            "reply": reply,

            "items": items,

            "profile": profile

        })


    # ========================================================
    # CLEAR
    # ========================================================

    @app.route(
        "/clear",
        methods=["POST"]
    )
    def clear():

        return jsonify({
            "success": True
        })


    # ========================================================
    # HEALTH CHECK
    # ========================================================

    @app.route(
        "/health",
        methods=["GET"]
    )
    def health():

        return jsonify({

            "status": "ok",

            "groq": bool(
                groq_client
            )

        })


    return app