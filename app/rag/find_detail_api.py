from playwright.sync_api import sync_playwright

URL = "https://www.myscheme.gov.in/schemes/rtif"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    def handle_request(request):
        url = request.url

        if "apisetu/schemes" in url:
            print("\n========================================")
            print("REQUEST FOUND")
            print("METHOD:", request.method)
            print("URL:", url)
            print("HEADERS:")

            headers = request.headers

            for key, value in headers.items():
                if key.lower() not in ["authorization", "cookie"]:
                    print(f"{key}: {value}")

    page.on("request", handle_request)

    print("Opening scheme page...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    # Give JavaScript time to make API calls
    page.wait_for_timeout(10000)

    print("\nFinished waiting.")

    browser.close()