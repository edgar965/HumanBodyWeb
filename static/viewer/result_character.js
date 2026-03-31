/**
 * Result-page 3D Character viewer — syncs to video.currentTime.
 *
 * Full controls: model preset, morphs (via WebSocket), cloth template/builder/primitive,
 * model/rig/clothes toggles, face bones checkbox.
 * Default: loaded from settings API (default_model_result preset).
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { fetchRetargetedClipForJob, fetchMergedClipForJob } from './retarget_hybrid.js?v=32';
import { buildRigifySkeleton } from './rigify_skeleton_builder.js?v=2';
import {
    base64ToFloat32, base64ToUint32, blenderToThreeCoords,
    sharedState, BODY_MATERIALS,
    loadRigifySkeleton, loadSkinWeights, loadSkinColors, loadHairColors,
    computeSkinAttributes, applySkinColorToMaterials,
    findHeadBoneIndex, skinifyHairGroup, applyHairColor,
    skinifyMesh, createSceneSetup,
} from './character_core.js?v=1';

// =========================================================================
// Tone mapping lookup
// =========================================================================
const TONE_MAPPINGS = {
    ACESFilmic: THREE.ACESFilmicToneMapping,
    Linear:     THREE.LinearToneMapping,
    Reinhard:   THREE.ReinhardToneMapping,
    Cineon:     THREE.CineonToneMapping,
    None:       THREE.NoToneMapping
};

// =========================================================================
// Main export
// =========================================================================

/**
 * @param {Object} opts
 * @param {string} opts.canvasId  - id of the <canvas> element
 * @param {string} opts.videoId   - id of the <video> element (master clock)
 * @param {string} opts.bvhUrl    - URL to the job-specific BVH file
 * @param {string} opts.panelId   - id of the side panel container
 * @param {string} opts.modelSelectId - id of the header model preset <select>
 */
