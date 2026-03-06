"""
Test with FRESH browser (no cache)
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        # Launch with NO CACHE
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()

        print("Loading page with FRESH browser (no cache)...")
        await page.goto('http://localhost:8081/humanbody/theatre/', wait_until='networkidle')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(4)

        print("\nTaking screenshot of FRESH load...")
        await page.screenshot(path='fresh_load.png')
        print("✓ Screenshot: fresh_load.png")

        # Check material color
        mat = await page.evaluate("""
            () => {
                const scene = window.scene;
                let charMat = null;
                scene.traverse((obj) => {
                    if (obj.isMesh && obj.geometry && obj.geometry.attributes.position.count > 50000) {
                        charMat = {
                            color: '#' + obj.material.color.getHexString(),
                            opacity: obj.material.opacity,
                            transparent: obj.material.transparent
                        };
                    }
                });
                return charMat;
            }
        """)
        print(f"\nCharacter Material: {mat}")

        print("\n\nKeeping browser open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
