"""
Test both issues: Settings dropdown + Animation play
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        print("=== TEST 1: Settings-Theatre Dropdown ===")
        await page.goto('http://localhost:8081/settings/theatre/')
        await page.wait_for_selector('.settings-card', timeout=5000)
        await asyncio.sleep(1)

        dropdown_info = await page.evaluate("""
            () => {
                const select = document.querySelector('select[name="theatre_default_animation"]');
                const optgroups = select.querySelectorAll('optgroup');
                const options = select.querySelectorAll('option');

                return {
                    optgroupCount: optgroups.length,
                    optionCount: options.length,
                    firstOptgroup: optgroups[0]?.label || 'NONE',
                    firstOption: optgroups[0]?.querySelectorAll('option')[0]?.textContent || 'NONE'
                };
            }
        """)
        print(f"Dropdown: {dropdown_info}")
        await page.screenshot(path='test_settings_dropdown_fixed.png', full_page=True)

        print("\n=== TEST 2: Animation Play in Theatre ===")
        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(2)

        print("Loading character...")
        await page.click('[data-tab="tab-models"]')
        await asyncio.sleep(1)
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
        await asyncio.sleep(3)

        print("Loading animation...")
        await page.click('[data-tab="tab-animations"]')
        await asyncio.sleep(1)
        await page.evaluate("() => document.querySelector('.anim-cat-header')?.click()")
        await asyncio.sleep(0.5)

        anim_loaded = await page.evaluate("""
            () => {
                const firstItem = document.querySelector('.anim-cat-body .anim-item');
                if (firstItem) {
                    firstItem.click();
                    return true;
                }
                return false;
            }
        """)
        print(f"Animation loaded: {anim_loaded}")
        await asyncio.sleep(3)

        print("Checking animation state BEFORE play...")
        state_before = await page.evaluate("""
            () => {
                return {
                    hasActiveMixer: !!window.activeMixer,
                    isPlaying: window.isPlaying,
                    playBtnText: document.getElementById('btnPlayPause')?.textContent?.trim()
                };
            }
        """)
        print(f"Before play: {state_before}")

        print("Clicking play button...")
        await page.click('#btnPlayPause')
        await asyncio.sleep(0.5)

        state_after = await page.evaluate("""
            () => {
                return {
                    isPlaying: window.isPlaying,
                    playBtnText: document.getElementById('btnPlayPause')?.textContent?.trim(),
                    currentTime: window.currentTime,
                    animDuration: window.animDuration
                };
            }
        """)
        print(f"After play: {state_after}")

        await asyncio.sleep(2)
        await page.screenshot(path='test_animation_playing.png')
        print("✓ Screenshot: test_animation_playing.png")

        print("\n\nBrowser stays open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
