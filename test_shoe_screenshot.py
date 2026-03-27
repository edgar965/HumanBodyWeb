"""Take screenshot of shoe fitting result."""
import time, os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:4040"
SHOTS = "A:/HumanBodyTest/HumanBodyWeb/test_screenshots"


def run():
    os.makedirs(SHOTS, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        page.goto(f"{BASE}/humanbody/config/", wait_until="networkidle")
        time.sleep(6)

        # Remove default cloth
        try:
            page.locator('#cloth-remove-all').click(timeout=1000)
            time.sleep(0.5)
        except:
            pass

        # Set meta sliders (age=59, mass=123, tone=50, height=175)
        print("[1] Setting meta sliders...")
        page.evaluate("""() => {
            const setSlider = (id, val) => {
                const el = document.getElementById(id);
                if (el) {
                    el.value = val;
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                }
            };
            setSlider('meta-age', 59);
            setSlider('meta-mass', 123);
            setSlider('meta-tone', 50);
            setSlider('meta-height', 175);
        }""")
        time.sleep(3)

        # Create shoe
        print("[2] Creating shoe...")
        page.locator('[data-panel-key="garment_fit"] h3').click()
        time.sleep(1)
        page.locator('.garment-item[data-garment-id="shoes/shoes01"]').click()
        time.sleep(0.5)
        page.locator('#garment-create').click()
        time.sleep(10)

        # --- Screenshots from multiple angles ---

        # 1. Low 3/4 view (feet focus)
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.4, -0.05, 0.5);
            v.controls.update();
        }""")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS}/shoe_result_34view.png")
        print("  -> shoe_result_34view.png")

        # 2. Front close-up
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.03, 0);
            v.camera.position.set(0, 0.03, 0.35);
            v.controls.update();
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/shoe_result_front.png")
        print("  -> shoe_result_front.png")

        # 3. Side view
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.5, 0.05, 0);
            v.controls.update();
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/shoe_result_side.png")
        print("  -> shoe_result_side.png")

        # 4. Back view
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(-0.3, 0.1, -0.4);
            v.controls.update();
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/shoe_result_back.png")
        print("  -> shoe_result_back.png")

        print("\nDone! 4 screenshots saved.")
        browser.close()


if __name__ == "__main__":
    run()
