from playwright.sync_api import sync_playwright


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    page.goto(
        "https://www.myscheme.gov.in/search",
        wait_until="networkidle",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    resources = page.evaluate(
        """
        () => performance
            .getEntriesByType("resource")
            .map(e => e.name)
        """
    )

    print("=" * 60)
    print("NETWORK REQUESTS")
    print("=" * 60)

    for url in resources:

        url_lower = url.lower()

        if (
            "api" in url_lower
            or "search" in url_lower
            or "scheme" in url_lower
        ):
            print(url)

    browser.close()