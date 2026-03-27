"""Playwright test: diagnose Pos slider + shoe coverage issues."""
import time, json, os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:4040"
SHOTS = "A:/HumanBodyTest/HumanBodyWeb/test_screenshots"


def run():
    os.makedirs(SHOTS, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))

        print("[1] Loading page...")
        page.goto(f"{BASE}/humanbody/config/", wait_until="networkidle")
        time.sleep(6)

        # Remove default cloth
        try:
            page.locator('#cloth-remove-all').click(timeout=1000)
            time.sleep(0.5)
        except:
            pass

        # Open Garment Fit panel
        print("[2] Opening Garment Fit panel...")
        page.locator('[data-panel-key="garment_fit"] h3').click()
        time.sleep(1)

        # Select and create shoe
        print("[3] Creating shoe...")
        shoe = page.locator('.garment-item[data-garment-id="shoes/shoes01"]')
        shoe.click()
        time.sleep(0.5)
        page.locator('#garment-create').click()
        time.sleep(6)

        # Take baseline screenshot
        page.screenshot(path=f"{SHOTS}/pos_test_00_baseline.png")

        # === TEST: Pos slider diagnostic ===
        print("\n[4] === POS SLIDER DIAGNOSTIC ===")

        # Check initial state
        state0 = page.evaluate("""() => {
            const v = window.__viewer;
            const mesh = v.garmentMeshes && v.garmentMeshes['shoes/shoes01'];
            if (!mesh) return {error: 'no shoe mesh'};
            return {
                isSkinned: mesh.isSkinnedMesh || false,
                position: {x: mesh.position.x, y: mesh.position.y, z: mesh.position.z},
                scale: {x: mesh.scale.x, y: mesh.scale.y, z: mesh.scale.z},
                selectedGarmentId: v.selectedGarmentId || '(not exposed)',
                hasGarmentState: !!v.garmentState,
            };
        }""")
        print(f"  Initial mesh state: {json.dumps(state0, indent=2)}")

        # Check if selectedGarmentId is set
        sel = page.evaluate("""() => {
            const v = window.__viewer;
            return {
                selectedGarmentId: v.selectedGarmentId,
                garmentMeshKeys: v.garmentMeshes ? Object.keys(v.garmentMeshes) : [],
                garmentStateKeys: v.garmentState ? Object.keys(v.garmentState) : [],
            };
        }""")
        print(f"  Selection state: {json.dumps(sel, indent=2)}")

        # Try setting Pos Y to 25 (= 0.25m) via the slider
        print("\n[5] Setting Pos Y slider to 25 (0.25m)...")
        page.evaluate("""() => {
            const slider = document.getElementById('garment-pos-y');
            if (!slider) return 'SLIDER NOT FOUND';
            slider.value = 25;
            slider.dispatchEvent(new Event('input', {bubbles: true}));
            return 'dispatched input event';
        }""")
        time.sleep(0.5)

        state1 = page.evaluate("""() => {
            const v = window.__viewer;
            const mesh = v.garmentMeshes && v.garmentMeshes['shoes/shoes01'];
            if (!mesh) return {error: 'no shoe mesh'};
            return {
                position: {x: mesh.position.x, y: mesh.position.y, z: mesh.position.z},
                sliderValue: document.getElementById('garment-pos-y')?.value,
            };
        }""")
        print(f"  After Pos Y=25: {json.dumps(state1, indent=2)}")
        page.screenshot(path=f"{SHOTS}/pos_test_01_posY_25.png")

        # Try setting Pos Y to -25 (= -0.25m)
        print("\n[6] Setting Pos Y slider to -25 (-0.25m)...")
        page.evaluate("""() => {
            const slider = document.getElementById('garment-pos-y');
            slider.value = -25;
            slider.dispatchEvent(new Event('input', {bubbles: true}));
        }""")
        time.sleep(0.5)
        state2 = page.evaluate("""() => {
            const v = window.__viewer;
            const mesh = v.garmentMeshes && v.garmentMeshes['shoes/shoes01'];
            if (!mesh) return {error: 'no shoe mesh'};
            return {
                position: {x: mesh.position.x, y: mesh.position.y, z: mesh.position.z},
            };
        }""")
        print(f"  After Pos Y=-25: {json.dumps(state2, indent=2)}")
        page.screenshot(path=f"{SHOTS}/pos_test_02_posY_neg25.png")

        # Try direct mesh.position change
        print("\n[7] Direct mesh.position.y = 0.3...")
        page.evaluate("""() => {
            const v = window.__viewer;
            const mesh = v.garmentMeshes['shoes/shoes01'];
            mesh.position.y = 0.3;
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/pos_test_03_direct_posY_0.3.png")

        # Check bounding box of rendered shoe
        print("\n[8] Checking shoe vertex world positions...")
        bbox = page.evaluate("""() => {
            const v = window.__viewer;
            const mesh = v.garmentMeshes['shoes/shoes01'];
            if (!mesh) return {error: 'no mesh'};

            // Get bounding box in world space
            mesh.geometry.computeBoundingBox();
            const box = mesh.geometry.boundingBox.clone();

            // For skinned mesh, need to compute bounding box differently
            const pos = mesh.geometry.attributes.position;
            let minY = Infinity, maxY = -Infinity;
            let minYWorld = Infinity, maxYWorld = -Infinity;

            // Local positions (pre-skinning)
            for (let i = 0; i < pos.count; i++) {
                const y = pos.getY(i);
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
            }

            return {
                meshPosition: {x: mesh.position.x, y: mesh.position.y, z: mesh.position.z},
                localBbox: {
                    minY: box.min.y, maxY: box.max.y,
                    minX: box.min.x, maxX: box.max.x,
                },
                vertexYRange: {min: minY, max: maxY},
                isSkinned: mesh.isSkinnedMesh,
                hasSkeleton: !!mesh.skeleton,
                bindMatrixIdentity: mesh.bindMatrix ? mesh.bindMatrix.equals(new THREE.Matrix4()) : null,
            };
        }""")
        print(f"  Shoe mesh analysis: {json.dumps(bbox, indent=2)}")

        # Reset pos back to 0
        page.evaluate("""() => {
            const v = window.__viewer;
            const mesh = v.garmentMeshes['shoes/shoes01'];
            mesh.position.set(0, 0, 0);
        }""")
        time.sleep(0.3)

        # === Zoom to feet ===
        print("\n[9] Zooming to feet for shoe fit check...")
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.4, 0.1, 0.5);
            v.controls.update();
        }""")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS}/pos_test_04_feet_closeup.png")

        # Front view
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0, 0.05, 0.6);
            v.controls.update();
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/pos_test_05_feet_front.png")

        # Side view
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.6, 0.05, 0);
            v.controls.update();
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/pos_test_06_feet_side.png")

        # Bottom view (looking up at soles)
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.3, -0.15, 0.3);
            v.controls.update();
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/pos_test_07_feet_bottom.png")

        # Console messages
        print("\n=== Console (garment/error/warn) ===")
        for msg in console_msgs:
            if 'arment' in msg or 'error' in msg.lower() or 'warn' in msg.lower():
                print(f"  {msg}")

        print("\nDone!")
        time.sleep(2)
        browser.close()


if __name__ == "__main__":
    run()
