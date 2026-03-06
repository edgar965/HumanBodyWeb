"""
Test ALL presets - create screenshots for comparison
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=800)
        page = await browser.new_page()

        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(3)

        presets = [
            ('ballet_stage', 'Ballet Stage'),
            ('studio_bright', 'Studio Bright'),
            ('cinematic_moody', 'Cinematic Moody'),
            ('fashion_show', 'Fashion Show'),
            ('sunset_warm', 'Sunset Warm')
        ]

        for preset_key, preset_name in presets:
            print(f"\n{'='*60}")
            print(f"Testing: {preset_name}")
            print('='*60)

            # Open Settings menu
            await page.click('.menu-item:has-text("Settings")')
            await asyncio.sleep(0.3)

            # Click preset
            await page.click(f'[data-preset="{preset_key}"]')
            await asyncio.sleep(1.5)

            # Take screenshot
            filename = f'preset_{preset_key}.png'
            await page.screenshot(path=filename)
            print(f"✓ Screenshot: {filename}")

        print("\n" + "="*60)
        print("ALLE PRESETS GETESTET!")
        print("="*60)
        print("\nScreenshots:")
        for preset_key, preset_name in presets:
            print(f"  - preset_{preset_key}.png  ({preset_name})")

        print("\n\nKeeping browser open for 10 seconds...")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
