"""
Test Theatre Rig und Animation
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        # Open console to see errors (handle Unicode properly)
        def handle_console(msg):
            try:
                text = msg.text.encode('ascii', 'replace').decode('ascii')
                print(f'CONSOLE: {text}')
            except Exception as e:
                print(f'CONSOLE: [encoding error: {e}]')

        page.on('console', handle_console)
        page.on('pageerror', lambda err: print(f'PAGE ERROR: {err}'))

        print("=== Loading Theatre ===")
        await page.goto('http://localhost:8081/humanbody/theatre/')
        await page.wait_for_selector('#theatre-canvas', timeout=10000)
        await asyncio.sleep(3)

        # Check if skeleton data loaded
        skel_loaded = await page.evaluate('() => window.defSkeletonData !== null && window.defSkeletonData !== undefined')
        print(f"Skeleton data loaded: {skel_loaded}")

        if skel_loaded:
            bone_count = await page.evaluate('() => window.defSkeletonData?.bones?.length || 0')
            print(f"Bone count: {bone_count}")

        print("\n=== Loading Model (FemaleWithHair) ===")
        await page.click('[data-tab="tab-models"]')
        await asyncio.sleep(1)

        # Click FemaleWithHair
        await page.evaluate("""
            () => {
                const items = Array.from(document.querySelectorAll('.anim-item'));
                const item = items.find(i => i.textContent.includes('FemaleWithHair'));
                if (item) item.click();
            }
        """)
        await asyncio.sleep(4)

        # Check if character was converted to SkinnedMesh
        char_state = await page.evaluate("""
            () => {
                if (!window.loadedCharacters || window.loadedCharacters.length === 0) {
                    return { loaded: false };
                }
                const char = window.loadedCharacters[0];
                return {
                    loaded: true,
                    isSkinnedMesh: char.userData.isSkinnedMesh || false,
                    hasSkeletonHelper: !!char.userData.skeletonHelper,
                    presetName: char.userData.presetName
                };
            }
        """)
        print(f"Character state: {char_state}")

        # Check scene for SkeletonHelper
        scene_state = await page.evaluate("""
            () => {
                let skeletonHelpers = [];
                window.scene.traverse(obj => {
                    if (obj.isSkeletonHelper || obj.userData?.isRig) {
                        skeletonHelpers.push({
                            type: obj.type,
                            visible: obj.visible,
                            isRig: obj.userData?.isRig,
                            isSkeletonHelper: obj.isSkeletonHelper
                        });
                    }
                });
                return { skeletonHelpers };
            }
        """)
        print(f"Scene skeleton helpers: {scene_state}")

        print("\n=== Clicking Rig Toggle Button ===")
        await page.click('#btn-toggle-rig')
        await asyncio.sleep(1)

        # Check if rig is now visible
        rig_visible = await page.evaluate("""
            () => {
                let visible = [];
                window.scene.traverse(obj => {
                    if (obj.isSkeletonHelper || obj.userData?.isRig) {
                        visible.push({ type: obj.type, visible: obj.visible });
                    }
                });
                return visible;
            }
        """)
        print(f"Rig visibility after toggle: {rig_visible}")

        await page.screenshot(path='test_theatre_rig.png', full_page=True)
        print("\nScreenshot: test_theatre_rig.png")

        print("\n=== Loading Animation ===")
        await page.click('[data-tab="tab-animations"]')
        await asyncio.sleep(1)

        # Expand first category
        await page.evaluate("() => document.querySelector('.anim-cat-header')?.click()")
        await asyncio.sleep(0.5)

        # Click first animation
        await page.evaluate("() => document.querySelector('.anim-cat-body .anim-item')?.click()")
        await asyncio.sleep(3)

        # Check animation state
        anim_state = await page.evaluate("""
            () => ({
                hasActiveMixer: !!window.activeMixer,
                animDuration: window.animDuration,
                isPlaying: window.isPlaying
            })
        """)
        print(f"Animation state (before play): {anim_state}")

        # Click play button (timeline play/pause button)
        print("\n=== Clicking Play Button ===")
        await page.click('#btnPlayPause')
        await asyncio.sleep(2)

        # Check if animation is now playing
        anim_state_after = await page.evaluate("""
            () => ({
                hasActiveMixer: !!window.activeMixer,
                animDuration: window.animDuration,
                isPlaying: window.isPlaying,
                currentTime: window.currentAnimTime || 0
            })
        """)
        print(f"Animation state (after play): {anim_state_after}")

        await page.screenshot(path='test_theatre_anim.png', full_page=True)
        print("Screenshot: test_theatre_anim.png")

        print("\nBrowser stays open for 20 seconds...")
        await asyncio.sleep(20)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
