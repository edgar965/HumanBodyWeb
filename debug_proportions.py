"""Debug: Measure HumanBody + SMPL-X meshes via API and compare.

Fetches both meshes server-side using the same measurement method
as _measure_smplx_body(), without needing a browser.

Usage:
    python debug_proportions.py [job_uuid]
    python debug_proportions.py --betas "0.4 -0.5 0.5 -0.5 -0.5"
    python debug_proportions.py --baseline male   (zero-morph HB baseline)
"""
import sys
import os
import json
import struct
import base64
import argparse
import urllib.request

API_BASE = "http://localhost:8081"

HEIGHT_FRACS = {
    'shoulders': 0.77, 'chest': 0.70, 'waist': 0.60,
    'hips': 0.50, 'thighs': 0.37,
}


def b64_to_float32(b64_str):
    raw = base64.b64decode(b64_str)
    return list(struct.unpack(f'<{len(raw)//4}f', raw))


def measure_mesh(verts_flat, height_fracs, arm_limit=0.3, tol=0.025):
    """Measure width/depth at height fractions.  verts_flat = [x,y,z,x,y,z,...]"""
    n = len(verts_flat) // 3
    xs = [verts_flat[i*3] for i in range(n)]
    ys = [verts_flat[i*3+1] for i in range(n)]
    zs = [verts_flat[i*3+2] for i in range(n)]

    min_y = min(ys)
    max_y = max(ys)
    height = max_y - min_y

    result = {'height': height}
    for region, frac in height_fracs.items():
        y_level = min_y + height * frac
        x_limit = 0.35 if region == 'shoulders' else arm_limit

        sel_x, sel_z = [], []
        for i in range(n):
            if abs(ys[i] - y_level) < tol and abs(xs[i]) < x_limit:
                sel_x.append(xs[i])
                sel_z.append(zs[i])

        if len(sel_x) < 5:
            result[region] = (0, 0, 0)
            continue
        w = max(sel_x) - min(sel_x)
        d = max(sel_z) - min(sel_z)
        result[region] = (w, d, len(sel_x))

    return result


def blender_to_yup(verts_flat):
    """Convert Blender coords (Z-up) to Y-up in-place."""
    for i in range(0, len(verts_flat), 3):
        y, z = verts_flat[i+1], verts_flat[i+2]
        verts_flat[i+1] = z
        verts_flat[i+2] = -y
    return verts_flat


def fetch_json(url, post_data=None):
    """Fetch JSON from API."""
    if post_data:
        data = json.dumps(post_data).encode()
        req = urllib.request.Request(url, data=data,
                                     headers={'Content-Type': 'application/json'})
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def measure_humanbody(body_type='Male_Caucasian', morphs=None, meta=None):
    """Fetch + measure HumanBody mesh via API."""
    url = f"{API_BASE}/api/character/mesh/?body_type={body_type}"
    if morphs:
        for k, v in morphs.items():
            if abs(v) > 0.001:
                url += f"&morph_{k}={v}"
    if meta:
        ranges = {'height': (150, 200), 'mass': (45, 200),
                  'tone': (0, 100), 'age': (18, 100)}
        for k, v in meta.items():
            r = ranges.get(k)
            if r:
                neutral = (r[0] + r[1]) / 2
                half = (r[1] - r[0]) / 2
                internal = (v - neutral) / half if half else 0
                url += f"&meta_{k}={internal}"

    data = fetch_json(url)
    if 'vertices' not in data:
        print(f"  ERROR: No vertices in response. Keys: {list(data.keys())}")
        return None
    verts = b64_to_float32(data['vertices'])
    blender_to_yup(verts)
    return measure_mesh(verts, HEIGHT_FRACS)


def measure_smplx(betas, gender='neutral'):
    """Fetch + measure SMPL-X mesh via API."""
    url = f"{API_BASE}/api/character/smplx-mesh/"
    data = fetch_json(url, {'betas': betas, 'gender': gender})
    if not data.get('ok') or 'vertices' not in data:
        print(f"  ERROR: SMPL-X mesh failed. Keys: {list(data.keys())}")
        return None
    verts = b64_to_float32(data['vertices'])
    # SMPL-X is already Y-up from generate_mesh
    return measure_mesh(verts, HEIGHT_FRACS)


