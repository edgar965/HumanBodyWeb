"""
Simple debug - Check actual light intensity values in console
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)

        # Wait for init
        await asyncio.sleep(3)

        print("\n1. Reading INITIAL light intensities...")
        intensities = await page.evaluate("""
            () => {
                const scene = window.scene;
                if (!scene) return { error: 'scene not found' };

                const lights = {};
                scene.traverse((obj) => {
                    if (obj.isSpotLight) {
                        lights[obj.name || 'unnamed'] = {
                            intensity: obj.intensity,
                            color: `rgb(${obj.color.r.toFixed(2)}, ${obj.color.g.toFixed(2)}, ${obj.color.b.toFixed(2)})`,
                            pos: `(${obj.position.x.toFixed(1)}, ${obj.position.y.toFixed(1)}, ${obj.position.z.toFixed(1)})`
                        };
                    }
                });
                return lights;
            }
        """)
        print("BEFORE:", intensities)

        # Click Studio Bright
        print("\n2. Clicking Studio Bright preset...")
        await page.click('.menu-item:has-text("Settings")')
        await asyncio.sleep(0.5)
        await page.click('[data-preset="studio_bright"]')
        await asyncio.sleep(1)

        print("\n3. Reading AFTER light intensities...")
        intensities_after = await page.evaluate("""
            () => {
                const scene = window.scene;
                if (!scene) return { error: 'scene not found' };

                const lights = {};
                scene.traverse((obj) => {
                    if (obj.isSpotLight) {
                        lights[obj.name || 'unnamed'] = {
                            intensity: obj.intensity,
                            color: `rgb(${obj.color.r.toFixed(2)}, ${obj.color.g.toFixed(2)}, ${obj.color.b.toFixed(2)})`,
                            pos: `(${obj.position.x.toFixed(1)}, ${obj.position.y.toFixed(1)}, ${obj.position.z.toFixed(1)})`
                        };
                    }
                });
                return lights;
            }
        """)
        print("AFTER:", intensities_after)

        print("\n4. Keeping browser open for manual testing...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
