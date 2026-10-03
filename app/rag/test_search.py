from app.rag.search import search_schemes


queries = [
    "scholarships for students",
    "financial assistance for farmers",
    "women entrepreneurship schemes",
    "education schemes for girls",
]


for query in queries:

    print("\n" + "=" * 70)
    print("QUERY:", query)
    print("=" * 70)

    results = search_schemes(
        query,
        top_k=5
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print(f"\n{i}. {result['schemeName']}")
        print("Category:", result.get("category"))
        print("State:", result.get("state"))

        print(
            "Score:",
            result.get("score")
        )