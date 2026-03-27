"""
Test SMPL garment selection on test-smpl page
"""
from playwright.sync_api import sync_playwright, expect
import time

def test_smpl_garment_selection():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        page.goto('http://localhost:4040/test-smpl/')

        # Wait for bodies to load
        page.wait_for_timeout(3000)

        print("\n=== Initial State ===")
        # Check garmentMeshes in viewer.js
        garment_meshes = page.evaluate("""
            Object.keys(window.garmentMeshes || {})
        """)
        print(f"garmentMeshes keys: {garment_meshes}")

        # Load an SMPL garment
        print("\n=== Loading SMPL Garment ===")
        page.click('#smpl-garment-library-toggle')
        page.wait_for_timeout(500)

        # Click first garment in list
        first_garment = page.locator('.smpl-garment-item').first
        garment_name = first_garment.locator('.smpl-garment-name').text_content()
        print(f"Loading garment: {garment_name}")

        load_btn = first_garment.locator('button:has-text("Laden")')
        load_btn.click()

        # Wait for garment to load
        page.wait_for_timeout(2000)

        print("\n=== After Loading ===")
        garment_meshes = page.evaluate("""
            Object.keys(window.garmentMeshes || {})
        """)
        print(f"garmentMeshes keys: {garment_meshes}")

        # Check selectable targets
        selectable = page.evaluate("""
            (function() {
                if (typeof getSelectableTargets !== 'function') {
                    return {error: 'getSelectableTargets not found'};
                }
                const targets = getSelectableTargets();
                return targets.map(t => ({
                    type: t.type,
                    id: t.id,
                    label: t.label,
                    hasRoot: !!t.root,
                    rootType: t.root?.type,
                    rootName: t.root?.name
                }));
            })()
        """)
        print(f"Selectable targets: {selectable}")

        # Try to click on the garment mesh
        print("\n=== Attempting Canvas Click ===")
        canvas = page.locator('canvas')
        canvas_box = canvas.bounding_box()

        # Click center of canvas (where body should be)
        click_x = canvas_box['x'] + canvas_box['width'] / 2
        click_y = canvas_box['y'] + canvas_box['height'] / 2

        print(f"Clicking at canvas center: ({click_x}, {click_y})")
        page.mouse.click(click_x, click_y)
        page.wait_for_timeout(500)

        # Check if anything got selected
        selected = page.evaluate("""
            window._selectedItem
        """)
        print(f"Selected item after click: {selected}")

        # Check hovered item
        hovered = page.evaluate("""
            window._hoveredItem
        """)
        print(f"Hovered item: {hovered}")

        # Move mouse around to find the garment
        print("\n=== Mouse Movement Test ===")
        for dy in [-100, -50, 0, 50, 100]:
            for dx in [-100, -50, 0, 50, 100]:
                x = canvas_box['x'] + canvas_box['width'] / 2 + dx
                y = canvas_box['y'] + canvas_box['height'] / 2 + dy
                page.mouse.move(x, y)
                page.wait_for_timeout(50)

                hovered = page.evaluate("window._hoveredItem")
                if hovered:
                    print(f"Found hovered item at offset ({dx}, {dy}): {hovered}")
                    break
            if hovered:
                break

        # Check raycaster setup
        print("\n=== Raycaster Debug ===")
        raycast_info = page.evaluate("""
            (function() {
                const canvas = document.querySelector('canvas');
                const rect = canvas.getBoundingClientRect();
                const targets = getSelectableTargets();
                const roots = targets.map(t => t.root);

                return {
                    canvas_size: {w: rect.width, h: rect.height},
                    target_count: targets.length,
                    roots_count: roots.length,
                    scene_children: window.scene?.children?.length || 0
                };
            })()
        """)
        print(f"Raycast info: {raycast_info}")

        input("\n\nPress Enter to close browser...")
        browser.close()

if __name__ == '__main__':
    test_smpl_garment_selection()
