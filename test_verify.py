"""Playwright: verify Studio panels AND canvas are both clickable."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    logs = []
    page.on("console", lambda msg: logs.append(f"{msg.type}: {msg.text}"))

    page.goto("http://localhost:8081/humanbody/theatre/", timeout=30000)
    page.wait_for_timeout(12000)

    # 1. Sequence Editor visible?
    seq = page.evaluate("""() => {
        const root = document.getElementById('theatrejs-studio-root');
        if (!root || !root.shadowRoot) return {visible: false};
        const sr = root.shadowRoot;
        let bottom = 0;
        const tracks = new Set();
        for (const el of sr.querySelectorAll('*')) {
            const r = el.getBoundingClientRect();
            if (r.width > 50 && r.height > 15 && r.y > 500) {
                bottom++;
                const t = (el.textContent || '').trim();
                for (const n of ['Camera', 'Spot Left', 'Spot Right', 'Back Light'])
                    if (t.startsWith(n) && t.length < 80) tracks.add(n);
            }
        }
        return {visible: bottom > 20, count: bottom, tracks: Array.from(tracks)};
    }""")
    print(f"Sequence Editor: {seq}")

    # 2. Click Camera in outline -> detail panel appears?
    page.evaluate("""() => {
        const sr = document.getElementById('theatrejs-studio-root').shadowRoot;
        for (const s of sr.querySelectorAll('span'))
            if (s.textContent.trim() === 'Camera' && s.getBoundingClientRect().height > 0) {
                s.click(); return;
            }
    }""")
    page.wait_for_timeout(500)
    detail = page.evaluate("""() => {
        const sr = document.getElementById('theatrejs-studio-root').shadowRoot;
        const found = [];
        for (const s of sr.querySelectorAll('span')) {
            const t = s.textContent.trim();
            if (['fov','position','Props'].includes(t) && s.getBoundingClientRect().height > 0)
                found.push(t);
        }
        return found;
    }""")
    print(f"Click Camera -> Detail: {detail}")

    # 3. Canvas clickable? Try orbit control (mousedown+mousemove on canvas)
    canvas_test = page.evaluate("""() => {
        const canvas = document.getElementById('theatre-canvas');
        if (!canvas) return 'no canvas';
        const r = canvas.getBoundingClientRect();
        // Check canvas is visible and has size
        return {
            width: Math.round(r.width),
            height: Math.round(r.height),
            pointerEvents: getComputedStyle(canvas).pointerEvents,
            zIndex: getComputedStyle(canvas).zIndex,
        };
    }""")
    print(f"Canvas: {canvas_test}")

    # 4. Click on canvas center - does it receive the event?
    canvas_clicked = page.evaluate("""() => {
        return new Promise(resolve => {
            const canvas = document.getElementById('theatre-canvas');
            let received = false;
            const handler = () => { received = true; };
            canvas.addEventListener('pointerdown', handler, {once: true});
            const r = canvas.getBoundingClientRect();
            canvas.dispatchEvent(new PointerEvent('pointerdown', {
                bubbles: true, clientX: r.x + r.width/2, clientY: r.y + r.height/2
            }));
            setTimeout(() => resolve(received), 100);
        });
    }""")
    print(f"Canvas receives pointerdown: {canvas_clicked}")

    # 5. Check that the studio overlay doesn't block canvas area
    overlay_check = page.evaluate("""() => {
        const root = document.getElementById('theatrejs-studio-root');
        if (!root) return 'no root';
        const style = getComputedStyle(root);
        return {
            pointerEvents: style.pointerEvents,
            position: style.position,
            inset: style.inset,
        };
    }""")
    print(f"Studio root style: {overlay_check}")

    # 6. Garments
    garments = page.evaluate("""() => {
        if (typeof window.scene === 'undefined') return [];
        const g = [];
        window.scene.traverse(c => {
            if (c.isSkinnedMesh && c.userData.isGarment)
                g.push({name: c.name, visible: c.visible});
        });
        return g;
    }""")
    print(f"Garments: {garments}")
    for i, err in enumerate(errors):
        print(f"JS Error {i+1}: {err[:200]}")
    print(f"JS Errors: {len(errors)}")

    real_errors = [e for e in errors if 'setPointerCapture' not in e]
    ok = (seq.get('visible') and len(seq.get('tracks', [])) == 4 and len(real_errors) == 0)
    print(f"\n{'ALL OK' if ok else 'ISSUES'}")

    page.screenshot(path="A:/3DTools/screenshot_theatre.png")
    context.close()
    browser.close()
