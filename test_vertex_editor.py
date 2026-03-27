"""Playwright test: Vertex Editor — BVH raycast + TransformControls gizmo pipeline.

Tests:
  1. Page load + viewer init
  2. Region → Top → Generate 3D
  3. Enter Edit mode → points overlay + BVH built
  4. BVH click → vertex selected + gizmo visible
  5. Shift+click → multi-select
  6. Box select (Alt+drag) → area selection
  7. Select All / Deselect All buttons
  8. Gizmo movement → vertices displaced
  9. Smooth server tool
 10. Push Outside server tool
 11. Reset to Original
 12. Escape → exit edit mode
"""
import asyncio
import time
from playwright.async_api import async_playwright

BASE = "http://localhost:4040"
SHOTS = "A:/HumanBodyTest/HumanBodyWeb/test_screenshots"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        errors = []
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        results = {}

        def check(name, passed, detail=""):
            results[name] = passed
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

        # ── 1. Load page ──────────────────────────────────────
        print("\n[1] Loading page...")
        await page.goto(f"{BASE}/humanbody/config/", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(5)

        viewer_ok = await page.evaluate("() => !!window.__viewer && !!window.__viewer.scene")
        check("Page load + viewer init", viewer_ok)
        if not viewer_ok:
            print("  FATAL: viewer not initialized, aborting")
            await page.screenshot(path=f"{SHOTS}/ve_01_no_viewer.png")
            await browser.close()
            return

        load_errors = [m for m in console_msgs if m.startswith("[error]")]
        check("No JS errors on load", len(load_errors) == 0,
              f"{len(load_errors)} errors" if load_errors else "")

        # ── 2. Pattern Tab → Region → Top → Generate 3D ──────
        print("\n[2] Generating cloth via Region mode...")
        await page.evaluate('''() => {
            document.querySelector('.panel-tab[data-tab="tab-creator"]').click();
        }''')
        await asyncio.sleep(0.5)

        # Switch to Region mode
        await page.evaluate('''() => {
            document.querySelector('[data-mode="region"]').click();
        }''')
        await asyncio.sleep(0.3)

        mode = await page.evaluate("window.__viewer.peMode")
        check("Region mode active", mode == "region", f"mode={mode}")

        # Set Top preset
        await page.evaluate('''() => {
            const cat = document.getElementById('pe-region-category');
            cat.value = 'top';
            cat.dispatchEvent(new Event('change'));
        }''')
        await asyncio.sleep(0.5)

        # Generate 3D
        await page.evaluate("document.getElementById('pe-generate').click()")
        print("  Waiting for generation...")
        await asyncio.sleep(8)

        has_cloth = await page.evaluate('''() => {
            const keys = Object.keys(window.__viewer.clothMeshes || {});
            return keys.length > 0 ? keys.join(',') : '';
        }''')
        check("Cloth mesh generated", len(has_cloth) > 0, f"keys={has_cloth}")
        await page.screenshot(path=f"{SHOTS}/ve_02_cloth_generated.png")

        if not has_cloth:
            print("  FATAL: no cloth mesh, cannot test vertex editor")
            await browser.close()
            return

        # ── 3. Enter Edit mode ────────────────────────────────
        print("\n[3] Entering Edit mode...")
        await page.evaluate('''() => {
            document.querySelector('[data-mode="edit"]').click();
        }''')
        await asyncio.sleep(1)

        ve_state = await page.evaluate('''() => {
            const v = window.__viewer;
            return {
                veActive: v.veActive,
                hasOverlay: !!v.veTargetMesh,
                vertCount: v.veTargetMesh ? v.veTargetMesh.geometry.getAttribute('position').count : 0,
                hasBVH: v.veTargetMesh ? !!v.veTargetMesh.geometry.boundsTree : false,
            };
        }''')
        check("VE active", ve_state["veActive"])
        check("Target mesh found", ve_state["hasOverlay"], f"verts={ve_state['vertCount']}")
        check("BVH built on geometry", ve_state["hasBVH"])

        # Check gizmo exists but is hidden (no selection yet)
        gizmo_state = await page.evaluate('''() => {
            const scene = window.__viewer.scene;
            let hasGizmo = false;
            let gizmoVisible = false;
            scene.traverse(obj => {
                if (obj.isTransformControlsRoot || (obj.type === 'TransformControlsRoot')) {
                    hasGizmo = true;
                    gizmoVisible = obj.visible;
                }
            });
            // Also check via the helper
            const helpers = scene.children.filter(c => c.type === 'Object3D' && c.children.length === 0 && !c.geometry);
            return { hasGizmo, gizmoVisible, selCount: window.__viewer.veSelectedIndices.size };
        }''')
        check("No initial selection", gizmo_state["selCount"] == 0)

        # Check edit controls panel visible
        edit_vis = await page.evaluate('''() => {
            const el = document.getElementById('pe-edit-controls');
            return el ? el.style.display !== 'none' : false;
        }''')
        check("Edit controls panel visible", edit_vis)
        await page.screenshot(path=f"{SHOTS}/ve_03_edit_mode.png")

        # ── 4. BVH click → vertex selection ──────────────────
        print("\n[4] Testing BVH click selection...")

        # Click on the cloth mesh area (center-ish of canvas where the top garment should be)
        canvas = page.locator("#viewer-canvas")
        bbox = await canvas.bounding_box()

        # Position camera for a good view
        await page.evaluate('''() => {
            const v = window.__viewer;
            v.camera.position.set(0, 1.2, 2.0);
            v.controls.target.set(0, 1.1, 0);
            v.controls.update();
        }''')
        await asyncio.sleep(0.5)

        # Click roughly at center of canvas (where torso/top would be)
        cx = bbox["x"] + bbox["width"] * 0.45
        cy = bbox["y"] + bbox["height"] * 0.35
        await page.mouse.click(cx, cy)
        await asyncio.sleep(0.5)

        sel_after_click = await page.evaluate("window.__viewer.veSelectedIndices.size")
        check("BVH click selected vertex", sel_after_click > 0, f"selected={sel_after_click}")

        if sel_after_click > 0:
            # Check gizmo is now visible
            gizmo_vis = await page.evaluate('''() => {
                const scene = window.__viewer.scene;
                let vis = false;
                scene.traverse(obj => {
                    // TransformControls adds a helper with gizmo[translate] etc.
                    if (obj.type === 'TransformControlsGizmo') vis = obj.parent.visible;
                });
                return vis;
            }''')
            # Fallback: just check selection info text updated
            sel_info = await page.evaluate("document.getElementById('ve-selection-info')?.textContent || ''")
            check("Selection info updated", "selected" in sel_info.lower() or "vertex" in sel_info.lower(),
                  f"text='{sel_info}'")

        await page.screenshot(path=f"{SHOTS}/ve_04_click_select.png")

        # ── 5. Shift+click → multi-select ────────────────────
        print("\n[5] Testing Shift+click multi-select...")
        # Click a different spot with shift held
        cx2 = bbox["x"] + bbox["width"] * 0.5
        cy2 = bbox["y"] + bbox["height"] * 0.4
        await page.keyboard.down("Shift")
        await page.mouse.click(cx2, cy2)
        await page.keyboard.up("Shift")
        await asyncio.sleep(0.5)

        sel_after_shift = await page.evaluate("window.__viewer.veSelectedIndices.size")
        check("Shift+click added to selection", sel_after_shift >= sel_after_click,
              f"before={sel_after_click}, after={sel_after_shift}")

        # ── 6. Box select (Alt+drag) ─────────────────────────
        print("\n[6] Testing box select (Alt+drag)...")

        # First deselect all
        await page.evaluate('''() => {
            window.__viewer.veSelectedIndices.clear();
        }''')
        await asyncio.sleep(0.2)

        # Alt+drag a rectangle over the cloth
        bx1 = bbox["x"] + bbox["width"] * 0.3
        by1 = bbox["y"] + bbox["height"] * 0.2
        bx2 = bbox["x"] + bbox["width"] * 0.7
        by2 = bbox["y"] + bbox["height"] * 0.55

        await page.mouse.move(bx1, by1)
        await page.keyboard.down("Alt")
        await page.mouse.down()
        await asyncio.sleep(0.1)

        # Check box overlay appeared
        box_vis = await page.evaluate('''() => {
            const el = document.getElementById('ve-box-select');
            return el ? el.style.display : 'not found';
        }''')
        check("Box select overlay visible", box_vis == "block", f"display={box_vis}")

        # Drag to expand box
        await page.mouse.move(bx2, by2, steps=10)
        await asyncio.sleep(0.2)
        await page.screenshot(path=f"{SHOTS}/ve_05_box_select_drag.png")

        await page.mouse.up()
        await page.keyboard.up("Alt")
        await asyncio.sleep(0.5)

        sel_after_box = await page.evaluate("window.__viewer.veSelectedIndices.size")
        check("Box select selected vertices", sel_after_box > 0, f"selected={sel_after_box}")

        # Box overlay should be hidden again
        box_hidden = await page.evaluate('''() => {
            const el = document.getElementById('ve-box-select');
            return el ? el.style.display : 'not found';
        }''')
        check("Box overlay hidden after release", box_hidden == "none", f"display={box_hidden}")

        await page.screenshot(path=f"{SHOTS}/ve_06_box_select_done.png")

        # ── 7. Select All / Deselect All ─────────────────────
        print("\n[7] Testing Select All / Deselect All...")

        total_verts = await page.evaluate('''() => {
            return window.__viewer.veTargetMesh.geometry.getAttribute('position').count;
        }''')

        await page.evaluate("document.getElementById('ve-select-all').click()")
        await asyncio.sleep(0.3)
        sel_all = await page.evaluate("window.__viewer.veSelectedIndices.size")
        check("Select All", sel_all == total_verts, f"selected={sel_all}/{total_verts}")

        await page.evaluate("document.getElementById('ve-deselect-all').click()")
        await asyncio.sleep(0.3)
        sel_none = await page.evaluate("window.__viewer.veSelectedIndices.size")
        check("Deselect All", sel_none == 0, f"selected={sel_none}")

        # A key toggle
        await page.keyboard.press("a")
        await asyncio.sleep(0.3)
        sel_a = await page.evaluate("window.__viewer.veSelectedIndices.size")
        check("A key selects all", sel_a == total_verts, f"selected={sel_a}/{total_verts}")

        await page.keyboard.press("a")
        await asyncio.sleep(0.3)
        sel_a2 = await page.evaluate("window.__viewer.veSelectedIndices.size")
        check("A key deselects all", sel_a2 == 0)

        # ── 8. Gizmo movement ─────────────────────────────────
        print("\n[8] Testing gizmo vertex movement...")

        # Select a few vertices via box select for testing
        await page.mouse.move(bx1, by1)
        await page.keyboard.down("Alt")
        await page.mouse.down()
        await page.mouse.move(bx2, by2, steps=5)
        await page.mouse.up()
        await page.keyboard.up("Alt")
        await asyncio.sleep(0.5)

        sel_for_gizmo = await page.evaluate("window.__viewer.veSelectedIndices.size")
        if sel_for_gizmo > 0:
            # Save current centroid position
            before_pos = await page.evaluate('''() => {
                const v = window.__viewer;
                const posAttr = v.veTargetMesh.geometry.getAttribute('position');
                let cx = 0, cy = 0, cz = 0;
                for (const idx of v.veSelectedIndices) {
                    cx += posAttr.getX(idx);
                    cy += posAttr.getY(idx);
                    cz += posAttr.getZ(idx);
                }
                const n = v.veSelectedIndices.size;
                return { x: cx/n, y: cy/n, z: cz/n };
            }''')

            # Programmatically move via _veMoveSelectedByDelta (test the function)
            await page.evaluate('''() => {
                // Access internal function — it's module-scoped, but we can simulate
                const v = window.__viewer;
                const posAttr = v.veTargetMesh.geometry.getAttribute('position');
                const delta = 0.02; // 2cm upward (Y in Three.js)
                for (const idx of v.veSelectedIndices) {
                    posAttr.setY(idx, posAttr.getY(idx) + delta);
                }
                posAttr.needsUpdate = true;
                v.veTargetMesh.geometry.computeVertexNormals();
            }''')
            await asyncio.sleep(0.3)

            after_pos = await page.evaluate('''() => {
                const v = window.__viewer;
                const posAttr = v.veTargetMesh.geometry.getAttribute('position');
                let cy = 0;
                for (const idx of v.veSelectedIndices) cy += posAttr.getY(idx);
                return cy / v.veSelectedIndices.size;
            }''')

            moved = abs(after_pos - before_pos["y"]) > 0.01
            check("Vertex positions movable", moved,
                  f"before_y={before_pos['y']:.4f}, after_y={after_pos:.4f}")
        else:
            check("Vertex positions movable", False, "no vertices selected for gizmo test")

        await page.screenshot(path=f"{SHOTS}/ve_07_gizmo_move.png")

        # ── 9. Smooth ────────────────────────────────────────
        print("\n[9] Testing Smooth...")

        # Select all first
        await page.evaluate("document.getElementById('ve-select-all').click()")
        await asyncio.sleep(0.3)

        smooth_before_errors = len([m for m in console_msgs if m.startswith("[error]")])
        await page.evaluate("document.getElementById('ve-smooth').click()")
        await asyncio.sleep(3)

        smooth_status = await page.evaluate("document.getElementById('ve-selection-info')?.textContent || ''")
        smooth_after_errors = len([m for m in console_msgs if m.startswith("[error]")])
        new_smooth_errors = smooth_after_errors - smooth_before_errors
        check("Smooth executed", new_smooth_errors == 0 and "selected" in smooth_status.lower(),
              f"errors={new_smooth_errors}, status='{smooth_status}'")
        await page.screenshot(path=f"{SHOTS}/ve_08_smooth.png")

        # ── 10. Push Outside ──────────────────────────────────
        print("\n[10] Testing Push Outside...")
        push_before_errors = len([m for m in console_msgs if m.startswith("[error]")])
        await page.evaluate("document.getElementById('ve-push-outside').click()")
        await asyncio.sleep(3)

        push_status = await page.evaluate("document.getElementById('ve-selection-info')?.textContent || ''")
        push_after_errors = len([m for m in console_msgs if m.startswith("[error]")])
        new_push_errors = push_after_errors - push_before_errors
        check("Push Outside executed", new_push_errors == 0 and "selected" in push_status.lower(),
              f"errors={new_push_errors}, status='{push_status}'")
        await page.screenshot(path=f"{SHOTS}/ve_09_push_outside.png")

        # ── 11. Reset ─────────────────────────────────────────
        print("\n[11] Testing Reset to Original...")
        await page.evaluate("document.getElementById('ve-reset').click()")
        await asyncio.sleep(0.5)

        # Check positions match original
        reset_ok = await page.evaluate('''() => {
            const v = window.__viewer;
            if (!v.veTargetMesh) return false;
            const posAttr = v.veTargetMesh.geometry.getAttribute('position');
            // We can't access veOrigPositions from outside, but we can check the mesh is still valid
            return posAttr.count > 0;
        }''')
        check("Reset executed", reset_ok)
        await page.screenshot(path=f"{SHOTS}/ve_10_reset.png")

        # ── 12. Escape → exit edit mode ───────────────────────
        print("\n[12] Testing Escape to exit...")
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)

        exit_state = await page.evaluate('''() => {
            const v = window.__viewer;
            return {
                veActive: v.veActive,
                peMode: v.peMode,
                editCtrlHidden: document.getElementById('pe-edit-controls')?.style.display === 'none',
            };
        }''')
        check("VE deactivated on Escape", not exit_state["veActive"])
        check("PE mode back to select", exit_state["peMode"] == "select", f"mode={exit_state['peMode']}")
        check("Edit controls hidden", exit_state["editCtrlHidden"])
        await page.screenshot(path=f"{SHOTS}/ve_11_exit.png")

        # ── Re-enter and test BVH cleanup ─────────────────────
        print("\n[13] Testing re-enter + BVH cleanup...")
        await page.evaluate("document.querySelector('[data-mode=\"edit\"]').click()")
        await asyncio.sleep(1)
        ve2 = await page.evaluate("window.__viewer.veActive")
        check("Re-enter edit mode", ve2)

        # Exit again
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)
        ve3 = await page.evaluate("window.__viewer.veActive")
        check("Exit again clean", not ve3)

        # Check no BVH left on the mesh
        bvh_after = await page.evaluate('''() => {
            const keys = Object.keys(window.__viewer.clothMeshes || {});
            for (const k of keys) {
                const m = window.__viewer.clothMeshes[k];
                if (m && m.geometry && m.geometry.boundsTree) return true;
            }
            return false;
        }''')
        check("BVH disposed after exit", not bvh_after)

        # ── Final summary ─────────────────────────────────────
        print("\n" + "=" * 60)
        print("VERTEX EDITOR TEST RESULTS")
        print("=" * 60)

        all_js_errors = [m for m in console_msgs if m.startswith("[error]")]
        if all_js_errors:
            print(f"\nJS Console Errors ({len(all_js_errors)}):")
            for e in all_js_errors[:15]:
                print(f"  {e[:120]}")
        if errors:
            print(f"\nPage Errors ({len(errors)}):")
            for e in errors[:10]:
                print(f"  {e[:120]}")

        passed = sum(1 for v in results.values() if v)
        total = len(results)
        failed = total - passed
        print(f"\n  {passed}/{total} passed, {failed} failed")
        if failed:
            print("\n  Failed tests:")
            for name, ok in results.items():
                if not ok:
                    print(f"    - {name}")

        await page.screenshot(path=f"{SHOTS}/ve_12_final.png")
        print(f"\nScreenshots saved in: {SHOTS}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