export async function initResultCharacter({ canvasId, videoId, bvhUrl, bvhFaceUrl, jobId, panelId, modelSelectId }) {
    const canvas = document.getElementById(canvasId);
    const video  = document.getElementById(videoId);
    const loadingEl = document.getElementById('characterLoading');
    const panel = panelId ? document.getElementById(panelId) : null;
    if (!canvas || !video) {
        console.error('[result_character] Missing elements:', { canvas: !!canvas, video: !!video });
        return;
    }

    // Viewport wrapper has fixed CSS height (500px) — use it for sizing
    const viewport = canvas.parentElement;
    const w = viewport.clientWidth;
    const h = viewport.clientHeight || 500;

    // --- Scene setup (shared with scene_config.js) ---
    const { renderer, scene, camera, controls, keyLight, fillLight, backLight, ambient, grid }
        = createSceneSetup(canvas);
    window._debugScene = scene;  // DEBUG: expose for Playwright comparison

    applySceneSettings(renderer, scene, camera, keyLight, fillLight, backLight, ambient);

    // --- State (shared data from character_core.js, local rendering state here) ---
    let bodyMesh = null;
    let bodyGeometry = null;
    let rigifySkeleton = null;
    let isSkinned = false;
    let mixer = null;
    let currentAction = null;
    let currentBodyType = 'Female_Caucasian';
    let currentPresetName = '';
    let bvhClipDuration = 0;
    let skeletonHelper = null;
    let rigVisible = false;
    let clothesVisible = true;
    let enableFootCorrection = false;
    let deltaNormMode = undefined;  // undefined = auto, true = on, false = off

    // Cloth
    const clothMeshes = {};
    const gltfLoader = new GLTFLoader();

    // Hair
    let hairMesh = null;

    // Convenience aliases for shared state (read via sharedState.*)
    const ss = sharedState;

    // Garment meshes (MH garments, separate from cloth templates)
    const garmentMeshes = {};

    // Current morph/meta state (from preset) — used for garment fit + WS resync
    let currentMorphs = {};
    let currentMeta = {};

    // --- Resize ---
    function onResize() {
        const cw = viewport.clientWidth;
        const ch = viewport.clientHeight || 500;
        renderer.setSize(cw, ch, false);
        camera.aspect = cw / ch;
        camera.updateProjectionMatrix();
    }
    window.addEventListener('resize', onResize);
    if (typeof ResizeObserver !== 'undefined') {
        new ResizeObserver(onResize).observe(viewport);
    }

    // --- Render loop (sync to video or bvh_player fallback clock) ---
    function _videoOK() {
        return video.duration > 0 && isFinite(video.duration) && !isNaN(video.duration);
    }

    function animate() {
        requestAnimationFrame(animate);
        controls.update();

        if (mixer && bvhClipDuration > 0) {
            // Get progress from video or bvh_player's fallback clock
            let progress;
            if (_videoOK()) {
                progress = video.currentTime / video.duration;
            } else if (typeof window.bvhPlayerProgress === 'number') {
                progress = window.bvhPlayerProgress;
            } else {
                progress = 0;
            }

            // Reset action if clamped/paused (e.g. video replayed after ending)
            if (currentAction && currentAction.paused) {
                currentAction.reset();
                currentAction.play();
            }
            // Proportional mapping: BVH may have different FPS than video
            mixer.setTime(progress * bvhClipDuration);
        }

        renderer.render(scene, camera);
    }
    animate();

    // --- WebSocket for morphs ---
    let ws = null;
    let wsReady = false;
    let morphTimer = null;
    let pendingMorphs = {};

    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const url = `${protocol}://${window.location.host}/ws/character/`;
        ws = new WebSocket(url);
        ws.binaryType = 'arraybuffer';

        ws.onopen = () => {
            wsReady = true;
            wsSend({ type: 'body_type', value: currentBodyType });
            // Re-sync morphs + meta from current preset
            if (Object.keys(currentMorphs).length > 0) {
                wsSend({ type: 'morph_batch', morphs: currentMorphs });
            }
            for (const [name, val] of Object.entries(currentMeta)) {
                if (Math.abs(val) > 0.001) {
                    wsSend({ type: 'meta', name, value: val });
                }
            }
        };
        ws.onclose = () => {
            wsReady = false;
            setTimeout(connectWebSocket, 3000);
        };
        ws.onerror = () => {};
        ws.onmessage = (event) => {
            if (event.data instanceof ArrayBuffer) {
                updateMeshVertices(event.data);
            } else {
                try {
                    const msg = JSON.parse(event.data);
                    if (msg.type === 'reload_mesh') {
                        _reloadBodyMesh(msg.body_type);
                    }
                } catch (e) { /* ignore */ }
            }
        };
    }

    function wsSend(msg) {
        if (ws && wsReady) ws.send(JSON.stringify(msg));
    }

    function sendMorphThrottled(key, value) {
        pendingMorphs[key] = value;
        if (!morphTimer) {
            morphTimer = setTimeout(() => {
                if (Object.keys(pendingMorphs).length === 1) {
                    const [k, v] = Object.entries(pendingMorphs)[0];
                    wsSend({ type: 'morph', key: k, value: v });
                } else {
                    wsSend({ type: 'morph_batch', morphs: pendingMorphs });
                }
                pendingMorphs = {};
                morphTimer = null;
            }, 33);
        }
    }

    function updateMeshVertices(float32Buffer) {
        if (!bodyGeometry) return;
        const positions = bodyGeometry.attributes.position;
        const newData = new Float32Array(float32Buffer);
        blenderToThreeCoords(newData);
        positions.array.set(newData);
        positions.needsUpdate = true;
        bodyGeometry.computeBoundingSphere();
    }

    // --- Fetch default preset name from settings ---
    let defaultPresetName = 'femaleWithClothes';
    try {
        const settingsResp = await fetch('/api/settings/humanbody/');
        const settingsData = await settingsResp.json();
        if (settingsData.result) defaultPresetName = settingsData.result;
    } catch (e) {
        console.warn('[result_character] Failed to fetch settings, using default preset');
    }

    // --- Fetch preset data ---
    let presetData = null;
    try {
        const presetResp = await fetch(`/api/character/model/${encodeURIComponent(defaultPresetName)}/`);
        if (presetResp.ok) {
            presetData = await presetResp.json();
            if (presetData.body_type) currentBodyType = presetData.body_type;
            currentPresetName = defaultPresetName;
            currentMorphs = presetData.morphs || {};
            currentMeta = presetData.meta || {};
        }
    } catch (e) {
        console.warn('[result_character] Failed to fetch preset:', defaultPresetName);
    }

    // --- Load all data ---
    let morphData = null;
    let hairData = null;
    try {
        const [, , , morphResp, hairResp] = await Promise.all([
            loadMesh(currentBodyType),
            loadRigifySkeleton(),
            loadSkinWeights(currentBodyType),
            fetch('/api/character/morphs/').then(r => r.json()),
            fetch('/api/character/hairstyles/').then(r => r.json()).catch(() => null),
        ]);
        morphData = morphResp;
        hairData = hairResp;
        if (morphData.skin_colors) ss.skinColors = morphData.skin_colors;
        if (hairData && hairData.colors) ss.hairColorData = hairData.colors;
    } catch (e) {
        console.error('[result_character] Data load failed:', e);
        if (loadingEl) loadingEl.textContent = 'Fehler beim Laden';
        return;
    }

    // Convert to skinned mesh
    if (bodyMesh && ss.rigifySkeletonData && ss.skinWeightData) {
        convertToRigifySkinnedMesh();
    }

    // Apply initial skin color
    applySkinColor(currentBodyType);

    // Load BVH (hybrid mode loads two BVHs and merges them)
    if (isSkinned) {
        loadBVH();
    }

    // Connect WebSocket for morphs
    connectWebSocket();

    // Hide loading indicator
    if (loadingEl) loadingEl.style.display = 'none';

    // --- Populate model preset dropdown (header) ---
    if (modelSelectId) {
        const extSelect = document.getElementById(modelSelectId);
        if (extSelect) {
            try {
                const modelsResp = await fetch('/api/character/models/');
                const modelsData = await modelsResp.json();
                extSelect.innerHTML = '';
                (modelsData.presets || []).forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.name;
                    opt.textContent = p.label || p.name;
                    if (p.name === currentPresetName) opt.selected = true;
                    extSelect.appendChild(opt);
                });
                extSelect.addEventListener('change', () => reloadForPreset(extSelect.value));
            } catch (e) {
                console.warn('[result_character] Failed to load model presets list');
            }
        }
    }


    // --- Foot correction checkbox ---
    const footChk = document.getElementById('footCorrection');
    if (footChk) {
        footChk.addEventListener('change', () => {
            enableFootCorrection = footChk.checked;
            if (isSkinned) loadBVH();
        });
    }

    // --- Delta normalization select ---
    const deltaNormSel = document.getElementById('deltaNormSelect');
    if (deltaNormSel) {
        deltaNormSel.addEventListener('change', () => {
            const v = deltaNormSel.value;
            deltaNormMode = v === 'auto' ? undefined : v === '1';
            if (isSkinned) loadBVH();
        });
    }

    // --- Hair toggle button (header) ---
    const btnHair = document.getElementById('btnToggleHair');
    if (btnHair) {
        btnHair.addEventListener('click', () => {
            if (hairMesh) {
                hairMesh.visible = !hairMesh.visible;
                btnHair.classList.toggle('active', hairMesh.visible);
            }
        });
    }

    // --- Build UI panel ---
    if (panel && morphData) {
        buildControlPanel(panel, morphData);
    }

    // Load preset's clothes + hair + garments after skinning
    if (isSkinned && presetData) {
        loadPresetClothAndHair(presetData);
    } else if (isSkinned) {
        // Fallback: hardcoded defaults if preset fetch failed
        loadCloth('tpl_TPL_TSHIRT', {
            method: 'template', template: 'TPL_TSHIRT',
            segments: 32, tightness: 0.5, top_extend: 0, bottom_extend: 0,
        });
        loadCloth('tpl_TPL_PANTS', {
            method: 'template', template: 'TPL_PANTS',
            segments: 32, tightness: 0.5, top_extend: 0, bottom_extend: 0,
        });
        if (hairData && hairData.hairstyles) {
            const defaultHair = hairData.hairstyles.find(h => h.name === 'ballerina')
                             || hairData.hairstyles[0];
            if (defaultHair) loadHair(defaultHair.url);
        }
    }

    // =====================================================================
    // Preset loading
    // =====================================================================

    /**
     * Load cloth, hair, and garments from a preset data object.
     * Removes all existing cloth/hair/garments first.
     */
    function loadPresetClothAndHair(preset) {
        removeAllCloth();
        removeAllGarments();
        removeHair();

        // 1. Load cloth templates
        if (preset.cloth && preset.cloth.length > 0) {
            for (const c of preset.cloth) {
                const tpl = c.template || 'TPL_TSHIRT';
                const params = {
                    method: 'template',
                    template: tpl,
                    segments: c.segments || 32,
                    tightness: c.tightness !== undefined ? c.tightness : 0.5,
                    top_extend: c.top_extend || 0,
                    bottom_extend: c.bottom_extend || 0,
                };
                if (c.color) params.color = c.color;
                loadCloth(`tpl_${tpl}`, params, c.color, true);
            }
        }

        // 2. Load hairstyle
        if (preset.hair_style && preset.hair_style.url) {
            loadHair(preset.hair_style.url);
            // Apply hair color after a short delay for the GLTF to load
            if (preset.hair_style.color && ss.hairColorData[preset.hair_style.color]) {
                setTimeout(() => {
                    if (hairMesh) applyHairColor(hairMesh, preset.hair_style.color, ss.hairColorData);
                }, 1000);
            }
        } else if (hairData && hairData.hairstyles) {
            // Fallback: load first available hairstyle
            const defaultHair = hairData.hairstyles.find(h => h.name === 'ballerina')
                             || hairData.hairstyles[0];
            if (defaultHair) loadHair(defaultHair.url);
        }

        // 3. Load MH garments
        if (preset.garments && preset.garments.length > 0) {
            const loadGarments = async () => {
                for (const g of preset.garments) {
                    await loadGarment(g.id, {
                        offset: g.offset || 0.006,
                        stiffness: g.stiffness || 0.8,
                        color: g.color,
                        roughness: g.roughness,
                        metalness: g.metalness,
                    });
                }
            };
            // Delay slightly to let body mesh settle
            setTimeout(() => loadGarments(), 800);
        }
    }

    /**
     * Switch to a different model preset.
     * Fetches preset data, reloads body if type changed, then loads cloth/hair/garments.
     */
    async function reloadForPreset(presetName) {
        if (presetName === currentPresetName) return;

        if (loadingEl) {
            loadingEl.style.display = '';
            loadingEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Lade Modell...';
        }

        try {
            const resp = await fetch(`/api/character/model/${encodeURIComponent(presetName)}/`);
            if (!resp.ok) {
                console.error('[result_character] Failed to load preset:', presetName);
                if (loadingEl) loadingEl.style.display = 'none';
                return;
            }
            const preset = await resp.json();
            currentPresetName = presetName;

            // Update header dropdown
            if (modelSelectId) {
                const extSelect = document.getElementById(modelSelectId);
                if (extSelect && extSelect.value !== presetName) extSelect.value = presetName;
            }
            // Update side panel dropdown
            const panelSelect = document.getElementById('rc-model-preset');
            if (panelSelect && panelSelect.value !== presetName) panelSelect.value = presetName;

            const newBodyType = preset.body_type || 'Female_Caucasian';

            // Update morph/meta state from new preset
            currentMorphs = preset.morphs || {};
            currentMeta = preset.meta || {};

            if (newBodyType !== currentBodyType) {
                // Body type changed — full mesh reload
                await _reloadBodyMesh(newBodyType);
            } else {
                // Same body type — just remove old cloth/hair/garments
                removeAllCloth();
                removeAllGarments();
                removeHair();
            }

            // Send morphs + meta to server for the new preset
            if (Object.keys(currentMorphs).length > 0) {
                wsSend({ type: 'morph_batch', morphs: currentMorphs });
            }
            for (const [name, val] of Object.entries(currentMeta)) {
                if (Math.abs(val) > 0.001) {
                    wsSend({ type: 'meta', name, value: val });
                }
            }

            // Update morph sliders in UI
            document.querySelectorAll('#rc-panel input[type="range"][data-morph]').forEach(s => {
                const v = currentMorphs[s.dataset.morph] || 0;
                s.value = Math.round(v * 100);
                if (s.nextElementSibling) s.nextElementSibling.textContent = String(Math.round(v * 100));
            });

            // Load preset's cloth/hair/garments
            if (isSkinned) {
                loadPresetClothAndHair(preset);
            }
        } catch (e) {
            console.error('[result_character] Preset switch failed:', e);
        }

        if (loadingEl) loadingEl.style.display = 'none';
    }

    // =====================================================================
    // UI Panel Builder
    // =====================================================================

    function buildControlPanel(container, data) {
        container.innerHTML = '';

        // --- Toggle buttons bar ---
        const toggleBar = el('div', 'rc-toggle-bar');

        const modelBtn = el('button', 'rc-toggle-btn active');
        modelBtn.innerHTML = '<i class="fas fa-user"></i> Model';
        modelBtn.addEventListener('click', () => {
            if (bodyMesh) bodyMesh.visible = !bodyMesh.visible;
            modelBtn.classList.toggle('active', bodyMesh && bodyMesh.visible);
        });
        toggleBar.appendChild(modelBtn);

        const rigBtn = el('button', 'rc-toggle-btn');
        rigBtn.innerHTML = '<i class="fas fa-bone"></i> Rig';
        rigBtn.addEventListener('click', () => {
            rigVisible = !rigVisible;
            if (rigVisible) {
                if (!skeletonHelper && rigifySkeleton) {
                    skeletonHelper = new THREE.SkeletonHelper(rigifySkeleton.rootBone);
                    skeletonHelper.material.depthTest = false;
                    skeletonHelper.material.depthWrite = false;
                    skeletonHelper.material.color.set(0x00ffaa);
                    skeletonHelper.material.linewidth = 2;
                    skeletonHelper.renderOrder = 999;
                    scene.add(skeletonHelper);
                }
                if (skeletonHelper) skeletonHelper.visible = true;
            } else {
                if (skeletonHelper) skeletonHelper.visible = false;
            }
            rigBtn.classList.toggle('active', rigVisible);
            // Also toggle 2D skeleton overlay on the video panel
            if (typeof window.setBvhOverlayVisible === 'function') {
                window.setBvhOverlayVisible(rigVisible);
            }
        });
        toggleBar.appendChild(rigBtn);

        const clothBtn = el('button', 'rc-toggle-btn active');
        clothBtn.innerHTML = '<i class="fas fa-tshirt"></i> Kleider';
        clothBtn.addEventListener('click', () => {
            clothesVisible = !clothesVisible;
            for (const m of Object.values(clothMeshes)) {
                if (m) m.visible = clothesVisible;
            }
            for (const m of Object.values(garmentMeshes)) {
                if (m) m.visible = clothesVisible;
            }
            clothBtn.classList.toggle('active', clothesVisible);
        });
        toggleBar.appendChild(clothBtn);

        const hairBtn = el('button', 'rc-toggle-btn active');
        hairBtn.innerHTML = '<i class="fas fa-hat-wizard"></i> Haar';
        hairBtn.addEventListener('click', () => {
            if (hairMesh) {
                hairMesh.visible = !hairMesh.visible;
                hairBtn.classList.toggle('active', hairMesh.visible);
            }
        });
        toggleBar.appendChild(hairBtn);

        // Video floating window toggle
        const floatingEl = document.getElementById('floatingVideo');
        if (floatingEl) {
            const videoBtn = el('button', 'rc-toggle-btn active');
            videoBtn.innerHTML = '<i class="fas fa-video"></i> Original';
            videoBtn.addEventListener('click', () => {
                floatingEl.classList.toggle('hidden');
                videoBtn.classList.toggle('active', !floatingEl.classList.contains('hidden'));
            });
            toggleBar.appendChild(videoBtn);

            // Close button hides + deactivates toggle
            const closeBtn = document.getElementById('floatingVideoClose');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    floatingEl.classList.add('hidden');
                    videoBtn.classList.remove('active');
                });
            }

            // Drag by titlebar
            const titlebar = document.getElementById('floatingVideoTitlebar');
            if (titlebar) {
                let dragX = 0, dragY = 0, startX = 0, startY = 0;
                titlebar.addEventListener('mousedown', (e) => {
                    if (e.target.closest('.floating-video-close')) return;
                    e.preventDefault();
                    startX = e.clientX; startY = e.clientY;
                    const onMove = (ev) => {
                        dragX = ev.clientX - startX; dragY = ev.clientY - startY;
                        startX = ev.clientX; startY = ev.clientY;
                        const rect = floatingEl.getBoundingClientRect();
                        floatingEl.style.left = rect.left + dragX + 'px';
                        floatingEl.style.top = rect.top + dragY + 'px';
                        floatingEl.style.bottom = 'auto';
                    };
                    const onUp = () => {
                        document.removeEventListener('mousemove', onMove);
                        document.removeEventListener('mouseup', onUp);
                    };
                    document.addEventListener('mousemove', onMove);
                    document.addEventListener('mouseup', onUp);
                });
            }

            // Resize handle (corner drag — width + height)
            const resizeHandle = document.getElementById('floatingVideoResize');
            if (resizeHandle) {
                resizeHandle.addEventListener('mousedown', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const startW = floatingEl.offsetWidth;
                    const startH = floatingEl.offsetHeight;
                    const startMX = e.clientX;
                    const startMY = e.clientY;
                    const onMove = (ev) => {
                        const newW = Math.max(200, startW + (ev.clientX - startMX));
                        const newH = Math.max(120, startH + (ev.clientY - startMY));
                        floatingEl.style.width = newW + 'px';
                        floatingEl.style.height = newH + 'px';
                    };
                    const onUp = () => {
                        document.removeEventListener('mousemove', onMove);
                        document.removeEventListener('mouseup', onUp);
                    };
                    document.addEventListener('mousemove', onMove);
                    document.addEventListener('mouseup', onUp);
                });
            }

            // Start visible
        }

        // 3D viewport fullscreen toggle + resize
        const charContainer = document.getElementById('resultCharacter');
        const charViewport = document.getElementById('characterViewport');
        const fsBtn = document.getElementById('btnViewportFullscreen');
        const resizeHandle = document.getElementById('viewportResizeHandle');

        if (fsBtn && charContainer && charViewport) {
            let isFullscreen = true; // starts fullscreen
            let customHeight = null;

            fsBtn.addEventListener('click', () => {
                isFullscreen = !isFullscreen;
                if (isFullscreen) {
                    charContainer.classList.add('result-character-fullscreen');
                    charViewport.style.height = '';
                    customHeight = null;
                    fsBtn.innerHTML = '<i class="fas fa-expand"></i>';
                } else {
                    charContainer.classList.remove('result-character-fullscreen');
                    charViewport.style.height = (customHeight || 500) + 'px';
                    fsBtn.innerHTML = '<i class="fas fa-compress"></i>';
                }
                // Trigger Three.js resize
                window.dispatchEvent(new Event('resize'));
            });

            if (resizeHandle) {
                resizeHandle.addEventListener('mousedown', (e) => {
                    e.preventDefault();
                    const startY = e.clientY;
                    const startH = charViewport.offsetHeight;
                    // Switch to manual mode on drag
                    if (isFullscreen) {
                        isFullscreen = false;
                        charContainer.classList.remove('result-character-fullscreen');
                        fsBtn.innerHTML = '<i class="fas fa-compress"></i>';
                    }
                    const onMove = (ev) => {
                        const newH = Math.max(250, startH + (ev.clientY - startY));
                        charViewport.style.height = newH + 'px';
                        customHeight = newH;
                        window.dispatchEvent(new Event('resize'));
                    };
                    const onUp = () => {
                        document.removeEventListener('mousemove', onMove);
                        document.removeEventListener('mouseup', onUp);
                    };
                    document.addEventListener('mousemove', onMove);
                    document.addEventListener('mouseup', onUp);
                });
            }
        }

        container.appendChild(toggleBar);

        // --- Tab bar ---
        const tabBar = el('div', 'rc-tab-bar');
        const tabEigen = el('div', 'rc-tab active');
        tabEigen.textContent = 'Eigenschaften';
        tabEigen.dataset.tab = 'eigenschaften';
        const tabAssets = el('div', 'rc-tab');
        tabAssets.textContent = 'Assets';
        tabAssets.dataset.tab = 'assets';
        const tabAnim = el('div', 'rc-tab');
        tabAnim.textContent = 'Animation';
        tabAnim.dataset.tab = 'animation';
        const tabScene = el('div', 'rc-tab');
        tabScene.textContent = 'Szene';
        tabScene.dataset.tab = 'szene';
        tabBar.append(tabEigen, tabAssets, tabAnim, tabScene);
        container.appendChild(tabBar);

        // --- Tab content ---
        const tabContent = el('div', 'rc-tab-content');

        // === Eigenschaften tab ===
        const eigenPane = el('div', 'rc-tab-pane active');
        eigenPane.id = 'rc-tab-eigenschaften';

        // Model Preset
        const presetSection = makeSection('Modell', true);
        const presetSelect = el('select', 'rc-select');
        presetSelect.id = 'rc-model-preset';
        fetch('/api/character/models/').then(r => r.json()).then(modelsData => {
            (modelsData.presets || []).forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.name;
                opt.textContent = p.label || p.name;
                if (p.name === currentPresetName) opt.selected = true;
                presetSelect.appendChild(opt);
            });
        }).catch(() => {});
        presetSelect.addEventListener('change', () => reloadForPreset(presetSelect.value));
        presetSection.body.appendChild(presetSelect);
        eigenPane.appendChild(presetSection.el);

        // Morphs
        const morphSection = makeSection('Morphs', false);
        const resetBtn = el('button', 'rc-btn-sm');
        resetBtn.textContent = 'Reset';
        resetBtn.addEventListener('click', () => {
            morphSection.body.querySelectorAll('input[type="range"]').forEach(s => {
                s.value = 0;
                s.nextElementSibling.textContent = '0';
            });
            wsSend({ type: 'reset', body_type: currentBodyType });
        });
        morphSection.header.appendChild(resetBtn);

        const cats = {};
        (data.morphs || []).forEach(m => {
            if (!cats[m.category]) cats[m.category] = [];
            cats[m.category].push(m);
        });

        (data.categories || []).sort().forEach(cat => {
            const morphs = cats[cat];
            if (!morphs || morphs.length === 0) return;

            const catDiv = el('div', 'rc-morph-cat');
            const catHeader = el('div', 'rc-morph-cat-header');
            catHeader.textContent = `${cat} (${morphs.length})`;
            catHeader.addEventListener('click', () => catDiv.classList.toggle('open'));
            catDiv.appendChild(catHeader);

            const catBody = el('div', 'rc-morph-cat-body');
            morphs.forEach(m => {
                const row = el('div', 'rc-slider-row');
                const label = el('label', '');
                label.textContent = m.name.split('_').slice(1).join(' ') || m.name;
                label.title = m.name;

                const slider = document.createElement('input');
                slider.type = 'range';
                slider.min = -100; slider.max = 100; slider.step = 1;
                slider.dataset.morph = m.name;
                // Initialize from current preset morphs
                const presetVal = currentMorphs[m.name] || 0;
                slider.value = Math.round(presetVal * 100);

                const valSpan = el('span', 'rc-slider-val');
                valSpan.textContent = slider.value;

                slider.addEventListener('input', () => {
                    valSpan.textContent = slider.value;
                    const v = parseInt(slider.value) / 100.0;
                    currentMorphs[m.name] = v;
                    sendMorphThrottled(m.name, v);
                });

                row.append(label, slider, valSpan);
                catBody.appendChild(row);
            });

            catDiv.appendChild(catBody);
            morphSection.body.appendChild(catDiv);
        });
        eigenPane.appendChild(morphSection.el);
        tabContent.appendChild(eigenPane);

        // === Assets tab ===
        const assetsPane = el('div', 'rc-tab-pane');
        assetsPane.id = 'rc-tab-assets';

        // Cloth Template
        const clothSection = makeSection('Cloth - Template', true);

        const tplRow = el('div', 'rc-slider-row');
        const tplLabel = el('label', ''); tplLabel.textContent = 'Template';
        const tplSelect = el('select', 'rc-select');
        tplSelect.id = 'rc-cloth-tpl-type';
        tplRow.append(tplLabel, tplSelect);
        clothSection.body.appendChild(tplRow);

        const segSlider = makeSliderRow('Segments', 'rc-cloth-segments', 16, 64, 32, 2, v => v);
        const tightSlider = makeSliderRow('Tightness', 'rc-cloth-tightness', 0, 100, 50, 1, v => (v/100).toFixed(2));
        const topSlider = makeSliderRow('Top', 'rc-cloth-top', -30, 30, 0, 1, v => (v/100).toFixed(2) + ' m');
        const botSlider = makeSliderRow('Bottom', 'rc-cloth-bot', -30, 50, 0, 1, v => (v/100).toFixed(2) + ' m');

        clothSection.body.append(segSlider.row, tightSlider.row, topSlider.row, botSlider.row);

        const colorRow = el('div', 'rc-slider-row');
        const colorLabel = el('label', ''); colorLabel.textContent = 'Color';
        const colorInput = document.createElement('input');
        colorInput.type = 'color'; colorInput.value = '#404870'; colorInput.id = 'rc-cloth-color';
        colorInput.style.cssText = 'width:40px;height:24px;border:none;cursor:pointer;';
        colorRow.append(colorLabel, colorInput);
        clothSection.body.appendChild(colorRow);

        const clothBtns = el('div', 'rc-btn-row');
        const createBtn = el('button', 'rc-btn'); createBtn.innerHTML = '<i class="fas fa-plus"></i> Create';
        const updateBtn = el('button', 'rc-btn'); updateBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Update';
        const deleteBtn = el('button', 'rc-btn rc-btn-danger'); deleteBtn.innerHTML = '<i class="fas fa-times"></i>';
        const removeAllBtn = el('button', 'rc-btn rc-btn-danger'); removeAllBtn.innerHTML = '<i class="fas fa-trash"></i>';

        function getTplParams() {
            return {
                method: 'template',
                template: tplSelect.value || 'TPL_TSHIRT',
                segments: parseInt(segSlider.input.value),
                tightness: parseInt(tightSlider.input.value) / 100,
                top_extend: parseInt(topSlider.input.value) / 100,
                bottom_extend: parseInt(botSlider.input.value) / 100,
            };
        }

        createBtn.addEventListener('click', () => {
            const p = getTplParams();
            loadCloth(`tpl_${p.template}`, p);
        });
        updateBtn.addEventListener('click', () => {
            const p = getTplParams();
            const key = `tpl_${p.template}`;
            if (clothMeshes[key]) loadCloth(key, p);
        });
        deleteBtn.addEventListener('click', () => {
            const tpl = tplSelect.value || 'TPL_TSHIRT';
            removeClothRegion(`tpl_${tpl}`);
        });
        removeAllBtn.addEventListener('click', () => removeAllCloth());

        clothBtns.append(createBtn, updateBtn, deleteBtn, removeAllBtn);
        clothSection.body.appendChild(clothBtns);
        assetsPane.appendChild(clothSection.el);

        fetch('/api/character/cloth/regions/').then(r => r.json()).then(d => {
            (d.templates || []).forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.key; opt.textContent = t.label;
                tplSelect.appendChild(opt);
            });
        }).catch(() => {});

        tabContent.appendChild(assetsPane);

        // === Animation tab ===
        const animPane = el('div', 'rc-tab-pane');
        animPane.id = 'rc-tab-animation';
        const animEmpty = el('div', 'rc-tab-empty');
        animEmpty.innerHTML = '<i class="fas fa-running" style="font-size:1.5rem;margin-bottom:8px;display:block;"></i>Animation wird vom Video gesteuert';
        animPane.appendChild(animEmpty);
        tabContent.appendChild(animPane);

        // === Szene tab ===
        const scenePane = el('div', 'rc-tab-pane');
        scenePane.id = 'rc-tab-szene';
        const sceneEmpty = el('div', 'rc-tab-empty');
        sceneEmpty.innerHTML = '<i class="fas fa-lightbulb" style="font-size:1.5rem;margin-bottom:8px;display:block;"></i>Szene-Einstellungen';
        scenePane.appendChild(sceneEmpty);
        tabContent.appendChild(scenePane);

        container.appendChild(tabContent);

        // --- Tab switching ---
        tabBar.querySelectorAll('.rc-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                tabBar.querySelectorAll('.rc-tab').forEach(t => t.classList.remove('active'));
                tabContent.querySelectorAll('.rc-tab-pane').forEach(p => p.classList.remove('active'));
                tab.classList.add('active');
                const pane = document.getElementById('rc-tab-' + tab.dataset.tab);
                if (pane) pane.classList.add('active');
            });
        });
    }

    // =====================================================================
    // UI Helpers
    // =====================================================================

    function el(tag, cls) {
        const e = document.createElement(tag);
        if (cls) e.className = cls;
        return e;
    }

    function makeSection(title, open) {
        const div = el('div', 'rc-section' + (open ? '' : ' collapsed'));
        const header = el('div', 'rc-section-header');
        header.innerHTML = `<span>${title}</span><span class="rc-chevron">&#9660;</span>`;
        header.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') return;
            div.classList.toggle('collapsed');
        });
        const body = el('div', 'rc-section-body');
        div.append(header, body);
        return { el: div, header, body };
    }

    function makeSliderRow(label, id, min, max, val, step, fmt) {
        const row = el('div', 'rc-slider-row');
        const lab = el('label', ''); lab.textContent = label;
        const input = document.createElement('input');
        input.type = 'range'; input.id = id;
        input.min = min; input.max = max; input.value = val; input.step = step;
        const valSpan = el('span', 'rc-slider-val');
        valSpan.textContent = fmt(val);
        input.addEventListener('input', () => { valSpan.textContent = fmt(parseInt(input.value)); });
        row.append(lab, input, valSpan);
        return { row, input, valSpan };
    }

    // =====================================================================
    // Body mesh reload (internal — used by preset switching)
    // =====================================================================

    async function _reloadBodyMesh(newType) {
        if (newType === currentBodyType) return;
        currentBodyType = newType;

        // Stop animation
        if (mixer) { mixer.stopAllAction(); mixer = null; currentAction = null; }

        // Remove old mesh
        if (bodyMesh) {
            scene.remove(bodyMesh);
            if (bodyMesh.geometry) bodyMesh.geometry.dispose();
            const mats = Array.isArray(bodyMesh.material) ? bodyMesh.material : [bodyMesh.material];
            mats.forEach(m => m.dispose());
            bodyMesh = null;
        }
        bodyGeometry = null;
        rigifySkeleton = null;
        isSkinned = false;
        if (skeletonHelper) { scene.remove(skeletonHelper); skeletonHelper = null; }

        // Remove clothes + hair + garments (topology mismatch)
        removeAllCloth();
        removeAllGarments();
        removeHair();

        try {
            await Promise.all([
                loadMesh(newType),
                loadSkinWeights(newType),
            ]);

            if (bodyMesh && ss.rigifySkeletonData && ss.skinWeightData) {
                convertToRigifySkinnedMesh();
            }

            applySkinColor(newType);
            wsSend({ type: 'body_type', value: newType });

            // Re-apply BVH via server retarget
            if (isSkinned) {
                await loadBVH();
            }
        } catch (e) {
            console.error('[result_character] Body type switch failed:', e);
        }
    }

    // =====================================================================
    // Data loading functions
    // =====================================================================

    async function loadMesh(bodyType) {
        try {
            const resp = await fetch('/api/character/mesh/?body_type=' + encodeURIComponent(bodyType));
            const data = await resp.json();
            if (data.error) { console.error('[result_character] mesh error:', data.error); return false; }

            const vertBuf = base64ToFloat32(data.vertices);
            blenderToThreeCoords(vertBuf);
            const positions = new THREE.BufferAttribute(vertBuf, 3);

            let index = null;
            if (data.faces) {
                const faceBuf = base64ToUint32(data.faces);
                index = new THREE.BufferAttribute(faceBuf, 1);
            }

            let uvAttr = null;
            if (data.uvs) {
                const uvBuf = base64ToFloat32(data.uvs);
                uvAttr = new THREE.BufferAttribute(uvBuf, 2);
            }

            const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
                color: d.color, roughness: d.roughness, metalness: d.metalness,
                side: THREE.DoubleSide,
                transparent: d.transparent || false,
                opacity: d.opacity !== undefined ? d.opacity : 1.0,
            }));

            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', positions);
            if (index) geo.setIndex(index);
            if (uvAttr) geo.setAttribute('uv', uvAttr);

            const groups = data.groups || [];

            if (data.normals) {
                const normalBuf = base64ToFloat32(data.normals);
                blenderToThreeCoords(normalBuf);
                geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
            } else {
                geo.computeVertexNormals();
            }

            if (index && groups.length > 0) {
                for (const g of groups) geo.addGroup(g.start, g.count, g.materialIndex);
                bodyMesh = new THREE.Mesh(geo, materials);
            } else {
                bodyMesh = new THREE.Mesh(geo, materials[0]);
            }

            bodyGeometry = geo;
            scene.add(bodyMesh);

            applySceneSkinSettings(bodyMesh);
            return true;
        } catch (e) {
            console.error('[result_character] Failed to load mesh:', e);
            return false;
        }
    }

    // loadRigifySkeleton(), loadSkinWeights() — imported from character_core.js

    function convertToRigifySkinnedMesh() {
        if (isSkinned || !bodyMesh || !bodyGeometry) return;
        bodyGeometry = bodyGeometry.clone();
        const { skinIndices, skinWeights } = computeSkinAttributes(bodyGeometry, ss.skinWeightData);
        bodyGeometry.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
        bodyGeometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));
        rigifySkeleton = buildRigifySkeleton(ss.rigifySkeletonData, ss.skinWeightData);
        const mat = bodyMesh.material;
        const pos = bodyMesh.position.clone();
        scene.remove(bodyMesh);
        bodyMesh = new THREE.SkinnedMesh(bodyGeometry, mat);
        bodyMesh.position.copy(pos);
        bodyMesh.add(rigifySkeleton.rootBone);
        bodyMesh.bind(rigifySkeleton.skeleton);
        scene.add(bodyMesh);
        isSkinned = true;
    }

    function applySkinColor(bodyType) {
        if (!bodyMesh) return;
        const mats = Array.isArray(bodyMesh.material) ? bodyMesh.material : [bodyMesh.material];
        applySkinColorToMaterials(mats, bodyType, ss.skinColors);
    }

    // =====================================================================
    // Cloth (templates)
    // =====================================================================

    async function loadCloth(key, params, presetColor, useApiColor = false) {
        if (!isSkinned || !rigifySkeleton) return;

        try {
            const qs = Object.entries(params)
                .map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
            const resp = await fetch(`/api/character/cloth/?${qs}`);
            const data = await resp.json();
            if (data.error) { console.error('Cloth error:', data.error); return; }

            removeClothRegion(key);

            const vertBuf = base64ToFloat32(data.vertices);
            blenderToThreeCoords(vertBuf);
            const faceBuf = base64ToUint32(data.faces);
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);

            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
            geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

            // Color priority: preset > API default > color picker (manual)
            let matColor;
            if (presetColor) {
                matColor = new THREE.Color(presetColor);
            } else if (useApiColor && data.color) {
                matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
            } else {
                const colorPicker = document.getElementById('rc-cloth-color');
                matColor = colorPicker
                    ? new THREE.Color(colorPicker.value)
                    : new THREE.Color(data.color[0], data.color[1], data.color[2]);
            }

            const mat = new THREE.MeshStandardMaterial({
                color: matColor, roughness: 0.8, metalness: 0.0,
                side: THREE.DoubleSide,
            });

            const skInfo = (isSkinned && rigifySkeleton) ? {
                skeleton: rigifySkeleton.skeleton, bindMatrix: bodyMesh.bindMatrix
            } : null;
            const mesh = skinifyMesh(geo, mat, skInfo, data);

            mesh.visible = clothesVisible;
            clothMeshes[key] = mesh;
            scene.add(mesh);
        } catch (e) {
            console.error('Failed to load cloth:', e);
        }
    }

    function removeClothRegion(key) {
        const m = clothMeshes[key];
        if (m) {
            scene.remove(m);
            m.geometry.dispose();
            m.material.dispose();
            delete clothMeshes[key];
        }
    }

    function removeAllCloth() {
        for (const key of Object.keys(clothMeshes)) {
            removeClothRegion(key);
        }
    }

    // =====================================================================
    // MH Garments
    // =====================================================================

    async function loadGarment(garmentId, opts = {}) {
        if (!isSkinned || !rigifySkeleton) return;

        try {
            const offset = opts.offset !== undefined ? opts.offset : 0.006;
            const stiffness = opts.stiffness !== undefined ? opts.stiffness : 0.8;

            // Build color params — only send if explicitly provided, else server uses template default
            let hasColor = false;
            let cr = 0, cg = 0, cb = 0;
            if (Array.isArray(opts.color)) {
                cr = opts.color[0]; cg = opts.color[1]; cb = opts.color[2];
                hasColor = true;
            } else if (typeof opts.color === 'string') {
                const c = new THREE.Color(opts.color);
                cr = c.r; cg = c.g; cb = c.b;
                hasColor = true;
            }

            let qs = `garment_id=${encodeURIComponent(garmentId)}&body_type=${encodeURIComponent(currentBodyType)}`;
            qs += `&offset=${offset}&stiffness=${stiffness}`;
            if (hasColor) {
                qs += `&color_r=${cr.toFixed(3)}&color_g=${cg.toFixed(3)}&color_b=${cb.toFixed(3)}`;
            }
            // Include current morph + meta values for correct body-shape fitting
            for (const [k, v] of Object.entries(currentMorphs)) {
                if (Math.abs(v) > 0.001) qs += `&morph_${k}=${v}`;
            }
            for (const [k, v] of Object.entries(currentMeta)) {
                if (Math.abs(v) > 0.001) qs += `&meta_${k}=${v}`;
            }

            const resp = await fetch(`/api/character/garment/fit/?${qs}`);
            const data = await resp.json();
            if (data.error) {
                console.error('Garment fit error:', data.error);
                return;
            }

            removeGarment(garmentId);

            const vertBuf = base64ToFloat32(data.vertices);
            blenderToThreeCoords(vertBuf);
            const faceBuf = base64ToUint32(data.faces);

            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
            geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
            geo.computeVertexNormals();

            const matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
            const roughness = opts.roughness !== undefined ? opts.roughness : 0.8;
            const metalness = opts.metalness !== undefined ? opts.metalness : 0.0;
            const mat = new THREE.MeshStandardMaterial({
                color: matColor, roughness, metalness,
                side: THREE.DoubleSide,
                polygonOffset: true,
                polygonOffsetFactor: -1,
                polygonOffsetUnit: -1,
            });

            const skInfo = (isSkinned && rigifySkeleton) ? {
                skeleton: rigifySkeleton.skeleton, bindMatrix: bodyMesh.bindMatrix
            } : null;
            const mesh = skinifyMesh(geo, mat, skInfo, data);

            mesh.visible = clothesVisible;
            garmentMeshes[garmentId] = mesh;
            scene.add(mesh);
            console.log('[result_character] Garment loaded:', garmentId);
        } catch (e) {
            console.error('Failed to load garment:', e);
        }
    }

    function removeGarment(garmentId) {
        const m = garmentMeshes[garmentId];
        if (m) {
            scene.remove(m);
            m.geometry.dispose();
            m.material.dispose();
            delete garmentMeshes[garmentId];
        }
    }

    function removeAllGarments() {
        for (const key of Object.keys(garmentMeshes)) {
            removeGarment(key);
        }
    }

    // =====================================================================
    // Hair
    // =====================================================================

    // _findHeadBoneIndex, _skinifyHairGroup, applyHairColor — from character_core.js

    function loadHair(url) {
        removeHair();
        if (!isSkinned || !rigifySkeleton || !ss.skinWeightData) return;

        gltfLoader.load(url, (gltf) => {
            let hairGroup = gltf.scene;
            const headBoneIdx = findHeadBoneIndex(ss.skinWeightData);
            if (headBoneIdx >= 0) {
                hairGroup = skinifyHairGroup(hairGroup, headBoneIdx,
                    rigifySkeleton.skeleton, bodyMesh.bindMatrix);
            }
            hairMesh = hairGroup;

            // Apply stored hair color
            if (Object.keys(ss.hairColorData).length > 0) {
                const firstName = Object.keys(ss.hairColorData)[0];
                applyHairColor(hairMesh, firstName, ss.hairColorData);
            }
            scene.add(hairMesh);
            console.log('[result_character] Hair loaded:', url);
        }, undefined, (err) => {
            console.error('[result_character] Failed to load hair:', err);
        });
    }

    function removeHair() {
        if (hairMesh) {
            scene.remove(hairMesh);
            hairMesh.traverse(child => {
                if (child.isMesh) {
                    child.geometry.dispose();
                    if (child.material) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach(m => m.dispose());
                        } else {
                            child.material.dispose();
                        }
                    }
                }
            });
            hairMesh = null;
        }
    }

    // =====================================================================
    // BVH loading + retarget
    // =====================================================================

    async function applyBvhRetarget() {
        console.log('[result_character] applyBvhRetarget called, jobId=', jobId, 'rigifySkeleton=', !!rigifySkeleton, 'bodyMesh=', !!bodyMesh);
        if (mixer) { mixer.stopAllAction(); mixer = null; currentAction = null; }

        let bodyH = 1.68;
        if (bodyMesh) {
            const bb = new THREE.Box3().setFromObject(bodyMesh);
            if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;
        }
        console.log('[result_character] bodyHeight=', bodyH);

        const clip = await fetchRetargetedClipForJob(jobId, rigifySkeleton, {
            bodyHeight: bodyH,
            footCorrection: enableFootCorrection,
            deltaNorm: deltaNormMode,
        });

        console.log('[result_character] clip:', clip.duration, 'sec,', clip.tracks.length, 'tracks');

        mixer = new THREE.AnimationMixer(bodyMesh);
        currentAction = mixer.clipAction(clip);
        currentAction.setLoop(THREE.LoopOnce);
        currentAction.clampWhenFinished = true;
        currentAction.play();
        bvhClipDuration = clip.duration;
        console.log('[result_character] Animation playing, bvhClipDuration=', bvhClipDuration);
    }

    /**
     * Position camera in front of the character based on actual retargeted bone positions.
     * Uses DEF-thigh.L/R to determine the lateral axis, then cross(up, right) = forward.
     */
    function positionCameraAfterRetarget() {
        if (!rigifySkeleton || !mixer || !bodyMesh) return;

        // Apply frame 0 so bones have their actual animated positions
        mixer.setTime(0);
        bodyMesh.updateWorldMatrix(true, true);
        rigifySkeleton.rootBone.updateWorldMatrix(true, true);

        const thighL = rigifySkeleton.boneByName['DEF-thigh.L'];
        const thighR = rigifySkeleton.boneByName['DEF-thigh.R'];
        if (!thighL || !thighR) return;

        const posL = new THREE.Vector3();
        const posR = new THREE.Vector3();
        thighL.getWorldPosition(posL);
        thighR.getWorldPosition(posR);

        // Character's right direction: from left thigh to right thigh
        const right = new THREE.Vector3().subVectors(posR, posL);
        right.y = 0;
        if (right.lengthSq() < 0.0001) return;
        right.normalize();

        // Forward = up × right (character's facing direction)
        const up = new THREE.Vector3(0, 1, 0);
        const forward = new THREE.Vector3().crossVectors(up, right).normalize();

        // Compute character center from spine
        const spine = rigifySkeleton.boneByName['DEF-spine.003']
                   || rigifySkeleton.boneByName['DEF-spine.001']
                   || rigifySkeleton.boneByName['DEF-spine'];
        const center = new THREE.Vector3();
        if (spine) {
            spine.getWorldPosition(center);
        } else {
            center.addVectors(posL, posR).multiplyScalar(0.5);
        }

        const dist = 3.5;
        camera.position.set(
            center.x + forward.x * dist,
            center.y + 0.1,
            center.z + forward.z * dist
        );
        controls.target.copy(center);
        controls.update();
    }

    async function loadBVH() {
        try {
            if (bvhFaceUrl) {
                // Hybrid mode: body + face merged on server
                await applyHybridRetarget();
            } else {
                // Single BVH mode
                await applyBvhRetarget();
            }
            positionCameraAfterRetarget();
        } catch (err) {
            console.error('[result_character] BVH retarget error:', err);
            // Show error visually
            if (loadingEl) {
                loadingEl.style.display = '';
                loadingEl.innerHTML = '<span style="color:#e74c3c"><i class="fas fa-exclamation-triangle"></i> Retarget: ' + (err.message || err) + '</span>';
            }
        }
    }

    async function applyHybridRetarget() {
        if (mixer) { mixer.stopAllAction(); mixer = null; currentAction = null; }

        let bodyH = 1.68;
        if (bodyMesh) {
            const bb = new THREE.Box3().setFromObject(bodyMesh);
            if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;
        }

        const clip = await fetchMergedClipForJob(jobId, rigifySkeleton, {
            bodyHeight: bodyH,
            footCorrection: enableFootCorrection,
            deltaNorm: deltaNormMode,
        });

        mixer = new THREE.AnimationMixer(bodyMesh);
        currentAction = mixer.clipAction(clip);
        currentAction.setLoop(THREE.LoopOnce);
        currentAction.clampWhenFinished = true;
        currentAction.play();
        bvhClipDuration = clip.duration;
    }

    // =====================================================================
    // Scene settings from localStorage
    // =====================================================================

    function applySceneSettings(rend, sc, cam, kl, fl, bl, amb) {
        const saved = localStorage.getItem('humanbody_scene_settings');
        if (!saved) return;
        try {
            const s = JSON.parse(saved);
            if (s.lighting) {
                if (s.lighting.key) {
                    kl.intensity = s.lighting.key.intensity;
                    kl.color.set(s.lighting.key.color);
                    kl.position.set(...s.lighting.key.pos);
                }
                if (s.lighting.fill) {
                    fl.intensity = s.lighting.fill.intensity;
                    fl.color.set(s.lighting.fill.color);
                    fl.position.set(...s.lighting.fill.pos);
                }
                if (s.lighting.back) {
                    bl.intensity = s.lighting.back.intensity;
                    bl.color.set(s.lighting.back.color);
                    bl.position.set(...s.lighting.back.pos);
                }
                if (s.lighting.ambient) {
                    amb.intensity = s.lighting.ambient.intensity;
                    amb.color.set(s.lighting.ambient.color);
                }
            }
            if (s.renderer) {
                if (s.renderer.toneMapping && TONE_MAPPINGS[s.renderer.toneMapping] !== undefined) {
                    rend.toneMapping = TONE_MAPPINGS[s.renderer.toneMapping];
                }
                if (s.renderer.exposure !== undefined) {
                    rend.toneMappingExposure = s.renderer.exposure;
                }
                if (s.renderer.background) {
                    sc.background.set(s.renderer.background);
                }
            }
            if (s.camera && s.camera.fov) {
                cam.fov = s.camera.fov;
                cam.updateProjectionMatrix();
            }
        } catch (e) {
            console.warn('[result_character] Failed to load scene settings:', e);
        }
    }

    function applySceneSkinSettings(mesh) {
        const saved = localStorage.getItem('humanbody_scene_settings');
        const mat = mesh && mesh.material
            ? (Array.isArray(mesh.material) ? mesh.material[0] : mesh.material)
            : null;
        if (!saved || !mat) return;
        try {
            const s = JSON.parse(saved);
            if (s.skin) {
                // NOTE: skin COLOR is NOT applied from scene settings —
                // it comes from SKIN_COLORS per ethnicity (body type).
                if (s.skin.roughness !== undefined) mat.roughness = s.skin.roughness;
                if (s.skin.metalness !== undefined) mat.metalness = s.skin.metalness;
            }
        } catch (e) { /* ignore */ }
    }
}
