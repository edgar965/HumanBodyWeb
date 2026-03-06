"""
Test Theatre toolbar and character with hair/garments
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        print("Loading Theatre page...")
        await page.goto('http://localhost:8081/humanbody/theatre/', wait_until='networkidle')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(3)

        print("\n1. Taking screenshot of initial view with toolbar...")
        await page.screenshot(path='theatre_toolbar_initial.png')
        print("✓ Screenshot: theatre_toolbar_initial.png")

        print("\n2. Checking toolbar buttons...")
        toolbar_check = await page.evaluate("""
            () => {
                const translateBtn = document.getElementById('btn-translate-mode');
                const rotateBtn = document.getElementById('btn-rotate-mode');
                const lightsBtn = document.getElementById('btn-toggle-lights');

                return {
                    hasTranslateBtn: !!translateBtn,
                    hasRotateBtn: !!rotateBtn,
                    hasLightsBtn: !!lightsBtn,
                    translateActive: translateBtn?.classList.contains('active'),
                    rotateActive: rotateBtn?.classList.contains('active'),
                    lightsActive: lightsBtn?.classList.contains('active')
                };
            }
        """)
        print(f"Toolbar buttons: {toolbar_check}")

        print("\n3. Clicking rotate mode button...")
        await page.click('#btn-rotate-mode')
        await asyncio.sleep(1)

        rotate_check = await page.evaluate("""
            () => {
                return {
                    rotateActive: document.getElementById('btn-rotate-mode')?.classList.contains('active'),
                    translateActive: document.getElementById('btn-translate-mode')?.classList.contains('active'),
                    transformMode: window.transformControls?.mode
                };
            }
        """)
        print(f"After rotate click: {rotate_check}")

        print("\n4. Loading FemaleGarment preset (with hair and clothes)...")
        await page.evaluate("""
            async () => {
                const preset = await fetch('/api/character/model/FemaleGarment/').then(r => r.json());
                console.log('Preset loaded:', preset);
                window.lastPreset = preset;

                // Import loadCharacterFromPreset
                const { loadCharacterFromPreset } = await import('/static/theatre/theatre-app.js');
                const group = await loadCharacterFromPreset(window.scene, preset, 'FemaleGarment');
                console.log('Character loaded:', group);
            }
        """)
        await asyncio.sleep(5) # Wait for assets to load

        print("\n5. Taking screenshot after loading character with garments...")
        await page.screenshot(path='theatre_with_garments.png')
        print("✓ Screenshot: theatre_with_garments.png")

        print("\n6. Checking scene objects...")
        scene_check = await page.evaluate("""
            () => {
                const scene = window.scene;
                let meshCount = 0;
                let skinnedMeshCount = 0;
                let groups = 0;

                scene.traverse((obj) => {
                    if (obj.isMesh) meshCount++;
                    if (obj.isSkinnedMesh) skinnedMeshCount++;
                    if (obj.isGroup && obj.children.length > 0) groups++;
                });

                return { meshCount, skinnedMeshCount, groups };
            }
        """)
        print(f"Scene objects: {scene_check}")

        print("\n7. Toggling lights off...")
        await page.click('#btn-toggle-lights')
        await asyncio.sleep(1)
        await page.screenshot(path='theatre_lights_hidden.png')
        print("✓ Screenshot: theatre_lights_hidden.png")

        print("\n\nKeeping browser open for 20 seconds...")
        print("Manually test:")
        print("  - Click translate/rotate mode buttons")
        print("  - Click on a light icon and try rotating it")
        print("  - Toggle lights visibility")
        await asyncio.sleep(20)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
