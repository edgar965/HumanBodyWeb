"""
Simple test - just take screenshots of Theatre with toolbar
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        page = await browser.new_page()

        print("Loading Theatre page...")
        await page.goto('http://localhost:8081/humanbody/theatre/', wait_until='networkidle')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(2)

        print("\n1. Toolbar initial state...")
        await page.screenshot(path='theatre_toolbar.png', full_page=True)
        print("✓ Screenshot: theatre_toolbar.png")

        print("\n2. Clicking rotate mode...")
        await page.click('#btn-rotate-mode')
        await asyncio.sleep(1)
        await page.screenshot(path='theatre_rotate_mode.png', full_page=True)
        print("✓ Screenshot: theatre_rotate_mode.png")

        print("\n3. Loading FemaleGarment model...")
        await page.click('[data-tab="tab-models"]')
        await asyncio.sleep(1)
        await page.screenshot(path='theatre_models_tab.png', full_page=True)
        print("✓ Screenshot: theatre_models_tab.png")

        # Check if model list is loaded
        models_loaded = await page.evaluate("""
            () => {
                const list = document.getElementById('model-list');
                return list ? list.innerHTML.includes('FemaleGarment') : false;
            }
        """)
        print(f"Models loaded: {models_loaded}")

        if models_loaded:
            print("\n4. Clicking FemaleGarment...")
            # Wait for model items to be clickable
            await asyncio.sleep(2)

            # Find and click FemaleGarment
            clicked = await page.evaluate("""
                () => {
                    const items = document.querySelectorAll('.anim-item');
                    for (const item of items) {
                        if (item.textContent.includes('FemaleGarment')) {
                            item.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            print(f"FemaleGarment clicked: {clicked}")

            if clicked:
                print("Waiting for character to load...")
                await asyncio.sleep(5)
                await page.screenshot(path='theatre_with_garment.png', full_page=True)
                print("✓ Screenshot: theatre_with_garment.png")

        print("\n5. Testing light visibility toggle...")
        await page.click('#btn-toggle-lights')
        await asyncio.sleep(1)
        await page.screenshot(path='theatre_lights_off.png', full_page=True)
        print("✓ Screenshot: theatre_lights_off.png")

        print("\n6. Toggling lights back on...")
        await page.click('#btn-toggle-lights')
        await asyncio.sleep(1)

        print("\n7. Testing Settings-Theatre page (two-level animation selection)...")
        await page.goto('http://localhost:8081/settings/theatre/')
        await page.wait_for_selector('.settings-card', timeout=5000)
        await asyncio.sleep(1)
        await page.screenshot(path='settings_theatre_anim.png', full_page=True)
        print("✓ Screenshot: settings_theatre_anim.png")

        print("\n\nAll done! Browser will stay open for 10 seconds...")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