def print_comparison(hb, sx, label="HumanBody vs SMPL-X"):
    """Print comparison table."""
    print(f"\n{'='*95}")
    print(f"  {label}")
    print(f"{'='*95}")

    if hb and sx:
        # Scale SMPL-X to HB height
        scale = hb['height'] / max(sx['height'], 0.01)
        print(f"  Heights: HB={hb['height']:.3f}m, SMPL-X={sx['height']:.3f}m, "
              f"Scale={scale:.3f}")

    print(f"\n  {'Region':<15} | {'HB width':>10} | {'SX width':>10} | "
          f"{'W Delta%':>8} | {'HB depth':>10} | {'SX depth':>10} | "
          f"{'D Delta%':>8} | {'HB verts':>8} | {'SX verts':>8} | {'Status':>6}")
    print(f"  {'-'*110}")

    all_ok = True
    for region in HEIGHT_FRACS:
        hb_w, hb_d, hb_n = hb.get(region, (0, 0, 0)) if hb else (0, 0, 0)
        sx_w, sx_d, sx_n = sx.get(region, (0, 0, 0)) if sx else (0, 0, 0)

        # Scale SMPL-X to HB height
        if hb and sx and sx['height'] > 0.01:
            scale = hb['height'] / sx['height']
            sx_w *= scale
            sx_d *= scale

        w_d = ((hb_w - sx_w) / sx_w * 100) if sx_w > 0.001 else 0
        d_d = ((hb_d - sx_d) / sd if (sd := sx_d) > 0.001 else 0) if sx_d > 0.001 else 0
        d_d = ((hb_d - sx_d) / sx_d * 100) if sx_d > 0.001 else 0
        ok = abs(w_d) < 15 and abs(d_d) < 15
        if not ok:
            all_ok = False
        status = "OK" if ok else "MISS"
        print(f"  {region:<15} | {hb_w:>10.4f} | {sx_w:>10.4f} | "
              f"{w_d:>+7.1f}% | {hb_d:>10.4f} | {sx_d:>10.4f} | "
              f"{d_d:>+7.1f}% | {hb_n:>8} | {sx_n:>8} | {status:>6}")

    print()
    if all_ok:
        print("  ==> ALL regions within +/-15% tolerance")
    else:
        print("  ==> Some regions OUTSIDE +/-15% tolerance")
    return all_ok


