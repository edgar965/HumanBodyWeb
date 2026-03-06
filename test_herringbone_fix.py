"""
Test Herringbone Pattern Fix (flatShading: false + computeVertexNormals)
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        page = await browser.new_page()

        print("Loading Theatre page...")
        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(2)

        print("Loading FemaleWithHair model...")
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

        # Zoom in on character (close-up view for skin detail)
        print("Zooming in for close-up...")
        await page.evaluate("""
            () => {
                // Zoom camera closer
                if (window.controls && window.camera) {
                    window.camera.position.set(0, 1.5, 1.5);
                    window.controls.target.set(0, 1.3, 0);
                    window.controls.update();
                }
            }
        """)
        await asyncio.sleep(2)

        print("Taking screenshots...")
        await page.screenshot(path='herringbone_fix_normal.png', full_page=True)

        # Zoom even closer for neck/shoulder detail
        await page.evaluate("""
            () => {
                if (window.controls && window.camera) {
                    window.camera.position.set(0.3, 1.4, 0.8);
                    window.controls.target.set(0, 1.3, 0);
                    window.controls.update();
                }
            }
        """)
        await asyncio.sleep(1)
        await page.screenshot(path='herringbone_fix_closeup.png', full_page=True)

        print("Screenshots saved:")
        print("  - herringbone_fix_normal.png")
        print("  - herringbone_fix_closeup.png")
        print("\nCheck if diagonal stripes (herringbone pattern) are GONE!")

        print("\nBrowser stays open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
