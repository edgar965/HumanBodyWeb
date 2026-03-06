"""Playwright: Test body shape morphs + expression + JSON display."""
from playwright.sync_api import sync_playwright

JOB_URL = "http://localhost:8081/humanbody/photo-to-3d/?job=92621313-044f-4572-a7be-a39988fdd049"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1600, "height": 900})

        logs = []
        page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        page.goto(JOB_URL, timeout=90000)
        page.wait_for_timeout(14000)

        # Check expression logs
        print("=== EXPRESSION LOGS ===")
        for log in logs:
            if 'FaceExpr' in log or 'expression' in log.lower():
                try:
                    print(f"  {log[:300]}")
                except:
                    pass

        # Check body morph application
        print("\n=== BODY MORPH LOGS ===")
        for log in logs:
            if 'morph' in log.lower() or 'Shoulders' in log or 'Torso' in log or 'Pelvis' in log:
                try:
                    print(f"  {log[:300]}")
                except:
                    pass

        # Check JSON panel
        json_el = page.evaluate("""() => {
            const el = document.getElementById('detection-json');
            if (!el) return 'NOT FOUND';
            if (el.style.display === 'none') return 'HIDDEN';
            return el.textContent.substring(0, 800);
        }""")
        print(f"\n=== JSON PANEL ===")
        try:
            print(f"  {json_el[:800]}")
        except:
            print(f"  (encoding error)")

        # Screenshot
        page.screenshot(path="A:/3DTools/HumanBodyWeb/debug_body_shape.png")
        print("\n=== Screenshot saved ===")

        # Scroll left panel to show JSON
        page.evaluate("""() => {
            const left = document.querySelector('.viewer-left');
            if (left) left.scrollTop = left.scrollHeight;
        }""")
        page.wait_for_timeout(500)
        page.screenshot(path="A:/3DTools/HumanBodyWeb/debug_body_shape_scrolled.png")
        print("=== Scrolled screenshot saved ===")

        browser.close()

if __name__ == "__main__":
    main()
