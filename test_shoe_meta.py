"""Test shoe fitting with specific meta slider values matching user's session."""
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

        # Set meta sliders to match user's session
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

        # Open Garment Fit panel + create shoe
        print("[2] Creating shoe...")
        page.locator('[data-panel-key="garment_fit"] h3').click()
        time.sleep(1)
        page.locator('.garment-item[data-garment-id="shoes/shoes01"]').click()
        time.sleep(0.5)
        page.locator('#garment-create').click()
        time.sleep(6)

        # Camera views
        views = {
            "front_low": {"cam": [0, 0.05, 0.4], "tgt": [0, 0.03, 0]},
            "low34": {"cam": [0.4, -0.05, 0.5], "tgt": [0, 0.05, 0]},
            "side": {"cam": [0.5, 0.05, 0], "tgt": [0, 0.05, 0]},
            "back": {"cam": [0, 0.05, -0.4], "tgt": [0, 0.05, 0]},
        }

        for name, v in views.items():
            cam, tgt = v["cam"], v["tgt"]
            page.evaluate(f"""() => {{
                const v = window.__viewer;
                v.controls.target.set({tgt[0]}, {tgt[1]}, {tgt[2]});
                v.camera.position.set({cam[0]}, {cam[1]}, {cam[2]});
                v.controls.update();
            }}""")
            time.sleep(1)
            page.screenshot(path=f"{SHOTS}/shoe_meta_{name}.png")

        # Coverage analysis
        debug = page.evaluate("""() => {
            const v = window.__viewer;
            const body = v.bodyMesh;
            const shoe = v.garmentMeshes['shoes/shoes01'];
            if (!body || !shoe) return {error: 'no body or shoe mesh'};

            const bpos = body.geometry.attributes.position;
            const spos = shoe.geometry.attributes.position;

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
                    if(x<fMinX)fMinX=x;if(x>fMaxX)fMaxX=x;
                    if(y<fMinY)fMinY=y;if(y>fMaxY)fMaxY=y;
                    if(z<fMinZ)fMinZ=z;if(z>fMaxZ)fMaxZ=z;
                }
            }

            let sMinX=Infinity,sMaxX=-Infinity,sMinY=Infinity,sMaxY=-Infinity,sMinZ=Infinity,sMaxZ=-Infinity;
            for (let i = 0; i < spos.count; i++) {
                const x=spos.getX(i),y=spos.getY(i),z=spos.getZ(i);
                if(x<sMinX)sMinX=x;if(x>sMaxX)sMaxX=x;
                if(y<sMinY)sMinY=y;if(y>sMaxY)sMaxY=y;
                if(z<sMinZ)sMinZ=z;if(z>sMaxZ)sMaxZ=z;
            }

            return {
                body_feet: {minX:+fMinX.toFixed(4),maxX:+fMaxX.toFixed(4),minY:+fMinY.toFixed(4),maxY:+fMaxY.toFixed(4),minZ:+fMinZ.toFixed(4),maxZ:+fMaxZ.toFixed(4),count:fCount},
                shoe: {minX:+sMinX.toFixed(4),maxX:+sMaxX.toFixed(4),minY:+sMinY.toFixed(4),maxY:+sMaxY.toFixed(4),minZ:+sMinZ.toFixed(4),maxZ:+sMaxZ.toFixed(4),count:spos.count},
                fully_enclosed: (sMinX<=fMinX&&sMaxX>=fMaxX)&&(sMinY<=fMinY&&sMaxY>=fMaxY)&&(sMinZ<=fMinZ&&sMaxZ>=fMaxZ),
            };
        }""")

        print("\n=== SHOE ANALYSIS (with meta sliders) ===")
        print(json.dumps(debug, indent=2))

        browser.close()


if __name__ == "__main__":
    run()
