import * as THREE from 'three';
// BVHLoader only needed for non-skinned fallback (asset-loader.js has its own)
import studio from '@theatre/studio';
import { createScene } from './scene-setup.js';
import { setupTheatre, createCameraSheet, createLightSheet, getAllTheatreObjects } from './theatre-bridge.js';
import { loadGLBFromFile, loadCharacterFromPreset, loadBVHFromText } from './asset-loader.js';
import { VideoExporter } from './video-export.js';
import {
    fetchSceneList, fetchScene, saveScene,
    fetchModelList, fetchModel,
    fetchAnimationList, fetchBVH,
} from './scene-manager.js';
import { PRESETS, applyPreset } from './presets.js';
import { fetchRetargetedClip, fetchRetargetedClipFromText, detectBVHFormat } from './retarget_hybrid.js';
import { buildRigifySkeleton } from './rigify_skeleton_builder.js';
import { KeyframeUI } from './keyframe-ui.js';

// Theatre.js ignores the getProject({ state }) param if localStorage exists.
// Clear stale localStorage so our state.json (with correct sequence length) takes effect.
// Force-clear if the stored state has an outdated sequence length (e.g. 300).
try {
    const stored = localStorage.getItem('theatre-0.4.persistent');
    if (stored) {
        const hasUserKeyframes = stored.includes('"keyframes":[{');
        if (!hasUserKeyframes) {
            localStorage.removeItem('theatre-0.4.persistent');
            console.log('[Theatre Studio] Cleared stale localStorage (no user keyframes)');
        }
    }
} catch (_) { /* ignore */ }

// Theatre Studio MUST be initialized at module level (before DOMContentLoaded)
studio.initialize().then(() => {
    console.log('[Theatre Studio] initialized successfully');
    // Force Studio visible (it remembers hide state in localStorage)
    studio.ui.restore();
    // Wait for render() setTimeout to create DOM element
    setTimeout(() => {
        const root = document.getElementById('theatrejs-studio-root');
        if (root) {
            root.style.setProperty('z-index', '900', 'important');

            // Fix: position:fixed so context menus are positioned correctly
            root.style.setProperty('position', 'fixed', 'important');
            root.style.setProperty('top', '0', 'important');
            root.style.setProperty('left', '0', 'important');
            root.style.setProperty('width', '100vw', 'important');
            root.style.setProperty('height', '100vh', 'important');
            root.style.setProperty('pointer-events', 'none', 'important');

            if (root.shadowRoot) {
                const sr = root.shadowRoot;
                const style = document.createElement('style');
                style.textContent = `
                    :host { font-size: 13px !important; }
                    svg { transform: scale(1.3); }
                    [data-testid] { min-height: 28px; }

                    /* Re-enable pointer events only on the Sequence Editor (bottom timeline) */
                    [data-testid="SequenceEditor"],
                    [data-testid="GlobalToolbar"] {
                        pointer-events: auto !important;
                    }

                    /* Outline panel: shift right to clear sidebar */
                    div[class] > div[class]:nth-child(3) {
                        left: 220px !important;
                        pointer-events: auto !important;
                    }
                    /* Detail panel (properties): shift left to clear right panel */
                    div[class] > div[class]:nth-child(4) {
                        pointer-events: auto !important;
                    }

                    /* Context menus + popovers must be clickable */
                    [data-radix-popper-content-wrapper],
                    [data-radix-menu-content],
                    [role="menu"],
                    [role="dialog"] {
                        pointer-events: auto !important;
                        z-index: 99999 !important;
                    }
                `;
                sr.prepend(style);
            }
            console.log('[Theatre Studio] UI visible, position:fixed, context menu fix active');
        }
    }, 100);
}).catch(err => {
    console.error('[Theatre Studio] initialize() FAILED:', err);
});
window.studio = studio;

