"""Playwright: shoe animation binding test."""
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

        print("=== LOADING ===")
        page.goto(f"{BASE}/humanbody/config/", wait_until="networkidle")
        time.sleep(6)

        # Open Garment Fit panel and create shoe
        page.locator('[data-panel-key="garment_fit"] h3').click()
        time.sleep(1)

        shoe = page.locator('.garment-item[data-garment-id="shoes/shoes01"]')
        shoe.click()
        time.sleep(0.3)
        page.evaluate("() => { document.getElementById('garment-color').value = '#8B4513'; }")
        page.locator('#garment-create').click()
        time.sleep(5)

        page.screenshot(path=f"{SHOTS}/70_shoe_rest.png")

        # Play animation
        print("=== PLAY ANIMATION ===")
        play_btn = page.locator('#play-demo-anim')
        if play_btn.count() > 0 and play_btn.is_visible():
            play_btn.click()
            time.sleep(2)
            page.screenshot(path=f"{SHOTS}/71_shoe_anim_2s.png")
            time.sleep(3)
            page.screenshot(path=f"{SHOTS}/72_shoe_anim_5s.png")

            # Side view during animation
            page.evaluate("""() => {
                const v = window.__viewer;
                v.camera.position.set(2.0, 0.5, 0);
                v.controls.target.set(0, 0.5, 0);
                v.controls.update();
            }""")
            time.sleep(2)
            page.screenshot(path=f"{SHOTS}/73_shoe_anim_side.png")

            # Stop
            play_btn.click()
            time.sleep(1)
        else:
            print("Play button not found!")

        # Console
        print("\n=== Console ===")
        for msg in console_msgs:
            if 'arment' in msg or 'error' in msg.lower() or 'Error' in msg or 'anim' in msg.lower():
                print(f"  {msg}")

        print("\nDone!")
        browser.close()


if __name__ == "__main__":
    import os
    os.makedirs(SHOTS, exist_ok=True)
    run()
