"""
Test Animation + Rig Anzeigen Buttons
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        print("=== Loading Theatre ===")
        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(2)

        print("=== Loading Model ===")
        await page.click('[data-tab="tab-models"]')
        await asyncio.sleep(1)
        await page.evaluate("() => document.querySelector('.anim-item')?.click()")
        await asyncio.sleep(3)

        print("=== Loading Animation ===")
        await page.click('[data-tab="tab-animations"]')
        await asyncio.sleep(1)
        await page.evaluate("() => document.querySelector('.anim-cat-header')?.click()")
        await asyncio.sleep(0.5)
        await page.evaluate("() => document.querySelector('.anim-cat-body .anim-item')?.click()")
        await asyncio.sleep(3)

        state_after_load = await page.evaluate("""
            () => ({
                hasActiveMixer: !!window.activeMixer,
                animDuration: window.animDuration,
                isPlaying: window.isPlaying
            })
        """)
        print(f"After loading animation: {state_after_load}")

        print("=== Clicking Toolbar Rig Button ===")
        rig_btn = await page.query_selector('#btn-toggle-rig')
        if rig_btn:
            await rig_btn.click()
            await asyncio.sleep(1)
            is_active = await page.evaluate("() => document.getElementById('btn-toggle-rig')?.classList.contains('active')")
            print(f"Rig button active: {is_active}")
        else:
            print("RIG BUTTON NOT FOUND!")

        print("=== Clicking Toolbar Play Button ===")
        play_btn = await page.query_selector('#btn-play-animation')
        if play_btn:
            await play_btn.click()
            await asyncio.sleep(1)
            state_playing = await page.evaluate("() => ({ isPlaying: window.isPlaying })")
            print(f"After clicking play: {state_playing}")
        else:
            print("PLAY BUTTON NOT FOUND!")

        await page.screenshot(path='test_anim_rig.png', full_page=True)
        print("Screenshot: test_anim_rig.png")

        print("\nBrowser stays open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
