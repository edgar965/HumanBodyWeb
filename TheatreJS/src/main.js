import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import studio from '@theatre/studio';
import { createScene } from './scene-setup.js';
import { setupTheatre, createCameraSheet, createLightSheet } from './theatre-bridge.js';
import { loadGLBFromFile, loadCharacterFromPreset, loadBVHFromText } from './asset-loader.js';
import { VideoExporter } from './video-export.js';
import {
    fetchSceneList, fetchScene, saveScene,
    fetchModelList, fetchModel,
    fetchAnimationList, fetchBVH,
} from './scene-manager.js';
import { PRESETS, applyPreset } from './presets.js';
import { retargetBVHToDefClip } from './retarget_hybrid.js';

// Wait for DOM before initialising
window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('theatre-canvas');
    if (!canvas) {
        console.error('theatre-canvas not found');
        return;
    }

    // 1. Theatre Studio overlay - DEAKTIVIERT (kein UI-Panel oben rechts!)
    // studio.initialize();

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

        // Build defSkeleton object (same structure as viewer.js expects)
        const defSkeleton = {
            skeleton: skinnedMesh.skeleton,
            rootBone: skinnedMesh.skeleton.bones[0],
            bones: skinnedMesh.skeleton.bones,
            boneByName: {}
        };
        for (const bone of skinnedMesh.skeleton.bones) {
            defSkeleton.boneByName[bone.name] = bone;
        }

        // Retarget BVH clip to DEF skeleton
        const retargetedClip = retargetBVHToDefClip(result, defSkeleton, animName || result.clip.name);

        if (!retargetedClip || retargetedClip.tracks.length === 0) {
            console.error('Retargeting failed - no tracks generated');
            throw new Error('Retargeting failed');
        }

        // Create AnimationMixer on the SkinnedMesh with retargeted clip
        const mixer = new THREE.AnimationMixer(skinnedMesh);
        const action = mixer.clipAction(retargetedClip);
        action.setLoop(THREE.LoopRepeat);
        action.play();
        action.paused = true; // Start paused for player control

        const duration = retargetedClip.duration || 1;

        console.log('✓ BVH animation retargeted and loaded on SkinnedMesh:', animName, duration + 's', retargetedClip.tracks.length, 'tracks');

        return { mixer, action, duration };
    }

    /**
     * Convert a character mesh to SkinnedMesh with skeleton binding.
     * This enables BVH animations to deform the character mesh (not just bones).
     * Similar to Dashboard-Scene's convertToDefSkinnedMesh().
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
        const bodyMesh = characterGroup.children.find(c => c.isMesh);
        if (!bodyMesh) {
            console.warn('No mesh found in character group');
            return null;
        }

        console.log('Converting to SkinnedMesh...');

        // Clone geometry
        const geo = bodyMesh.geometry.clone();
        const vCount = geo.attributes.position.count;

        // Build skinIndices and skinWeights buffers
        const skinIndices = new Float32Array(vCount * 4);
        const skinWeights = new Float32Array(vCount * 4);

        for (let i = 0; i < vCount; i++) {
            const wi = skinWeightData.indices[i] || [0, 0, 0, 0];
            const ww = skinWeightData.weights[i] || [1, 0, 0, 0];
            skinIndices[i * 4 + 0] = wi[0];
            skinIndices[i * 4 + 1] = wi[1];
            skinIndices[i * 4 + 2] = wi[2];
            skinIndices[i * 4 + 3] = wi[3];
            skinWeights[i * 4 + 0] = ww[0];
            skinWeights[i * 4 + 1] = ww[1];
            skinWeights[i * 4 + 2] = ww[2];
            skinWeights[i * 4 + 3] = ww[3];
        }

        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));

        // Create skeleton from defSkeletonData
        const bones = [];
        const boneInverses = [];

        for (const boneData of defSkeletonData.bones) {
            const bone = new THREE.Bone();
            bone.name = boneData.name;
            bone.position.fromArray(boneData.position);
            bone.quaternion.fromArray(boneData.quaternion);
            bone.scale.fromArray(boneData.scale);
            bones.push(bone);

            // Bone inverse matrix
            const invMatrix = new THREE.Matrix4();
            if (boneData.inverse) {
                invMatrix.fromArray(boneData.inverse);
            }
            boneInverses.push(invMatrix);
        }

        // Build bone hierarchy
        for (let i = 0; i < defSkeletonData.bones.length; i++) {
            const parentIdx = defSkeletonData.bones[i].parent;
            if (parentIdx >= 0) {
                bones[parentIdx].add(bones[i]);
            }
        }

        const skeleton = new THREE.Skeleton(bones, boneInverses);
        const rootBone = bones[0];

        // Create SkinnedMesh
        const material = bodyMesh.material; // Reuse existing material
        const skinnedMesh = new THREE.SkinnedMesh(geo, material);
        skinnedMesh.castShadow = true;
        skinnedMesh.receiveShadow = true;

        // Add root bone to skinned mesh and bind
        skinnedMesh.add(rootBone);
        skinnedMesh.bind(skeleton);

        // Replace old mesh
        const pos = bodyMesh.position.clone();
        const rot = bodyMesh.rotation.clone();
        const scale = bodyMesh.scale.clone();

        characterGroup.remove(bodyMesh);
        skinnedMesh.position.copy(pos);
        skinnedMesh.rotation.copy(rot);
        skinnedMesh.scale.copy(scale);
        characterGroup.add(skinnedMesh);

        // Create SkeletonHelper for visualization
        const skeletonHelper = new THREE.SkeletonHelper(rootBone);
        skeletonHelper.visible = false; // Hidden by default
        skeletonHelper.material.linewidth = 2;
        skeletonHelper.userData.isRig = true; // Mark for toggle button
        scene.add(skeletonHelper);

        // Store references
        characterGroup.userData.isSkinnedMesh = true;
        characterGroup.userData.skinnedMesh = skinnedMesh;
        characterGroup.userData.skeleton = skeleton;
        characterGroup.userData.rootBone = rootBone;
        characterGroup.userData.skeletonHelper = skeletonHelper;

        console.log('✓ Converted to SkinnedMesh with', bones.length, 'bones');
        return skinnedMesh;
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

    // 4. Register camera & spotlights as animatable Theatre objects
    createCameraSheet(sheet, camera);
    createLightSheet(sheet, 'Spot Left', lights.spotLeft);
    createLightSheet(sheet, 'Spot Right', lights.spotRight);
    createLightSheet(sheet, 'Back Light', lights.backLight);

    // 5. Video exporter
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

    // Toggle rig visibility (skeleton)
    const btnToggleRig = document.getElementById('btn-toggle-rig');
    let rigVisible = false;
    if (btnToggleRig) {
        btnToggleRig.addEventListener('click', () => {
            rigVisible = !rigVisible;

            scene.traverse((obj) => {
                if (obj.isSkeletonHelper || obj.userData.isRig) {
                    obj.visible = rigVisible;
                }
            });

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
            const bvhText = await fetchBVH(category, name);

            // If we have a selected character, convert it to SkinnedMesh first
            let targetMesh = null;
            if (selectedCharacter) {
                targetMesh = convertCharacterToSkinnedMesh(selectedCharacter, scene);
            }

            // If we have a SkinnedMesh, use it for animation; otherwise fall back to BVH bones
            const { mixer, action, duration } = targetMesh
                ? loadBVHOnSkinnedMesh(bvhText, targetMesh, scene, `${category}/${name}`)
                : loadBVHFromText(bvhText, scene, `${category}/${name}`);

            // Replace current mixer
            if (activeMixer) activeMixer.stopAllAction();
            activeMixer = mixer;
            currentAction = action;

            // Expose to window for debugging
            window.activeMixer = activeMixer;

            // Update player UI
            updatePlayerDuration(duration);
            isPlaying = false;
            currentTime = 0;
            animDuration = duration;

            // Expose to window
            window.isPlaying = false;
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
        const pos = garmentMesh.position;

        content.innerHTML = `
            <div style="padding:16px;max-height:calc(100vh - 200px);overflow-y:auto;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-tshirt"></i> ${garmentId}
                </h3>

                <!-- Material Properties -->
                <div style="margin-bottom:20px;">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);"><i class="fas fa-palette"></i> Material</h4>

                    <div style="margin-bottom:12px;">
                        <label style="display:block;font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">Farbe</label>
                        <input type="color" id="garment-color" value="${colorHex}"
                               style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);cursor:pointer;" />
                    </div>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Roughness</span>
                            <span id="garment-roughness-value">${roughness.toFixed(2)}</span>
                        </div>
                        <input type="range" id="garment-roughness" min="0" max="1" step="0.01" value="${roughness}" style="width:100%;cursor:pointer;" />
                    </div>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Metalness</span>
                            <span id="garment-metalness-value">${metalness.toFixed(2)}</span>
                        </div>
                        <input type="range" id="garment-metalness" min="0" max="1" step="0.01" value="${metalness}" style="width:100%;cursor:pointer;" />
                    </div>
                </div>

                <!-- Fit Properties -->
                <div style="margin-bottom:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);"><i class="fas fa-compress-arrows-alt"></i> Fit</h4>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Offset (Abstand)</span>
                            <span id="garment-offset-value">${offset.toFixed(3)}</span>
                        </div>
                        <input type="range" id="garment-offset" min="0" max="50" step="0.1" value="${offset * 1000}" style="width:100%;cursor:pointer;" />
                    </div>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Stiffness (Steifigkeit)</span>
                            <span id="garment-stiffness-value">${stiffness.toFixed(2)}</span>
                        </div>
                        <input type="range" id="garment-stiffness" min="0" max="100" step="1" value="${stiffness * 100}" style="width:100%;cursor:pointer;" />
                    </div>
                </div>

                <!-- Transform -->
                <div style="margin-bottom:16px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);"><i class="fas fa-arrows-alt"></i> Transform</h4>

                    <label style="display:block;font-size:0.75rem;color:var(--text-muted);margin-bottom:6px;">Position</label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;margin-bottom:12px;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="garment-pos-x" value="${pos.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="garment-pos-y" value="${pos.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="garment-pos-z" value="${pos.z.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Material-Änderungen wirken sofort<br>
                    <i class="fas fa-info-circle"></i> Fit-Änderungen erfordern Garment-Reload (TODO)
                </div>
            </div>
        `;

        // Wire up event listeners
        const colorPicker = document.getElementById('garment-color');
        const roughnessSlider = document.getElementById('garment-roughness');
        const roughnessValue = document.getElementById('garment-roughness-value');
        const metalnessSlider = document.getElementById('garment-metalness');
        const metalnessValue = document.getElementById('garment-metalness-value');
        const offsetSlider = document.getElementById('garment-offset');
        const offsetValue = document.getElementById('garment-offset-value');
        const stiffnessSlider = document.getElementById('garment-stiffness');
        const stiffnessValue = document.getElementById('garment-stiffness-value');
        const posX = document.getElementById('garment-pos-x');
        const posY = document.getElementById('garment-pos-y');
        const posZ = document.getElementById('garment-pos-z');

        if (colorPicker) {
            colorPicker.oninput = (e) => {
                mat.color.setHex(parseInt(e.target.value.substring(1), 16));
            };
        }

        if (roughnessSlider && roughnessValue) {
            roughnessSlider.oninput = (e) => {
                const val = parseFloat(e.target.value);
                mat.roughness = val;
                roughnessValue.textContent = val.toFixed(2);
            };
        }

        if (metalnessSlider && metalnessValue) {
            metalnessSlider.oninput = (e) => {
                const val = parseFloat(e.target.value);
                mat.metalness = val;
                metalnessValue.textContent = val.toFixed(2);
            };
        }

        // Offset and Stiffness: update display only (need refit to apply)
        if (offsetSlider && offsetValue) {
            offsetSlider.oninput = (e) => {
                const val = parseFloat(e.target.value) / 1000;
                offsetValue.textContent = val.toFixed(3);
                garmentMesh.userData.offset = val;
            };
        }

        if (stiffnessSlider && stiffnessValue) {
            stiffnessSlider.oninput = (e) => {
                const val = parseFloat(e.target.value) / 100;
                stiffnessValue.textContent = val.toFixed(2);
                garmentMesh.userData.stiffness = val;
            };
        }

        // Position: update garment position
        if (posX && posY && posZ) {
            const updatePos = () => {
                garmentMesh.position.set(
                    parseFloat(posX.value),
                    parseFloat(posY.value),
                    parseFloat(posZ.value)
                );
            };
            posX.oninput = updatePos;
            posY.oninput = updatePos;
            posZ.oninput = updatePos;
        }
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
