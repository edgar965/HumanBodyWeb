"""Playwright: Final test — expression, body morphs, JSON display."""
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

        # Check expression was applied
        print("=== EXPRESSION LOGS ===")
        for log in logs:
            if 'FaceExpr' in log:
                try:
                    print(f"  {log[:300]}")
                except:
                    pass

        # Check mesh morph count
        print("\n=== MESH API ===")
        mesh_morph_count = page.evaluate("""() => {
            // Can't access module scope, check from console logs
            return document.getElementById('detection-json') ? 'JSON panel exists' : 'NO JSON panel';
        }""")
        print(f"  {mesh_morph_count}")

        # Check JSON panel content
        json_el = page.evaluate("""() => {
            const el = document.getElementById('detection-json');
            if (!el) return 'NOT FOUND';
            if (el.style.display === 'none') return 'HIDDEN';
            return el.textContent.substring(0, 500);
        }""")
        print(f"\n=== JSON PANEL ===")
        print(f"  {json_el[:500]}")

        # Screenshot
        page.screenshot(path="A:/3DTools/HumanBodyWeb/debug_final.png")
        print("\n=== Screenshot saved ===")

        # Scroll down in left panel to show JSON
        page.evaluate("""() => {
            const left = document.querySelector('.viewer-left');
            if (left) left.scrollTop = left.scrollHeight;
        }""")
        page.wait_for_timeout(500)
        page.screenshot(path="A:/3DTools/HumanBodyWeb/debug_final_scrolled.png")
        print("=== Scrolled screenshot saved ===")

        browser.close()

if __name__ == "__main__":
    main()
