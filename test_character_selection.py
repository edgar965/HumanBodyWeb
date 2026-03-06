"""
Test Character Selection in Theatre (Task #10)
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        print("=== Loading Theatre page ===")
        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(2)

        print("=== Loading FemaleWithHair model ===")
        await page.click('[data-tab="tab-models"]')
        await asyncio.sleep(1)
        await page.evaluate("""
            () => {
                const items = document.querySelectorAll('.anim-item');
                for (const item of items) {
                    if (item.textContent.includes('FemaleWithHair')) {
                        item.click();
                        return;
                    }
                }
            }
        """)
        await asyncio.sleep(4)

        print("=== Clicking on character mesh ===")
        # Click in center of canvas (where character should be)
        canvas = await page.query_selector('#theatre-canvas')
        box = await canvas.bounding_box()
        await page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
        await asyncio.sleep(1)

        # Check if Properties panel shows character info
        props_content = await page.evaluate("""
            () => {
                const content = document.getElementById('properties-content');
                return content ? content.textContent : 'NO CONTENT';
            }
        """)
        print(f"Properties content: {props_content[:200]}")

        # Check if Eigenschaften tab is active
        props_tab_active = await page.evaluate("""
            () => {
                const tab = document.querySelector('[data-tab="tab-properties"]');
                return tab ? tab.classList.contains('active') : false;
            }
        """)
        print(f"Eigenschaften tab active: {props_tab_active}")

        # Check if panel shows "FemaleWithHair" or "Female"
        has_char_info = 'FemaleWithHair' in props_content or 'Female' in props_content or 'Position' in props_content
        print(f"Character info visible: {has_char_info}")

        await page.screenshot(path='test_character_selection.png', full_page=True)
        print("Screenshot: test_character_selection.png")

        if has_char_info and props_tab_active:
            print("\n✓ SUCCESS: Character selection works!")
        else:
            print("\n✗ FAILED: Character selection not working")

        print("\nBrowser stays open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
