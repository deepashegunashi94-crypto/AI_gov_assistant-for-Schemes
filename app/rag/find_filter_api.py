from playwright.sync_api import sync_playwright

URL = "https://www.myscheme.gov.in/search"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    def handle_request(request):
        if "/api/apisetu/search/schemes" in request.url:
            print("\n========================================")
            print("SEARCH API REQUEST")
            print("URL:")
            print(request.url)

    page.on("request", handle_request)

    print("Opening myScheme search page...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    print("\nBrowser is open.")
    print("Click the 'Education & Learning' category filter.")
    print("Then wait a few seconds.")
    print("Close the browser when finished.")

    page.wait_for_timeout(60000)

    browser.close()