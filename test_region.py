"""Playwright test for Pattern Editor Region mode."""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]

        # Find or navigate to character viewer
        page = None
        for pg in ctx.pages:
            if 'humanbody/config' in pg.url:
                page = pg
                break

        if not page:
            page = await ctx.new_page()
            await page.goto('http://localhost:4040/humanbody/config/',
                            wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)  # wait for viewer init

        print(f'Page: {page.url}')

        # Inspect all tabs first
        tabs_info = await page.evaluate('''() => {
            const tabs = document.querySelectorAll('.panel-tab');
            return Array.from(tabs).map(t => ({
                dataTab: t.getAttribute('data-tab'),
                text: t.textContent.trim(),
                visible: t.offsetParent !== null
            }));
        }''')
        print('Tabs found:')
        for t in tabs_info:
            print(f'  {t}')

        # Click the Pattern tab via JS (try different selector)
        clicked = await page.evaluate('''() => {
            const tabs = document.querySelectorAll('.panel-tab');
            for (const t of tabs) {
                if (t.textContent.trim() === 'Pattern' || t.getAttribute('data-tab') === 'tab-creator') {
                    t.click();
                    return true;
                }
            }
            return false;
        }''')
        await asyncio.sleep(0.5)
        print(f'Clicked Pattern tab: {clicked}')

        # Check PE elements
        pe_found = await page.evaluate('''() => {
            const ids = ['pe-mode-btns', 'pe-region-controls', 'pe-pattern-controls', 'pe-generate'];
            return ids.map(id => {
                const el = document.getElementById(id);
                return {id, found: !!el, visible: el ? el.offsetParent !== null : false};
            });
        }''')
        print('Pattern elements:')
        for e in pe_found:
            print(f'  {e}')

        # Click Region button via JS
        await page.evaluate('''() => {
            const btn = document.querySelector('[data-mode="region"]');
            if (btn) btn.click();
        }''')
        await asyncio.sleep(0.3)
        mode = await page.evaluate('window.__viewer ? window.__viewer.peMode : "no viewer"')
        print(f'PE mode after region click: {mode}')

        # Check visibility
        vis = await page.evaluate('''() => {
            const rc = document.getElementById('pe-region-controls');
            const pc = document.getElementById('pe-pattern-controls');
            return {
                regionDisplay: rc ? rc.style.display : 'NOT_FOUND',
                regionVisible: rc ? rc.offsetParent !== null : false,
                patternDisplay: pc ? pc.style.display : 'NOT_FOUND',
                patternVisible: pc ? pc.offsetParent !== null : false,
            };
        }''')
        print(f'Visibility: {vis}')

        # Delete existing preview first
        await page.evaluate('''() => {
            const v = window.__viewer;
            if (v && v.removeClothRegion) v.removeClothRegion('pe_preview');
        }''')
        await asyncio.sleep(0.3)

        # Set Top preset
        await page.evaluate('''() => {
            const cat = document.getElementById('pe-region-category');
            if (cat) { cat.value = 'top'; cat.dispatchEvent(new Event('change')); }
        }''')
        await asyncio.sleep(0.5)

        # Force regeneration by clicking Generate button
        await page.evaluate('''() => {
            const btn = document.getElementById('pe-generate');
            if (btn) btn.click();
        }''')
        print('Triggered generation, waiting...')

        # Wait for generation to complete
        await asyncio.sleep(8)

        # Check what body query string is being sent
        bqs = await page.evaluate('window.__viewer._buildBodyQueryString()')
        # Count morph params
        import urllib.parse
        params = urllib.parse.parse_qs(bqs)
        morph_count = sum(1 for k in params if k.startswith('morph_'))
        meta_count = sum(1 for k in params if k.startswith('meta_'))
        nonzero_morphs = sum(1 for k, v in params.items()
                            if k.startswith('morph_') and float(v[0]) != 0.0)
        body_type = params.get('body_type', ['?'])[0]
        print(f'Body: {body_type}, {morph_count} morphs ({nonzero_morphs} nonzero), {meta_count} meta')

        status = await page.evaluate(
            'document.getElementById("pe-save-status") ? document.getElementById("pe-save-status").textContent : "no status el"'
        )
        print(f'Status: {status}')

        # Check if cloth mesh was created
        has_cloth = await page.evaluate('''() => {
            const v = window.__viewer;
            if (!v) return 'no viewer';
            const keys = Object.keys(v.clothMeshes || {});
            return keys.length > 0 ? 'clothMeshes: ' + keys.join(', ') : 'no cloth meshes';
        }''')
        print(f'Cloth: {has_cloth}')

        # Rotate camera to side view
        await page.evaluate('''() => {
            const v = window.__viewer;
            if (v && v.controls && v.camera) {
                v.camera.position.set(2.5, 1.0, 0);
                v.controls.target.set(0, 0.9, 0);
                v.controls.update();
            }
        }''')
        await asyncio.sleep(0.5)

        # Take side view screenshot
        await page.screenshot(path='A:/HumanBodyTest/HumanBodyWeb/test_screenshots/region_test_side.png')
        print('Side screenshot saved')

        # Test Pants preset
        await page.evaluate('''() => {
            const v = window.__viewer;
            if (v && v.removeClothRegion) v.removeClothRegion('pe_preview');
            const cat = document.getElementById('pe-region-category');
            if (cat) { cat.value = 'pants'; cat.dispatchEvent(new Event('change')); }
        }''')
        await asyncio.sleep(0.5)
        await page.evaluate('document.getElementById("pe-generate").click()')
        await asyncio.sleep(8)

        # Front view for pants
        await page.evaluate('''() => {
            const v = window.__viewer;
            if (v && v.controls && v.camera) {
                v.camera.position.set(0, 0.6, 2.5);
                v.controls.target.set(0, 0.5, 0);
                v.controls.update();
            }
        }''')
        await asyncio.sleep(0.3)
        pants_status = await page.evaluate('document.getElementById("pe-save-status").textContent')
        print(f'Pants: {pants_status}')
        await page.screenshot(path='A:/HumanBodyTest/HumanBodyWeb/test_screenshots/region_test_pants.png')
        print('Pants screenshot saved')


asyncio.run(main())
