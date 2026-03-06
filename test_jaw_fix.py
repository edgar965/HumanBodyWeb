"""Playwright: Test jaw fix — no more beak, expression via bones only."""
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

        # Check expression applied
        print("=== EXPRESSION ===")
        for log in logs:
            if 'FaceExpr' in log:
                try:
                    print(f"  {log[:300]}")
                except:
                    pass

        # Check mesh URL for problematic morphs
        print("\n=== MESH URL CHECK ===")
        for log in logs:
            if 'Jaw_Angle' in log or 'Mouth_Corners' in log:
                try:
                    print(f"  PROBLEM: {log[:200]}")
                except:
                    pass
        else:
            print("  OK: No Jaw_Angle or Mouth_CornersPosZ in logs")

        # Front view screenshot
        page.screenshot(path="A:/3DTools/HumanBodyWeb/debug_jaw_fix_front.png")
        print("\n=== Front screenshot saved ===")

        # Rotate camera to 3/4 view using mouse drag
        canvas = page.locator('canvas').first
        box = canvas.bounding_box()
        if box:
            cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
            # Drag left to rotate view
            page.mouse.move(cx, cy)
            page.mouse.down()
            page.mouse.move(cx - 200, cy - 50, steps=20)
            page.mouse.up()
            page.wait_for_timeout(500)
            page.screenshot(path="A:/3DTools/HumanBodyWeb/debug_jaw_fix_side.png")
            print("=== Side screenshot saved ===")

        browser.close()

if __name__ == "__main__":
    main()
