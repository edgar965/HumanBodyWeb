"""
Debug Theatre Menu - Settings Presets funktionieren nicht
"""
import asyncio
import sys
from playwright.async_api import async_playwright

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        # Collect console messages
        console_messages = []
        page.on('console', lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # Collect errors
        page.on('pageerror', lambda err: print(f"ERROR Page Error: {err}"))

        print("Opening Theatre page...")
        await page.goto('http://localhost:8081/humanbody/theatre/')

        # Wait for canvas to be ready
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        print("OK Canvas loaded")

        # Wait for Three.js to initialize
        await asyncio.sleep(2)

        # Take screenshot of initial state
        await page.screenshot(path='theatre_01_initial.png')
        print("SCREENSHOT 1: Initial state")

        # Try to hover over Settings menu
        print("\nHovering over Settings menu...")
        settings_menu = page.locator('.menu-item:has-text("Settings")')
        await settings_menu.hover()
        await asyncio.sleep(1)

        # Take screenshot of menu open
        await page.screenshot(path='theatre_02_menu_open.png')
        print("SCREENSHOT 2: Menu should be open")

        # Check if dropdown is visible
        dropdown_visible = await page.locator('.menu-item:has-text("Settings") .menu-dropdown').is_visible()
        print(f"Dropdown visible: {dropdown_visible}")

        if not dropdown_visible:
            print("ERROR: Dropdown not visible on hover!")
            # Try clicking instead
            print("Trying click instead of hover...")
            await settings_menu.click()
            await asyncio.sleep(1)
            dropdown_visible = await page.locator('.menu-item:has-text("Settings") .menu-dropdown').is_visible()
            print(f"After click - Dropdown visible: {dropdown_visible}")

        # Try to click on Studio Bright preset
        print("\nClicking on 'Studio Bright' preset...")

        # Wait for the preset button to be visible
        studio_bright = page.locator('[data-preset="studio_bright"]')

        if await studio_bright.is_visible():
            print("OK Studio Bright button is visible")
            await studio_bright.click()
            print("OK Clicked Studio Bright")
            await asyncio.sleep(2)

            # Take screenshot after preset click
            await page.screenshot(path='theatre_03_after_preset.png')
            print("SCREENSHOT 3: After Studio Bright click")
        else:
            print("ERROR: Studio Bright button not visible!")
            await page.screenshot(path='theatre_03_button_not_visible.png')

        # Print console messages
        print("\nConsole messages:")
        for msg in console_messages:
            print(f"  {msg}")

        # Check light intensity via JS
        print("\nChecking light intensities...")
        intensity_check = await page.evaluate("""
            () => {
                // Find spotLeft in the scene
                const canvas = document.getElementById('theatre-canvas');
                if (!canvas) return { error: 'Canvas not found' };

                // Try to get the Three.js renderer from window
                return { note: 'Need to expose lights to window for inspection' };
            }
        """)
        print(f"Intensity check: {intensity_check}")

        print("\nKeeping browser open for 30 seconds for manual inspection...")
        await asyncio.sleep(30)

        await browser.close()
        print("\nDebug session complete. Check screenshots:")
        print("  - theatre_01_initial.png")
        print("  - theatre_02_menu_open.png")
        print("  - theatre_03_after_preset.png")

if __name__ == '__main__':
    asyncio.run(main())
