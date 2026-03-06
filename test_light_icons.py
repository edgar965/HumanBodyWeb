"""
Test light icons and properties panel
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=800)
        context = await browser.new_context()
        page = await context.new_page()

        print("Loading Theatre page...")
        await page.goto('http://localhost:8081/humanbody/theatre/', wait_until='networkidle')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(3)

        print("\n1. Taking screenshot of initial view with light icons...")
        await page.screenshot(path='theatre_light_icons.png')
        print("✓ Screenshot: theatre_light_icons.png")

        # Click on a light icon (approximate center of left spotlight)
        print("\n2. Clicking on left spotlight icon...")
        canvas = await page.query_selector('#theatre-canvas')
        box = await canvas.bounding_box()
        # Click left upper area where spotlight should be
        await page.mouse.click(box['x'] + box['width'] * 0.3, box['y'] + box['height'] * 0.2)
        await asyncio.sleep(1)

        print("\n3. Taking screenshot after clicking light...")
        await page.screenshot(path='theatre_light_selected.png')
        print("✓ Screenshot: theatre_light_selected.png")

        print("\n\nKeeping browser open for 15 seconds...")
        print("Manually test clicking on light icons!")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
