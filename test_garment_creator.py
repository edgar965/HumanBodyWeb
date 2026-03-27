"""Playwright test: Garment Creator — verify all sliders, buttons, and selection."""
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:4040"
SHOTS = "A:/HumanBodyTest/HumanBodyWeb/test_screenshots"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        errors = []
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        # --- Load page ---
        print("[1] Loading Konfiguration page...")
        page.goto(f"{BASE}/humanbody/config/", wait_until="networkidle")
        time.sleep(6)

        # Check for JS errors
        js_errors = [m for m in console_msgs if m.startswith("[error]")]
        if js_errors:
            print(f"  JS ERRORS on load: {js_errors[:5]}")
        if errors:
            print(f"  PAGE ERRORS on load: {errors[:5]}")

        # Check if gc-panel exists
        gc_panel = page.locator('#gc-panel')
        print(f"  gc-panel visible: {gc_panel.is_visible()}")

        # --- Switch to Creator tab ---
        print("[2] Clicking Creator tab...")
        creator_tab = page.locator('.panel-tab[data-tab="tab-creator"]')
        print(f"  Creator tab exists: {creator_tab.count() > 0}")
        if creator_tab.count() == 0:
            print("  FAIL: Creator tab not found!")
            page.screenshot(path=f"{SHOTS}/gc_01_no_tab.png")
            browser.close()
            return

        creator_tab.click()
        time.sleep(1)

        # Check tab-creator is now active
        is_active = page.evaluate("document.getElementById('tab-creator')?.classList.contains('active')")
        print(f"  tab-creator active: {is_active}")

        # Check gc-panel is now visible
        print(f"  gc-panel visible after tab click: {gc_panel.is_visible()}")

        page.screenshot(path=f"{SHOTS}/gc_02_creator_tab.png")

        # --- Test sliders ---
        print("[3] Testing sliders...")
        sliders = {
            'gc-zmin': {'val_id': 'gc-zmin-val', 'set': 40, 'expect': '0.40'},
            'gc-zmax': {'val_id': 'gc-zmax-val', 'set': 100, 'expect': '1.00'},
            'gc-looseness': {'val_id': 'gc-looseness-val', 'set': 50, 'expect': '0.50'},
            'gc-grow': {'val_id': 'gc-grow-val', 'set': 4, 'expect': '4'},
            'gc-xlimit': {'val_id': 'gc-xlimit-val', 'set': 50, 'expect': '0.50 m'},
            'gc-roughness': {'val_id': 'gc-roughness-val', 'set': 60, 'expect': '0.60'},
            'gc-metalness': {'val_id': 'gc-metalness-val', 'set': 20, 'expect': '0.20'},
        }

        for slider_id, cfg in sliders.items():
            el = page.locator(f'#{slider_id}')
            val_el = page.locator(f'#{cfg["val_id"]}')
            exists = el.count() > 0
            if not exists:
                print(f"  FAIL: {slider_id} NOT FOUND")
                continue

            # Set slider value and trigger input event
            page.evaluate(f"""() => {{
                const el = document.getElementById('{slider_id}');
                el.value = {cfg['set']};
                el.dispatchEvent(new Event('input', {{bubbles: true}}));
            }}""")
            time.sleep(0.2)

            displayed = val_el.text_content().strip()
            ok = cfg['expect'] in displayed
            print(f"  {slider_id}: set={cfg['set']}, display='{displayed}', expected='{cfg['expect']}' -> {'OK' if ok else 'FAIL'}")

        # --- Test preset dropdown ---
        print("[4] Testing preset dropdown...")
        preset_sel = page.locator('#gc-preset')
        print(f"  Preset select exists: {preset_sel.count() > 0}")
        if preset_sel.count() > 0:
            # Get options
            options = page.evaluate("() => Array.from(document.getElementById('gc-preset').options).map(o => o.value)")
            print(f"  Options: {options}")

            # Select TOP preset
            page.select_option('#gc-preset', 'TOP')
            time.sleep(0.5)

            # Check sliders updated
            zmin_val = page.locator('#gc-zmin-val').text_content().strip()
            zmax_val = page.locator('#gc-zmax-val').text_content().strip()
            arms_checked = page.evaluate("document.getElementById('gc-arms')?.checked")
            print(f"  After TOP preset: zmin={zmin_val}, zmax={zmax_val}, arms={arms_checked}")

        # --- Test Preview button ---
        print("[5] Testing Preview button...")
        preview_btn = page.locator('#gc-preview')
        print(f"  Preview button exists: {preview_btn.count() > 0}")
        print(f"  Preview button visible: {preview_btn.is_visible()}")
        print(f"  Preview button enabled: {preview_btn.is_enabled()}")

        if preview_btn.count() > 0 and preview_btn.is_visible():
            # Check highlight appeared after preset selection
            has_highlight_before = page.evaluate("() => !!window.__viewer?._gcHighlightMesh")
            print(f"  Highlight mesh before preview: {has_highlight_before}")

            # Check no preview mesh before click
            has_preview_before = page.evaluate("() => !!window.__viewer?.clothMeshes?.['gc_preview']")
            print(f"  Preview mesh before click: {has_preview_before}")

            preview_btn.click()
            print("  Clicked Preview, waiting 5s...")
            time.sleep(5)

            # Check highlight is REMOVED after preview
            has_highlight_after = page.evaluate("() => !!window.__viewer?._gcHighlightMesh")
            print(f"  Highlight mesh after preview: {has_highlight_after} -> {'OK (removed)' if not has_highlight_after else 'FAIL (still present)'}")

            # Check console for GC messages
            gc_msgs = [m for m in console_msgs if 'GC' in m or 'gc' in m.lower() or 'Creator' in m]
            print(f"  GC console messages: {gc_msgs[-5:] if gc_msgs else 'none'}")

            # Check for errors after click
            new_errors = [m for m in console_msgs if m.startswith("[error]")]
            if len(new_errors) > len(js_errors):
                print(f"  NEW ERRORS after preview: {new_errors[len(js_errors):]}")

            has_preview_after = page.evaluate("() => !!window.__viewer?.clothMeshes?.['gc_preview']")
            print(f"  Preview mesh after click: {has_preview_after}")

            # Check garment color
            garment_color = page.evaluate("""() => {
                const m = window.__viewer?.clothMeshes?.['gc_preview'];
                if (!m) return null;
                return '#' + m.material.color.getHexString();
            }""")
            print(f"  Garment color: {garment_color}")

            page.screenshot(path=f"{SHOTS}/gc_03_after_preview.png")

        # --- Test Create button ---
        print("[6] Testing Create button...")
        create_btn = page.locator('#gc-create')
        print(f"  Create button exists: {create_btn.count() > 0}")

        # --- Test Delete button ---
        print("[7] Testing Delete button...")
        delete_btn = page.locator('#gc-delete')
        print(f"  Delete button exists: {delete_btn.count() > 0}")
        if delete_btn.count() > 0 and delete_btn.is_visible():
            delete_btn.click()
            time.sleep(1)
            has_preview_after_delete = page.evaluate("() => !!window.__viewer?.clothMeshes?.['gc_preview']")
            print(f"  Preview mesh after delete: {has_preview_after_delete}")

        # --- Test Color picker ---
        print("[8] Testing Color picker...")
        color_el = page.locator('#gc-color')
        print(f"  Color picker exists: {color_el.count() > 0}")

        # --- Test Save section ---
        print("[9] Testing Save section...")
        save_name = page.locator('#gc-save-name')
        save_cat = page.locator('#gc-save-category')
        save_btn = page.locator('#gc-save')
        print(f"  Save name input: {save_name.count() > 0}")
        print(f"  Save category select: {save_cat.count() > 0}")
        print(f"  Save button: {save_btn.count() > 0}")

        # --- Test that body has NO blue highlight when not previewing ---
        print("[10] Checking no blue highlight on body...")
        page.screenshot(path=f"{SHOTS}/gc_04_no_highlight.png")

        # --- Check model is not blue ---
        # Switch away from Creator tab
        page.locator('.panel-tab[data-tab="tab-eigenschaften"]').click()
        time.sleep(1)
        page.screenshot(path=f"{SHOTS}/gc_05_after_tab_switch.png")

        # --- Check click-to-select works after using creator ---
        print("[11] Testing click-to-select on body mesh...")
        # Click roughly on the body in the canvas
        canvas = page.locator('#viewer-canvas')
        canvas.click(position={"x": 400, "y": 400})
        time.sleep(0.5)
        selected = page.evaluate("() => window.__viewer?._selectedItem")
        print(f"  Selected item after click: {selected}")

        # --- Summary ---
        print("\n=== SUMMARY ===")
        all_errors = [m for m in console_msgs if m.startswith("[error]")]
        if all_errors:
            print(f"JS Errors ({len(all_errors)}):")
            for e in all_errors[:10]:
                print(f"  {e}")
        if errors:
            print(f"Page Errors ({len(errors)}):")
            for e in errors[:10]:
                print(f"  {e}")
        if not all_errors and not errors:
            print("No errors detected!")

        page.screenshot(path=f"{SHOTS}/gc_06_final.png")

        print("\nDone. Screenshots in:", SHOTS)
        browser.close()


if __name__ == "__main__":
    run()
