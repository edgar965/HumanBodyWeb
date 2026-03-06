"""
Debug skin herringbone pattern
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

        print("\nLoading FemaleGarment...")
        await page.click('[data-tab="tab-models"]')
        await asyncio.sleep(2)

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
        await asyncio.sleep(5)

        print("\nTaking close-up screenshot...")
        await page.screenshot(path='debug_skin_closeup.png')

        print("\nChecking renderer settings...")
        settings = await page.evaluate("""
            () => {
                const scene = window.scene;
                let renderer = null;

                // Find renderer from canvas
                const canvas = document.getElementById('theatre-canvas');
                if (canvas) {
                    renderer = canvas.getContext('webgl2') || canvas.getContext('webgl');
                }

                return {
                    exposure: window.renderer?.toneMappingExposure,
                    toneMapping: window.renderer?.toneMapping,
                    shadowMapEnabled: window.renderer?.shadowMap?.enabled,
                    shadowMapType: window.renderer?.shadowMap?.type
                };
            }
        """)
        print(f"Renderer settings: {settings}")

        print("\nChecking material properties...")
        materials = await page.evaluate("""
            () => {
                const scene = window.scene;
                const mats = [];

                scene.traverse((obj) => {
                    if (obj.isMesh && obj.material) {
                        if (Array.isArray(obj.material)) {
                            for (let i = 0; i < obj.material.length; i++) {
                                const m = obj.material[i];
                                mats.push({
                                    index: i,
                                    color: m.color?.getHexString(),
                                    roughness: m.roughness,
                                    metalness: m.metalness,
                                    side: m.side,
                                    flatShading: m.flatShading,
                                    hasNormals: obj.geometry.attributes.normal !== undefined
                                });
                            }
                        } else {
                            const m = obj.material;
                            mats.push({
                                color: m.color?.getHexString(),
                                roughness: m.roughness,
                                metalness: m.metalness,
                                side: m.side,
                                flatShading: m.flatShading,
                                hasNormals: obj.geometry.attributes.normal !== undefined
                            });
                        }
                    }
                });

                return mats;
            }
        """)
        print(f"Materials found: {len(materials)}")
        for i, mat in enumerate(materials[:5]):  # Show first 5
            print(f"  [{i}] {mat}")

        print("\n\nBrowser stays open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
