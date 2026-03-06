"""Debug test: Check Male SkinnedMesh face with and without expression."""
import sys, os, json, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8081'
PAGE = f'{BASE}/humanbody/photo-to-3d/'
PHOTO_DIR = r'A:\3DTools\HumanBodyWeb\media\photo_analysis'
OUT = r'A:\3DTools\HumanBodyWeb'


def find_test_photo():
    for f in os.listdir(PHOTO_DIR):
        if f.endswith(('.png', '.jpg')) and os.path.getsize(os.path.join(PHOTO_DIR, f)) > 10000:
            return os.path.join(PHOTO_DIR, f)
    return None


def run():
    photo_path = find_test_photo()
    print(f'Test photo: {photo_path}')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        ctx = browser.new_context(no_viewport=True)
        page = ctx.new_page()

        def on_console(msg):
            text = msg.text.encode('ascii', 'replace').decode()
            if 'Photo' in text or 'skeleton' in text.lower() or 'bone' in text.lower() or 'skin' in text.lower() or 'error' in msg.type:
                print(f'  [{msg.type}] {text}')
        page.on('console', on_console)

        # Load page
        print('\n=== 1. Load page ===')
        page.goto(PAGE, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(4000)

        # Screenshot: Female at rest (initial state)
        page.screenshot(path=os.path.join(OUT, 'test_face_01_female_rest.png'))
        print('  -> test_face_01_female_rest.png')

        # Switch to Male WITHOUT analysis (just change body type dropdown)
        print('\n=== 2. Switch to Male_Caucasian (no analysis) ===')
        page.select_option('#body-type-select', 'Male_Caucasian')
        page.wait_for_timeout(5000)  # Wait for mesh + skeleton reload

        page.screenshot(path=os.path.join(OUT, 'test_face_02_male_rest.png'))
        print('  -> test_face_02_male_rest.png')

        # Check bone count and skeleton state via console
        bone_info = page.evaluate("""() => {
            // We can't access module vars directly, but we can check DOM
            return {
                body_type: document.getElementById('body-type-select')?.value,
                vertex_count: document.getElementById('vertex-count')?.textContent,
            };
        }""")
        print(f'  Body type: {bone_info["body_type"]}')
        print(f'  Vertex count: {bone_info["vertex_count"]}')

        # Now upload photo and analyze with PyMAF-X
        print('\n=== 3. Upload photo + analyze with PyMAF-X ===')
        page.locator('#photo-input').set_input_files(photo_path)
        page.wait_for_timeout(1000)

        # Select PyMAF-X
        pymafx = page.locator('.backend-item[data-backend="pymafx"]')
        if pymafx.count() > 0:
            pymafx.click()
            print('  Selected PyMAF-X')

        page.locator('#btn-analyze').click()
        print('  Analyzing...')
        page.wait_for_function(
            "() => !document.getElementById('btn-analyze').classList.contains('loading')",
            timeout=120000
        )
        print('  Done!')
        page.wait_for_timeout(3000)

        page.screenshot(path=os.path.join(OUT, 'test_face_03_pymafx_with_expr.png'))
        print('  -> test_face_03_pymafx_with_expr.png')

        # Get expression values
        expr_info = page.evaluate("""() => {
            const params = document.querySelectorAll('.detection-param');
            const result = {};
            params.forEach(p => {
                const name = p.querySelector('.param-name')?.textContent || '';
                const val = p.querySelector('.param-val')?.textContent || '';
                result[name] = val;
            });
            return result;
        }""")
        print(f'  Expression info: {json.dumps(expr_info, ensure_ascii=False, indent=2)}')

        # Rotate camera to side view for jaw check
        print('\n=== 4. Side view ===')
        canvas = page.locator('#viewer-canvas')
        box = canvas.bounding_box()
        if box:
            cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
            # Drag to rotate to side view (~90 degrees)
            page.mouse.move(cx, cy)
            page.mouse.down()
            for step in range(30):
                page.mouse.move(cx - step * 12, cy, steps=1)
            page.mouse.up()
        page.wait_for_timeout(2000)

        page.screenshot(path=os.path.join(OUT, 'test_face_04_side_view.png'))
        print('  -> test_face_04_side_view.png (side view with expression)')

        # Now RESET expression to 0 and take screenshot
        print('\n=== 5. Reset expression to zero ===')
        page.evaluate("""() => {
            const panel = document.getElementById('smplx-panel');
            if (panel) {
                panel.querySelectorAll('input[data-expr-idx]').forEach(s => {
                    s.value = 0;
                    s.dispatchEvent(new Event('input', { bubbles: true }));
                });
            }
        }""")
        page.wait_for_timeout(2000)

        page.screenshot(path=os.path.join(OUT, 'test_face_05_side_no_expr.png'))
        print('  -> test_face_05_side_no_expr.png (side view, expression zeroed)')

        print('\n=== 6. Done - browser open for 10s ===')
        page.wait_for_timeout(10000)
        browser.close()


if __name__ == '__main__':
    run()
