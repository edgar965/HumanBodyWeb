"""
Test all 3 fixes: Settings dropdown, Animation play, White hair
"""
import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=400)
        page = await browser.new_page()

        print("=== FIX 1: Settings-Theatre Dropdown ===")
        await page.goto('http://localhost:8081/settings/theatre/')
        await page.wait_for_selector('.settings-card', timeout=5000)
        await asyncio.sleep(1)

        dropdown = await page.evaluate("""
            () => {
                const select = document.querySelector('select[name="theatre_default_animation"]');
                const optgroups = select.querySelectorAll('optgroup');
                return {
                    optgroupCount: optgroups.length,
                    firstGroup: optgroups[0]?.label || 'NONE',
                    firstOptionCount: optgroups[0]?.querySelectorAll('option').length || 0
                };
            }
        """)
        print(f"Dropdown: {dropdown}")
        print(f"✓ Fixed!" if dropdown['optgroupCount'] > 0 else "✗ Still broken!")

        print("\n=== FIX 2 & 3: Animation Play + Hair Color ===")
        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(2)

        # Load character with hair
        await page.click('[data-tab="tab-models"]')
        await asyncio.sleep(1)
        await page.evaluate("""
            () => {
                const items = document.querySelectorAll('.anim-item');
                for (const item of items) {
                    if (item.textContent.includes('FemaleWithHair')) {
                        item.click();
                        return;
                    }
                }
            }
        """)
        await asyncio.sleep(4)
        await page.screenshot(path='fix_hair_color.png')
        print("✓ Screenshot: fix_hair_color.png (check if hair is dark, not white)")

        # Load animation
        await page.click('[data-tab="tab-animations"]')
        await asyncio.sleep(1)
        await page.evaluate("() => document.querySelector('.anim-cat-header')?.click()")
        await asyncio.sleep(0.5)
        await page.evaluate("() => document.querySelector('.anim-cat-body .anim-item')?.click()")
        await asyncio.sleep(3)

        state_loaded = await page.evaluate("""
            () => ({
                hasActiveMixer: !!window.activeMixer,
                animDuration: window.animDuration,
                isPlaying: window.isPlaying
            })
        """)
        print(f"After loading animation: {state_loaded}")

        # Click play
        await page.click('#btnPlayPause')
        await asyncio.sleep(0.5)

        state_playing = await page.evaluate("() => ({ isPlaying: window.isPlaying })")
        print(f"After clicking play: {state_playing}")
        print(f"✓ Animation plays!" if state_playing['isPlaying'] else "✗ Animation doesn't play!")

        await asyncio.sleep(2)
        await page.screenshot(path='fix_animation_playing.png')
        print("✓ Screenshot: fix_animation_playing.png")

        print("\n\nAll fixes tested! Browser stays open for 15 seconds...")
        await asyncio.sleep(15)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
