"""Test: default character loads as proper entry, selectable + deletable."""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        errors = []
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}"))

        await page.goto("http://localhost:4040/humanbody/scene/", timeout=15000)
        await page.wait_for_timeout(4000)

        # 1. Default character loaded
        chars = await page.query_selector_all(".character-item")
        vtx = await page.text_content("#vertex-count")
        char_count = await page.text_content("#char-count")
        print(f"On load: {len(chars)} chars, {vtx} verts, count={char_count}")

        # 2. Expand panel if collapsed
        char_panel = await page.query_selector("[data-panel-key='charaktere']")
        if char_panel:
            is_collapsed = await char_panel.evaluate("el => el.classList.contains('collapsed')")
            if is_collapsed:
                await (await char_panel.query_selector("h3")).click()
                await page.wait_for_timeout(300)

        # 3. Select via list
        item = await page.query_selector(".character-item")
        if item:
            name = await (await item.query_selector(".character-item-name")).text_content()
            print(f"  Name: {name}")
            await item.click()
            await page.wait_for_timeout(300)
            print(f"Selected: {await page.query_selector('.character-item.selected') is not None}")

        # 4. Deselect Esc
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(300)
        print(f"Deselect Esc: {await page.query_selector('.character-item.selected') is None}")

        # 5. Re-select + delete via menu
        item2 = await page.query_selector(".character-item")
        if item2:
            await item2.click()
            await page.wait_for_timeout(300)
            page.on("dialog", lambda d: d.accept())
            await page.click("text=Bearbeiten")
            await page.wait_for_timeout(300)
            await page.click("[data-action='delete']")
            await page.wait_for_timeout(500)
            remaining = await page.query_selector_all(".character-item")
            print(f"After delete: {len(remaining)} chars")

        # 6. Datei > Neu reloads default
        await page.click("text=Datei")
        await page.wait_for_timeout(300)
        await page.click("[data-action='new']")
        await page.wait_for_timeout(4000)
        chars_new = await page.query_selector_all(".character-item")
        print(f"After Neu: {len(chars_new)} chars")

        await page.screenshot(path="test_screenshots/scene_default_char.png")

        for e in errors:
            if "error" in e.lower():
                print(f"  ERR: {e}")

        await browser.close()
        print("Done!")

asyncio.run(test())
