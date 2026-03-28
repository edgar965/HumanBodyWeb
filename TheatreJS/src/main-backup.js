import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
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
import { retargetBVHToDefClip, detectBVHFormat } from './retarget_hybrid.js';
import { KeyframeUI } from './keyframe-ui.js';

// Wait for DOM before initialising
window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('theatre-canvas');
    if (!canvas) {
        console.error('theatre-canvas not found');
        return;
    }

    // 1. Theatre Studio overlay - DISABLED (verdeckt UI)
    // studio.initialize();
    // window.studio = studio;

    // 2. Three.js scene (ballet stage)
    const { scene, camera, renderer, controls, lights, lightIcons, transformControls } = createScene(canvas);

    // DEBUG: Expose for console debugging
    window.scene = scene;
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
    let defSkeletonData = null;
    let skinWeightData = null;
    let skeletonLoadingPromise = null;
    let defSkeleton = null;  // { skeleton, rootBone, bones, boneByName } - like Dashboard
    let skeletonHelper = null;  // Single global SkeletonHelper - like Dashboard
    let rigVisible = false;  // Rig visibility state - like Dashboard

    /**
     * Build 176-bone THREE.Skeleton from DEF skeleton data + skin weight bone order.
     * Bone indices match skinWeightData.bone_names (authoritative for skinIndex).
     * COPIED FROM Dashboard-Scene viewer.js (lines 709-774)
     */
    function buildDefSkeleton(skelData, swData) {
        // Build lookup: bone name -> skeleton data entry
        const skelByName = {};
        for (const b of skelData.bones) {
            skelByName[b.name] = b;
        }

        const bones = [];
        const boneByName = {};
        let rootBone = null;

        // Create bones in skin weight order (= authoritative index order)
        // Sanitize names: Three.js PropertyBinding uses dots as separators,
        // so bone names like "DEF-upper_arm.L" break track name parsing.
        for (const name of swData.bone_names) {
            const bone = new THREE.Bone();
            bone.name = name.replace(/\./g, '_');  // DEF-upper_arm.L -> DEF-upper_arm_L
            bones.push(bone);
            boneByName[name] = bone;  // Original name as key for mapping lookups
        }

        // Set local transforms and build parent-child hierarchy
        for (let i = 0; i < swData.bone_names.length; i++) {
            const name = swData.bone_names[i];
            const bone = bones[i];
            const data = skelByName[name];

            if (!data) continue;

            // Convert Blender local position (x,y,z) -> Three.js (x,z,-y)
            const p = data.local_position;
            bone.position.set(p[0], p[2], -p[1]);

            // Convert Blender quaternion [w,x,y,z] -> Three.js Quaternion(x,z,-y,w)
            const q = data.local_quaternion;
            bone.quaternion.set(q[1], q[3], -q[2], q[0]);

            // Parent-child (lookup by original name)
            if (data.parent && boneByName[data.parent]) {
                boneByName[data.parent].add(bone);
            } else {
                // Root bone (no skinning parent)
                if (!rootBone) rootBone = bone;
            }
        }

        // Collect orphan roots (bones without skinning parent that aren't the main root)
        for (let i = 0; i < bones.length; i++) {
            const name = swData.bone_names[i];
            const data = skelByName[name];
            if (!data) continue;
            if (!data.parent && bones[i] !== rootBone) {
                // Attach to main root
                if (rootBone) rootBone.add(bones[i]);
            }
        }

        if (!rootBone && bones.length > 0) rootBone = bones[0];

        // Update world matrices before creating skeleton
        rootBone.updateWorldMatrix(true, true);

        const skeleton = new THREE.Skeleton(bones);

        return { skeleton, rootBone, bones, boneByName };
    }

    // Load skeleton and skin weights data
    async function loadSkeletonAndWeights() {
        if (skeletonLoadingPromise) return skeletonLoadingPromise;

        skeletonLoadingPromise = (async () => {
            try {
                const [skelResp, weightsResp] = await Promise.all([
                    fetch('/api/character/def-skeleton/'),
                    fetch('/api/character/skin-weights/')
                ]);
                if (skelResp.ok) defSkeletonData = await skelResp.json();
                if (weightsResp.ok) skinWeightData = await weightsResp.json();
                console.log('✓ Loaded skeleton and skin weights:', defSkeletonData?.bones?.length || 0, 'bones');

                // Build defSkeleton object using Dashboard's buildDefSkeleton function
                if (defSkeletonData && skinWeightData) {
                    defSkeleton = buildDefSkeleton(defSkeletonData, skinWeightData);
                    console.log('✓ Built defSkeleton:', defSkeleton.bones.length, 'bones');

                    // Make defSkeletonData available globally for test
                    window.defSkeletonData = defSkeletonData;
                    window.defSkeleton = defSkeleton;
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
        if (defSkeletonData && skinWeightData && !characterGroup.userData.isSkinnedMesh) {
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
     * Load BVH animation on a SkinnedMesh (character with skeleton).
     * Uses retargeting to map BVH bone names to DEF skeleton bone names.
     */
    function loadBVHOnSkinnedMesh(bvhText, skinnedMesh, scene, animName) {
        const bvhLoader = new BVHLoader();
        const result = bvhLoader.parse(bvhText);

        // Retarget BVH clip to DEF skeleton bone names
        if (!defSkeletonData) {
            console.error('DEF skeleton data not loaded - cannot retarget animation');
            throw new Error('Skeleton data not loaded');
        }

        // Validate SkinnedMesh has proper skeleton
        if (!skinnedMesh || !skinnedMesh.skeleton) {
            console.error('SkinnedMesh has no skeleton');
            throw new Error('SkinnedMesh not properly initialized');
        }

        if (!skinnedMesh.skeleton.bones || skinnedMesh.skeleton.bones.length === 0) {
            console.error('SkinnedMesh skeleton has no bones');
            throw new Error('Skeleton has no bones');
        }

        // Use GLOBAL defSkeleton (not local build - bones must match skin weights)
        if (!defSkeleton || !defSkeleton.boneByName) {
            console.error('Global defSkeleton not loaded - cannot retarget');
            throw new Error('Skeleton not ready');
        }

        // Detect BVH format (MIXAMO, CMU, AIST, etc.) - CRITICAL for correct retargeting!
        const bvhBones = result.skeleton.bones;
        const format = detectBVHFormat(bvhBones);
        console.log(`BVH format detected: ${format}, retargeting to DEF skeleton...`);

        // Retarget BVH to DEF skeleton using CORRECT parameters (like Dashboard)
        // retargetBVHToDefClip(bvhResult, defSkel, FORMAT, opts)
        const retargetedClip = retargetBVHToDefClip(result, defSkeleton, format, { bodyMesh: skinnedMesh });

        if (!retargetedClip || retargetedClip.tracks.length === 0) {
            console.error('Retargeting failed - no tracks generated');
            throw new Error('Retargeting failed');
        }

        console.log(`✓ Retargeted clip: ${retargetedClip.tracks.length} tracks, ${retargetedClip.duration.toFixed(2)}s`);

        // Create AnimationMixer on the SkinnedMesh with retargeted clip
        const mixer = new THREE.AnimationMixer(skinnedMesh);
        const action = mixer.clipAction(retargetedClip);
        action.setLoop(THREE.LoopRepeat);
        action.play();
        action.paused = true; // Start paused for player control

        const duration = retargetedClip.duration || 1;

        console.log('✓ BVH animation loaded on SkinnedMesh:', animName, duration + 's');

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
        if (!defSkeletonData || !skinWeightData) {
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

        // Rebuild skeleton — reusing a Skeleton whose bones were created before
        // parenting to SkinnedMesh causes stale boneTexture/boneMatrices state.
        // Use global defSkeleton built by loadSkeletonAndWeights
        if (!defSkeleton) {
            defSkeleton = buildDefSkeleton(defSkeletonData, skinWeightData);
        }

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
        skinnedMesh.add(defSkeleton.rootBone);
        skinnedMesh.bind(defSkeleton.skeleton);

        // Replace old mesh in character group
        characterGroup.remove(bodyMesh);
        characterGroup.add(skinnedMesh);

        // Store references
        characterGroup.userData.isSkinnedMesh = true;
        characterGroup.userData.skinnedMesh = skinnedMesh;
        characterGroup.userData.skeleton = defSkeleton.skeleton;
        characterGroup.userData.rootBone = defSkeleton.rootBone;

        console.log('✓ SkinnedMesh created:',
            'bones:', defSkeleton.skeleton.bones.length,
            'skinIndex:', !!geo.attributes.skinIndex,
            'skinWeight:', !!geo.attributes.skinWeight);

        // Make skinnedMesh globally accessible for animation
        window.loadedCharacters = window.loadedCharacters || [];
        if (!window.loadedCharacters.includes(characterGroup)) {
            window.loadedCharacters.push(characterGroup);
        }

        // Bind garments to skeleton (like Dashboard viewer.js)
        characterGroup.traverse((child) => {
            if (child.isSkinnedMesh && child !== skinnedMesh && child.userData.needsBinding) {
                child.add(defSkeleton.rootBone);
                child.bind(defSkeleton.skeleton, skinnedMesh.bindMatrix);
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
            skinnedChild.bind(defSkeleton.skeleton, bodyMesh.bindMatrix);
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
        const charIntersects = raycaster.intersectObjects(loadedCharacters, true);
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
    createCameraSheet(sheet, camera);
    createLightSheet(sheet, 'Spot Left', lights.spotLeft);
    createLightSheet(sheet, 'Spot Right', lights.spotRight);
    createLightSheet(sheet, 'Back Light', lights.backLight);

    // 5. Initialize Keyframe UI for Camera/Light animation
    const theatreObjects = getAllTheatreObjects();
    const keyframeUI = new KeyframeUI(project, sheet, theatreObjects);
    window.keyframeUI = keyframeUI; // Expose for debugging

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
                if (!skeletonHelper && defSkeleton) {
                    skeletonHelper = new THREE.SkeletonHelper(defSkeleton.rootBone);
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

    async function handleAnimLoad(category, name) {
        try {
            // Remember if animation was playing before switch
            const wasPlaying = isPlaying;

            const bvhText = await fetchBVH(category, name);

            // If we have a selected character, convert it to SkinnedMesh first
            let targetMesh = null;
            if (selectedCharacter) {
                console.log('Selected character found, converting to SkinnedMesh...');
                targetMesh = convertCharacterToSkinnedMesh(selectedCharacter, scene);
                console.log('targetMesh:', !!targetMesh, 'isSkinnedMesh:', targetMesh?.isSkinnedMesh);
            } else {
                console.log('No selected character - using BVH bones only');
            }

            // FIRST: Stop and reset old animation to T-Pose
            if (activeMixer && currentAction) {
                currentAction.stop();
                currentAction.reset();  // Reset to T-Pose
                activeMixer.update(0);  // Force update to apply reset
                activeMixer.stopAllAction();
                activeMixer.uncacheRoot(activeMixer.getRoot());
            }

            // THEN: Load new animation
            const { mixer, action, duration } = targetMesh
                ? loadBVHOnSkinnedMesh(bvhText, targetMesh, scene, `${category}/${name}`)
                : loadBVHFromText(bvhText, scene, `${category}/${name}`);
            activeMixer = mixer;
            currentAction = action;

            // Expose to window for debugging
            window.activeMixer = activeMixer;

            // Update player UI
            updatePlayerDuration(duration);
            currentTime = 0;
            animDuration = duration;

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

    // ── Export Video ──
    const menuExportVideo = document.getElementById('menu-export-video');
    if (menuExportVideo) {
        menuExportVideo.addEventListener('click', async () => {
            if (exporter.isRecording) {
                menuExportVideo.innerHTML = '<i class="fas fa-file-video"></i> Export Video';
                await exporter.stopAndDownload();
            } else {
                exporter.start(30);
                menuExportVideo.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
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
            if (!activeMixer) return;
            isPlaying = !isPlaying;
            window.isPlaying = isPlaying; // Expose to window
            if (isPlaying && currentAction) {
                currentAction.paused = false;
                currentAction.play();
            } else if (currentAction) {
                currentAction.paused = true;
            }
            updatePlayerUI();
        });
    }

    if (btnStop) {
        btnStop.addEventListener('click', () => {
            if (!activeMixer) return;
            isPlaying = false;
            currentTime = 0;
            setAnimationTime(0);
            if (currentAction) {
                currentAction.stop();
                currentAction.reset();  // Reset to T-Pose (like Dashboard viewer.js)
                currentAction.paused = true;
            }
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

        // Sync light icons with lights (wenn bewegt via TransformControls)
        if (selectedLightIcon && selectedLightIcon.userData.light) {
            const light = selectedLightIcon.userData.light;
            light.position.copy(selectedLightIcon.position);
            selectedLightIcon.lookAt(light.target.position);
        }

        controls.update();
        renderer.render(scene, camera);
    }
    animate();
});
