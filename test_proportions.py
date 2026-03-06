"""Playwright: Quantitative proportions comparison HumanBody vs SMPL-X.

Measures body width/depth at defined Y-heights on both meshes
and outputs a comparison table + multi-angle screenshots.

Usage:
    python test_proportions.py [job_uuid]
"""
import sys
import json
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081/humanbody/photo-to-3d/"
DEFAULT_JOB = "92621313-044f-4572-a7be-a39988fdd049"
SCREENSHOT_DIR = "A:/3DTools/HumanBodyWeb"

# Y-heights relative to foot=0 (meters) for measurement slices
# Aligned with _HEIGHT_FRACS in smplest_x_wrapper.py
MEASURE_POINTS = {
    'Shoulders':   1.41,   # 0.77 * ~1.83m
    'Chest':       1.28,   # 0.70
    'Waist':       1.10,   # 0.60
    'Hips':        0.92,   # 0.50
    'Upper Thigh': 0.68,   # 0.37
}

MEASURE_JS = """(args) => {
    const { yHeights } = args;

    function base64ToFloat32(b64) {
        const bin = atob(b64);
        const u8 = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
        return new Float32Array(u8.buffer);
    }

    function measureSlice(positions, yHeight, tolerance, xLimit) {
        const maxX_abs = xLimit || 999;
        let minX = Infinity, maxX = -Infinity;
        let minZ = Infinity, maxZ = -Infinity;
        let count = 0;
        for (let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const y = positions[i + 1];
            if (Math.abs(y - yHeight) < tolerance && Math.abs(x) < maxX_abs) {
                minX = Math.min(minX, x);
                maxX = Math.max(maxX, x);
                minZ = Math.min(minZ, positions[i + 2]);
                maxZ = Math.max(maxZ, positions[i + 2]);
                count++;
            }
        }
        if (count < 3) return null;
        return { width: maxX - minX, depth: maxZ - minZ, verts: count };
    }

    function blenderToThree(buf) {
        for (let i = 0; i < buf.length; i += 3) {
            const y = buf[i + 1], z = buf[i + 2];
            buf[i + 1] = z;
            buf[i + 2] = -y;
        }
    }

    const results = { humanBody: {}, smplx: {} };

    return new Promise(async (resolve) => {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const jobId = urlParams.get('job');

            let bodyType = 'Male_Caucasian';
            let morphParams = '';
            let metaParams = '';
            let betas = new Array(10).fill(0);

            if (jobId) {
                const jobResp = await fetch(`/api/character/photo-job/${jobId}/`);
                const jobData = await jobResp.json();
                if (jobData.ok) {
                    bodyType = jobData.body_type || bodyType;
                    if (jobData.betas) betas = jobData.betas.slice(0, 10);
                    if (jobData.morphs) {
                        for (const [k, v] of Object.entries(jobData.morphs)) {
                            if (Math.abs(v) > 0.001) morphParams += `&morph_${k}=${v}`;
                        }
                    }
                    if (jobData.meta_sliders) {
                        const ranges = {
                            height: {min:150,max:200}, mass: {min:45,max:200},
                            tone: {min:0,max:100}, age: {min:18,max:100}
                        };
                        for (const [k, v] of Object.entries(jobData.meta_sliders)) {
                            const r = ranges[k];
                            if (r) {
                                const neutral = (r.min + r.max) / 2;
                                const half = (r.max - r.min) / 2;
                                const internal = half ? (v - neutral) / half : 0;
                                metaParams += `&meta_${k}=${internal}`;
                            }
                        }
                    }
                }
            }

            // Fetch HumanBody mesh
            const hbUrl = `/api/character/mesh/?body_type=${encodeURIComponent(bodyType)}${morphParams}${metaParams}`;
            const hbResp = await fetch(hbUrl);
            const hbData = await hbResp.json();

            if (hbData.vertices) {
                const hbVerts = base64ToFloat32(hbData.vertices);
                blenderToThree(hbVerts);
                for (const [name, y] of Object.entries(yHeights)) {
                    // xLimit=0.3 excludes arms at shoulder/chest height
                    const m = measureSlice(hbVerts, y, 0.025, 0.3);
                    if (m) results.humanBody[name] = m;
                }
            }

            // Fetch SMPL-X mesh
            const smplxResp = await fetch('/api/character/smplx-mesh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ betas, gender: 'neutral' }),
            });
            const smplxData = await smplxResp.json();

            if (smplxData.ok && smplxData.vertices) {
                const smplxVerts = base64ToFloat32(smplxData.vertices);

                // Compute scale factor (match heights)
                let hbMaxY = -Infinity;
                const hbV = base64ToFloat32(hbData.vertices);
                blenderToThree(hbV);
                for (let i = 1; i < hbV.length; i += 3) {
                    if (hbV[i] > hbMaxY) hbMaxY = hbV[i];
                }
                let smplxMaxY = -Infinity;
                for (let i = 1; i < smplxVerts.length; i += 3) {
                    if (smplxVerts[i] > smplxMaxY) smplxMaxY = smplxVerts[i];
                }
                const scale = hbMaxY / Math.max(smplxMaxY, 0.01);

                results.scale = {
                    hbHeight: hbMaxY,
                    smplxHeight: smplxMaxY,
                    scaleFactor: scale,
                };

                for (const [name, y] of Object.entries(yHeights)) {
                    const localY = y / scale;
                    const m = measureSlice(smplxVerts, localY, 0.025 / scale, 0.3 / scale);
                    if (m) {
                        results.smplx[name] = {
                            width: m.width * scale,
                            depth: m.depth * scale,
                            verts: m.verts,
                        };
                    }
                }
            }

            resolve(results);
        } catch (e) {
            resolve({ error: e.message });
        }
    });
}"""


