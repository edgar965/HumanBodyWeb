"""Playwright test: Garment fitting verification with individual garment screenshots."""
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:4040"
SHOTS = "A:/HumanBodyTest/HumanBodyWeb/test_screenshots"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))

        print("[1] Loading page...")
        page.goto(f"{BASE}/humanbody/config/", wait_until="networkidle")
        time.sleep(5)

        # Remove any default cloth
        try:
            page.locator('#cloth-remove-all').click(timeout=1000)
            time.sleep(0.5)
        except:
            pass

        # Open Garment Fit panel
        print("[2] Opening Garment Fit panel...")
        page.locator('[data-panel-key="garment_fit"] h3').click()
        time.sleep(1)

        # === TEST 1: SHOE ONLY ===
        print("[3] Testing Shoes01 (solo)...")
        shoe = page.locator('.garment-item[data-garment-id="shoes/shoes01"]')
        shoe.click()
        time.sleep(0.3)
        page.evaluate("() => { document.getElementById('garment-color').value = '#8B4513'; }")
        page.locator('#garment-create').click()
        time.sleep(5)

        # Full view
        page.screenshot(path=f"{SHOTS}/30_shoe_only.png")

        # Zoom to feet
        page.evaluate("""() => {
            const canvas = document.getElementById('viewer-canvas');
            for (let i = 0; i < 15; i++)
                canvas.dispatchEvent(new WheelEvent('wheel', {
                    deltaY: -100, clientX: 700, clientY: 800, bubbles: true
                }));
        }""")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS}/31_shoe_closeup.png")

        # Remove shoe
        page.locator('#garment-remove').click()
        time.sleep(0.5)

        # Zoom back
        page.evaluate("""() => {
            const canvas = document.getElementById('viewer-canvas');
            for (let i = 0; i < 15; i++)
                canvas.dispatchEvent(new WheelEvent('wheel', {
                    deltaY: 100, clientX: 700, clientY: 450, bubbles: true
                }));
        }""")
        time.sleep(0.5)

        # === TEST 2: FEMALE CASUALSUIT ONLY ===
        print("[4] Testing Female Casualsuit01 (solo)...")
        suit_f = page.locator('.garment-item[data-garment-id="tops/female_casualsuit01"]')
        suit_f.click()
        time.sleep(0.3)
        page.evaluate("() => { document.getElementById('garment-color').value = '#4a5a80'; }")
        page.locator('#garment-create').click()
        time.sleep(5)
        page.screenshot(path=f"{SHOTS}/32_female_suit_only.png")

        # Remove
        page.locator('#garment-remove').click()
        time.sleep(0.5)

        # === TEST 3: MALE CASUALSUIT ONLY ===
        print("[5] Testing Male Casualsuit01 (solo)...")
        suit_m = page.locator('.garment-item[data-garment-id="tops/male_casualsuit01"]')
        suit_m.click()
        time.sleep(0.3)
        page.evaluate("() => { document.getElementById('garment-color').value = '#3a6a3a'; }")
        page.locator('#garment-create').click()
        time.sleep(5)
        page.screenshot(path=f"{SHOTS}/33_male_suit_only.png")

        # Remove
        page.locator('#garment-remove').click()
        time.sleep(0.5)

        # === TEST 4: ALL GARMENTS TOGETHER ===
        print("[6] Adding all garments...")
        shoe.click()
        time.sleep(0.2)
        page.evaluate("() => { document.getElementById('garment-color').value = '#8B4513'; }")
        page.locator('#garment-create').click()
        time.sleep(4)

        suit_f.click()
        time.sleep(0.2)
        page.evaluate("() => { document.getElementById('garment-color').value = '#4a5a80'; }")
        page.locator('#garment-create').click()
        time.sleep(4)

        page.screenshot(path=f"{SHOTS}/34_shoes_and_suit.png")

        # === TEST 5: REMOVE ALL ===
        print("[7] Remove all garments...")
        page.locator('#garment-remove-all').click()
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/35_all_removed.png")

        # Print relevant console messages
        print("\nConsole (garment/error):")
        for msg in console_msgs:
            if 'arment' in msg or 'error' in msg.lower() or 'Error' in msg:
                print(f"  {msg}")

        print("\nDone!")
        browser.close()


if __name__ == "__main__":
    import os
    os.makedirs(SHOTS, exist_ok=True)
    run()
