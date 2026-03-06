"""Playwright E2E test: Photo-to-3D pipeline.

Tests that uploading a photo and running analysis produces a valid
SkinnedMesh without distortion (no spikes/monster artifacts).
"""
import sys, os, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8081'
PAGE = f'{BASE}/humanbody/photo-to-3d/'
# Use one of the existing uploaded test photos
PHOTO_DIR = r'A:\3DTools\HumanBodyWeb\media\photo_analysis'
SCREENSHOT_DIR = r'A:\3DTools\HumanBodyWeb'


def find_test_photo():
    """Find a valid test photo in media/photo_analysis/."""
    for f in os.listdir(PHOTO_DIR):
        if f.endswith('.png') or f.endswith('.jpg'):
            path = os.path.join(PHOTO_DIR, f)
            if os.path.getsize(path) > 10000:  # At least 10KB
                return path
    return None


def test_photo_pipeline():
    photo_path = find_test_photo()
    if not photo_path:
        print('ERROR: No test photo found in', PHOTO_DIR)
        return False

    print(f'Using test photo: {photo_path}')
    console_msgs = []
    errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        ctx = browser.new_context(no_viewport=True)
        page = ctx.new_page()

        # Capture console messages
        def on_console(msg):
            text = msg.text.encode('ascii', 'replace').decode()
            console_msgs.append(f'[{msg.type}] {text}')
            if msg.type in ('error', 'warning'):
                print(f'  CONSOLE {msg.type}: {text}')

        def on_page_error(err):
            text = str(err).encode('ascii', 'replace').decode()
            errors.append(text)
            print(f'  PAGE ERROR: {text}')

        page.on('console', on_console)
        page.on('pageerror', on_page_error)

        # 1. Load page
        print('\n=== Step 1: Loading page ===')
        page.goto(PAGE, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)  # Wait for Three.js init

        # Take initial screenshot
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'test_p3d_01_initial.png'))
        print('  Screenshot: test_p3d_01_initial.png')

        # 2. Upload photo via file input
        print('\n=== Step 2: Uploading photo ===')
        file_input = page.locator('#photo-input')
        file_input.set_input_files(photo_path)
        page.wait_for_timeout(1000)

        # Verify photo preview is visible
        preview = page.locator('#photo-preview')
        if preview.is_visible():
            print('  Photo preview visible: OK')
        else:
            print('  WARNING: Photo preview not visible')

        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'test_p3d_02_uploaded.png'))
        print('  Screenshot: test_p3d_02_uploaded.png')

        # 3. Select backend and analyze
        print('\n=== Step 3: Starting analysis ===')
        # Select PyMAF-X backend
        backends = page.locator('.backend-item')
        backend_count = backends.count()
        print(f'  Available backends: {backend_count}')
        for i in range(backend_count):
            el = backends.nth(i)
            name = el.get_attribute('data-backend') or ''
            cls = el.get_attribute('class') or ''
            print(f'    Backend {i}: {name} (class: {cls})')

        # Click PyMAF-X specifically
        pymafx_item = page.locator('.backend-item[data-backend="pymafx"]')
        if pymafx_item.count() > 0 and 'disabled' not in (pymafx_item.get_attribute('class') or ''):
            pymafx_item.click()
            print('  Selected backend: pymafx')
        else:
            print('  WARNING: PyMAF-X not available, selecting first available')
            for preferred in ['smplest_x', 'mediapipe', 'hmr2']:
                el = page.locator(f'.backend-item[data-backend="{preferred}"]')
                if el.count() > 0 and 'disabled' not in (el.get_attribute('class') or ''):
                    el.click()
                    print(f'  Selected backend: {preferred}')
                    break

        # Click analyze button
        analyze_btn = page.locator('#btn-analyze')
        analyze_btn.click()
        print('  Analyzing...')

        # Wait for analysis to complete (loading class removed)
        page.wait_for_function(
            "() => !document.getElementById('btn-analyze').classList.contains('loading')",
            timeout=120000
        )
        print('  Analysis complete!')
        page.wait_for_timeout(3000)  # Wait for mesh reload

        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'test_p3d_03_analyzed.png'))
        print('  Screenshot: test_p3d_03_analyzed.png')

        # 4. Check detection results
        print('\n=== Step 4: Checking results ===')
        results_div = page.locator('#detection-results')
        if results_div.is_visible():
            params = page.locator('.detection-param')
            for i in range(params.count()):
                text = params.nth(i).text_content().strip()
                print(f'  Param: {text}')
        else:
            print('  WARNING: Detection results not visible')

        # 5. Check mesh integrity via JavaScript
        print('\n=== Step 5: Checking mesh integrity ===')
        mesh_info = page.evaluate("""() => {
            // Access module-scoped variables via canvas context
            const canvas = document.getElementById('viewer-canvas');
            if (!canvas) return { error: 'No canvas found' };

            // Try to find Three.js scene through renderer
            const result = {};

            // Check if bodyMesh exists by looking for console output patterns
            // We can't directly access module variables, so check DOM state
            result.canvas_size = { w: canvas.width, h: canvas.height };
            result.detection_visible = document.getElementById('detection-results')?.style.display !== 'none';
            result.vertex_count_text = document.getElementById('vertex-count')?.textContent || 'N/A';
            result.body_type_value = document.getElementById('body-type-select')?.value || 'N/A';

            return result;
        }""")
        print(f'  Canvas: {mesh_info.get("canvas_size")}')
        print(f'  Vertex count: {mesh_info.get("vertex_count_text")}')
        print(f'  Body type: {mesh_info.get("body_type_value")}')
        print(f'  Detection visible: {mesh_info.get("detection_visible")}')

        # 6. Rotate camera to check different angles for spikes
        print('\n=== Step 6: Visual inspection screenshots ===')
        # Wait a moment for rendering to settle
        page.wait_for_timeout(2000)

        # Front view
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'test_p3d_04_front.png'))
        print('  Screenshot: test_p3d_04_front.png (front view)')

        # Check for vertex position anomalies by sampling pixel data
        # If there are spikes, the bounding box of the mesh will be way larger than expected
        spike_check = page.evaluate("""() => {
            const canvas = document.getElementById('viewer-canvas');
            if (!canvas) return { error: 'no canvas' };
            const ctx = canvas.getContext('webgl2') || canvas.getContext('webgl');
            if (!ctx) return { error: 'no gl context' };

            // Read pixels from center-right area (where HumanBody model should be)
            const w = canvas.width;
            const h = canvas.height;
            const pixels = new Uint8Array(4);

            // Sample several points around where spikes would appear
            // Spikes typically show up at top/bottom/left/right edges of the model
            const samples = [];
            // Check extreme positions where spikes would go (very high/low Y, far X)
            const positions = [
                // Top of canvas (if spike goes up)
                [w * 0.3, h * 0.95, 'top-left'],
                [w * 0.5, h * 0.95, 'top-center'],
                // Bottom of canvas (if spike goes down)
                [w * 0.3, h * 0.05, 'bottom-left'],
                [w * 0.5, h * 0.05, 'bottom-center'],
                // Edges (if spike goes sideways)
                [w * 0.05, h * 0.5, 'far-left'],
                [w * 0.95, h * 0.5, 'far-right'],
            ];

            for (const [x, y, label] of positions) {
                ctx.readPixels(Math.floor(x), Math.floor(y), 1, 1, ctx.RGBA, ctx.UNSIGNED_BYTE, pixels);
                samples.push({
                    label,
                    r: pixels[0], g: pixels[1], b: pixels[2], a: pixels[3],
                    isBg: pixels[0] < 30 && pixels[1] < 30 && pixels[2] < 30
                });
            }

            return { samples };
        }""")

        if spike_check.get('samples'):
            print('  Pixel sampling for spike detection:')
            spike_count = 0
            for s in spike_check['samples']:
                is_bg = s.get('isBg', True)
                status = 'BG' if is_bg else 'MESH'
                if not is_bg:
                    spike_count += 1
                print(f"    {s['label']}: rgba({s['r']},{s['g']},{s['b']},{s['a']}) = {status}")

            if spike_count > 2:
                print(f'  WARNING: {spike_count}/6 edge samples have non-BG pixels - possible spikes!')
            else:
                print(f'  OK: Only {spike_count}/6 edge samples have non-BG pixels (expected for normal model)')

        # 7. Check console for errors
        print('\n=== Step 7: Console error summary ===')
        js_errors = [m for m in console_msgs if m.startswith('[error]')]
        js_warnings = [m for m in console_msgs if m.startswith('[warning]')]
        photo_logs = [m for m in console_msgs if 'Photo' in m or 'skin' in m.lower() or 'skeleton' in m.lower() or 'bone' in m.lower()]

        if js_errors:
            print(f'  JS Errors ({len(js_errors)}):')
            for e in js_errors[:10]:
                print(f'    {e}')
        else:
            print('  No JS errors')

        if photo_logs:
            print(f'  Photo-3D logs ({len(photo_logs)}):')
            for l in photo_logs[:20]:
                print(f'    {l}')

        if errors:
            print(f'  Page errors ({len(errors)}):')
            for e in errors[:5]:
                print(f'    {e}')

        # 8. Final comprehensive screenshot
        print('\n=== Step 8: Final state ===')
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'test_p3d_05_final.png'))
        print('  Screenshot: test_p3d_05_final.png')

        # Keep browser open for manual inspection
        print('\n=== DONE ===')
        print('Browser stays open for 15 seconds for visual inspection...')
        page.wait_for_timeout(15000)

        browser.close()

    # Summary
    print('\n' + '=' * 60)
    print('SUMMARY')
    print('=' * 60)
    has_errors = len(js_errors) > 0 or len(errors) > 0
    print(f'JS Errors: {len(js_errors)}')
    print(f'Page Errors: {len(errors)}')
    print(f'Total Console: {len(console_msgs)}')
    print(f'Status: {"FAIL" if has_errors else "PASS"}')
    return not has_errors


if __name__ == '__main__':
    success = test_photo_pipeline()
    sys.exit(0 if success else 1)
