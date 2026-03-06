"""
Debug - List ALL scene objects
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

        print("\n=== SCENE OBJECTS ===")
        objects = await page.evaluate("""
            () => {
                const scene = window.scene;
                const result = [];

                scene.traverse((obj) => {
                    result.push({
                        type: obj.type,
                        name: obj.name || '(unnamed)',
                        isLight: obj.isLight || false,
                        isSpotLight: obj.isSpotLight || false,
                        intensity: obj.intensity,
                        position: obj.position ? `(${obj.position.x.toFixed(1)}, ${obj.position.y.toFixed(1)}, ${obj.position.z.toFixed(1)})` : 'N/A'
                    });
                });

                return result;
            }
        """)

        for obj in objects:
            if obj['isLight'] or 'Light' in obj['type']:
                print(f"  {obj['type']:20s} name={obj['name']:20s} intensity={obj['intensity']} pos={obj['position']}")

        print("\n=== WINDOW.LIGHTS ===")
        window_lights = await page.evaluate("""
            () => {
                const lights = window.lights;
                if (!lights) return { error: 'window.lights not found' };

                return {
                    spotLeft: lights.spotLeft ? {
                        type: lights.spotLeft.type,
                        intensity: lights.spotLeft.intensity,
                        position: `(${lights.spotLeft.position.x}, ${lights.spotLeft.position.y}, ${lights.spotLeft.position.z})`
                    } : 'NOT FOUND',
                    spotRight: lights.spotRight ? {
                        type: lights.spotRight.type,
                        intensity: lights.spotRight.intensity,
                        position: `(${lights.spotRight.position.x}, ${lights.spotRight.position.y}, ${lights.spotRight.position.z})`
                    } : 'NOT FOUND',
                    backLight: lights.backLight ? {
                        type: lights.backLight.type,
                        intensity: lights.backLight.intensity,
                        position: `(${lights.backLight.position.x}, ${lights.backLight.position.y}, ${lights.backLight.position.z})`
                    } : 'NOT FOUND'
                };
            }
        """)
        print(window_lights)

        print("\n\nKeeping browser open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
