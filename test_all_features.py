"""
Test all new Theatre features
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=400)
        page = await browser.new_page()

        print("Loading Theatre page...")
        await page.goto('http://localhost:8081/humanbody/theatre/', wait_until='networkidle')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(2)

        print("\n1. Loading character with garments...")
        await page.click('[data-tab="tab-models"]')
        await asyncio.sleep(1)

        await page.evaluate("""
            () => {
                const items = document.querySelectorAll('.anim-item');
                for (const item of items) {
                    if (item.textContent.includes('FemaleGarment')) {
                        item.click();
                        break;
                    }
                }
            }
        """)
        await asyncio.sleep(4)
        await page.screenshot(path='test_01_character.png')
        print("✓ Screenshot: test_01_character.png")

        print("\n2. Loading animation...")
        await page.click('[data-tab="tab-animations"]')
        await asyncio.sleep(1)

        # Expand first category and click first animation
        await page.evaluate("""
            () => {
                const catHeader = document.querySelector('.anim-cat-header');
                if (catHeader) catHeader.click();
            }
        """)
        await asyncio.sleep(0.5)

        clicked = await page.evaluate("""
            () => {
                const firstItem = document.querySelector('.anim-cat-body .anim-item');
                if (firstItem) {
                    firstItem.click();
                    return true;
                }
                return false;
            }
        """)
        print(f"Animation clicked: {clicked}")

        if clicked:
            await asyncio.sleep(3)
            await page.screenshot(path='test_02_animation_loaded.png')
            print("✓ Screenshot: test_02_animation_loaded.png")

            print("\n3. Clicking play...")
            await page.click('#btnPlayPause')
            await asyncio.sleep(2)
            await page.screenshot(path='test_03_playing.png')
            print("✓ Screenshot: test_03_playing.png")

        print("\n4. Clicking on a light icon...")
        # Click on canvas where left spotlight should be
        canvas = await page.query_selector('#theatre-canvas')
        box = await canvas.bounding_box()
        await page.mouse.click(box['x'] + box['width'] * 0.3, box['y'] + box['height'] * 0.2)
        await asyncio.sleep(1)
        await page.screenshot(path='test_04_light_properties.png')
        print("✓ Screenshot: test_04_light_properties.png")

        print("\n5. Testing toolbar buttons...")
        # Click rig toggle
        await page.click('#btn-toggle-rig')
        await asyncio.sleep(0.5)
        await page.screenshot(path='test_05_rig_visible.png')
        print("✓ Screenshot: test_05_rig_visible.png")

        print("\n\nAll tests done! Browser stays open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
