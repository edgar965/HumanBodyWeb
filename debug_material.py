"""
Debug - Check character material opacity and transparency
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

        print("\n=== CHARACTER MATERIAL DEBUG ===")
        mat_info = await page.evaluate("""
            () => {
                const scene = window.scene;
                const results = [];

                scene.traverse((obj) => {
                    if (obj.isMesh && obj.geometry && obj.geometry.attributes.position) {
                        const mat = obj.material;
                        const vcount = obj.geometry.attributes.position.count;

                        results.push({
                            name: obj.name || '(unnamed)',
                            vertices: vcount,
                            material: {
                                type: mat.type,
                                color: mat.color ? {
                                    hex: '#' + mat.color.getHexString(),
                                    rgb: `rgb(${(mat.color.r * 255).toFixed(0)}, ${(mat.color.g * 255).toFixed(0)}, ${(mat.color.b * 255).toFixed(0)})`
                                } : 'N/A',
                                opacity: mat.opacity,
                                transparent: mat.transparent,
                                visible: obj.visible,
                                side: mat.side === 0 ? 'FrontSide' : mat.side === 1 ? 'BackSide' : 'DoubleSide',
                                roughness: mat.roughness,
                                metalness: mat.metalness,
                                wireframe: mat.wireframe,
                            },
                            position: `(${obj.position.x.toFixed(2)}, ${obj.position.y.toFixed(2)}, ${obj.position.z.toFixed(2)})`,
                            rotation: `(${(obj.rotation.x * 180 / Math.PI).toFixed(1)}°, ${(obj.rotation.y * 180 / Math.PI).toFixed(1)}°, ${(obj.rotation.z * 180 / Math.PI).toFixed(1)}°)`,
                            visible: obj.visible,
                        });
                    }
                });

                return results;
            }
        """)

        for i, mesh in enumerate(mat_info):
            print(f"\n[{i}] {mesh['name']} - {mesh['vertices']} vertices")
            print(f"    Position: {mesh['position']}")
            print(f"    Rotation: {mesh['rotation']}")
            print(f"    Visible: {mesh['visible']}")
            print(f"    Material Type: {mesh['material']['type']}")
            print(f"    Color: {mesh['material']['color']['hex']} {mesh['material']['color']['rgb']}")
            print(f"    Opacity: {mesh['material']['opacity']}")
            print(f"    Transparent: {mesh['material']['transparent']}")
            print(f"    Side: {mesh['material']['side']}")
            print(f"    Roughness: {mesh['material']['roughness']}, Metalness: {mesh['material']['metalness']}")
            print(f"    Wireframe: {mesh['material']['wireframe']}")

        print("\n\nKeeping browser open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
