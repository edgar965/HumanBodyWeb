/**
 * Result-page 3D Character viewer — syncs to video.currentTime.
 *
 * Full controls: body type, morphs (via WebSocket), cloth template/builder/primitive,
 * model/rig/clothes toggles, face bones checkbox.
 * Default: Female_Caucasian with clothes.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { detectBVHFormat, retargetBVHToDefClip } from './retarget_hybrid.js?v=25';

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
// Material definitions (must match animations.js)
// =========================================================================
const BODY_MATERIALS = [
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },  // 0 Skin
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },  // 1 Censor
    { color: 0x111111, roughness: 0.8,  metalness: 0.0 },  // 2 Eyelash
    { color: 0x0a0a0a, roughness: 0.1,  metalness: 0.0 },  // 3 Pupil
    { color: 0xf4f0e8, roughness: 0.2,  metalness: 0.0 },  // 4 Sclera
    { color: 0xf4f0e8, roughness: 0.05, metalness: 0.0, opacity: 0.3, transparent: true },  // 5 Cornea
    { color: 0x4a7a9b, roughness: 0.15, metalness: 0.0 },  // 6 Iris
    { color: 0xb55a6a, roughness: 0.7,  metalness: 0.0 },  // 7 Tongue
    { color: 0xf0ece0, roughness: 0.3,  metalness: 0.0 },  // 8 Teeth
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },  // 9 Nails Hand
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },  // 10 Nails Feet
];

// =========================================================================
// Helpers
// =========================================================================
function base64ToFloat32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Float32Array(bytes.buffer);
}

function base64ToUint32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Uint32Array(bytes.buffer);
}

function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1];
        const z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

// =========================================================================
// Main export
// =========================================================================

/**
 * @param {Object} opts
 * @param {string} opts.canvasId  - id of the <canvas> element
 * @param {string} opts.videoId   - id of the <video> element (master clock)
 * @param {string} opts.bvhUrl    - URL to the job-specific BVH file
 * @param {string} opts.panelId   - id of the side panel container
 */