def main():
    parser = argparse.ArgumentParser(description='Debug proportions comparison')
    parser.add_argument('job_id', nargs='?', default=None,
                        help='Job UUID to load betas/morphs from')
    parser.add_argument('--betas', type=str, default=None,
                        help='Space-separated betas string')
    parser.add_argument('--baseline', type=str, default=None,
                        help='Measure zero-morph HB baseline (male/female)')
    args = parser.parse_args()

    if args.baseline:
        gender = args.baseline.lower()
        body_type = 'Male_Caucasian' if gender == 'male' else 'Female_Caucasian'
        print(f"\n=== HumanBody BASELINE: {body_type} (zero morphs) ===")
        hb = measure_humanbody(body_type)
        if hb:
            print(f"  Height: {hb['height']:.4f}m")
            print(f"\n  {'Region':<15} | {'Width':>10} | {'Depth':>10} | {'Verts':>8}")
            print(f"  {'-'*55}")
            for region in HEIGHT_FRACS:
                w, d, n = hb.get(region, (0, 0, 0))
                print(f"  {region:<15} | {w:>10.4f} | {d:>10.4f} | {n:>8}")

        print(f"\n=== SMPL-X BASELINE: zero betas ===")
        sx = measure_smplx([0]*10, 'neutral')
        if sx:
            print(f"  Height: {sx['height']:.4f}m")
            print(f"\n  {'Region':<15} | {'Width':>10} | {'Depth':>10} | {'Verts':>8}")
            print(f"  {'-'*55}")
            for region in HEIGHT_FRACS:
                w, d, n = sx.get(region, (0, 0, 0))
                print(f"  {region:<15} | {w:>10.4f} | {d:>10.4f} | {n:>8}")

        if hb and sx:
            print_comparison(hb, sx, f"Baseline: {body_type} vs SMPL-X zero-betas")
        return

    # Load job data
    betas = [0] * 10
    morphs = {}
    meta = {}
    body_type = 'Male_Caucasian'
    gender = 'male'

    if args.betas:
        betas = [float(x) for x in args.betas.split()]
        betas += [0] * max(0, 10 - len(betas))
    elif args.job_id:
        job_url = f"{API_BASE}/api/character/photo-job/{args.job_id}/"
        job_data = fetch_json(job_url)
        if job_data.get('ok'):
            betas = job_data.get('betas', betas)
            morphs = job_data.get('morphs', {})
            meta = job_data.get('meta_sliders', {})
            body_type = job_data.get('body_type', body_type)
            gender = 'male' if 'Male' in body_type else 'female'
            print(f"Job: {args.job_id}")
            print(f"Body type: {body_type}")
            print(f"Meta: {json.dumps(meta)}")
            print(f"Betas: {[round(b,3) for b in betas[:10]]}")
            print(f"Morph count: {len(morphs)}")
        else:
            print(f"Job not found: {args.job_id}")
            return

    # 1. HumanBody with morphs+meta (as viewer sees it)
    print("\n=== Measuring HumanBody WITH morphs+meta ===")
    hb_morphed = measure_humanbody(body_type, morphs, meta)

    # 2. HumanBody baseline (zero morphs)
    print("=== Measuring HumanBody BASELINE (zero morphs) ===")
    hb_baseline = measure_humanbody(body_type)

    # 3. SMPL-X with betas
    print("=== Measuring SMPL-X WITH betas ===")
    sx_betas = measure_smplx(betas, 'neutral')

    # 4. SMPL-X baseline
    print("=== Measuring SMPL-X BASELINE (zero betas) ===")
    sx_zero = measure_smplx([0]*10, 'neutral')

    # Print comparisons
    if hb_morphed and sx_betas:
        print_comparison(hb_morphed, sx_betas,
                         "HumanBody (with morphs) vs SMPL-X (with betas) — FINAL RESULT")

    if hb_baseline and sx_zero:
        print_comparison(hb_baseline, sx_zero,
                         "HumanBody BASELINE vs SMPL-X BASELINE — Structural gap")

    if hb_morphed and hb_baseline:
        print(f"\n{'='*95}")
        print(f"  HumanBody morphed vs baseline — Effect of morphs")
        print(f"{'='*95}")
        print(f"\n  {'Region':<15} | {'Base W':>10} | {'Morph W':>10} | "
              f"{'W chg%':>8} | {'Base D':>10} | {'Morph D':>10} | {'D chg%':>8}")
        print(f"  {'-'*90}")
        for region in HEIGHT_FRACS:
            bw, bd, _ = hb_baseline.get(region, (0, 0, 0))
            mw, md, _ = hb_morphed.get(region, (0, 0, 0))
            wc = ((mw - bw) / bw * 100) if bw > 0.001 else 0
            dc = ((md - bd) / bd * 100) if bd > 0.001 else 0
            print(f"  {region:<15} | {bw:>10.4f} | {mw:>10.4f} | "
                  f"{wc:>+7.1f}% | {bd:>10.4f} | {md:>10.4f} | {dc:>+7.1f}%")

    # Morph summary
    if morphs:
        print(f"\n{'='*95}")
        print(f"  Active morphs ({len(morphs)} total)")
        print(f"{'='*95}")
        for k in sorted(morphs.keys()):
            v = morphs[k]
            bar = '#' * int(abs(v) * 20)
            sign = '+' if v > 0 else '-' if v < 0 else ' '
            print(f"  {k:<35} {sign}{abs(v):>6.3f}  {'|':>2} {bar}")


if __name__ == '__main__':
    main()
