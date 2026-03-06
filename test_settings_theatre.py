"""
Test Settings-Theatre animation dropdown
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        print("Loading Settings-Theatre page...")
        await page.goto('http://localhost:8081/settings/theatre/')
        await page.wait_for_selector('.settings-card', timeout=5000)
        await asyncio.sleep(1)

        print("\nChecking animation dropdown...")
        dropdown_html = await page.evaluate("""
            () => {
                const select = document.querySelector('select[name="theatre_default_animation"]');
                if (!select) return 'NOT FOUND';

                const options = select.querySelectorAll('option');
                const optgroups = select.querySelectorAll('optgroup');

                return {
                    hasSelect: !!select,
                    optionCount: options.length,
                    optgroupCount: optgroups.length,
                    innerHTML: select.innerHTML.substring(0, 500)
                };
            }
        """)
        print(f"Dropdown info: {dropdown_html}")

        print("\nTaking screenshot...")
        await page.screenshot(path='settings_theatre_dropdown_debug.png', full_page=True)

        print("\nClicking dropdown...")
        await page.click('select[name="theatre_default_animation"]')
        await asyncio.sleep(1)
        await page.screenshot(path='settings_theatre_dropdown_open.png', full_page=True)

        print("\n\nBrowser stays open for 10 seconds...")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
