"""
Quick test: Settings dropdown only
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        page = await browser.new_page()

        await page.goto('http://localhost:8081/settings/theatre/')
        await page.wait_for_selector('.settings-card', timeout=5000)
        await asyncio.sleep(1)

        dropdown = await page.evaluate("""
            () => {
                const select = document.querySelector('select[name="theatre_default_animation"]');
                const optgroups = select.querySelectorAll('optgroup');
                return {
                    optgroupCount: optgroups.length,
                    firstGroup: optgroups[0]?.label || 'NONE',
                    firstOptionCount: optgroups[0]?.querySelectorAll('option').length || 0
                };
            }
        """)
        print(f"Dropdown: {dropdown}")
        print("FIXED!" if dropdown['optgroupCount'] > 0 else "STILL BROKEN!")

        await page.screenshot(path='dropdown_test.png', full_page=True)
        print("Screenshot: dropdown_test.png")

        await asyncio.sleep(5)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
