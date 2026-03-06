"""
Complete Theatre Debug - Check if lights ACTUALLY change
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()

        console_messages = []
        page.on('console', lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on('pageerror', lambda err: print(f"ERROR: {err}"))

        print("=" * 60)
        print("THEATRE DEBUG - Complete Test")
        print("=" * 60)

        print("\n1. Loading page...")
        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        print("OK Page loaded")

        # Wait for Three.js init
        await asyncio.sleep(3)

        # Take initial screenshot
        await page.screenshot(path='debug_01_initial.png')
        print("\n2. Screenshot 1: Initial state")

        # Inject code to expose lights to window
        print("\n3. Injecting debug code to expose lights...")
        await page.evaluate("""
            () => {
                // Try to find and expose lights from the scene
                window.DEBUG_LIGHTS_FOUND = false;
                window.DEBUG_LIGHTS = {};

                // Give it a moment for the app to initialize
                setTimeout(() => {
                    // The lights should be in the Three.js scene
                    // We need to wait for them to be created
                    console.log('[DEBUG] Attempting to find lights in scene...');
                }, 1000);
            }
        """)

        # Click on Settings menu
        print("\n4. Clicking Settings menu...")
        await page.click('.menu-item:has-text("Settings")')
        await asyncio.sleep(1)
        await page.screenshot(path='debug_02_menu_open.png')
        print("SCREENSHOT 2: Settings menu open")

        # Check if Studio Bright is visible
        studio_visible = await page.locator('[data-preset="studio_bright"]').is_visible()
        print(f"Studio Bright visible: {studio_visible}")

        if not studio_visible:
            print("ERROR: Studio Bright button not visible!")
            await browser.close()
            return

        # Get light intensities BEFORE clicking preset
        print("\n5. Reading light intensities BEFORE preset change...")
        before_intensities = await page.evaluate("""
            () => {
                // Try to access the scene from global scope
                // The app might expose it or we can try to find it
                return {
                    note: 'Cannot read lights - need to expose them in main.js'
                };
            }
        """)
        print(f"BEFORE: {before_intensities}")

        # Click Studio Bright
        print("\n6. Clicking Studio Bright preset...")
        await page.click('[data-preset="studio_bright"]')
        await asyncio.sleep(2)
        await page.screenshot(path='debug_03_after_studio_bright.png')
        print("SCREENSHOT 3: After Studio Bright")

        # Check if menu closed
        menu_closed = not await page.locator('.menu-item.active').is_visible()
        print(f"Menu closed after click: {menu_closed}")

        # Get light intensities AFTER clicking preset
        print("\n7. Reading light intensities AFTER preset change...")
        after_intensities = await page.evaluate("""
            () => {
                return {
                    note: 'Cannot read lights - need to expose them in main.js'
                };
            }
        """)
        print(f"AFTER: {after_intensities}")

        # Print all console messages
        print("\n8. Console messages:")
        for msg in console_messages[-20:]:  # Last 20 messages
            print(f"  {msg}")

        # Visual comparison instruction
        print("\n" + "=" * 60)
        print("VISUAL CHECK:")
        print("Compare these screenshots:")
        print("  debug_01_initial.png")
        print("  debug_03_after_studio_bright.png")
        print("\nIf they look IDENTICAL, the preset is NOT working!")
        print("=" * 60)

        # Keep browser open for manual inspection
        print("\nKeeping browser open for 20 seconds...")
        print("Manually click different presets and watch console!")
        await asyncio.sleep(20)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
