"""Quick check: PE mode buttons not clipped."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:4040/humanbody/config/", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(5)

        # Switch to Pattern tab
        await page.evaluate('''() => {
            document.querySelector('.panel-tab[data-tab="tab-creator"]').click();
        }''')
        await asyncio.sleep(0.5)

        # Check all 5 buttons visible
        btns = await page.evaluate('''() => {
            const btns = document.querySelectorAll('#pe-mode-btns .btn-toggle');
            return Array.from(btns).map(b => ({
                mode: b.dataset.mode,
                text: b.textContent.trim(),
                rect: b.getBoundingClientRect(),
                visible: b.offsetParent !== null
            }));
        }''')

        panel_rect = await page.evaluate('''() => {
            const p = document.querySelector('.viewer-panel');
            return p ? p.getBoundingClientRect() : null;
        }''')

        print(f"Panel right edge: {panel_rect['right']:.0f}")
        for b in btns:
            clipped = b['rect']['right'] > panel_rect['right']
            print(f"  {b['mode']:8s} text='{b['text']:8s}' right={b['rect']['right']:.0f} {'CLIPPED' if clipped else 'OK'}")

        await page.screenshot(path="A:/HumanBodyTest/HumanBodyWeb/test_screenshots/ve_mode_btns.png")
        await browser.close()

asyncio.run(main())
