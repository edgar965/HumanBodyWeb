"""Diagnostic test: shoe mesh wireframe + hidden body to find gaps."""
import time, json, os
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

        # Set meta sliders
        print("[1] Setting meta sliders: age=59, mass=123, tone=50, height=175")
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
        time.sleep(8)

        # Set camera to low34 view
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.4, -0.05, 0.5);
            v.controls.update();
        }""")
        time.sleep(1)

        # 1. Normal view (reference)
        page.screenshot(path=f"{SHOTS}/diag_01_normal.png")
        print("  -> diag_01_normal.png")

        # 2. Shoe wireframe view
        page.evaluate("""() => {
            const v = window.__viewer;
            const shoe = v.garmentMeshes['shoes/shoes01'];
            if (shoe) shoe.material.wireframe = true;
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/diag_02_wireframe.png")
        print("  -> diag_02_wireframe.png")

        # 3. Shoe wireframe + body hidden
        page.evaluate("""() => {
            const v = window.__viewer;
            if (v.bodyMesh) v.bodyMesh.visible = false;
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/diag_03_wireframe_nobody.png")
        print("  -> diag_03_wireframe_nobody.png")

        # 4. Shoe solid + body hidden (see shoe surface alone)
        page.evaluate("""() => {
            const v = window.__viewer;
            const shoe = v.garmentMeshes['shoes/shoes01'];
            if (shoe) shoe.material.wireframe = false;
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/diag_04_solid_nobody.png")
        print("  -> diag_04_solid_nobody.png")

        # 5. Side view - shoe solid, no body
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.5, 0.05, 0);
            v.controls.update();
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/diag_05_side_nobody.png")
        print("  -> diag_05_side_nobody.png")

        # 6. Side view - shoe solid + body
        page.evaluate("""() => {
            const v = window.__viewer;
            if (v.bodyMesh) v.bodyMesh.visible = true;
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/diag_06_side_body.png")
        print("  -> diag_06_side_body.png")

        # 7. Front view close up
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.03, 0);
            v.camera.position.set(0, 0.03, 0.3);
            v.controls.update();
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/diag_07_front_close.png")
        print("  -> diag_07_front_close.png")

        # 8. Front view - body hidden
        page.evaluate("""() => {
            const v = window.__viewer;
            if (v.bodyMesh) v.bodyMesh.visible = false;
        }""")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS}/diag_08_front_nobody.png")
        print("  -> diag_08_front_nobody.png")

        # 9. Detailed mesh analysis
        analysis = page.evaluate("""() => {
            const v = window.__viewer;
            const shoe = v.garmentMeshes['shoes/shoes01'];
            if (!shoe) return {error: 'no shoe'};

            const geo = shoe.geometry;
            const pos = geo.attributes.position;
            const idx = geo.index;

            // Count degenerate faces (area < epsilon)
            let degenerateCount = 0;
            let totalFaces = idx.count / 3;
            let minArea = Infinity, maxArea = 0;

            for (let f = 0; f < totalFaces; f++) {
                const i0 = idx.getX(f*3), i1 = idx.getX(f*3+1), i2 = idx.getX(f*3+2);
                const x0=pos.getX(i0),y0=pos.getY(i0),z0=pos.getZ(i0);
                const x1=pos.getX(i1),y1=pos.getY(i1),z1=pos.getZ(i1);
                const x2=pos.getX(i2),y2=pos.getY(i2),z2=pos.getZ(i2);
                // cross product magnitude / 2
                const ex = x1-x0, ey = y1-y0, ez = z1-z0;
                const fx = x2-x0, fy = y2-y0, fz = z2-z0;
                const cx = ey*fz-ez*fy, cy = ez*fx-ex*fz, cz = ex*fy-ey*fx;
                const area = Math.sqrt(cx*cx+cy*cy+cz*cz) / 2;
                if (area < 1e-8) degenerateCount++;
                if (area < minArea) minArea = area;
                if (area > maxArea) maxArea = area;
            }

            return {
                vertexCount: pos.count,
                faceCount: totalFaces,
                degenerateFaces: degenerateCount,
                minFaceArea: minArea,
                maxFaceArea: maxArea,
                indexCount: idx.count,
            };
        }""")
        print(f"\n=== MESH ANALYSIS ===")
        print(json.dumps(analysis, indent=2))

        browser.close()


if __name__ == "__main__":
    run()
