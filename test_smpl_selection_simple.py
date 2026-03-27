"""
Simple test for SMPL garment selection
"""
from playwright.sync_api import sync_playwright
import time

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        page.goto('http://localhost:4040/test-smpl/')

        # Wait for page to load
        page.wait_for_timeout(3000)

        print("\n=== Loading SMPL Garment ===")
        # Select first garment
        first_item = page.locator('.smpl-garment-item').first
        first_item.click()
        page.wait_for_timeout(300)

        # Click load button
        page.click('#smpl-garment-load')
        page.wait_for_timeout(3000)

        # Check what's loaded
        info = page.evaluate("""
            ({
                smplGarments: Object.keys(window.smplGarmentMeshes || {}),
                selectableTargets: getSelectableTargets().map(t => ({
                    type: t.type,
                    id: t.id,
                    label: t.label
                }))
            })
        """)
        print(f"SMPL garments: {info['smplGarments']}")
        print(f"Selectable targets: {info['selectableTargets']}")

        # Try clicking on canvas
        print("\n=== Clicking Canvas ===")
        canvas = page.locator('canvas')
        box = canvas.bounding_box()

        # Click near SMPL body (left side)
        x = box['x'] + box['width'] * 0.3
        y = box['y'] + box['height'] * 0.5

        page.mouse.move(x, y)
        page.wait_for_timeout(500)

        hovered = page.evaluate("window._hoveredItem")
        print(f"Hovered: {hovered}")

        page.mouse.click(x, y)
        page.wait_for_timeout(500)

        selected = page.evaluate("window._selectedItem")
        print(f"Selected: {selected}")

        # Check equipped list
        equipped = page.locator('.equipped-item-name').all_text_contents()
        print(f"Equipped list: {equipped}")

        input("\n\nPress Enter to close...")
        browser.close()

if __name__ == '__main__':
    test()