export async function initResultCharacter({ canvasId, videoId, bvhUrl, panelId, bodyTypeSelectId }) {
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

    // --- Renderer (false = don't override CSS width/height) ---
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h, false);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.6;

    // --- Scene ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    // --- Camera ---
    const camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    camera.position.set(0, 1.0, 3.5);

    // --- Controls ---
    const controls = new OrbitControls(camera, canvas);
    controls.target.set(0, 0.9, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 0.5;
    controls.maxDistance = 15;
    controls.update();

    // --- Lighting ---
    const keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
    keyLight.position.set(2, 4, -5);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
    fillLight.position.set(-3, 3, -4);
    scene.add(fillLight);

    const backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
    backLight.position.set(0, 4, 5);
    scene.add(backLight);

    const ambient = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambient);

    applySceneSettings(renderer, scene, camera, keyLight, fillLight, backLight, ambient);

    // --- Grid ---
    const grid = new THREE.GridHelper(4, 20, 0x333355, 0x222244);
    scene.add(grid);

    // --- State ---
    let bodyMesh = null;
    let bodyGeometry = null;
    let defSkeletonData = null;
    let skinWeightData = null;
    let defSkeleton = null;
    let isSkinned = false;
    let mixer = null;
    let currentAction = null;
    let currentBodyType = 'Female_Caucasian';
    let cachedBvhResult = null;
    let cachedBvhFormat = null;
    let bvhClipDuration = 0;
    let skinColors = {};
    let skeletonHelper = null;
    let rigVisible = false;
    let clothesVisible = true;

    // Cloth
    const clothMeshes = {};
    const gltfLoader = new GLTFLoader();

    // Hair
    let hairMesh = null;
    let hairColorData = {};

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

    // --- Render loop (sync to video) ---
    function animate() {
        requestAnimationFrame(animate);
        controls.update();

        if (mixer && video.duration && bvhClipDuration > 0) {
            // Reset action if clamped/paused (e.g. video replayed after ending)
            if (currentAction && currentAction.paused) {
                currentAction.reset();
                currentAction.play();
            }
            // Proportional mapping: BVH may have different FPS than video
            const progress = video.currentTime / video.duration;
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
                        reloadForBodyType(msg.body_type);
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

    // --- Load all data ---
    let morphData = null;
    let hairData = null;
    try {
        const [, , , morphResp, hairResp] = await Promise.all([
            loadMesh(currentBodyType),
            loadDefSkeleton(),
            loadSkinWeights(currentBodyType),
            fetch('/api/character/morphs/').then(r => r.json()),
            fetch('/api/character/hairstyles/').then(r => r.json()).catch(() => null),
        ]);
        morphData = morphResp;
        hairData = hairResp;
        if (morphData.skin_colors) skinColors = morphData.skin_colors;
        if (hairData && hairData.colors) hairColorData = hairData.colors;
    } catch (e) {
        console.error('[result_character] Data load failed:', e);
        if (loadingEl) loadingEl.textContent = 'Fehler beim Laden';
        return;
    }

    // Convert to skinned mesh
    if (bodyMesh && defSkeletonData && skinWeightData) {
        convertToDefSkinnedMesh();
    }

    // Apply initial skin color
    applySkinColor(currentBodyType);

    // Load BVH
    if (isSkinned) {
        loadBVH(bvhUrl);
    }

    // Connect WebSocket for morphs
    connectWebSocket();

    // Hide loading indicator
    if (loadingEl) loadingEl.style.display = 'none';

    // --- Populate external body type dropdown ---
    if (bodyTypeSelectId && morphData) {
        const extSelect = document.getElementById(bodyTypeSelectId);
        if (extSelect) {
            (morphData.body_types || []).forEach(bt => {
                const opt = document.createElement('option');
                opt.value = bt;
                opt.textContent = bt.replace(/_/g, ' ');
                if (bt === currentBodyType) opt.selected = true;
                extSelect.appendChild(opt);
            });
            extSelect.addEventListener('change', () => reloadForBodyType(extSelect.value));
        }
    }


    // --- Foot correction checkbox ---
    const footChk = document.getElementById('footCorrection');
    if (footChk) {
        footChk.addEventListener('change', () => {
            enableFootCorrection = footChk.checked;
            if (cachedBvhResult && cachedBvhFormat) {
                applyBvhRetarget(cachedBvhResult, cachedBvhFormat);
            }
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

    // Load default clothes + hair after skinning
    if (isSkinned) {
        loadCloth('tpl_TPL_TSHIRT', {
            method: 'template', template: 'TPL_TSHIRT',
            segments: 32, tightness: 0.5, top_extend: 0, bottom_extend: 0,
        });
        loadCloth('tpl_TPL_PANTS', {
            method: 'template', template: 'TPL_PANTS',
            segments: 32, tightness: 0.5, top_extend: 0, bottom_extend: 0,
        });
        // Load default hairstyle (ballerina, matching ModelWithClothes.py)
        if (hairData && hairData.hairstyles) {
            const defaultHair = hairData.hairstyles.find(h => h.name === 'ballerina')
                             || hairData.hairstyles[0];
            if (defaultHair) loadHair(defaultHair.url);
        }
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
                if (!skeletonHelper && defSkeleton) {
                    skeletonHelper = new THREE.SkeletonHelper(defSkeleton.rootBone);
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
        });
        toggleBar.appendChild(rigBtn);

        const clothBtn = el('button', 'rc-toggle-btn active');
        clothBtn.innerHTML = '<i class="fas fa-tshirt"></i> Kleider';
        clothBtn.addEventListener('click', () => {
            clothesVisible = !clothesVisible;
            for (const m of Object.values(clothMeshes)) {
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

        container.appendChild(toggleBar);

        // --- Body Type ---
        const btSection = makeSection('Body Type', true);
        const btSelect = el('select', 'rc-select');
        btSelect.id = 'rc-body-type';
        (data.body_types || []).forEach(bt => {
            const opt = document.createElement('option');
            opt.value = bt;
            opt.textContent = bt.replace(/_/g, ' ');
            if (bt === currentBodyType) opt.selected = true;
            btSelect.appendChild(opt);
        });
        btSelect.addEventListener('change', () => reloadForBodyType(btSelect.value));
        btSection.body.appendChild(btSelect);
        container.appendChild(btSection.el);

        // --- Morphs ---
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
                slider.min = -100; slider.max = 100; slider.value = 0; slider.step = 1;

                const valSpan = el('span', 'rc-slider-val');
                valSpan.textContent = '0';

                slider.addEventListener('input', () => {
                    valSpan.textContent = slider.value;
                    sendMorphThrottled(m.name, parseInt(slider.value) / 100.0);
                });

                row.append(label, slider, valSpan);
                catBody.appendChild(row);
            });

            catDiv.appendChild(catBody);
            morphSection.body.appendChild(catDiv);
        });
        container.appendChild(morphSection.el);

        // --- Cloth Template ---
        const clothSection = makeSection('Cloth - Template', true);

        // Template type select
        const tplRow = el('div', 'rc-slider-row');
        const tplLabel = el('label', ''); tplLabel.textContent = 'Template';
        const tplSelect = el('select', 'rc-select');
        tplSelect.id = 'rc-cloth-tpl-type';
        tplRow.append(tplLabel, tplSelect);
        clothSection.body.appendChild(tplRow);

        // Sliders
        const segSlider = makeSliderRow('Segments', 'rc-cloth-segments', 16, 64, 32, 2, v => v);
        const tightSlider = makeSliderRow('Tightness', 'rc-cloth-tightness', 0, 100, 50, 1, v => (v/100).toFixed(2));
        const topSlider = makeSliderRow('Top', 'rc-cloth-top', -30, 30, 0, 1, v => (v/100).toFixed(2) + ' m');
        const botSlider = makeSliderRow('Bottom', 'rc-cloth-bot', -30, 50, 0, 1, v => (v/100).toFixed(2) + ' m');

        clothSection.body.append(segSlider.row, tightSlider.row, topSlider.row, botSlider.row);

        // Color
        const colorRow = el('div', 'rc-slider-row');
        const colorLabel = el('label', ''); colorLabel.textContent = 'Color';
        const colorInput = document.createElement('input');
        colorInput.type = 'color'; colorInput.value = '#404870'; colorInput.id = 'rc-cloth-color';
        colorInput.style.cssText = 'width:40px;height:24px;border:none;cursor:pointer;';
        colorRow.append(colorLabel, colorInput);
        clothSection.body.appendChild(colorRow);

        // Buttons
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
        container.appendChild(clothSection.el);

        // Load cloth regions data to populate template select
        fetch('/api/character/cloth/regions/').then(r => r.json()).then(d => {
            (d.templates || []).forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.key; opt.textContent = t.label;
                tplSelect.appendChild(opt);
            });
        }).catch(() => {});
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
    // Body type switching
    // =====================================================================

    async function reloadForBodyType(newType) {
        if (newType === currentBodyType) return;
        currentBodyType = newType;

        // Update dropdowns if they exist
        const btSelect = document.getElementById('rc-body-type');
        if (btSelect && btSelect.value !== newType) btSelect.value = newType;
        if (bodyTypeSelectId) {
            const extSelect = document.getElementById(bodyTypeSelectId);
            if (extSelect && extSelect.value !== newType) extSelect.value = newType;
        }

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
        defSkeleton = null;
        isSkinned = false;
        if (skeletonHelper) { scene.remove(skeletonHelper); skeletonHelper = null; }

        // Remove clothes + hair (topology mismatch)
        removeAllCloth();
        removeHair();

        if (loadingEl) {
            loadingEl.style.display = '';
            loadingEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Lade ' + newType.replace(/_/g, ' ') + '...';
        }

        try {
            await Promise.all([
                loadMesh(newType),
                loadSkinWeights(newType),
            ]);

            if (bodyMesh && defSkeletonData && skinWeightData) {
                convertToDefSkinnedMesh();
            }

            applySkinColor(newType);
            wsSend({ type: 'body_type', value: newType });

            // Re-apply BVH from cache
            if (isSkinned && cachedBvhResult) {
                applyBvhRetarget(cachedBvhResult, cachedBvhFormat);
            }

            // Recreate default clothes + hair
            if (isSkinned) {
                if (!newType.startsWith('Male_')) {
                    loadCloth('tpl_TPL_TSHIRT', {
                        method: 'template', template: 'TPL_TSHIRT',
                        segments: 32, tightness: 0.5, top_extend: 0, bottom_extend: 0,
                    });
                    loadCloth('tpl_TPL_PANTS', {
                        method: 'template', template: 'TPL_PANTS',
                        segments: 32, tightness: 0.5, top_extend: 0, bottom_extend: 0,
                    });
                }
                // Reload hair
                if (hairData && hairData.hairstyles) {
                    const defaultHair = hairData.hairstyles.find(h => h.name === 'ballerina')
                                     || hairData.hairstyles[0];
                    if (defaultHair) loadHair(defaultHair.url);
                }
            }
        } catch (e) {
            console.error('[result_character] Body type switch failed:', e);
        }

        if (loadingEl) loadingEl.style.display = 'none';
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

    async function loadDefSkeleton() {
        try {
            const resp = await fetch('/api/character/def-skeleton/');
            if (resp.ok) {
                defSkeletonData = await resp.json();
                return true;
            }
        } catch (e) {
            console.warn('[result_character] DEF skeleton not available:', e);
        }
        return false;
    }

    async function loadSkinWeights(bodyType) {
        try {
            const resp = await fetch('/api/character/skin-weights/?body_type=' + encodeURIComponent(bodyType));
            if (resp.ok) {
                skinWeightData = await resp.json();
                return true;
            }
        } catch (e) {
            console.warn('[result_character] Skin weights not available:', e);
        }
        return false;
    }

    // =====================================================================
    // Skeleton building
    // =====================================================================

    function buildDefSkeleton(skelData, swData) {
        const skelByName = {};
        for (const b of skelData.bones) skelByName[b.name] = b;

        const bones = [];
        const boneByName = {};
        let rootBone = null;

        for (const name of swData.bone_names) {
            const bone = new THREE.Bone();
            bone.name = name.replace(/\./g, '_');
            bones.push(bone);
            boneByName[name] = bone;
        }

        for (let i = 0; i < swData.bone_names.length; i++) {
            const name = swData.bone_names[i];
            const bone = bones[i];
            const data = skelByName[name];
            if (!data) continue;

            const p = data.local_position;
            bone.position.set(p[0], p[2], -p[1]);
            const q = data.local_quaternion;
            bone.quaternion.set(q[1], q[3], -q[2], q[0]);

            if (data.parent && boneByName[data.parent]) {
                boneByName[data.parent].add(bone);
            } else {
                if (!rootBone) rootBone = bone;
            }
        }

        for (let i = 0; i < bones.length; i++) {
            const name = swData.bone_names[i];
            const data = skelByName[name];
            if (!data) continue;
            if (!data.parent && bones[i] !== rootBone) {
                if (rootBone) rootBone.add(bones[i]);
            }
        }

        if (!rootBone && bones.length > 0) rootBone = bones[0];
        rootBone.updateWorldMatrix(true, true);
        const skeleton = new THREE.Skeleton(bones);
        return { skeleton, rootBone, bones, boneByName };
    }

    function convertToDefSkinnedMesh() {
        if (isSkinned || !bodyMesh || !bodyGeometry) return;

        bodyGeometry = bodyGeometry.clone();

        const vCount = bodyGeometry.attributes.position.count;
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

        bodyGeometry.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
        bodyGeometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));

        defSkeleton = buildDefSkeleton(defSkeletonData, skinWeightData);

        const mat = bodyMesh.material;
        const pos = bodyMesh.position.clone();
        scene.remove(bodyMesh);

        bodyMesh = new THREE.SkinnedMesh(bodyGeometry, mat);
        bodyMesh.position.copy(pos);
        bodyMesh.add(defSkeleton.rootBone);
        bodyMesh.bind(defSkeleton.skeleton);
        scene.add(bodyMesh);
        isSkinned = true;
    }

    // =====================================================================
    // Skin color
    // =====================================================================

    function applySkinColor(bodyType) {
        if (!bodyMesh) return;
        const parts = bodyType.split('_');
        const ethnicity = parts.length >= 2 ? parts.slice(1).join('_') : bodyType;
        const rgb = skinColors[ethnicity];
        if (!rgb) return;
        const mats = Array.isArray(bodyMesh.material) ? bodyMesh.material : [bodyMesh.material];
        for (let i = 0; i < Math.min(2, mats.length); i++) {
            mats[i].color.setRGB(
                Math.pow(rgb[0], 1/2.2),
                Math.pow(rgb[1], 1/2.2),
                Math.pow(rgb[2], 1/2.2)
            );
        }
    }

    // =====================================================================
    // Cloth
    // =====================================================================

    async function loadCloth(key, params) {
        if (!isSkinned || !defSkeleton) return;

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

            const colorPicker = document.getElementById('rc-cloth-color');
            const matColor = colorPicker
                ? new THREE.Color(colorPicker.value)
                : new THREE.Color(data.color[0], data.color[1], data.color[2]);

            const mat = new THREE.MeshStandardMaterial({
                color: matColor, roughness: 0.8, metalness: 0.0,
                side: THREE.DoubleSide,
            });

            let mesh;
            if (data.skin_indices && data.skin_weights) {
                const siBuf = base64ToFloat32(data.skin_indices);
                const swBuf = base64ToFloat32(data.skin_weights);
                geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
                geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
                mesh = new THREE.SkinnedMesh(geo, mat);
                mesh.bind(defSkeleton.skeleton, bodyMesh.bindMatrix);
            } else {
                mesh = new THREE.Mesh(geo, mat);
            }

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
    // Hair
    // =====================================================================

    function _findHeadBoneIndex() {
        if (!skinWeightData) return -1;
        const names = skinWeightData.bone_names;
        for (const tryName of ['DEF-spine.006', 'DEF-spine.005', 'DEF-head']) {
            const idx = names.indexOf(tryName);
            if (idx >= 0) return idx;
        }
        return -1;
    }

    function _skinifyHairGroup(gltfScene, headBoneIdx) {
        const meshChildren = [];
        gltfScene.traverse(child => {
            if (child.isMesh) meshChildren.push(child);
        });
        const group = new THREE.Group();
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
            child.updateWorldMatrix(true, false);
            skinnedChild.applyMatrix4(child.matrixWorld);
            skinnedChild.bind(defSkeleton.skeleton, bodyMesh.bindMatrix);
            group.add(skinnedChild);
        }
        return group;
    }

    function loadHair(url) {
        removeHair();
        if (!isSkinned || !defSkeleton || !skinWeightData) return;

        gltfLoader.load(url, (gltf) => {
            let hairGroup = gltf.scene;
            const headBoneIdx = _findHeadBoneIndex();
            if (headBoneIdx >= 0) {
                hairGroup = _skinifyHairGroup(hairGroup, headBoneIdx);
            }
            hairMesh = hairGroup;

            // Apply stored hair color
            if (Object.keys(hairColorData).length > 0) {
                const firstName = Object.keys(hairColorData)[0];
                applyHairColorToMesh(hairMesh, firstName);
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

    function applyHairColorToMesh(obj, colorName) {
        const rgb = hairColorData[colorName];
        if (!rgb) return;
        const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
        obj.traverse(child => {
            if (child.isMesh && child.material) {
                const mats = Array.isArray(child.material) ? child.material : [child.material];
                mats.forEach(m => { m.color.copy(color); });
            }
        });
    }

    // =====================================================================
    // BVH loading + retarget
    // =====================================================================

    let enableFootCorrection = false;

    function applyBvhRetarget(bvhResult, format) {
        // Stop old mixer first
        if (mixer) { mixer.stopAllAction(); mixer = null; currentAction = null; }

        const retargetOpts = { bodyMesh };
        if (enableFootCorrection) retargetOpts.footCorrection = true;
        const clip = retargetBVHToDefClip(bvhResult, defSkeleton, format, retargetOpts);

        mixer = new THREE.AnimationMixer(bodyMesh);
        currentAction = mixer.clipAction(clip);
        currentAction.setLoop(THREE.LoopOnce);
        currentAction.clampWhenFinished = true;
        currentAction.play();
        bvhClipDuration = clip.duration;
    }

    /**
     * Position camera in front of the character based on actual retargeted bone positions.
     * Uses DEF-thigh.L/R to determine the lateral axis, then cross(up, right) = forward.
     */
    function positionCameraAfterRetarget() {
        if (!defSkeleton || !mixer || !bodyMesh) return;

        // Apply frame 0 so bones have their actual animated positions
        mixer.setTime(0);
        bodyMesh.updateWorldMatrix(true, true);
        defSkeleton.rootBone.updateWorldMatrix(true, true);

        const thighL = defSkeleton.boneByName['DEF-thigh.L'];
        const thighR = defSkeleton.boneByName['DEF-thigh.R'];
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
        const spine = defSkeleton.boneByName['DEF-spine.003']
                   || defSkeleton.boneByName['DEF-spine.001']
                   || defSkeleton.boneByName['DEF-spine'];
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

    function loadBVH(url) {
        const loader = new BVHLoader();
        loader.load(url, (result) => {
            const bones = result.skeleton.bones;
            if (bones.length === 0) return;

            const format = detectBVHFormat(bones);
            cachedBvhResult = result;
            cachedBvhFormat = format;

            applyBvhRetarget(result, format);
            positionCameraAfterRetarget();

            console.log(`[result_character] BVH loaded: ${format}, ${result.clip.duration.toFixed(1)}s`);
        }, undefined, (err) => {
            console.error('[result_character] BVH load error:', err);
        });
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
