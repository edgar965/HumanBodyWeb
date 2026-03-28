"""Quick check what JS errors occur on the Theatre page."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))

    page.goto("http://localhost:8081/humanbody/theatre/", timeout=30000)
    page.wait_for_timeout(12000)

    for i, err in enumerate(errors):
        print(f"Error {i+1}: {err[:300]}")

    context.close()
    browser.close()