// Wait for DOM before initialising
window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('theatre-canvas');
    if (!canvas) {
        console.error('theatre-canvas not found');
        return;
    }

    // 2. Three.js scene (ballet stage)
    const { scene, camera, renderer, controls, lights, lightIcons, transformControls } = createScene(canvas);

    // DEBUG: Expose for console debugging
    window.scene = scene;
    window.camera = camera;
    window.lights = lights;
    window.lightIcons = lightIcons;
    window.transformControls = transformControls;

    // Expose animation variables for debugging (will be set later)
    window.activeMixer = null;
    window.isPlaying = false;
    window.currentTime = 0;
    window.animDuration = 1;


    // ── Raycaster für Licht-Icon Clicks + Character Selection ──
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let selectedLightIcon = null;
    let selectedCharacter = null;  // Currently selected character group
    const loadedCharacters = [];   // Track all loaded character groups
    let reloadDebounceTimer = null; // Debounce for character reload

    // Skeleton and skin weights data (loaded once at startup)
    let rigifySkeletonData = null;
    let skinWeightData = null;
    let skeletonLoadingPromise = null;
    let rigifySkeleton = null;  // { skeleton, rootBone, bones, boneByName } - like Dashboard
    let skeletonHelper = null;  // Single global SkeletonHelper - like Dashboard
    let rigVisible = false;  // Rig visibility state - like Dashboard

    // Load skeleton and skin weights data
    async function loadSkeletonAndWeights() {
        if (skeletonLoadingPromise) return skeletonLoadingPromise;

        skeletonLoadingPromise = (async () => {
            try {
                const [skelResp, weightsResp] = await Promise.all([
                    fetch('/api/character/rigify-skeleton/'),
                    fetch('/api/character/skin-weights/')
                ]);
                if (skelResp.ok) rigifySkeletonData = await skelResp.json();
                if (weightsResp.ok) skinWeightData = await weightsResp.json();
                console.log('✓ Loaded skeleton and skin weights:', rigifySkeletonData?.bones?.length || 0, 'bones');

                // Build rigifySkeleton object using Dashboard's buildRigifySkeleton function
                if (rigifySkeletonData && skinWeightData) {
                    rigifySkeleton = buildRigifySkeleton(rigifySkeletonData, skinWeightData);
                    console.log('✓ Built rigifySkeleton:', rigifySkeleton.bones.length, 'bones');

                    // Make rigifySkeletonData available globally for test
                    window.rigifySkeletonData = rigifySkeletonData;
                    window.rigifySkeleton = rigifySkeleton;
                }

                // Auto-convert any characters that were loaded before skeleton was ready
                for (const char of loadedCharacters) {
                    if (!char.userData.isSkinnedMesh) {
                        autoConvertToSkinnedMesh(char);
                    }
                }
            } catch (err) {
                console.warn('Failed to load skeleton/weights:', err);
            }
        })();

        return skeletonLoadingPromise;
    }

    // Load at startup
    loadSkeletonAndWeights();

    /**
     * Helper: Auto-convert character to SkinnedMesh if skeleton data is loaded.
     * Creates SkeletonHelper for visualization.
     */
    function autoConvertToSkinnedMesh(characterGroup) {
        // Only convert if skeleton data is ready
        if (rigifySkeletonData && skinWeightData && !characterGroup.userData.isSkinnedMesh) {
            setTimeout(() => {
                try {
                    convertCharacterToSkinnedMesh(characterGroup, scene);
                    console.log('✓ Auto-converted to SkinnedMesh:', characterGroup.userData.presetName);
                } catch (err) {
                    console.warn('Auto-convert failed:', err);
                }
            }, 100); // Small delay to ensure character is fully added to scene
        }
    }

    /**
     * Load BVH animation on a SkinnedMesh via server-side retarget API.
     */
    async function loadBVHOnSkinnedMesh(bvhText, skinnedMesh, scene, animName) {
        if (!rigifySkeleton || !rigifySkeleton.boneByName) {
            throw new Error('Skeleton not ready');
        }

        let bodyH = 1.68;
        if (skinnedMesh) {
            const bb = new THREE.Box3().setFromObject(skinnedMesh);
            if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;
        }

        const clip = await fetchRetargetedClipFromText(bvhText, rigifySkeleton, { bodyHeight: bodyH });

        const mixer = new THREE.AnimationMixer(skinnedMesh);
        const action = mixer.clipAction(clip);
        action.setLoop(THREE.LoopRepeat);
        action.play();
        action.paused = true;

        const duration = clip.duration || 1;
        console.log(`✓ Retargeted clip (API): ${clip.tracks.length} tracks, ${duration.toFixed(2)}s`);

        return { mixer, action, duration };
    }

    /**
     * Convert a character mesh to SkinnedMesh with skeleton binding.
     * This enables BVH animations to deform the character mesh (not just bones).
     * Similar to Dashboard-Scene's convertToDefSkinnedMesh().
     */
    /**
     * Convert character to SkinnedMesh using DEF skeleton.
     * COPIED FROM Dashboard-Scene viewer.js convertToDefSkinnedMesh (lines 780-828)
     */
    function convertCharacterToSkinnedMesh(characterGroup, scene) {
        if (!rigifySkeletonData || !skinWeightData) {
            console.warn('Cannot convert to SkinnedMesh: skeleton/weights not loaded');
            return null;
        }

        if (characterGroup.userData.isSkinnedMesh) {
            console.log('Already a SkinnedMesh');
            return characterGroup.userData.skinnedMesh;
        }

        // Find the body mesh (first child)
        const bodyMesh = characterGroup.children.find(c => c.isMesh && !c.userData.isHair && !c.userData.isGarment);
        if (!bodyMesh) {
            console.warn('No body mesh found in character group');
            return null;
        }

        console.log('Converting to SkinnedMesh...');

        // Clone geometry — the original has stale WebGL VAO state from non-skinned rendering
        const geo = bodyMesh.geometry.clone();
        const vCount = geo.attributes.position.count;

        // Build skinIndices and skinWeights buffers (Dashboard format)
        const skinIndices = new Float32Array(vCount * 4);
        const skinWeights = new Float32Array(vCount * 4);

        const swCount = skinWeightData.weights ? skinWeightData.weights.length : 0;
        if (vCount !== swCount) {
            console.error(`[SkinnedMesh] VERTEX COUNT MISMATCH! mesh=${vCount} weights=${swCount}`);
        }

        for (let v = 0; v < vCount; v++) {
            const infs = skinWeightData.weights[v] || [];
            const sorted = infs.slice().sort((a, b) => b[1] - a[1]).slice(0, 4);
            let sum = sorted.reduce((s, e) => s + e[1], 0);
            if (sum < 1e-6) sum = 1;
            for (let i = 0; i < 4; i++) {
                skinIndices[v * 4 + i] = i < sorted.length ? sorted[i][0] : 0;
                skinWeights[v * 4 + i] = i < sorted.length ? sorted[i][1] / sum : 0;
            }
        }

        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));

        // ALWAYS rebuild skeleton fresh (like Dashboard's convertToDefSkinnedMesh).
        // Reusing a skeleton whose bones were animated causes stale world matrices
        // and boneInverses that don't match the current bind context.
        rigifySkeleton = buildRigifySkeleton(rigifySkeletonData, skinWeightData);

        console.log(`[SkinnedMesh] verts=${vCount} weights=${swCount} bones=${rigifySkeleton.bones.length}`);

        // Create SkinnedMesh
        const material = bodyMesh.material; // Reuse existing material (array of materials)
        const pos = bodyMesh.position.clone();
        const rot = bodyMesh.rotation.clone();
        const scale = bodyMesh.scale.clone();

        const skinnedMesh = new THREE.SkinnedMesh(geo, material);
        skinnedMesh.position.copy(pos);
        skinnedMesh.rotation.copy(rot);
        skinnedMesh.scale.copy(scale);
        skinnedMesh.castShadow = true;
        skinnedMesh.receiveShadow = true;

        // Add root bone and bind skeleton
        skinnedMesh.add(rigifySkeleton.rootBone);
        skinnedMesh.bind(rigifySkeleton.skeleton);

        // Replace old mesh in character group
        characterGroup.remove(bodyMesh);
        characterGroup.add(skinnedMesh);

        // Store references
        characterGroup.userData.isSkinnedMesh = true;
        characterGroup.userData.skinnedMesh = skinnedMesh;
        characterGroup.userData.skeleton = rigifySkeleton.skeleton;
        characterGroup.userData.rootBone = rigifySkeleton.rootBone;

        // Recreate SkeletonHelper if it existed (rootBone changed)
        if (skeletonHelper) {
            const wasVisible = skeletonHelper.visible;
            scene.remove(skeletonHelper);
            skeletonHelper.dispose();
            skeletonHelper = new THREE.SkeletonHelper(rigifySkeleton.rootBone);
            skeletonHelper.material.depthTest = false;
            skeletonHelper.material.depthWrite = false;
            skeletonHelper.material.color.set(0x00ffaa);
            skeletonHelper.material.linewidth = 2;
            skeletonHelper.renderOrder = 999;
            scene.add(skeletonHelper);
            skeletonHelper.visible = wasVisible;
            console.log('✓ SkeletonHelper recreated for new skeleton');
        }

        console.log('✓ SkinnedMesh created:',
            'bones:', rigifySkeleton.skeleton.bones.length,
            'skinIndex:', !!geo.attributes.skinIndex,
            'skinWeight:', !!geo.attributes.skinWeight);

        // Make skinnedMesh globally accessible for animation
        window.loadedCharacters = window.loadedCharacters || [];
        if (!window.loadedCharacters.includes(characterGroup)) {
            window.loadedCharacters.push(characterGroup);
        }

        // Bind garments to skeleton (like Result page result_character.js:1319)
        // Do NOT add rootBone to garment — rootBone must stay in bodyMesh.
        // Garments share the same Skeleton object and use bodyMesh's bindMatrix.
        characterGroup.traverse((child) => {
            if (child.isSkinnedMesh && child !== skinnedMesh && child.userData.needsBinding) {
                child.bind(rigifySkeleton.skeleton, skinnedMesh.bindMatrix);
                delete child.userData.needsBinding;
                console.log('✓ Garment bound to skeleton:', child.name || child.userData.garmentId);
            }
        });

        // Convert hair to SkinnedMesh (like Dashboard viewer.js _skinifyHairGroup)
        const headBoneIdx = _findHeadBoneIndex();
        if (headBoneIdx >= 0) {
            const hairChildren = characterGroup.children.filter(c => c.userData.isHair);
            for (const hairGroup of hairChildren) {
                // Skip if already skinned
                let hasRegularMesh = false;
                hairGroup.traverse((child) => {
                    if (child.isMesh && !child.isSkinnedMesh) {
                        hasRegularMesh = true;
                    }
                });

                if (hasRegularMesh) {
                    const skinnedHairGroup = _skinifyHairGroup(hairGroup, headBoneIdx, skinnedMesh);
                    // Replace original hair group with skinned version
                    characterGroup.remove(hairGroup);
                    characterGroup.add(skinnedHairGroup);
                    console.log('✓ Hair converted to SkinnedMesh:', hairGroup.name || 'hair');
                }
            }
        }

        return skinnedMesh;
    }

    /**
     * Find head bone index for hair skinning (Dashboard viewer.js _findHeadBoneIndex)
     */
    function _findHeadBoneIndex() {
        if (!skinWeightData) return -1;
        const names = skinWeightData.bone_names;
        for (const tryName of ['DEF-spine.006', 'DEF-spine.005', 'DEF-head']) {
            const idx = names.indexOf(tryName);
            if (idx >= 0) return idx;
        }
        return -1;
    }

    /**
     * Convert hair meshes to SkinnedMesh bound to head bone.
     * COPIED FROM Dashboard viewer.js _skinifyHairGroup (lines 1941-1969)
     */
    function _skinifyHairGroup(gltfScene, headBoneIdx, bodyMesh) {
        // Collect all meshes from the GLB scene
        const meshChildren = [];
        gltfScene.traverse(child => {
            if (child.isMesh) meshChildren.push(child);
        });

        const group = new THREE.Group();
        group.userData.isHair = true;

        for (const child of meshChildren) {
            const geo = child.geometry.clone();
            const vCount = geo.attributes.position.count;
            const si = new Float32Array(vCount * 4);
            const sw = new Float32Array(vCount * 4);
            for (let v = 0; v < vCount; v++) {
                si[v * 4] = headBoneIdx;
                sw[v * 4] = 1.0;
            }
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(si, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));

            const skinnedChild = new THREE.SkinnedMesh(geo, child.material);
            // Apply the child's world transform so position is correct
            child.updateWorldMatrix(true, false);
            skinnedChild.applyMatrix4(child.matrixWorld);
            skinnedChild.bind(rigifySkeleton.skeleton, bodyMesh.bindMatrix);
            skinnedChild.userData.isHair = true;
            group.add(skinnedChild);
        }
        return group;
    }

    canvas.addEventListener('click', (event) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);

        // Try light icons first (higher priority)
        const clickableObjects = [
            lightIcons.spotLeftIcon,
            lightIcons.spotRightIcon,
            lightIcons.backLightIcon
        ];
        const lightIntersects = raycaster.intersectObjects(clickableObjects, true);

        if (lightIntersects.length > 0) {
            // Light icon clicked
            let clickedIcon = lightIntersects[0].object;
            while (clickedIcon.parent && !clickedIcon.userData.light) {
                clickedIcon = clickedIcon.parent;
            }

            if (clickedIcon.userData.light) {
                selectedLightIcon = clickedIcon;
                selectedCharacter = null;
                transformControls.attach(clickedIcon);
                console.log('✓ Licht ausgewählt:', clickedIcon.userData.light);
                showLightPanel(clickedIcon.userData.light);
                return;
            }
        }

        // Try character meshes (all loaded characters)
        // Filter out SkinnedMeshes without bound skeleton (causes bones error)
        let charIntersects;
        try {
            charIntersects = raycaster.intersectObjects(loadedCharacters, true);
        } catch (e) {
            return; // SkinnedMesh without skeleton, skip
        }
        if (charIntersects.length > 0) {
            const clickedMesh = charIntersects[0].object;

            // Check if it's a garment (higher priority than character)
            if (clickedMesh.userData.isGarment) {
                selectedCharacter = null;
                selectedLightIcon = null;
                transformControls.attach(clickedMesh);
                console.log('✓ Garment ausgewählt:', clickedMesh.name);
                showGarmentPanel(clickedMesh);
                return;
            }

            // Otherwise find the character group (walk up the hierarchy)
            let clickedChar = clickedMesh;
            while (clickedChar.parent && !clickedChar.userData.isCharacter) {
                clickedChar = clickedChar.parent;
            }

            if (clickedChar.userData.isCharacter) {
                selectedCharacter = clickedChar;
                selectedLightIcon = null;
                transformControls.attach(clickedChar);
                console.log('✓ Character ausgewählt:', clickedChar.userData.presetName);
                showCharacterPanel(clickedChar);
                return;
            }
        }

        // Nothing clicked - deselect
        transformControls.detach();
        selectedLightIcon = null;
        selectedCharacter = null;
        hideLightPanel();
    });

    // 3. Theatre project + sheet
    const { project, sheet } = setupTheatre();

    // Expose to window for Studio UI
    window.theatreProject = project;
    window.theatreSheet = sheet;

    // 4. Register camera & spotlights as animatable Theatre objects
    const cameraObj = createCameraSheet(sheet, camera);
    createLightSheet(sheet, 'Spot Left', lights.spotLeft);
    createLightSheet(sheet, 'Spot Right', lights.spotRight);
    createLightSheet(sheet, 'Back Light', lights.backLight);

    // Sync OrbitControls camera position back to Theatre.js
    // so the Detail Panel shows the actual camera position.
    controls.addEventListener('change', () => {
        if (window.isPlaying) return; // sequence drives camera during playback
        studio.transaction(({ set }) => {
            set(cameraObj.props.position.x, camera.position.x);
            set(cameraObj.props.position.y, camera.position.y);
            set(cameraObj.props.position.z, camera.position.z);
        });
    });

    // 5. Initialize Keyframe UI for Camera/Light animation
    const theatreObjects = getAllTheatreObjects();
    window.theatreObjects = theatreObjects; // Expose for Playwright tests & debugging
    const keyframeUI = new KeyframeUI(project, sheet, theatreObjects);
    window.keyframeUI = keyframeUI; // Expose for debugging

    // Open the Sequence Editor panel by selecting the sheet.
    // Tracks are pre-defined in theatre-state.json (Camera + 3 Lights).
    project.ready.then(() => {
        studio.setSelection([sheet]);
    });

    // 6. Video exporter
    const exporter = new VideoExporter(renderer.domElement);

    // 6. Track active mixers for BVH animation playback
    let activeMixer = null; // Only one animation at a time
    let currentAction = null;
    const clock = new THREE.Clock();

    // ── Menubar Dropdown (Click to open/close) ──
    document.querySelectorAll('.menu-item').forEach((menuItem) => {
        const dropdown = menuItem.querySelector('.menu-dropdown');
        if (!dropdown) return; // Skip menu items without dropdown (like Hilfe)

        menuItem.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close all other dropdowns
            document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
            // Toggle this dropdown
            menuItem.classList.toggle('active');
        });

        // Prevent dropdown from closing when clicking inside it
        dropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
        document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
    });

    // ── Settings (Presets) - IMPORTANT: Must be after dropdown setup! ──
    document.querySelectorAll('[data-preset]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const presetName = btn.getAttribute('data-preset');
            const preset = PRESETS[presetName];
            if (preset) {
                applyPreset(preset, camera, lights, controls);
                console.log('✓ Applied preset:', preset.name);
                // Close dropdown after selecting
                document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
            } else {
                console.error('Preset not found:', presetName);
            }
        });
    });

    // ── Tab Switching ──
    document.querySelectorAll('.panel-tab').forEach((tab) => {
        tab.addEventListener('click', () => {
            const targetId = tab.getAttribute('data-tab');
            document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            tab.classList.add('active');
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add('active');
        });
    });

    // ── Toolbar Buttons ──
    const btnTranslate = document.getElementById('btn-translate-mode');
    const btnRotate = document.getElementById('btn-rotate-mode');
    const btnToggleLights = document.getElementById('btn-toggle-lights');

    // Translate/Rotate mode switcher
    if (btnTranslate) {
        btnTranslate.addEventListener('click', () => {
            transformControls.setMode('translate');
            btnTranslate.classList.add('active');
            btnRotate.classList.remove('active');
        });
    }

    if (btnRotate) {
        btnRotate.addEventListener('click', () => {
            transformControls.setMode('rotate');
            btnRotate.classList.add('active');
            btnTranslate.classList.remove('active');
        });
    }

    // Toggle lights visibility
    let lightsVisible = true;
    if (btnToggleLights) {
        btnToggleLights.addEventListener('click', () => {
            lightsVisible = !lightsVisible;

            // Toggle all light icons
            Object.values(lightIcons).forEach(icon => {
                icon.visible = lightsVisible;
            });

            // Toggle button state
            if (lightsVisible) {
                btnToggleLights.classList.add('active');
            } else {
                btnToggleLights.classList.remove('active');
            }
        });
    }

    // Toggle model visibility (body mesh)
    const btnToggleModel = document.getElementById('btn-toggle-model');
    let modelVisible = true;
    if (btnToggleModel) {
        btnToggleModel.addEventListener('click', () => {
            modelVisible = !modelVisible;

            scene.traverse((obj) => {
                // Hide meshes that are part of character body (not garments, not lights)
                if (obj.isMesh && !obj.userData.isGarment && !obj.userData.isHair && !obj.userData.isRig) {
                    obj.visible = modelVisible;
                }
            });

            btnToggleModel.classList.toggle('active', modelVisible);
        });
    }

    // Toggle clothes/garments visibility
    const btnToggleClothes = document.getElementById('btn-toggle-clothes');
    let clothesVisible = true;
    if (btnToggleClothes) {
        btnToggleClothes.addEventListener('click', () => {
            clothesVisible = !clothesVisible;

            scene.traverse((obj) => {
                if (obj.isMesh && (obj.userData.isGarment || obj.userData.isHair)) {
                    obj.visible = clothesVisible;
                }
            });

            btnToggleClothes.classList.toggle('active', clothesVisible);
        });
    }

    // Toggle rig visibility (skeleton) - EXACTLY like Dashboard-Scene
    const btnToggleRig = document.getElementById('btn-toggle-rig');
    if (btnToggleRig) {
        btnToggleRig.addEventListener('click', () => {
            rigVisible = !rigVisible;
            if (rigVisible) {
                // Create helper if needed (from DEF skeleton when available)
                if (!skeletonHelper && rigifySkeleton) {
                    skeletonHelper = new THREE.SkeletonHelper(rigifySkeleton.rootBone);
                    skeletonHelper.material.depthTest = false;
                    skeletonHelper.material.depthWrite = false;
                    skeletonHelper.material.color.set(0x00ffaa);
                    skeletonHelper.material.linewidth = 2;
                    skeletonHelper.renderOrder = 999;
                    scene.add(skeletonHelper);
                    console.log('✓ SkeletonHelper created');
                }
                if (skeletonHelper) skeletonHelper.visible = true;
            } else {
                if (skeletonHelper) skeletonHelper.visible = false;
            }
            btnToggleRig.classList.toggle('active', rigVisible);
        });
    }

    // ── Kamera menu ──
    function setCameraKeyframe(time) {
        const seq = sheet.sequence;
        seq.position = time;
        studio.transaction(({ set }) => {
            set(cameraObj.props.position.x, camera.position.x);
            set(cameraObj.props.position.y, camera.position.y);
            set(cameraObj.props.position.z, camera.position.z);
            set(cameraObj.props.fov, camera.fov);
        });
        console.log(`✓ Camera keyframe at ${time.toFixed(2)}s:`,
            `pos(${camera.position.x.toFixed(2)}, ${camera.position.y.toFixed(2)}, ${camera.position.z.toFixed(2)})`,
            `fov=${camera.fov.toFixed(1)}`);
    }

    const menuCamSet = document.getElementById('menu-cam-set');
    if (menuCamSet) {
        menuCamSet.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
            // Set keyframe at current playhead position
            const time = sheet.sequence.position;
            setCameraKeyframe(time);
        });
    }

    // Delete camera keyframe at current playhead position
    const menuCamDeleteAt = document.getElementById('menu-cam-delete-at');
    if (menuCamDeleteAt) {
        menuCamDeleteAt.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
            const time = sheet.sequence.position;

            // Read Theatre.js state from localStorage, find and remove keyframes near playhead
            const stateKey = Object.keys(localStorage).find(k =>
                k.includes('theatre') || k.includes('Theatre'));
            if (!stateKey) { console.warn('No Theatre state in localStorage'); return; }

            try {
                const state = JSON.parse(localStorage.getItem(stateKey));
                const camTracks = state?.sheetsById?.Main?.sequence?.tracksByObject?.Camera?.trackData;
                if (!camTracks) { console.warn('No camera tracks found'); return; }

                let removed = 0;
                const tolerance = 0.05; // 50ms tolerance
                for (const [trackId, track] of Object.entries(camTracks)) {
                    if (!track.keyframes) continue;
                    const before = track.keyframes.length;
                    track.keyframes = track.keyframes.filter(kf =>
                        Math.abs(kf.position - time) > tolerance
                    );
                    removed += before - track.keyframes.length;
                }

                if (removed > 0) {
                    localStorage.setItem(stateKey, JSON.stringify(state));
                    console.log(`✓ Deleted ${removed} camera keyframe(s) at ${time.toFixed(2)}s — reloading`);
                    window.location.reload();
                } else {
                    console.log(`No camera keyframes found at ${time.toFixed(2)}s`);
                }
            } catch(err) {
                console.error('Failed to delete keyframe:', err);
            }
        });
    }

    const menuCamClear = document.getElementById('menu-cam-clear');
    if (menuCamClear) {
        menuCamClear.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));

            const stateKey = Object.keys(localStorage).find(k =>
                k.includes('theatre') || k.includes('Theatre'));
            if (!stateKey) return;

            try {
                const state = JSON.parse(localStorage.getItem(stateKey));
                const camTracks = state?.sheetsById?.Main?.sequence?.tracksByObject?.Camera?.trackData;
                if (camTracks) {
                    for (const track of Object.values(camTracks)) {
                        if (track.keyframes) track.keyframes = [];
                    }
                    localStorage.setItem(stateKey, JSON.stringify(state));
                    console.log('✓ All camera keyframes cleared — reloading');
                    window.location.reload();
                }
            } catch(err) {
                console.error('Failed to clear camera keyframes:', err);
            }
        });
    }

    // Play/pause animation (delegates to main play button)
    const btnPlayAnimation = document.getElementById('btn-play-animation');
    if (btnPlayAnimation) {
        btnPlayAnimation.addEventListener('click', () => {
            // Trigger the main play/pause button
            const mainPlayBtn = document.getElementById('btnPlayPause');
            if (mainPlayBtn) {
                mainPlayBtn.click();
            }
        });
    }

    // Toggle Theatre.js Studio panel
    const btnToggleStudio = document.getElementById('btn-toggle-studio');
    let studioVisible = true;
    if (btnToggleStudio) {
        btnToggleStudio.addEventListener('click', () => {
            studioVisible = !studioVisible;
            if (studioVisible) {
                studio.ui.restore();
            } else {
                studio.ui.hide();
            }
            btnToggleStudio.classList.toggle('active', studioVisible);
        });
    }

    // ── Tools menu handlers ──
    // Expose as global function so it can be called from menu AND from console
    window.rebuildTimeline = function() {
        const seq = sheet.sequence;
        const objs = window.theatreObjects || {};

        // Set sequence length
        try {
            studio.transaction(({ set }) => { set(seq.pointer.length, 10); });
        } catch(e) { console.warn('Set length failed:', e); }

        // Move playhead to 0, write all current values as keyframes
        seq.position = 0;
        const objEntries = Object.entries(objs);
        for (const [name, obj] of objEntries) {
            const vals = obj.value;
            if (!vals) continue;
            try {
                studio.transaction(({ set }) => {
                    for (const [key, val] of Object.entries(vals)) {
                        if (key === 'color') {
                            set(obj.props[key], val);
                        } else if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
                            for (const [subKey, subVal] of Object.entries(val)) {
                                set(obj.props[key][subKey], subVal);
                            }
                        } else {
                            set(obj.props[key], val);
                        }
                    }
                });
                console.log('✓ Timeline:', name, 'OK');
            } catch(e) {
                console.error('✗ Timeline:', name, e.message);
            }
        }

        studio.setSelection([sheet]);
        console.log('✓ Timeline rebuilt:', objEntries.length, 'objects');
    };

    window.clearTimeline = function() {
        for (const key of Object.keys(localStorage)) {
            if (key.includes('theatre') || key.includes('Theatre') || key.includes('HumanBody Theatre')) {
                localStorage.removeItem(key);
            }
        }
        if (window.keyframeUI) window.keyframeUI.keyframes = [];
        window.location.reload();
    };

    // Attach to menu items
    const menuTracksRebuild = document.getElementById('menu-tracks-rebuild');
    if (menuTracksRebuild) {
        menuTracksRebuild.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
            window.rebuildTimeline();
        });
    }

    const menuTracksClear = document.getElementById('menu-tracks-clear');
    if (menuTracksClear) {
        menuTracksClear.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
            window.clearTimeline();
        });
    }

    // ── Modal helpers ──
    function openModal(id) {
        const el = document.getElementById(id);
        if (el) el.style.display = 'flex';
    }

    function closeModal(id) {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    }

    document.querySelectorAll('[data-close-modal]').forEach((btn) => {
        btn.addEventListener('click', () => {
            btn.closest('.theatre-modal-overlay')?.style.removeProperty('display');
        });
    });

    document.querySelectorAll('.theatre-modal-overlay').forEach((overlay) => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.style.removeProperty('display');
        });
    });

    // ── Scene Load ──
    const menuSceneLoad = document.getElementById('menu-scene-load');
    if (menuSceneLoad) {
        menuSceneLoad.addEventListener('click', async () => {
            const body = document.getElementById('scene-list-body');
            body.innerHTML = '<div class="loading-msg">Lade Scenes...</div>';
            openModal('modal-scene-load');

            try {
                const scenes = await fetchSceneList();
                if (scenes.length === 0) {
                    body.innerHTML = '<div class="loading-msg">Keine Scenes gefunden.</div>';
                    return;
                }
                body.innerHTML = '';
                for (const s of scenes) {
                    const item = document.createElement('div');
                    item.style.cssText = 'padding:10px 14px;border-radius:6px;cursor:pointer;color:#ccc;font-size:0.85rem;';
                    item.innerHTML = `<span>${s.label || s.name}</span>`;
                    item.addEventListener('click', () => handleSceneLoad(s.name));
                    item.addEventListener('mouseenter', () => item.style.background = 'rgba(124, 92, 191, 0.2)');
                    item.addEventListener('mouseleave', () => item.style.background = '');
                    body.appendChild(item);
                }
            } catch (err) {
                body.innerHTML = `<div class="loading-msg">Fehler: ${err.message}</div>`;
            }
        });
    }

    async function handleSceneLoad(name) {
        closeModal('modal-scene-load');
        try {
            const sceneData = await fetchScene(name);
            console.log('Scene loaded:', name, sceneData);
            if (sceneData.characters && Array.isArray(sceneData.characters)) {
                for (const charDef of sceneData.characters) {
                    const charGroup = await loadCharacterFromPreset(scene, charDef, charDef.name || name);
                    charGroup.userData.isCharacter = true;
                    charGroup.userData.presetName = charDef.name || name;
                    charGroup.userData.bodyType = charDef.body_type || 'Unknown';
                    loadedCharacters.push(charGroup);
                    selectedCharacter = charGroup;  // Auto-select loaded character
                    autoConvertToSkinnedMesh(charGroup);
                }
            }
        } catch (err) {
            console.error('Scene load error:', err);
            alert('Scene laden fehlgeschlagen: ' + err.message);
        }
    }

    // ── Scene Save ──
    const menuSceneSave = document.getElementById('menu-scene-save');
    const sceneSaveBtn = document.getElementById('scene-save-btn');
    const sceneSaveInput = document.getElementById('scene-save-name');

    if (menuSceneSave) {
        menuSceneSave.addEventListener('click', () => {
            openModal('modal-scene-save');
            if (sceneSaveInput) {
                sceneSaveInput.value = '';
                sceneSaveInput.focus();
            }
        });
    }

    if (sceneSaveBtn && sceneSaveInput) {
        sceneSaveBtn.addEventListener('click', async () => {
            const name = sceneSaveInput.value.trim();
            if (!name) return;

            sceneSaveBtn.disabled = true;
            sceneSaveBtn.textContent = 'Speichere...';

            try {
                const sceneState = {
                    camera: {
                        position: camera.position.toArray(),
                        fov: camera.fov,
                        target: controls.target.toArray(),
                    },
                    lights: {
                        spotLeft: {
                            position: lights.spotLeft.position.toArray(),
                            intensity: lights.spotLeft.intensity,
                            color: '#' + lights.spotLeft.color.getHexString(),
                        },
                        spotRight: {
                            position: lights.spotRight.position.toArray(),
                            intensity: lights.spotRight.intensity,
                            color: '#' + lights.spotRight.color.getHexString(),
                        },
                        backLight: {
                            position: lights.backLight.position.toArray(),
                            intensity: lights.backLight.intensity,
                            color: '#' + lights.backLight.color.getHexString(),
                        },
                    },
                    characters: [],
                };

                const result = await saveScene(name, sceneState);
                console.log('Scene saved:', result);
                closeModal('modal-scene-save');
            } catch (err) {
                console.error('Scene save error:', err);
                alert('Scene speichern fehlgeschlagen: ' + err.message);
            }

            sceneSaveBtn.disabled = false;
            sceneSaveBtn.textContent = 'Speichern';
        });

        sceneSaveInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sceneSaveBtn.click();
        });
    }

    // ── Model Load (from right panel Modelle tab) ──
    const modelListEl = document.getElementById('model-list');
    const menuModelLoad = document.getElementById('menu-model-load');

    async function loadModelListIntoPanel() {
        try {
            const models = await fetchModelList();
            if (models.length === 0) {
                modelListEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Modelle gefunden.</div>';
                return;
            }
            modelListEl.innerHTML = '';
            for (const m of models) {
                const item = document.createElement('div');
                item.className = 'anim-item';
                item.textContent = m.label || m.name;
                item.addEventListener('click', async () => {
                    try {
                        const preset = await fetchModel(m.name);
                        const charGroup = await loadCharacterFromPreset(scene, preset, m.name);
                        charGroup.userData.isCharacter = true;
                        charGroup.userData.presetName = m.name;
                        charGroup.userData.bodyType = preset.body_type || 'Unknown';
                        loadedCharacters.push(charGroup);
                        selectedCharacter = charGroup;  // Auto-select loaded character
                        autoConvertToSkinnedMesh(charGroup);
                        console.log('Model loaded:', m.name);
                        // Highlight active
                        document.querySelectorAll('#model-list .anim-item').forEach(i => i.classList.remove('active'));
                        item.classList.add('active');
                    } catch (err) {
                        console.error('Model load error:', err);
                        alert('Modell laden fehlgeschlagen: ' + err.message);
                    }
                });
                modelListEl.appendChild(item);
            }
        } catch (err) {
            modelListEl.innerHTML = `<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${err.message}</div>`;
        }
    }

    // Auto-load model list into right panel
    loadModelListIntoPanel();

    // Also allow loading via left panel button (opens Modelle tab)
    if (menuModelLoad) {
        menuModelLoad.addEventListener('click', () => {
            // Switch to Modelle tab
            document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            const modelTab = document.querySelector('[data-tab="tab-models"]');
            const modelPane = document.getElementById('tab-models');
            if (modelTab) modelTab.classList.add('active');
            if (modelPane) modelPane.classList.add('active');
        });
    }

    // ── Animation Load (right panel) ──
    const animTreeEl = document.getElementById('anim-tree');

    async function loadAnimationTreeIntoPanel() {
        try {
            const categories = await fetchAnimationList();
            const catNames = Object.keys(categories);
            if (catNames.length === 0) {
                animTreeEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden.</div>';
                return;
            }
            animTreeEl.innerHTML = '';
            for (const catName of catNames) {
                const anims = categories[catName];
                const catDiv = document.createElement('div');
                catDiv.className = 'anim-cat';

                const header = document.createElement('div');
                header.className = 'anim-cat-header';
                header.innerHTML = `<i class="fas fa-chevron-right"></i> ${catName} (${anims.length})`;
                header.addEventListener('click', () => {
                    catDiv.classList.toggle('open');
                });
                catDiv.appendChild(header);

                const body = document.createElement('div');
                body.className = 'anim-cat-body';

                for (const anim of anims) {
                    const item = document.createElement('div');
                    item.className = 'anim-item';
                    item.textContent = anim.name;
                    item.addEventListener('click', async () => {
                        await handleAnimLoad(anim.category, anim.name);
                        // Highlight active
                        document.querySelectorAll('#anim-tree .anim-item').forEach(i => i.classList.remove('active'));
                        item.classList.add('active');
                    });
                    body.appendChild(item);
                }

                catDiv.appendChild(body);
                animTreeEl.appendChild(catDiv);
            }
        } catch (err) {
            animTreeEl.innerHTML = `<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${err.message}</div>`;
        }
    }

    // COPIED FROM Dashboard viewer.js stopAnimation (lines 1432-1466)
    function stopAnimation(destroy = false) {
        if (currentAction) {
            currentAction.stop();
            currentAction.reset();
            if (destroy) currentAction = null;
        }
        if (activeMixer && destroy) {
            activeMixer.stopAllAction();
            activeMixer = null;
        }
        // Reset skinned mesh back to bind pose — EXACTLY like Dashboard
        if (selectedCharacter && selectedCharacter.userData.isSkinnedMesh) {
            const skinnedMesh = selectedCharacter.userData.skinnedMesh;
            if (skinnedMesh && skinnedMesh.isSkinnedMesh) {
                skinnedMesh.skeleton.pose();
            }
        }
        isPlaying = false;
        window.isPlaying = false;
    }

    async function handleAnimLoad(category, name) {
        try {
            // Remember if animation was playing before switch
            const wasPlaying = isPlaying;

            // FIRST: Stop and reset old animation (Dashboard pattern)
            stopAnimation(true);

            let targetMesh = null;
            let duration = 0;

            if (selectedCharacter) {
                // Ensure SkinnedMesh exists (builds skeleton ONCE, binds garments+hair)
                targetMesh = convertCharacterToSkinnedMesh(selectedCharacter, scene);

                if (targetMesh && rigifySkeleton) {
                    // Body height for scaling
                    let bodyH = 1.68;
                    const bb = new THREE.Box3().setFromObject(targetMesh);
                    if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;

                    // Server-side retarget via API (like result_character.js applyBvhRetarget)
                    const clip = await fetchRetargetedClip(category, name, rigifySkeleton, { bodyHeight: bodyH });

                    // Mixer on mesh (like result_character.js:1502-1507)
                    activeMixer = new THREE.AnimationMixer(targetMesh);
                    currentAction = activeMixer.clipAction(clip);
                    currentAction.setLoop(THREE.LoopRepeat);
                    currentAction.play();
                    currentAction.paused = true;
                    duration = clip.duration || 1;

                    // Apply frame 0 immediately
                    activeMixer.setTime(0);
                    targetMesh.updateWorldMatrix(true, true);
                    rigifySkeleton.rootBone.updateWorldMatrix(true, true);

                    console.log(`✓ BVH loaded (API): ${duration.toFixed(1)}s, ${clip.tracks.length} tracks`);
                }
            }

            if (!targetMesh) {
                // Fallback: non-skinned BVH skeleton helper
                const bvhText = await fetchBVH(category, name);
                const { mixer, action, duration: d } = loadBVHFromText(bvhText, scene, `${category}/${name}`);
                activeMixer = mixer;
                currentAction = action;
                duration = d;
            }
            // Expose to window for debugging
            window.activeMixer = activeMixer;

            // Update player UI + Theatre.js sequence length
            updatePlayerDuration(duration);
            currentTime = 0;
            animDuration = duration;

            // Dynamically set Theatre.js sequence length to match BVH duration
            try {
                studio.transaction(({ set }) => {
                    set(sheet.sequence.pointer.length, Math.ceil(duration));
                });
                console.log(`✓ Theatre.js sequence length set to ${Math.ceil(duration)}s`);
            } catch (e) {
                console.warn('Could not set Theatre.js sequence length:', e);
            }

            // Auto-play if previous animation was playing
            if (wasPlaying) {
                isPlaying = true;
                if (currentAction) currentAction.paused = false;
                window.isPlaying = true;
                const btnPlayPause = document.getElementById('btnPlayPause');
                if (btnPlayPause) btnPlayPause.classList.add('playing');
                console.log('✓ Auto-playing new animation');
            } else {
                isPlaying = false;
                window.isPlaying = false;
                const btnPlayPause = document.getElementById('btnPlayPause');
                if (btnPlayPause) btnPlayPause.classList.remove('playing');
            }

            // Expose to window
            window.currentTime = 0;
            window.animDuration = duration;

            updatePlayerUI();

            console.log('Animation loaded:', category, name, duration);
        } catch (err) {
            console.error('Animation load error:', err);
            alert('Animation laden fehlgeschlagen: ' + err.message);
        }
    }

    // Auto-load animation tree
    loadAnimationTreeIntoPanel();

    // ── GLB Import ──
    const menuAddGLB = document.getElementById('menu-add-glb');
    const fileInput = document.getElementById('glb-file-input');
    if (menuAddGLB && fileInput) {
        menuAddGLB.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', async () => {
            const file = fileInput.files[0];
            if (!file) return;
            try {
                await loadGLBFromFile(file, scene);
            } catch (err) {
                console.error('GLB load error:', err);
                alert('Fehler beim Laden der GLB-Datei: ' + err.message);
            }
            fileInput.value = '';
        });
    }

    // ── Settings (Presets) ──
    document.querySelectorAll('[data-preset]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const presetName = btn.getAttribute('data-preset');
            const preset = PRESETS[presetName];
            if (preset) {
                applyPreset(preset, camera, lights, controls);
                console.log('✓ Applied preset:', preset.name);
            } else {
                console.error('Preset not found:', presetName);
            }
        });
    });

    // ── Add Light ──
    const menuAddLight = document.getElementById('menu-add-light');
    let extraLightCount = 0;

    if (menuAddLight) {
        menuAddLight.addEventListener('click', () => {
            extraLightCount++;
            const light = new THREE.PointLight(0xffffff, 1.0, 15);
            light.position.set(
                (Math.random() - 0.5) * 6,
                2 + Math.random() * 3,
                (Math.random() - 0.5) * 6
            );
            scene.add(light);

            const helper = new THREE.Mesh(
                new THREE.SphereGeometry(0.08, 8, 8),
                new THREE.MeshBasicMaterial({ color: 0xffff00 })
            );
            light.add(helper);

            createLightSheet(sheet, `Light ${extraLightCount}`, light);
        });
    }

    // ── Export MP4 ──
    const QUALITY_BITRATES = { low: 2_000_000, medium: 5_000_000, high: 8_000_000, ultra: 15_000_000 };
    const RESOLUTION_MAP = { '720p': [1280, 720], '1080p': [1920, 1080], '1440p': [2560, 1440], '4k': [3840, 2160] };

    const menuExportMp4 = document.getElementById('menu-export-mp4');
    const modalExportMp4 = document.getElementById('modal-export-mp4');
    const exportStartBtn = document.getElementById('export-mp4-start');
    const exportStatus = document.getElementById('export-mp4-status');

    if (menuExportMp4 && modalExportMp4) {
        // Open modal
        menuExportMp4.addEventListener('click', () => {
            // Pre-fill settings from server if available
            const vs = window._theatreVideoSettings || {};
            const resEl = document.getElementById('export-mp4-resolution');
            const fpsEl = document.getElementById('export-mp4-fps');
            const qualEl = document.getElementById('export-mp4-quality');
            const fmtEl = document.getElementById('export-mp4-format');
            if (resEl && vs.resolution) resEl.value = vs.resolution;
            if (fpsEl && vs.fps) fpsEl.value = String(vs.fps);
            if (qualEl && vs.quality) qualEl.value = vs.quality;
            if (fmtEl && vs.format) fmtEl.value = vs.format;

            modalExportMp4.classList.add('open');
            exportStatus.style.display = 'none';

            if (exporter.isRecording) {
                exportStartBtn.innerHTML = '<i class="fas fa-stop" style="color:#e74c3c;"></i> Aufnahme stoppen & exportieren';
            } else {
                exportStartBtn.innerHTML = '<i class="fas fa-circle" style="color:#e74c3c;"></i> Aufnahme starten';
            }
        });

        // Start/Stop recording
        exportStartBtn.addEventListener('click', async () => {
            if (exporter.isRecording) {
                // Stop and export
                exportStartBtn.disabled = true;
                exportStatus.style.display = 'block';
                exportStatus.textContent = 'Aufnahme gestoppt. Verarbeite...';

                const fmt = document.getElementById('export-mp4-format').value;
                const filename = document.getElementById('export-mp4-filename').value || 'theatre-export';
                const ext = fmt === 'webm' ? '.webm' : '.mp4';
                const outName = filename.endsWith(ext) ? filename : filename.replace(/\.\w+$/, '') + ext;

                try {
                    if (fmt === 'mp4') {
                        exportStatus.textContent = 'Konvertiere zu MP4 (ffmpeg)...';
                        await exporter.stopAndUpload('/api/theatre/convert-video/', outName);
                    } else {
                        await exporter.stopAndDownload(outName);
                    }
                    exportStatus.style.background = 'rgba(46,204,113,0.15)';
                    exportStatus.style.color = '#2ecc71';
                    exportStatus.textContent = 'Export erfolgreich: ' + outName;
                } catch (err) {
                    exportStatus.style.background = 'rgba(231,76,60,0.15)';
                    exportStatus.style.color = '#e74c3c';
                    exportStatus.textContent = 'Fehler: ' + err.message;
                }
                exportStartBtn.disabled = false;
                exportStartBtn.innerHTML = '<i class="fas fa-circle" style="color:#e74c3c;"></i> Aufnahme starten';
            } else {
                // Start recording
                const fps = parseInt(document.getElementById('export-mp4-fps').value) || 30;
                const quality = document.getElementById('export-mp4-quality').value || 'high';
                const resolution = document.getElementById('export-mp4-resolution').value || '1080p';
                const bitrate = QUALITY_BITRATES[quality] || 8_000_000;
                const [w, h] = RESOLUTION_MAP[resolution] || [1920, 1080];

                exporter.start({ fps, bitrate, width: w, height: h, renderer, camera });

                exportStatus.style.display = 'block';
                exportStatus.style.background = 'rgba(231,76,60,0.15)';
                exportStatus.style.color = '#e74c3c';
                exportStatus.textContent = `Aufnahme läuft (${resolution}, ${fps}fps)... Spiele die Animation ab und klicke dann "Stoppen".`;
                exportStartBtn.innerHTML = '<i class="fas fa-stop" style="color:#e74c3c;"></i> Aufnahme stoppen & exportieren';

                // Close modal so user can interact with the scene
                modalExportMp4.classList.remove('open');
            }
        });
    }

    // ── Animation Player Controls ──
    const btnPlayPause = document.getElementById('btnPlayPause');
    const btnStop = document.getElementById('btnStop');
    const btnFrameBack = document.getElementById('btnFrameBack');
    const btnFrameFwd = document.getElementById('btnFrameFwd');
    const timelineSlider = document.getElementById('timelineSlider');
    const timeCurrent = document.getElementById('timeCurrent');
    const timeDuration = document.getElementById('timeDuration');
    const playIcon = document.getElementById('playIcon');

    let isPlaying = false;
    let currentTime = 0;
    let animDuration = 1;
    let playbackSpeed = 1.0;

    function updatePlayerDuration(duration) {
        animDuration = duration || 1;
        timeDuration.textContent = formatTime(animDuration);
        timelineSlider.max = animDuration;
    }

    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    function updatePlayerUI() {
        timeCurrent.textContent = formatTime(currentTime);
        timelineSlider.value = currentTime;
        if (playIcon) {
            playIcon.className = isPlaying ? 'fas fa-pause' : 'fas fa-play';
        }
    }

    function setAnimationTime(time) {
        if (!activeMixer || !currentAction) return;
        currentTime = Math.max(0, Math.min(time, animDuration));
        currentAction.time = currentTime;
        activeMixer.update(0); // Force update without advancing time
        updatePlayerUI();
    }

    if (btnPlayPause) {
        btnPlayPause.addEventListener('click', () => {
            isPlaying = !isPlaying;
            window.isPlaying = isPlaying;
            if (isPlaying) {
                // Play BVH animation (if loaded)
                if (activeMixer && currentAction) {
                    currentAction.paused = false;
                    currentAction.play();
                }
                // Play Theatre.js sequence — use animation duration, fallback to 10s
                const seqLen = (animDuration > 1) ? animDuration : 10;
                sheet.sequence.play({ iterationCount: Infinity, rate: playbackSpeed, range: [0, seqLen] });
            } else {
                if (currentAction) currentAction.paused = true;
                sheet.sequence.pause();
            }
            updatePlayerUI();
        });
    }

    if (btnStop) {
        btnStop.addEventListener('click', () => {
            stopAnimation();
            currentTime = 0;
            // Keep animDuration — don't reset to 1!
            // Reset Theatre.js sequence to start
            sheet.sequence.pause();
            sheet.sequence.position = 0;
            isPlaying = false;
            window.isPlaying = false;
            updatePlayerUI();
        });
    }

    if (btnFrameBack) {
        btnFrameBack.addEventListener('click', () => {
            const fps = 30;
            setAnimationTime(currentTime - 1 / fps);
        });
    }

    if (btnFrameFwd) {
        btnFrameFwd.addEventListener('click', () => {
            const fps = 30;
            setAnimationTime(currentTime + 1 / fps);
        });
    }

    if (timelineSlider) {
        let isSliding = false;
        timelineSlider.addEventListener('mousedown', () => { isSliding = true; });
        timelineSlider.addEventListener('mouseup', () => { isSliding = false; });
        timelineSlider.addEventListener('input', () => {
            const time = parseFloat(timelineSlider.value);
            setAnimationTime(time);
            // Sync Theatre.js sequence position
            sheet.sequence.position = time;
        });
    }

    // Speed buttons
    document.querySelectorAll('.speed-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const speed = parseFloat(btn.getAttribute('data-speed'));
            playbackSpeed = speed;
            if (activeMixer) {
                activeMixer.timeScale = speed;
            }
            // Update Theatre.js sequence playback rate if playing
            if (isPlaying) {
                const seqLen = (animDuration > 1) ? animDuration : 10;
                sheet.sequence.play({ iterationCount: Infinity, rate: speed, range: [0, seqLen] });
            }
            document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT') return; // Don't trigger when typing

        if (e.code === 'Space') {
            e.preventDefault();
            if (btnPlayPause) btnPlayPause.click();
        } else if (e.code === 'ArrowLeft') {
            e.preventDefault();
            if (btnFrameBack) btnFrameBack.click();
        } else if (e.code === 'ArrowRight') {
            e.preventDefault();
            if (btnFrameFwd) btnFrameFwd.click();
        }
    });

    // ── Auto-load defaults from settings ──
    async function loadDefaults() {
        try {
            const resp = await fetch('/api/settings/theatre/');
            if (!resp.ok) return;
            const cfg = await resp.json();

            // Store video export settings for exporter
            window._theatreVideoSettings = {
                format: cfg.video_format || 'mp4',
                resolution: cfg.video_resolution || '1080p',
                fps: cfg.video_fps || 30,
                quality: cfg.video_quality || 'high',
            };

            // Apply lighting preset first
            if (cfg.preset) {
                const preset = PRESETS[cfg.preset];
                if (preset) {
                    applyPreset(preset, camera, lights, controls);
                    console.log('✓ Auto-applied preset:', preset.name);
                }
            }

            // Load model
            if (cfg.model) {
                try {
                    const modelData = await fetchModel(cfg.model);
                    const charGroup = await loadCharacterFromPreset(scene, modelData, cfg.model);
                    charGroup.userData.isCharacter = true;
                    charGroup.userData.presetName = cfg.model;
                    charGroup.userData.bodyType = modelData.body_type || 'Unknown';
                    loadedCharacters.push(charGroup);
                    selectedCharacter = charGroup;  // Auto-select loaded character
                    autoConvertToSkinnedMesh(charGroup);
                    console.log('✓ Auto-loaded model:', cfg.model);

                    // Load animation if model loaded successfully
                    if (cfg.animation) {
                        const [category, name] = cfg.animation.split('/');
                        if (category && name) {
                            await handleAnimLoad(category, name);
                            console.log('✓ Auto-loaded animation:', cfg.animation);
                        }
                    }
                } catch (err) {
                    console.warn('Auto-load model/animation failed:', err);
                }
            }
        } catch (err) {
            console.warn('Failed to load Theatre defaults:', err);
        }
    }

    // Load defaults after a short delay
    setTimeout(loadDefaults, 500);

    // ── Light Properties Panel (in Eigenschaften Tab) ──
    function showLightPanel(light) {
        // Switch to Eigenschaften tab
        document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        const propsTab = document.querySelector('[data-tab="tab-properties"]');
        const propsPane = document.getElementById('tab-properties');
        if (propsTab) propsTab.classList.add('active');
        if (propsPane) propsPane.classList.add('active');

        // Fill properties panel
        const content = document.getElementById('properties-content');
        if (!content) return;

        const lightName = light === lights.spotLeft ? 'Spot Left' :
                         light === lights.spotRight ? 'Spot Right' :
                         light === lights.backLight ? 'Back Light' : 'Light';

        const colorHex = '#' + light.color.getHexString();

        content.innerHTML = `
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-lightbulb"></i> ${lightName}
                </h3>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Intensität: <span id="light-intensity-value">${light.intensity.toFixed(1)}</span>
                    </label>
                    <input type="range" id="light-intensity" min="0" max="100" step="1" value="${light.intensity}"
                           style="width:100%;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Farbe
                    </label>
                    <input type="color" id="light-color" value="${colorHex}"
                           style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);background:var(--bg-primary);cursor:pointer;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="light-pos-x" value="${light.position.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-pos-y" value="${light.position.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-pos-z" value="${light.position.z.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Rotation (Grad)
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="light-rot-x" value="${(light.rotation.x * 180 / Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-rot-y" value="${(light.rotation.y * 180 / Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-rot-z" value="${(light.rotation.z * 180 / Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Ziehe das Licht-Icon in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;

        // Wire up event listeners
        const intensitySlider = document.getElementById('light-intensity');
        const intensityValue = document.getElementById('light-intensity-value');
        const colorPicker = document.getElementById('light-color');
        const posX = document.getElementById('light-pos-x');
        const posY = document.getElementById('light-pos-y');
        const posZ = document.getElementById('light-pos-z');

        if (intensitySlider) {
            intensitySlider.oninput = (e) => {
                light.intensity = parseFloat(e.target.value);
                intensityValue.textContent = light.intensity.toFixed(1);
            };
        }

        if (colorPicker) {
            colorPicker.oninput = (e) => {
                light.color.setHex(parseInt(e.target.value.substring(1), 16));
                // Update icon color
                if (selectedLightIcon) {
                    selectedLightIcon.children.forEach(child => {
                        if (child.material) {
                            child.material.color.copy(light.color);
                            if (child.material.emissive) child.material.emissive.copy(light.color);
                        }
                    });
                }
            };
        }

        if (posX && posY && posZ) {
            const updatePos = () => {
                light.position.set(
                    parseFloat(posX.value),
                    parseFloat(posY.value),
                    parseFloat(posZ.value)
                );
                if (selectedLightIcon) {
                    selectedLightIcon.position.copy(light.position);
                    selectedLightIcon.lookAt(light.target.position);
                }
            };
            posX.oninput = updatePos;
            posY.oninput = updatePos;
            posZ.oninput = updatePos;
        }

        // Rotation inputs
        const rotX = document.getElementById('light-rot-x');
        const rotY = document.getElementById('light-rot-y');
        const rotZ = document.getElementById('light-rot-z');

        if (rotX && rotY && rotZ) {
            const updateRot = () => {
                light.rotation.set(
                    parseFloat(rotX.value) * Math.PI / 180,
                    parseFloat(rotY.value) * Math.PI / 180,
                    parseFloat(rotZ.value) * Math.PI / 180
                );
                if (selectedLightIcon) {
                    selectedLightIcon.rotation.copy(light.rotation);
                }
            };
            rotX.oninput = updateRot;
            rotY.oninput = updateRot;
            rotZ.oninput = updateRot;
        }
    }

    function showGarmentPanel(garmentMesh) {
        // Switch to Eigenschaften tab
        document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        const propsTab = document.querySelector('[data-tab="tab-properties"]');
        const propsPane = document.getElementById('tab-properties');
        if (propsTab) propsTab.classList.add('active');
        if (propsPane) propsPane.classList.add('active');

        // Fill properties panel
        const content = document.getElementById('properties-content');
        if (!content) return;

        const garmentId = garmentMesh.userData.garmentId || garmentMesh.name || 'Garment';
        const mat = garmentMesh.material;
        const currentColor = mat.color;
        const colorHex = '#' + currentColor.getHexString();
        const roughness = mat.roughness ?? 0.8;
        const metalness = mat.metalness ?? 0;

        const offset = garmentMesh.userData.offset || 0.006;
        const stiffness = garmentMesh.userData.stiffness || 0.8;

        // EXACT COPY from Dashboard-Scene character_viewer.html lines 520-619
        content.innerHTML = `
            <div style="padding:16px;max-height:calc(100vh - 200px);overflow-y:auto;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-tshirt"></i> ${garmentId}
                </h3>

                <!-- Fit -->
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Fit</div>
                <div class="slider-row"><label>Offset</label>
                    <input type="range" id="garment-offset" min="0" max="30" value="${Math.round(offset * 1000)}" step="1">
                    <span class="slider-val" id="garment-offset-val">${offset.toFixed(3)}</span>
                </div>
                <div class="slider-row"><label>Stiffness</label>
                    <input type="range" id="garment-stiffness" min="0" max="100" value="${Math.round(stiffness * 100)}" step="1">
                    <span class="slider-val" id="garment-stiffness-val">${stiffness.toFixed(2)}</span>
                </div>
                <div class="slider-row"><label>Min. Abstand</label>
                    <input type="range" id="garment-min-dist" min="0" max="15" value="3" step="1">
                    <span class="slider-val" id="garment-min-dist-val">3 mm</span>
                </div>
                <div class="slider-row"><label>Schritt-Boden</label>
                    <input type="range" id="garment-crotch-floor" min="-40" max="40" value="0" step="1">
                    <span class="slider-val" id="garment-crotch-floor-val">0 mm</span>
                </div>
                <div class="slider-row"><label>Anheben</label>
                    <input type="range" id="garment-lift" min="-20" max="40" value="0" step="1">
                    <span class="slider-val" id="garment-lift-val">0 mm</span>
                </div>
                <div class="slider-row"><label>Schritt-Tiefe</label>
                    <input type="range" id="garment-crotch-depth" min="0" max="40" value="0" step="1">
                    <span class="slider-val" id="garment-crotch-depth-val">0 mm</span>
                </div>

                <!-- Farbe / Material -->
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Farbe / Material</div>
                <div class="slider-row"><label>Color</label>
                    <input type="color" id="garment-color" value="${colorHex}" style="width:40px;height:24px;border:none;cursor:pointer;">
                </div>
                <div class="slider-row"><label>Roughness</label>
                    <input type="range" id="garment-roughness" min="0" max="100" value="${Math.round(roughness * 100)}" step="1">
                    <span class="slider-val" id="garment-roughness-val">${roughness.toFixed(2)}</span>
                </div>
                <div class="slider-row"><label>Metalness</label>
                    <input type="range" id="garment-metalness" min="0" max="100" value="${Math.round(metalness * 100)}" step="1">
                    <span class="slider-val" id="garment-metalness-val">${metalness.toFixed(2)}</span>
                </div>

                <!-- Position -->
                <div id="garment-adjustments">
                    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Position</div>
                    <div class="slider-row"><label>Pos X</label>
                        <input type="range" id="garment-pos-x" min="-50" max="50" value="0" step="1">
                        <span class="slider-val" id="garment-pos-x-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Pos Y</label>
                        <input type="range" id="garment-pos-y" min="-50" max="50" value="0" step="1">
                        <span class="slider-val" id="garment-pos-y-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Pos Z</label>
                        <input type="range" id="garment-pos-z" min="-50" max="50" value="0" step="1">
                        <span class="slider-val" id="garment-pos-z-val">0.00 m</span>
                    </div>

                    <!-- Scale -->
                    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Scale</div>
                    <div class="slider-row"><label>Scale X</label>
                        <input type="range" id="garment-scale-x" min="50" max="200" value="100" step="1">
                        <span class="slider-val" id="garment-scale-x-val">1.00</span>
                    </div>
                    <div class="slider-row"><label>Scale Y</label>
                        <input type="range" id="garment-scale-y" min="50" max="200" value="100" step="1">
                        <span class="slider-val" id="garment-scale-y-val">1.00</span>
                    </div>
                    <div class="slider-row"><label>Scale Z</label>
                        <input type="range" id="garment-scale-z" min="50" max="200" value="100" step="1">
                        <span class="slider-val" id="garment-scale-z-val">1.00</span>
                    </div>

                    <!-- Region -->
                    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Region</div>
                    <div class="slider-row"><label>Top</label>
                        <input type="range" id="garment-region-top" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-top-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Upper</label>
                        <input type="range" id="garment-region-upper" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-upper-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Mid</label>
                        <input type="range" id="garment-region-mid" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-mid-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Lower</label>
                        <input type="range" id="garment-region-lower" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-lower-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Bottom</label>
                        <input type="range" id="garment-region-bottom" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-bottom-val">0.00 m</span>
                    </div>
                </div>
            </div>
        `;

        // Wire up event listeners - EXACTLY like Dashboard viewer.js _bindSlider/_garmentLiveSlider
        const _bindSlider = (sliderId, valId, formatter) => {
            const slider = document.getElementById(sliderId);
            const val = document.getElementById(valId);
            if (slider && val) {
                slider.oninput = () => {
                    val.textContent = formatter ? formatter(slider.value) : slider.value;
                };
            }
        };

        // Bind all sliders (display update only)
        _bindSlider('garment-offset', 'garment-offset-val', v => (v / 1000).toFixed(3));
        _bindSlider('garment-stiffness', 'garment-stiffness-val', v => (v / 100).toFixed(2));
        _bindSlider('garment-min-dist', 'garment-min-dist-val', v => v + ' mm');
        _bindSlider('garment-crotch-floor', 'garment-crotch-floor-val', v => v + ' mm');
        _bindSlider('garment-lift', 'garment-lift-val', v => v + ' mm');
        _bindSlider('garment-crotch-depth', 'garment-crotch-depth-val', v => v + ' mm');
        _bindSlider('garment-roughness', 'garment-roughness-val', v => (v / 100).toFixed(2));
        _bindSlider('garment-metalness', 'garment-metalness-val', v => (v / 100).toFixed(2));
        _bindSlider('garment-pos-x', 'garment-pos-x-val', v => (v / 100).toFixed(2) + ' m');
        _bindSlider('garment-pos-y', 'garment-pos-y-val', v => (v / 100).toFixed(2) + ' m');
        _bindSlider('garment-pos-z', 'garment-pos-z-val', v => (v / 100).toFixed(2) + ' m');
        _bindSlider('garment-scale-x', 'garment-scale-x-val', v => (v / 100).toFixed(2));
        _bindSlider('garment-scale-y', 'garment-scale-y-val', v => (v / 100).toFixed(2));
        _bindSlider('garment-scale-z', 'garment-scale-z-val', v => (v / 100).toFixed(2));
        for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) {
            _bindSlider(`garment-region-${rid}`, `garment-region-${rid}-val`, v => (v / 100).toFixed(2) + ' m');
        }

        // Live material updates (color, roughness, metalness)
        const colorPicker = document.getElementById('garment-color');
        if (colorPicker) {
            colorPicker.oninput = () => {
                mat.color.setHex(parseInt(colorPicker.value.substring(1), 16));
            };
        }

        const roughnessSlider = document.getElementById('garment-roughness');
        if (roughnessSlider) {
            roughnessSlider.oninput = () => {
                mat.roughness = parseInt(roughnessSlider.value) / 100;
            };
        }

        const metalnessSlider = document.getElementById('garment-metalness');
        if (metalnessSlider) {
            metalnessSlider.oninput = () => {
                mat.metalness = parseInt(metalnessSlider.value) / 100;
            };
        }

        // Note: Offset/Stiffness/Position/Scale/Region sliders update display only
        // Full implementation would need vertex buffer manipulation like Dashboard
        console.log('✓ Garment properties panel populated');
    }

    function showCharacterPanel(characterGroup) {
        // Switch to Eigenschaften tab
        document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        const propsTab = document.querySelector('[data-tab="tab-properties"]');
        const propsPane = document.getElementById('tab-properties');
        if (propsTab) propsTab.classList.add('active');
        if (propsPane) propsPane.classList.add('active');

        // Fill properties panel
        const content = document.getElementById('properties-content');
        if (!content) return;

        const charName = characterGroup.userData.presetName || 'Character';
        const bodyType = characterGroup.userData.bodyType || 'Unknown';
        const pos = characterGroup.position;
        const rot = characterGroup.rotation;

        content.innerHTML = `
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-user"></i> ${charName}
                </h3>

                <div style="margin-bottom:16px;font-size:0.8rem;">
                    <span style="color:var(--text-muted);">Body Type:</span>
                    <span style="color:var(--text);margin-left:8px;">${bodyType}</span>
                </div>

                <!-- Meta Sliders (Age, Mass, Tone, Height) -->
                <div style="margin-bottom:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);">
                        <i class="fas fa-sliders-h"></i> Meta-Parameter
                    </h4>
                    <div id="meta-sliders-container"></div>
                </div>

                <!-- Morph Sliders -->
                <div style="margin-bottom:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);">
                        <i class="fas fa-palette"></i> Morphs
                    </h4>
                    <div id="morph-sliders-container"></div>
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="char-pos-x" value="${pos.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-pos-y" value="${pos.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-pos-z" value="${pos.z.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Rotation (Grad)
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="char-rot-x" value="${(rot.x * 180 / Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-rot-y" value="${(rot.y * 180 / Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-rot-z" value="${(rot.z * 180 / Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Nutze die Transform-Controls in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;

        // Wire up event listeners for position
        const posX = document.getElementById('char-pos-x');
        const posY = document.getElementById('char-pos-y');
        const posZ = document.getElementById('char-pos-z');

        if (posX && posY && posZ) {
            const updatePos = () => {
                characterGroup.position.set(
                    parseFloat(posX.value),
                    parseFloat(posY.value),
                    parseFloat(posZ.value)
                );
            };
            posX.oninput = updatePos;
            posY.oninput = updatePos;
            posZ.oninput = updatePos;
        }

        // Wire up event listeners for rotation
        const rotX = document.getElementById('char-rot-x');
        const rotY = document.getElementById('char-rot-y');
        const rotZ = document.getElementById('char-rot-z');

        if (rotX && rotY && rotZ) {
            const updateRot = () => {
                characterGroup.rotation.set(
                    parseFloat(rotX.value) * Math.PI / 180,
                    parseFloat(rotY.value) * Math.PI / 180,
                    parseFloat(rotZ.value) * Math.PI / 180
                );
            };
            rotX.oninput = updateRot;
            rotY.oninput = updateRot;
            rotZ.oninput = updateRot;
        }

        // Populate Meta-Sliders (age, mass, tone, height)
        populateMetaSliders(characterGroup);

        // Populate Morph-Sliders (from preset morphs)
        populateMorphSliders(characterGroup);
    }

    function populateMetaSliders(characterGroup) {
        const container = document.getElementById('meta-sliders-container');
        if (!container) return;

        // Default meta definitions (like Dashboard-Scene)
        const metaDefs = {
            age: { min: -1.0, max: 1.0, label: 'Alter', step: 0.01 },
            mass: { min: -1.0, max: 1.0, label: 'Gewicht', step: 0.01 },
            tone: { min: -1.0, max: 1.0, label: 'Muskeltonus', step: 0.01 },
            height: { min: -1.0, max: 1.0, label: 'Höhe', step: 0.01 },
        };

        // Get current meta values from character (or default to 0)
        const currentMeta = characterGroup.userData.meta || { age: 0, mass: 0, tone: 0, height: 0 };

        let slidersHTML = '';
        for (const [name, def] of Object.entries(metaDefs)) {
            const value = currentMeta[name] || 0;
            const displayMin = def.min;
            const displayMax = def.max;

            slidersHTML += `
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${def.label}</span>
                        <span id="meta-${name}-value" style="color:var(--text);">${value.toFixed(2)}</span>
                    </div>
                    <input type="range" id="meta-${name}" min="${displayMin}" max="${displayMax}" step="${def.step}" value="${value}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `;
        }

        container.innerHTML = slidersHTML;

        // Wire up event listeners
        for (const name of Object.keys(metaDefs)) {
            const slider = document.getElementById(`meta-${name}`);
            const valueDisplay = document.getElementById(`meta-${name}-value`);
            if (slider && valueDisplay) {
                slider.oninput = async () => {
                    const val = parseFloat(slider.value);
                    valueDisplay.textContent = val.toFixed(2);
                    currentMeta[name] = val;
                    characterGroup.userData.meta = currentMeta;

                    // Reload character with new meta values
                    await reloadCharacterMesh(characterGroup);
                };
            }
        }
    }

    async function reloadCharacterMesh(characterGroup) {
        try {
            // Build query string from current userData
            const params = new URLSearchParams();
            params.set('body_type', characterGroup.userData.bodyType || 'Female_Caucasian');

            // Add all morphs
            const morphs = characterGroup.userData.morphs || {};
            for (const [key, val] of Object.entries(morphs)) {
                if (val !== undefined && val !== null) {
                    params.set(`morph_${key}`, String(val));
                }
            }

            // Add all meta values
            const meta = characterGroup.userData.meta || {};
            for (const [key, val] of Object.entries(meta)) {
                if (val !== undefined && val !== null) {
                    params.set(`meta_${key}`, String(val));
                }
            }

            const url = `/api/character/mesh/?${params.toString()}`;
            const resp = await fetch(url);
            if (!resp.ok) throw new Error(`Character mesh API error: ${resp.status}`);
            const data = await resp.json();

            // Find the body mesh in the character group
            const oldBodyMesh = characterGroup.children.find(c => c.isMesh && !c.userData.isHair && !c.userData.isGarment);
            if (!oldBodyMesh) {
                console.warn('Could not find body mesh to update');
                return;
            }

            // Decode new mesh data
            function base64ToFloat32(b64) {
                const binary = atob(b64);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
                return new Float32Array(bytes.buffer);
            }

            const verts = base64ToFloat32(data.vertices);

            // Convert from Blender Z-up to Three.js Y-up
            for (let i = 0; i < verts.length; i += 3) {
                const y = verts[i + 1];
                const z = verts[i + 2];
                verts[i + 1] = z;
                verts[i + 2] = -y;
            }

            // Update geometry positions
            oldBodyMesh.geometry.attributes.position.array.set(verts);
            oldBodyMesh.geometry.attributes.position.needsUpdate = true;

            // Recompute normals if not provided
            if (data.normals) {
                const normals = base64ToFloat32(data.normals);
                for (let i = 0; i < normals.length; i += 3) {
                    const y = normals[i + 1];
                    const z = normals[i + 2];
                    normals[i + 1] = z;
                    normals[i + 2] = -y;
                }
                oldBodyMesh.geometry.attributes.normal.array.set(normals);
                oldBodyMesh.geometry.attributes.normal.needsUpdate = true;
            } else {
                oldBodyMesh.geometry.computeVertexNormals();
            }

            console.log('✓ Character mesh reloaded');
        } catch (err) {
            console.error('Failed to reload character mesh:', err);
        }
    }

    function populateMorphSliders(characterGroup) {
        const container = document.getElementById('morph-sliders-container');
        if (!container) return;

        // Get current morph values from character userData
        const currentMorphs = characterGroup.userData.morphs || {};

        // If no morphs, show a message
        if (Object.keys(currentMorphs).length === 0) {
            container.innerHTML = '<div style="font-size:0.75rem;color:var(--text-muted);text-align:center;padding:10px;">Keine Morphs</div>';
            return;
        }

        // Build HTML for morph sliders
        let slidersHTML = '<div style="max-height:300px;overflow-y:auto;padding-right:4px;">';
        for (const [name, value] of Object.entries(currentMorphs)) {
            const displayValue = value || 0;
            slidersHTML += `
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${name}</span>
                        <span id="morph-${name}-value" style="color:var(--text);">${displayValue.toFixed(2)}</span>
                    </div>
                    <input type="range" id="morph-${name}" min="0" max="1" step="0.01" value="${displayValue}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `;
        }
        slidersHTML += '</div>';

        container.innerHTML = slidersHTML;

        // Wire up event listeners
        for (const name of Object.keys(currentMorphs)) {
            const slider = document.getElementById(`morph-${name}`);
            const valueDisplay = document.getElementById(`morph-${name}-value`);
            if (slider && valueDisplay) {
                slider.oninput = async () => {
                    const val = parseFloat(slider.value);
                    valueDisplay.textContent = val.toFixed(2);
                    currentMorphs[name] = val;
                    characterGroup.userData.morphs = currentMorphs;

                    // Reload character with new morph values
                    await reloadCharacterMesh(characterGroup);
                };
            }
        }
    }

    function hideLightPanel() {
        const content = document.getElementById('properties-content');
        if (!content) return;
        content.innerHTML = `
            <div style="padding:20px;color:var(--text-muted);font-size:0.85rem;text-align:center;">
                <i class="fas fa-hand-pointer" style="font-size:2rem;margin-bottom:10px;opacity:0.3;"></i>
                <p>Klicke auf ein Licht-Icon oder Character in der Szene<br>um Eigenschaften zu bearbeiten.</p>
            </div>
        `;
    }

    // ── Render loop ──
    function animate() {
        requestAnimationFrame(animate);
        const delta = clock.getDelta();

        // Update active BVH animation mixer
        if (activeMixer && isPlaying) {
            activeMixer.update(delta * playbackSpeed);
            currentTime = currentAction ? currentAction.time : 0;

            // Loop animation
            if (currentTime >= animDuration) {
                currentTime = 0;
                if (currentAction) currentAction.time = 0;
            }

            updatePlayerUI();
        }

        // Sync Theatre.js sequence playhead with our timeline slider
        if (isPlaying && timelineSlider) {
            const seqPos = sheet.sequence.position;
            timeCurrent.textContent = formatTime(seqPos);
        }

        // Sync light icons with lights (wenn bewegt via TransformControls)
        if (selectedLightIcon && selectedLightIcon.userData.light) {
            const light = selectedLightIcon.userData.light;
            light.position.copy(selectedLightIcon.position);
            selectedLightIcon.lookAt(light.target.position);
        }

        controls.update();
        // Temporarily hide SkinnedMeshes without skeleton to prevent render errors
        const hiddenMeshes = [];
        scene.traverse((child) => {
            if (child.isSkinnedMesh && !child.skeleton) {
                child.visible = false;
                hiddenMeshes.push(child);
            }
        });
        renderer.render(scene, camera);
        // Restore visibility so garments/meshes become visible once skeleton is bound
        for (const mesh of hiddenMeshes) {
            mesh.visible = true;
        }
    }
    animate();

    // ── Global API for server-side rendering (Playwright) ──
    window.__theatreSetTime = (t) => {
        if (activeMixer && currentAction) {
            currentAction.time = t;
            activeMixer.update(0);
        }
        renderer.render(scene, camera);
    };
    window.__theatreGetDuration = () => animDuration || 0;
    window.__theatreReady = false;

    // ── URL-Parameter Autoplay ──
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('autoplay') === '1') {
        // Wait for scene to load, then start playing
        setTimeout(() => {
            const playBtn = document.getElementById('btnPlayPause');
            if (playBtn && !isPlaying) playBtn.click();
            window.__theatreReady = true;
        }, 3000);
    }

    // ── Export Tab UI ──
    const exportCrf = document.getElementById('export-crf');
    const exportCrfVal = document.getElementById('export-crf-val');
    if (exportCrf && exportCrfVal) {
        exportCrf.addEventListener('input', () => { exportCrfVal.textContent = exportCrf.value; });
    }

    const exportRes = document.getElementById('export-resolution');
    const exportCustom = document.getElementById('export-custom-res');
    if (exportRes && exportCustom) {
        exportRes.addEventListener('change', () => {
            exportCustom.style.display = exportRes.value === 'custom' ? 'flex' : 'none';
        });
    }

    // Show/hide server-only options based on method
    const exportMethodSel = document.getElementById('export-method');
    const exportRegionSection = document.getElementById('export-region-section');
    if (exportMethodSel) {
        exportMethodSel.addEventListener('change', () => {
            if (exportRegionSection) exportRegionSection.style.display = exportMethodSel.value === 'server' ? '' : 'none';
        });
    }

    // Update export info whenever Export tab is shown
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            if (tab.getAttribute('data-tab') === 'tab-export') {
                const nameEl = document.getElementById('export-anim-name');
                const durEl = document.getElementById('export-anim-dur');
                if (nameEl) nameEl.textContent = currentAnimName || '—';
                if (durEl) durEl.textContent = animDuration ? animDuration.toFixed(1) : '—';
                // Auto-fill end time
                const endInput = document.getElementById('export-end');
                if (endInput && (!endInput.value || endInput.value === '0') && animDuration) {
                    endInput.value = animDuration.toFixed(1);
                }
            }
        });
    });

    // Export start button
    const exportBtn = document.getElementById('export-start-btn');
    const cancelBtn = document.getElementById('export-cancel-btn');
    const progressDiv = document.getElementById('export-progress');
    const progressBar = document.getElementById('export-progress-bar');
    const progressText = document.getElementById('export-progress-text');
    let exportAborted = false;

    if (exportBtn) {
        exportBtn.addEventListener('click', async () => {
            const method = document.getElementById('export-method').value;
            if (method === 'browser') {
                await exportBrowser();
            } else {
                await exportServer();
            }
        });
    }
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => { exportAborted = true; });
    }

    function getExportSettings() {
        const resSelect = document.getElementById('export-resolution').value;
        let w, h;
        if (resSelect === 'viewport') {
            const c = document.getElementById('theatre-canvas');
            w = c.clientWidth; h = c.clientHeight;
        } else if (resSelect === 'custom') {
            w = parseInt(document.getElementById('export-width').value) || 1920;
            h = parseInt(document.getElementById('export-height').value) || 1080;
        } else {
            const presets = { '720': [1280,720], '1080': [1920,1080], '1440': [2560,1440], '2160': [3840,2160] };
            [w, h] = presets[resSelect] || [1920, 1080];
        }
        return {
            width: w, height: h,
            fps: parseInt(document.getElementById('export-fps').value) || 30,
            format: document.getElementById('export-format').value || 'mp4',
            crf: parseInt(document.getElementById('export-crf').value) || 18,
            startTime: parseFloat(document.getElementById('export-start').value) || 0,
            endTime: parseFloat(document.getElementById('export-end').value) || 0,
            bg: document.getElementById('export-bg').value || 'scene',
            cropX: parseInt(document.getElementById('export-crop-x')?.value) || 0,
            cropY: parseInt(document.getElementById('export-crop-y')?.value) || 0,
            cropW: parseInt(document.getElementById('export-crop-w')?.value) || 0,
            cropH: parseInt(document.getElementById('export-crop-h')?.value) || 0,
        };
    }

    function showProgress(pct, text) {
        progressDiv.style.display = '';
        progressBar.style.width = pct + '%';
        progressText.textContent = text || (pct.toFixed(0) + '%');
    }

    // ── Browser Export (Frame-by-frame → PNG → Server ffmpeg) ──
    async function exportBrowser() {
        const s = getExportSettings();
        const canvas = document.getElementById('theatre-canvas');

        // Get actual animation duration from mixer
        let animDuration = 10;
        if (currentAction && currentAction.getClip()) {
            animDuration = currentAction.getClip().duration;
        }
        const startTime = s.startTime || 0;
        const endTime = (s.endTime > startTime) ? s.endTime : animDuration;
        const duration = endTime - startTime;
        const totalFrames = Math.ceil(duration * s.fps);

        exportBtn.style.display = 'none';
        cancelBtn.style.display = '';
        exportAborted = false;
        showProgress(0, `0 / ${totalFrames} Frames...`);

        // Pause real-time playback
        const wasPlaying = playing;
        playing = false;
        if (currentAction) currentAction.paused = true;

        // Capture frames as PNGs
        const frames = [];
        for (let f = 0; f < totalFrames; f++) {
            if (exportAborted) break;

            const t = startTime + f / s.fps;

            // Set animation time
            if (mixer && currentAction) {
                currentAction.time = t;
                mixer.update(0);
            }
            renderer.render(scene, camera);

            // Capture frame
            const blob = await new Promise(r => canvas.toBlob(r, 'image/png'));
            frames.push(blob);

            if (f % 10 === 0 || f === totalFrames - 1) {
                const pct = ((f + 1) / totalFrames) * 100;
                showProgress(pct, `${f + 1} / ${totalFrames} Frames (${(t).toFixed(1)}s)`);
            }

            // Yield to UI
            await new Promise(r => setTimeout(r, 0));
        }

        // Restore playback
        if (wasPlaying && currentAction) {
            currentAction.paused = false;
            playing = true;
        }

        if (exportAborted || frames.length === 0) {
            exportBtn.style.display = '';
            cancelBtn.style.display = 'none';
            progressDiv.style.display = 'none';
            return;
        }

        showProgress(100, 'Sende an Server für ffmpeg...');

        // Send frames to server for ffmpeg encoding
        const formData = new FormData();
        frames.forEach((blob, i) => {
            formData.append('frames', blob, `${String(i).padStart(6, '0')}.png`);
        });
        formData.append('fps', s.fps);
        formData.append('format', s.format);
        formData.append('crf', s.crf);
        formData.append('width', s.width);
        formData.append('height', s.height);

        try {
            const resp = await fetch('/api/theatre/encode-frames/', {
                method: 'POST',
                body: formData,
            });
            if (resp.ok) {
                const blob = await resp.blob();
                const ext = s.format === 'png' ? 'zip' : s.format;
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = `theatre_export.${ext}`;
                a.click(); URL.revokeObjectURL(url);
                showProgress(100, 'Export fertig!');
            } else {
                alert('Encoding fehlgeschlagen: ' + await resp.text());
            }
        } catch (e) {
            alert('Export-Fehler: ' + e.message);
        }

        exportBtn.style.display = '';
        cancelBtn.style.display = 'none';
        setTimeout(() => { progressDiv.style.display = 'none'; }, 3000);

        if (s.format === 'webm') {
            // Direct download
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url; a.download = 'theatre_export.webm';
            a.click(); URL.revokeObjectURL(url);
            progressDiv.style.display = 'none';
        } else {
            // Convert WebM → MP4 via server
            const formData = new FormData();
            formData.append('video', blob, 'export.webm');
            formData.append('crf', s.crf);
            formData.append('format', s.format);
            try {
                const resp = await fetch('/api/theatre/convert-video/', { method: 'POST', body: formData });
                if (resp.ok) {
                    const mpBlob = await resp.blob();
                    const url = URL.createObjectURL(mpBlob);
                    const a = document.createElement('a'); a.href = url; a.download = `theatre_export.${s.format}`;
                    a.click(); URL.revokeObjectURL(url);
                } else {
                    alert('Konvertierung fehlgeschlagen: ' + await resp.text());
                }
            } catch (e) {
                alert('Export-Fehler: ' + e.message);
            }
            progressDiv.style.display = 'none';
        }
    }

    // ── Server Export (Playwright + ffmpeg) ──
    async function exportServer() {
        const s = getExportSettings();

        // Get actual animation duration
        const actualDuration = animDuration || 10;
        const startTime = s.startTime || 0;
        const endTime = (s.endTime > startTime) ? s.endTime : actualDuration;

        exportBtn.style.display = 'none';
        cancelBtn.style.display = '';
        exportAborted = false;
        const totalFrames = Math.ceil((endTime - startTime) * s.fps);
        showProgress(0, `Server-Rendering: ${totalFrames} Frames (${(endTime-startTime).toFixed(1)}s @ ${s.fps}fps)...`);

        // Save current session state so Playwright can load the same scene
        try { sessionStorage.setItem('theatre-export-state', JSON.stringify({
            sceneUrl: window.location.href,
        })); } catch(e) {}

        cancelBtn.onclick = () => {
            exportAborted = true;
            exportBtn.style.display = '';
            cancelBtn.style.display = 'none';
            progressDiv.style.display = 'none';
        };

        try {
            const resp = await fetch('/api/theatre/render-video/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    width: s.width,
                    height: s.height,
                    fps: s.fps,
                    format: s.format,
                    crf: s.crf,
                    start_time: startTime,
                    end_time: endTime,
                    background: s.bg,
                    crop_x: s.cropX, crop_y: s.cropY,
                    crop_w: s.cropW, crop_h: s.cropH,
                    scene_url: window.location.href,
                }),
            });

            if (resp.ok) {
                const blob = await resp.blob();
                const url = URL.createObjectURL(blob);
                const ext = s.format === 'png' ? 'zip' : s.format;
                const a = document.createElement('a'); a.href = url; a.download = `theatre_export.${ext}`;
                a.click(); URL.revokeObjectURL(url);
                showProgress(100, 'Export fertig!');
            } else {
                alert('Server-Export fehlgeschlagen: ' + await resp.text());
            }
        } catch (e) {
            alert('Server-Export Fehler: ' + e.message);
        }

        exportBtn.style.display = '';
        cancelBtn.style.display = 'none';
        setTimeout(() => { progressDiv.style.display = 'none'; }, 3000);
    }
});
