"""
Debug - Check if light icons exist in scene
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(3)

        print("\n=== CHECKING LIGHT ICONS ===")
        icons = await page.evaluate("""
            () => {
                const scene = window.scene;
                const icons = [];

                scene.traverse((obj) => {
                    if (obj.userData && obj.userData.light) {
                        icons.push({
                            hasLight: true,
                            position: `(${obj.position.x.toFixed(2)}, ${obj.position.y.toFixed(2)}, ${obj.position.z.toFixed(2)})`,
                            children: obj.children.length,
                            visible: obj.visible
                        });
                    }
                });

                return {
                    lightIcons: window.lightIcons ? Object.keys(window.lightIcons) : 'NOT FOUND',
                    iconsInScene: icons.length,
                    icons: icons
                };
            }
        """)

        print(f"window.lightIcons: {icons['lightIcons']}")
        print(f"Icons in scene: {icons['iconsInScene']}")
        for i, icon in enumerate(icons['icons']):
            print(f"  [{i}] Position: {icon['position']}, Children: {icon['children']}, Visible: {icon['visible']}")

        print("\n\nKeeping browser open...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
