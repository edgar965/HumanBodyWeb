"""Playwright: verify camera orbit is preserved when FOV changes via Theatre.js.
The bug was: orbit camera, change FOV -> camera snaps back to initial position.
Fix: onValuesChange only applies position during playback."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))

    page.goto("http://localhost:8081/humanbody/theatre/", timeout=30000)
    page.wait_for_timeout(10000)

    # Step 1: Get initial camera position (default: 0, 1.2, 6)
    initial = page.evaluate("""() => {
        if (!window.camera) return null;
        return {
            x: Math.round(window.camera.position.x * 100) / 100,
            y: Math.round(window.camera.position.y * 100) / 100,
            z: Math.round(window.camera.position.z * 100) / 100,
            fov: window.camera.fov
        };
    }""")
    print(f"1. Initial camera: {initial}")

    # Step 2: Orbit camera (drag canvas)
    canvas = page.locator('#theatre-canvas')
    box = canvas.bounding_box()
    if box:
        cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
        page.mouse.move(cx, cy)
        page.mouse.down()
        for i in range(20):
            page.mouse.move(cx + i * 10, cy - i * 3)
        page.mouse.up()

    # Wait for damping to fully settle (2s)
    page.wait_for_timeout(2000)

    after_orbit = page.evaluate("""() => {
        if (!window.camera) return null;
        return {
            x: Math.round(window.camera.position.x * 100) / 100,
            y: Math.round(window.camera.position.y * 100) / 100,
            z: Math.round(window.camera.position.z * 100) / 100,
            fov: window.camera.fov
        };
    }""")
    print(f"2. After orbit (damping settled): {after_orbit}")

    orbit_moved = (
        after_orbit and initial and
        (abs(after_orbit['x'] - initial['x']) > 0.5 or
         abs(after_orbit['z'] - initial['z']) > 0.5)
    )
    print(f"   Camera moved significantly: {orbit_moved}")

    # Step 3: Change FOV via studio.transaction (proper Theatre.js API)
    result = page.evaluate("""() => {
        return new Promise(resolve => {
            try {
                const theatreObjs = window.theatreObjects;
                if (!theatreObjs || !theatreObjs.Camera) {
                    resolve({error: 'No Theatre Camera object'});
                    return;
                }

                const camera = window.camera;
                const posBefore = {
                    x: camera.position.x,
                    y: camera.position.y,
                    z: camera.position.z
                };

                // Change FOV via Theatre.js (triggers onValuesChange)
                window.studio.transaction(({ set }) => {
                    set(theatreObjs.Camera.props.fov, 30);
                });

                // Wait for callbacks + any damping
                setTimeout(() => {
                    const posAfter = {
                        x: camera.position.x,
                        y: camera.position.y,
                        z: camera.position.z
                    };

                    // Check: position should be approximately the same (within 0.3 for residual damping)
                    const dx = Math.abs(posAfter.x - posBefore.x);
                    const dy = Math.abs(posAfter.y - posBefore.y);
                    const dz = Math.abs(posAfter.z - posBefore.z);
                    const posPreserved = dx < 0.3 && dy < 0.3 && dz < 0.3;

                    // Check: position should NOT be near initial (0, 1.2, 6)
                    const distFromInitial = Math.sqrt(
                        Math.pow(posAfter.x - 0, 2) +
                        Math.pow(posAfter.y - 1.2, 2) +
                        Math.pow(posAfter.z - 6, 2)
                    );
                    const notSnappedBack = distFromInitial > 2.0;

                    resolve({
                        fovBefore: 50,
                        fovAfter: camera.fov,
                        posBefore: {
                            x: Math.round(posBefore.x * 100) / 100,
                            y: Math.round(posBefore.y * 100) / 100,
                            z: Math.round(posBefore.z * 100) / 100
                        },
                        posAfter: {
                            x: Math.round(posAfter.x * 100) / 100,
                            y: Math.round(posAfter.y * 100) / 100,
                            z: Math.round(posAfter.z * 100) / 100
                        },
                        maxDrift: Math.round(Math.max(dx, dy, dz) * 1000) / 1000,
                        distFromInitial: Math.round(distFromInitial * 100) / 100,
                        posPreserved: posPreserved,
                        notSnappedBack: notSnappedBack,
                        fovChanged: camera.fov === 30
                    });
                }, 1000);
            } catch (e) {
                resolve({error: e.message});
            }
        });
    }""")
    print(f"3. FOV change via Theatre.js:")
    if 'error' not in result:
        print(f"   FOV: {result['fovBefore']} -> {result['fovAfter']} (changed: {result['fovChanged']})")
        print(f"   Position before: {result['posBefore']}")
        print(f"   Position after:  {result['posAfter']}")
        print(f"   Max drift: {result['maxDrift']} (should be < 0.3)")
        print(f"   Dist from initial (0,1.2,6): {result['distFromInitial']} (should be > 2.0)")
        print(f"   Position preserved: {result['posPreserved']}")
        print(f"   NOT snapped back: {result['notSnappedBack']}")
    else:
        print(f"   ERROR: {result['error']}")

    ok = (
        orbit_moved and
        'error' not in result and
        result.get('posPreserved') and
        result.get('notSnappedBack') and
        result.get('fovChanged')
    )

    print(f"\nJS Errors: {len(errors)}")
    status = "ALL OK - Camera orbit preserved!" if ok else "ISSUES FOUND"
    print(f"\n{status}")

    page.screenshot(path="A:/3DTools/screenshot_camera_orbit.png")
    context.close()
    browser.close()
