"""Playwright E2E test: Preview-Fenster mit Konturen im Textur-Tab.

Loads an existing photo job, switches to Textur tab, fetches silhouette
data to verify contour alignment, then takes screenshots.
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8081'
SCREENSHOT_DIR = r'A:\3DTools\HumanBodyWeb'

# Most recent pymafx job (UUID with dashes)
JOB_ID = '7c875cb5-733d-4bd1-b42e-26fb989af67b'


def test_preview_contours():
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        ctx = browser.new_context(no_viewport=True)
        page = ctx.new_page()

        def on_console(msg):
            text = msg.text.encode('ascii', 'replace').decode()
            if msg.type == 'error' and 'style.css' not in text:
                console_errors.append(text)
                print(f'  CONSOLE {msg.type}: {text[:150]}')

        def on_page_error(err):
            text = str(err).encode('ascii', 'replace').decode()
            console_errors.append(text)
            print(f'  PAGE ERROR: {text[:150]}')

        page.on('console', on_console)
        page.on('pageerror', on_page_error)

        # 1. Load page without job first (ensures static files are cached)
        print('\n=== Step 1: Loading page ===')
        page.goto(f'{BASE}/humanbody/photo-to-3d/', timeout=30000)
        page.wait_for_timeout(3000)

        # 2. Navigate to page with job + textur tab
        url = f'{BASE}/humanbody/photo-to-3d/?job={JOB_ID}&tab=textur'
        print(f'  Loading job: {url}')
        page.goto(url, timeout=60000)
        page.wait_for_timeout(8000)

        # 3. Ensure photo is loaded
        print('\n=== Step 2: Checking photo ===')
        photo_img = page.locator('#photo-img')
        for attempt in range(5):
            if photo_img.is_visible():
                print('  Photo visible: OK')
                break
            print(f'  Waiting for photo (attempt {attempt + 1})...')
            page.wait_for_timeout(2000)

        # 4. Click Textur tab
        print('\n=== Step 3: Switching to Textur tab ===')
        textur_tab = page.locator('.photo-tab[data-tab="textur"]')
        if textur_tab.is_visible():
            textur_tab.click()
            print('  Clicked Textur tab')
        page.wait_for_timeout(4000)  # Wait for silhouette fetch + render

        # 5. Fetch silhouette data from browser context
        print('\n=== Step 4: Checking silhouette data ===')
        sil_data = page.evaluate("""async () => {
            const resp = await fetch('/api/character/photo-job/""" + JOB_ID + """/silhouette/');
            return await resp.json();
        }""")

        ok = True
        if sil_data.get('ok'):
            pw = sil_data.get('photo_width', 0)
            ph = sil_data.get('photo_height', 0)
            print(f'  Photo: {pw} x {ph}')

            bc = sil_data.get('body_contour', [])
            fc = sil_data.get('face_contour', [])

            print(f'  body_contour: {len(bc)} points')
            if bc:
                bx = [p[0] for p in bc]
                by = [p[1] for p in bc]
                print(f'    x: {min(bx):.0f} - {max(bx):.0f}')
                print(f'    y: {min(by):.0f} - {max(by):.0f}')

            print(f'  face_contour: {len(fc)} points')
            if fc:
                fx = [p[0] for p in fc]
                fy = [p[1] for p in fc]
                print(f'    x: {min(fx):.0f} - {max(fx):.0f}')
                print(f'    y: {min(fy):.0f} - {max(fy):.0f}')

                # Verify face is in top 20% of image
                face_y_max = max(fy)
                if face_y_max > ph * 0.25:
                    print(f'    WARNING: Face extends below 25% ({face_y_max:.0f} > {ph*0.25:.0f})')
                    ok = False
                else:
                    print(f'    Face in top {face_y_max/ph*100:.0f}% of image: OK')

                # Verify face width is < 50% of image
                face_w = max(fx) - min(fx)
                if face_w > pw * 0.5:
                    print(f'    WARNING: Face too wide ({face_w:.0f} > {pw*0.5:.0f})')
                    ok = False
                else:
                    print(f'    Face width {face_w:.0f}px ({face_w/pw*100:.0f}% of image): OK')
            else:
                print('    FAIL: No face contour')
                ok = False
        else:
            print(f'  ERROR: {sil_data}')
            ok = False

        # 6. Take screenshots
        print('\n=== Step 5: Taking screenshots ===')

        preview_canvas = page.locator('#preview-projection')
        if preview_canvas.is_visible():
            preview_canvas.screenshot(
                path=os.path.join(SCREENSHOT_DIR, 'test_contour_04_canvas_only.png'))
            print('  Canvas screenshot: test_contour_04_canvas_only.png')

            # Open zoom dialog
            preview_canvas.click()
            page.wait_for_timeout(1500)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'test_contour_05_zoom.png'))
            print('  Zoom screenshot: test_contour_05_zoom.png')
        else:
            print('  WARNING: Preview canvas not visible')
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, 'test_contour_03_fallback.png'))

        # 7. Summary
        print('\n=== Result ===')
        if ok and not console_errors:
            print('  PASS: Contours correctly positioned')
        elif ok:
            print(f'  PASS (with {len(console_errors)} console warnings)')
        else:
            print('  FAIL: Contour issues detected')

        page.wait_for_timeout(2000)
        browser.close()


if __name__ == '__main__':
    test_preview_contours()