def main():
    job_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JOB
    url = f"{BASE_URL}?job={job_id}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1600, "height": 900})

        logs = []
        page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        print(f"Loading job: {job_id}")
        page.goto(url, timeout=90000)

        # Wait for both models to load
        page.wait_for_timeout(16000)

        # Measure via API
        print("\n=== Measuring via API ===")
        results = page.evaluate(MEASURE_JS, {"yHeights": MEASURE_POINTS})

        # Print results table
        print("\n" + "=" * 85)
        print("PROPORTIONS COMPARISON: HumanBody vs SMPL-X (absolute measurement matching)")
        print("=" * 85)

        if 'error' in results:
            print(f"ERROR: {results['error']}")
        else:
            if 'scale' in results:
                s = results['scale']
                print(f"Heights: HB={s.get('hbHeight', 0):.3f}m, "
                      f"SMPL-X={s.get('smplxHeight', 0):.3f}m, "
                      f"Scale={s.get('scaleFactor', 0):.3f}")

            print(f"\n{'Region':<15} | {'HB width':>10} | {'SX width':>10} | "
                  f"{'W Delta%':>8} | {'HB depth':>10} | {'SX depth':>10} | "
                  f"{'D Delta%':>8} | {'Status':>8}")
            print("-" * 100)

            hb = results.get('humanBody', {})
            sx = results.get('smplx', {})
            all_ok = True
            for name in MEASURE_POINTS:
                hb_m = hb.get(name, {})
                sx_m = sx.get(name, {})
                hw = hb_m.get('width', 0)
                sw = sx_m.get('width', 0)
                hd = hb_m.get('depth', 0)
                sd = sx_m.get('depth', 0)
                w_delta = ((hw - sw) / sw * 100) if sw > 0.001 else 0
                d_delta = ((hd - sd) / sd * 100) if sd > 0.001 else 0
                ok = abs(w_delta) < 10 and abs(d_delta) < 10
                status = "OK" if ok else "MISS"
                if not ok:
                    all_ok = False
                print(f"{name:<15} | {hw:>10.4f} | {sw:>10.4f} | "
                      f"{w_delta:>+7.1f}% | {hd:>10.4f} | {sd:>10.4f} | "
                      f"{d_delta:>+7.1f}% | {status:>8}")

            print()
            if all_ok:
                print("==> ALL regions within +/-10% tolerance")
            else:
                print("==> Some regions OUTSIDE +/-10% tolerance")

        # Multi-angle screenshots
        print("\n=== Taking screenshots ===")
        page.wait_for_timeout(500)
        page.screenshot(path=f"{SCREENSHOT_DIR}/proportions_front.png")
        print("  Front: proportions_front.png")
        page.screenshot(path=f"{SCREENSHOT_DIR}/proportions_overview.png",
                       full_page=False)
        print("  Overview: proportions_overview.png")

        # Print relevant console logs
        print("\n=== Relevant Console Logs ===")
        for log in logs:
            if any(k in log for k in ['Photo', 'morph', 'SMPL', 'meta', 'load',
                                       'FaceExpr', 'Morph', 'Body']):
                try:
                    print(f"  {log[:200]}")
                except Exception:
                    pass

        browser.close()
        print("\nDone!")


if __name__ == "__main__":
    main()
