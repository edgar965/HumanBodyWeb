"""
Debug - Check character mesh position and material
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

        print("\n=== CHARACTER MESH INFO ===")
        char_info = await page.evaluate("""
            () => {
                const scene = window.scene;
                const meshes = [];

                scene.traverse((obj) => {
                    if (obj.isMesh && obj.geometry && obj.geometry.attributes.position) {
                        const mat = obj.material;
                        meshes.push({
                            name: obj.name || '(unnamed)',
                            type: obj.type,
                            vertexCount: obj.geometry.attributes.position.count,
                            position: `(${obj.position.x.toFixed(2)}, ${obj.position.y.toFixed(2)}, ${obj.position.z.toFixed(2)})`,
                            scale: `(${obj.scale.x.toFixed(2)}, ${obj.scale.y.toFixed(2)}, ${obj.scale.z.toFixed(2)})`,
                            material: {
                                type: mat ? mat.type : 'N/A',
                                color: mat && mat.color ? `rgb(${(mat.color.r * 255).toFixed(0)}, ${(mat.color.g * 255).toFixed(0)}, ${(mat.color.b * 255).toFixed(0)})` : 'N/A',
                                roughness: mat ? mat.roughness : 'N/A',
                                metalness: mat ? mat.metalness : 'N/A',
                            },
                            receiveShadow: obj.receiveShadow,
                            castShadow: obj.castShadow
                        });
                    }
                });

                return meshes;
            }
        """)

        for i, mesh in enumerate(char_info):
            print(f"\n[{i}] {mesh['name']}")
            print(f"    Type: {mesh['type']}, Vertices: {mesh['vertexCount']}")
            print(f"    Position: {mesh['position']}, Scale: {mesh['scale']}")
            print(f"    Material: {mesh['material']['type']}")
            print(f"    Color: {mesh['material']['color']}, Roughness: {mesh['material']['roughness']}, Metalness: {mesh['material']['metalness']}")
            print(f"    Shadows: cast={mesh['castShadow']}, receive={mesh['receiveShadow']}")

        print("\n\nKeeping browser open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
