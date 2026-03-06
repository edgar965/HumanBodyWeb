"""Quick test: Jobs page with bulk select/delete UI."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=['--start-maximized'])
    ctx = browser.new_context(no_viewport=True)
    page = ctx.new_page()
    page.goto('http://localhost:8081/humanbody/photo-to-3d/jobs/', wait_until='networkidle')
    page.wait_for_timeout(1000)

    # Check select-all checkbox exists
    sa = page.locator('#select-all')
    print(f'Select-All checkbox: {"OK" if sa.count() > 0 else "MISSING"}')

    # Count job checkboxes
    cbs = page.locator('.job-cb')
    print(f'Job checkboxes: {cbs.count()}')

    # Click select-all
    if sa.count() > 0 and cbs.count() > 0:
        sa.click()
        page.wait_for_timeout(500)
        checked = page.locator('.job-cb:checked').count()
        print(f'After select-all: {checked}/{cbs.count()} checked')

        # Check bulk-actions bar visible
        bar = page.locator('#bulk-actions')
        has_class = 'has-selection' in (bar.get_attribute('class') or '')
        print(f'Bulk-actions bar active: {has_class}')

        count_text = page.locator('#selection-count').text_content()
        print(f'Selection text: {count_text}')

    page.screenshot(path=r'A:\3DTools\HumanBodyWeb\test_jobs_page.png')
    print('Screenshot: test_jobs_page.png')

    page.wait_for_timeout(8000)
    browser.close()
