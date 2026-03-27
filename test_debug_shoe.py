"""Playwright debug: shoe fitting + slider verification."""
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

        # Select shoe
        print("[3] Creating shoe...")
        shoe = page.locator('.garment-item[data-garment-id="shoes/shoes01"]')
        shoe.click()
        time.sleep(0.5)
        page.locator('#garment-create').click()
        time.sleep(6)

        # Full view screenshot
        page.screenshot(path=f"{SHOTS}/debug_shoe_full.png")

        # Zoom to feet — standard 3/4 view
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.1, 0);
            v.camera.position.set(0.5, 0.15, 0.8);
            v.controls.update();
        }""")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS}/debug_shoe_feet_closeup.png")

        # Bottom view — camera below feet looking up
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.3, -0.15, 0.3);
            v.controls.update();
        }""")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS}/debug_shoe_bottom.png")

        # Side view — camera at foot level
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.6, 0.05, 0);
            v.controls.update();
        }""")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS}/debug_shoe_side.png")

        # Front view — straight on
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0, 0.05, 0.6);
            v.controls.update();
        }""")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS}/debug_shoe_front.png")

        # 3/4 low angle — like diagnostic screenshot
        page.evaluate("""() => {
            const v = window.__viewer;
            v.controls.target.set(0, 0.05, 0);
            v.camera.position.set(0.4, -0.05, 0.5);
            v.controls.update();
        }""")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS}/debug_shoe_low_angle.png")

        # Analyze coverage
        debug = page.evaluate("""() => {
            const v = window.__viewer;
            const body = v.bodyMesh;
            const gm = v.garmentMeshes;
            const shoe = gm['shoes/shoes01'];
            if (!body || !shoe) return {error: 'no body or shoe mesh'};

            const bpos = body.geometry.attributes.position;
            const spos = shoe.geometry.attributes.position;

            // Body feet: bottom 8% by Y
            let bMinY = Infinity, bMaxY = -Infinity;
            for (let i = 0; i < bpos.count; i++) {
                const y = bpos.getY(i);
                if (y < bMinY) bMinY = y;
                if (y > bMaxY) bMaxY = y;
            }
            const feetThresh = bMinY + (bMaxY - bMinY) * 0.08;
            let fMinX=Infinity,fMaxX=-Infinity,fMinY=Infinity,fMaxY=-Infinity,fMinZ=Infinity,fMaxZ=-Infinity;
            let fCount=0;
            for (let i = 0; i < bpos.count; i++) {
                if (bpos.getY(i) < feetThresh) {
                    fCount++;
                    const x=bpos.getX(i),y=bpos.getY(i),z=bpos.getZ(i);
                    if(x<fMinX)fMinX=x; if(x>fMaxX)fMaxX=x;
                    if(y<fMinY)fMinY=y; if(y>fMaxY)fMaxY=y;
                    if(z<fMinZ)fMinZ=z; if(z>fMaxZ)fMaxZ=z;
                }
            }

            // Shoe bbox
            let sMinX=Infinity,sMaxX=-Infinity,sMinY=Infinity,sMaxY=-Infinity,sMinZ=Infinity,sMaxZ=-Infinity;
            for (let i = 0; i < spos.count; i++) {
                const x=spos.getX(i),y=spos.getY(i),z=spos.getZ(i);
                if(x<sMinX)sMinX=x; if(x>sMaxX)sMaxX=x;
                if(y<sMinY)sMinY=y; if(y>sMaxY)sMaxY=y;
                if(z<sMinZ)sMinZ=z; if(z>sMaxZ)sMaxZ=z;
            }

            // Coverage check: does shoe bbox fully contain feet bbox?
            const coverage = {
                x_ok: sMinX <= fMinX && sMaxX >= fMaxX,
                y_ok: sMinY <= fMinY && sMaxY >= fMaxY,
                z_ok: sMinZ <= fMinZ && sMaxZ >= fMaxZ,
                x_gap_left: fMinX - sMinX,
                x_gap_right: sMaxX - fMaxX,
                y_gap_bottom: fMinY - sMinY,
                y_gap_top: sMaxY - fMaxY,
                z_gap_back: fMinZ - sMinZ,
                z_gap_front: sMaxZ - fMaxZ,
            };

            return {
                body_feet: {minX:fMinX,maxX:fMaxX,minY:fMinY,maxY:fMaxY,minZ:fMinZ,maxZ:fMaxZ,count:fCount},
                shoe: {minX:sMinX,maxX:sMaxX,minY:sMinY,maxY:sMaxY,minZ:sMinZ,maxZ:sMaxZ,count:spos.count},
                coverage: coverage,
                fully_enclosed: coverage.x_ok && coverage.y_ok && coverage.z_ok,
            };
        }""")

        print("\n=== SHOE COVERAGE ANALYSIS ===")
        print(json.dumps(debug, indent=2))

        if debug.get('fully_enclosed'):
            print("\nRESULT: PASS — feet fully enclosed by shoe mesh")
        else:
            print("\nRESULT: FAIL — body parts poke through shoe")
            c = debug.get('coverage', {})
            for axis, name in [('x', 'Width'), ('y', 'Height'), ('z', 'Depth')]:
                if not c.get(f'{axis}_ok'):
                    print(f"  {name}: shoe doesn't cover feet")

        # Console messages
        print("\n=== Console (garment/error) ===")
        for msg in console_msgs:
            if 'arment' in msg or 'error' in msg.lower() or 'warn' in msg.lower() or 'coverage' in msg.lower():
                print(f"  {msg}")

        print("\nDone!")
        time.sleep(3)
        browser.close()


if __name__ == "__main__":
    run()
