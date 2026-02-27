/**
 * Dual-Character Compare Viewer — slim factory for side-by-side comparison.
 * Each createViewer() call returns an independent Three.js instance with
 * own scene, camera, renderer, WebSocket, and morph controls.
 *
 * No cloth, hair, animations, rig — pure morph comparison.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ---------------------------------------------------------------------------
// Material definitions (same as viewer.js)
// ---------------------------------------------------------------------------
const BODY_MATERIALS = [
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },   // 0 Skin
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },   // 1 Censor
    { color: 0x111111, roughness: 0.8,  metalness: 0.0 },   // 2 Eyelash
    { color: 0x0a0a0a, roughness: 0.1,  metalness: 0.0 },   // 3 Pupil
    { color: 0xf4f0e8, roughness: 0.2,  metalness: 0.0 },   // 4 Sclera
    { color: 0xf4f0e8, roughness: 0.05, metalness: 0.0, opacity: 0.3, transparent: true }, // 5 Cornea
    { color: 0x4a7a9b, roughness: 0.15, metalness: 0.0 },   // 6 Iris
    { color: 0xb55a6a, roughness: 0.7,  metalness: 0.0 },   // 7 Tongue
    { color: 0xf0ece0, roughness: 0.3,  metalness: 0.0 },   // 8 Teeth
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },   // 9 Nails Hand
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },   // 10 Nails Feet
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function base64ToFloat32(b64) {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new Float32Array(bytes.buffer);
}

function base64ToUint32(b64) {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new Uint32Array(bytes.buffer);
}

/** Blender (X-right, Y-forward, Z-up) → Three.js (X-right, Y-up, Z-toward-camera) */
function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1];
        const z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------
/**
 * @param {Object} config
 * @param {string} config.canvasId   - Canvas element id
 * @param {string} config.panelId    - Panel container element id
 * @param {string} config.apiPrefix  - e.g. '/api/character-test'
 * @param {string} config.wsPath     - e.g. '/ws/character-test/'
 * @param {string} config.defaultBodyType - e.g. 'Caucasian' or 'Male_Caucasian'
 * @param {string} config.label      - Display label
 */
export function createViewer(config) {
    const { canvasId, panelId, apiPrefix, wsPath, defaultBodyType, label } = config;

    let scene, camera, renderer, controls;
    let bodyMesh = null, bodyGeometry = null;
    let vertexCount = 0;
    let ws = null, wsReady = false;
    let clock = new THREE.Clock();
    let frameCount = 0, fpsAccum = 0;

    // Morph data (stored for reset)
    let morphData = null;
    let skinColorMap = {};

    // Throttle morph sends
    let morphTimer = null;
    let pendingMorphs = {};

    // DOM refs (created dynamically)
    let statusSpan, vertexSpan, fpsSpan;
    let bodyTypeSelect;
    let metaSliderEls = {};
    let morphsPanel;
    let skinColorInput, skinRoughSlider, skinRoughVal, skinMetalSlider, skinMetalVal;

    // ----- WebSocket helpers -----
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

    // ----- Mesh -----
    function updateMeshVertices(float32Buffer) {
        if (!bodyGeometry) return;
        const positions = bodyGeometry.attributes.position;
        const newData = new Float32Array(float32Buffer);
        blenderToThreeCoords(newData);
        positions.array.set(newData);
        positions.needsUpdate = true;
        bodyGeometry.computeBoundingSphere();
    }

    function getSkinMat() {
        if (!bodyMesh || !bodyMesh.material) return null;
        return Array.isArray(bodyMesh.material) ? bodyMesh.material[0] : bodyMesh.material;
    }

    function syncSkinUI(mat) {
        if (skinColorInput) skinColorInput.value = '#' + mat.color.getHexString();
        if (skinRoughSlider) { skinRoughSlider.value = Math.round(mat.roughness * 100); skinRoughVal.textContent = mat.roughness.toFixed(2); }
        if (skinMetalSlider) { skinMetalSlider.value = Math.round(mat.metalness * 100); skinMetalVal.textContent = mat.metalness.toFixed(2); }
    }

    async function loadMesh() {
        try {
            const resp = await fetch(`${apiPrefix}/mesh/`);
            const data = await resp.json();
            if (data.error) { console.error(`[${label}] mesh error:`, data.error); return; }

            vertexCount = data.vertex_count;
            if (vertexSpan) vertexSpan.textContent = vertexCount.toLocaleString();

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

            let geo = new THREE.BufferGeometry();
            geo.setAttribute('position', positions);
            if (index) geo.setIndex(index);
            if (uvAttr) geo.setAttribute('uv', uvAttr);

            if (data.normals) {
                const normalBuf = base64ToFloat32(data.normals);
                blenderToThreeCoords(normalBuf);
                geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
            } else {
                geo.computeVertexNormals();
            }

            const groups = data.groups || [];
            if (index && groups.length > 0) {
                for (const g of groups) geo.addGroup(g.start, g.count, g.materialIndex);
                bodyMesh = new THREE.Mesh(geo, materials);
            } else {
                bodyMesh = new THREE.Mesh(geo, materials[0]);
            }

            bodyGeometry = geo;
            scene.add(bodyMesh);

            if (vertexSpan) vertexSpan.textContent = geo.attributes.position.count.toLocaleString();
        } catch (e) {
            console.error(`[${label}] Failed to load mesh:`, e);
        }
    }

    async function reloadMesh(bodyType) {
        console.log(`[${label}] Reloading mesh for`, bodyType);
        if (bodyMesh) {
            scene.remove(bodyMesh);
            bodyMesh.geometry?.dispose();
            bodyMesh = null;
            bodyGeometry = null;
        }
        try {
            const resp = await fetch(`${apiPrefix}/mesh/?body_type=${encodeURIComponent(bodyType)}`);
            const data = await resp.json();
            if (data.error) { console.error(`[${label}] mesh error:`, data.error); return; }

            vertexCount = data.vertex_count;
            if (vertexSpan) vertexSpan.textContent = vertexCount.toLocaleString();

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

            let geo = new THREE.BufferGeometry();
            geo.setAttribute('position', positions);
            if (index) geo.setIndex(index);
            if (uvAttr) geo.setAttribute('uv', uvAttr);

            if (data.normals) {
                const normalBuf = base64ToFloat32(data.normals);
                blenderToThreeCoords(normalBuf);
                geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
            } else {
                geo.computeVertexNormals();
            }

            const groups = data.groups || [];
            if (index && groups.length > 0) {
                for (const g of groups) geo.addGroup(g.start, g.count, g.materialIndex);
                bodyMesh = new THREE.Mesh(geo, materials);
            } else {
                bodyMesh = new THREE.Mesh(geo, materials[0]);
            }

            bodyGeometry = geo;
            scene.add(bodyMesh);
            if (vertexSpan) vertexSpan.textContent = geo.attributes.position.count.toLocaleString();
        } catch (e) {
            console.error(`[${label}] Failed to reload mesh:`, e);
        }
    }

    // ----- Morphs UI -----
    async function loadMorphs() {
        try {
            const resp = await fetch(`${apiPrefix}/morphs/`);
            const data = await resp.json();
            morphData = data;
            skinColorMap = data.skin_colors || {};

            // Body type dropdown
            data.body_types.forEach(bt => {
                const opt = document.createElement('option');
                opt.value = bt;
                opt.textContent = bt.replace(/_/g, ' ');
                bodyTypeSelect.appendChild(opt);
            });
            // Select default
            if (defaultBodyType && data.body_types.includes(defaultBodyType)) {
                bodyTypeSelect.value = defaultBodyType;
            }
            bodyTypeSelect.addEventListener('change', () => {
                wsSend({ type: 'body_type', value: bodyTypeSelect.value });
                // Update skin color based on ethnicity
                const parts = bodyTypeSelect.value.split('_');
                const ethnicity = parts[1] || parts[0];
                const colors = skinColorMap[ethnicity];
                const mat = getSkinMat();
                if (colors && mat) {
                    mat.color.setRGB(
                        Math.pow(colors[0], 1/2.2),
                        Math.pow(colors[1], 1/2.2),
                        Math.pow(colors[2], 1/2.2)
                    );
                    syncSkinUI(mat);
                }
            });

            // Meta sliders
            const metaNames = ['age', 'mass', 'tone', 'height'];
            metaNames.forEach(name => {
                const els = metaSliderEls[name];
                if (!els) return;
                const meta = data.meta_sliders?.[name];
                if (meta) {
                    els.slider.min = meta.min;
                    els.slider.max = meta.max;
                    els.slider.value = meta.default;
                    els.val.textContent = meta.default;
                }
                els.slider.addEventListener('input', () => {
                    const displayVal = parseInt(els.slider.value);
                    els.val.textContent = displayVal;
                    const min = parseInt(els.slider.min), max = parseInt(els.slider.max);
                    const neutral = (min + max) / 2;
                    const half = (max - min) / 2;
                    const internal = half ? (displayVal - neutral) / half : 0;
                    wsSend({ type: 'meta', name: name, value: internal });
                });
            });

            // Skin color
            if (skinColorInput) {
                skinColorInput.addEventListener('input', e => {
                    const mat = getSkinMat();
                    if (mat) mat.color.set(e.target.value);
                });
            }
            if (skinRoughSlider) {
                skinRoughSlider.addEventListener('input', () => {
                    const v = parseFloat(skinRoughSlider.value) / 100;
                    skinRoughVal.textContent = v.toFixed(2);
                    const mat = getSkinMat();
                    if (mat) mat.roughness = v;
                });
            }
            if (skinMetalSlider) {
                skinMetalSlider.addEventListener('input', () => {
                    const v = parseFloat(skinMetalSlider.value) / 100;
                    skinMetalVal.textContent = v.toFixed(2);
                    const mat = getSkinMat();
                    if (mat) mat.metalness = v;
                });
            }

            // Group morphs by category
            const morphCategories = {};
            data.morphs.forEach(m => {
                if (!morphCategories[m.category]) morphCategories[m.category] = [];
                morphCategories[m.category].push(m);
            });

            morphsPanel.innerHTML = '';

            data.categories.sort().forEach(cat => {
                const morphs = morphCategories[cat];
                if (!morphs || morphs.length === 0) return;

                const div = document.createElement('div');
                div.className = 'morph-category';

                const header = document.createElement('div');
                header.className = 'morph-category-header';
                header.textContent = `${cat} (${morphs.length})`;
                header.addEventListener('click', () => div.classList.toggle('open'));
                div.appendChild(header);

                const body = document.createElement('div');
                body.className = 'morph-category-body';

                morphs.forEach(m => {
                    const row = document.createElement('div');
                    row.className = 'slider-row';

                    const lbl = document.createElement('label');
                    lbl.textContent = m.name.split('_').slice(1).join(' ') || m.name;
                    lbl.title = m.name;

                    const slider = document.createElement('input');
                    slider.type = 'range';
                    slider.min = -100;
                    slider.max = 100;
                    slider.value = 0;
                    slider.step = 1;
                    slider.dataset.morph = m.name;

                    const valSpan = document.createElement('span');
                    valSpan.className = 'slider-val';
                    valSpan.textContent = '0';

                    slider.addEventListener('input', () => {
                        const v = parseInt(slider.value) / 100.0;
                        valSpan.textContent = slider.value;
                        sendMorphThrottled(m.name, v);
                    });

                    row.appendChild(lbl);
                    row.appendChild(slider);
                    row.appendChild(valSpan);
                    body.appendChild(row);
                });

                div.appendChild(body);
                morphsPanel.appendChild(div);
            });

        } catch (e) {
            console.error(`[${label}] Failed to load morphs:`, e);
        }
    }

    // ----- WebSocket -----
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const url = `${protocol}://${window.location.host}${wsPath}`;
        ws = new WebSocket(url);
        ws.binaryType = 'arraybuffer';

        ws.onopen = () => {
            wsReady = true;
            if (statusSpan) { statusSpan.textContent = 'Connected'; statusSpan.className = 'connected'; }
            // Sync body type to server
            if (bodyTypeSelect && bodyTypeSelect.value) {
                wsSend({ type: 'body_type', value: bodyTypeSelect.value });
            }
        };

        ws.onclose = () => {
            wsReady = false;
            if (statusSpan) { statusSpan.textContent = 'Disconnected'; statusSpan.className = 'disconnected'; }
            setTimeout(connectWebSocket, 2000);
        };

        ws.onerror = (e) => console.error(`[${label}] WS error:`, e);

        ws.onmessage = (event) => {
            if (event.data instanceof ArrayBuffer) {
                updateMeshVertices(event.data);
            } else {
                try {
                    const msg = JSON.parse(event.data);
                    if (msg.type === 'error') console.error(`[${label}] Server:`, msg.message);
                    else if (msg.type === 'reload_mesh') reloadMesh(msg.body_type);
                } catch (e) { /* ignore */ }
            }
        };
    }

    // ----- Build Panel DOM -----
    function buildPanel() {
        const panel = document.getElementById(panelId);
        if (!panel) return;
        panel.innerHTML = '';

        // -- Label header --
        const labelDiv = document.createElement('div');
        labelDiv.className = 'panel-section';
        labelDiv.style.cssText = 'padding:10px 16px;background:var(--bg-card);border-bottom:2px solid var(--accent);';
        labelDiv.innerHTML = `<h3 style="margin:0;font-size:0.9rem;color:var(--accent);cursor:default;">${label}</h3>`;
        panel.appendChild(labelDiv);

        // -- Body Type section --
        const btSection = document.createElement('div');
        btSection.className = 'panel-section';
        btSection.innerHTML = `<h3>Body Type <span class="chevron">&#9660;</span></h3>`;
        btSection.querySelector('h3').addEventListener('click', () => btSection.classList.toggle('collapsed'));

        const btBody = document.createElement('div');
        btBody.className = 'panel-body';

        bodyTypeSelect = document.createElement('select');
        bodyTypeSelect.className = 'viewer-select';
        btBody.appendChild(bodyTypeSelect);

        // Meta sliders
        ['age', 'mass', 'tone', 'height'].forEach(name => {
            const defaults = { age: [18,100,59], mass: [45,200,123], tone: [0,100,50], height: [150,200,175] };
            const [min, max, def] = defaults[name];
            const r = mkSliderRow(name.charAt(0).toUpperCase() + name.slice(1), min, max, def, 1);
            metaSliderEls[name] = { slider: r.slider, val: r.val };
            btBody.appendChild(r.row);
        });

        // Skin controls
        const skinDiv = document.createElement('div');
        skinDiv.style.cssText = 'margin-top:8px;border-top:1px solid var(--border);padding-top:8px;';

        // Color
        const cRow = document.createElement('div');
        cRow.className = 'slider-row';
        cRow.innerHTML = '<label>Skin</label>';
        skinColorInput = document.createElement('input');
        skinColorInput.type = 'color';
        skinColorInput.value = '#d4a574';
        skinColorInput.style.cssText = 'width:40px;height:24px;border:none;cursor:pointer;';
        cRow.appendChild(skinColorInput);
        skinDiv.appendChild(cRow);

        // Roughness
        const rr = mkSliderRow('Roughness', 0, 100, 55, 1);
        skinRoughSlider = rr.slider;
        skinRoughVal = rr.val;
        skinRoughVal.textContent = '0.55';
        skinDiv.appendChild(rr.row);

        // Metalness
        const mr = mkSliderRow('Metalness', 0, 100, 0, 1);
        skinMetalSlider = mr.slider;
        skinMetalVal = mr.val;
        skinMetalVal.textContent = '0.00';
        skinDiv.appendChild(mr.row);

        btBody.appendChild(skinDiv);
        btSection.appendChild(btBody);
        panel.appendChild(btSection);

        // -- Morphs section --
        const morphSection = document.createElement('div');
        morphSection.className = 'panel-section';

        const resetBtn = document.createElement('button');
        resetBtn.className = 'btn-reset';
        resetBtn.textContent = 'Reset';
        resetBtn.addEventListener('click', () => resetAll());

        const morphH3 = document.createElement('h3');
        morphH3.textContent = 'Morphs ';
        morphH3.appendChild(resetBtn);
        const chev = document.createElement('span');
        chev.className = 'chevron';
        chev.innerHTML = '&#9660;';
        morphH3.appendChild(chev);
        morphH3.addEventListener('click', (e) => {
            if (e.target === resetBtn) return;
            morphSection.classList.toggle('collapsed');
        });
        morphSection.appendChild(morphH3);

        morphsPanel = document.createElement('div');
        morphsPanel.className = 'panel-body';
        morphSection.appendChild(morphsPanel);
        panel.appendChild(morphSection);

        // -- Status bar --
        const statusBar = document.createElement('div');
        statusBar.className = 'status-bar';
        statusSpan = document.createElement('span');
        statusSpan.className = 'disconnected';
        statusSpan.textContent = 'Disconnected';
        vertexSpan = document.createElement('span');
        vertexSpan.textContent = '—';
        fpsSpan = document.createElement('span');
        fpsSpan.textContent = '—';
        statusBar.innerHTML = 'WS: ';
        statusBar.appendChild(statusSpan);
        statusBar.append(' | ');
        statusBar.appendChild(vertexSpan);
        statusBar.append(' verts | ');
        statusBar.appendChild(fpsSpan);
        statusBar.append(' fps');
        panel.appendChild(statusBar);
    }

    function mkSliderRow(labelText, min, max, value, step) {
        const row = document.createElement('div');
        row.className = 'slider-row';
        const lbl = document.createElement('label');
        lbl.textContent = labelText;
        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = min;
        slider.max = max;
        slider.value = value;
        slider.step = step;
        const val = document.createElement('span');
        val.className = 'slider-val';
        val.textContent = value;
        row.appendChild(lbl);
        row.appendChild(slider);
        row.appendChild(val);
        return { row, slider, val };
    }

    function resetAll() {
        // Reset morph sliders
        if (morphsPanel) {
            morphsPanel.querySelectorAll('input[type="range"]').forEach(s => {
                s.value = 0;
                s.nextElementSibling.textContent = '0';
            });
        }
        // Reset meta sliders
        ['age', 'mass', 'tone', 'height'].forEach(name => {
            const els = metaSliderEls[name];
            if (!els) return;
            const meta = morphData?.meta_sliders?.[name];
            if (meta) { els.slider.value = meta.default; els.val.textContent = meta.default; }
        });
        // Reset skin
        const mat = getSkinMat();
        if (mat) {
            const parts = (bodyTypeSelect?.value || '').split('_');
            const ethnicity = parts[1] || parts[0];
            const colors = skinColorMap[ethnicity];
            if (colors) {
                mat.color.setRGB(Math.pow(colors[0], 1/2.2), Math.pow(colors[1], 1/2.2), Math.pow(colors[2], 1/2.2));
            } else {
                mat.color.setHex(0xd4a574);
            }
            mat.roughness = 0.55;
            mat.metalness = 0.0;
            syncSkinUI(mat);
        }
        wsSend({ type: 'reset', body_type: bodyTypeSelect?.value || defaultBodyType });
    }

    // ----- Render loop -----
    function animate() {
        requestAnimationFrame(animate);
        const dt = clock.getDelta();
        controls.update();
        renderer.render(scene, camera);

        frameCount++;
        fpsAccum += dt;
        if (fpsAccum >= 1.0) {
            if (fpsSpan) fpsSpan.textContent = frameCount;
            frameCount = 0;
            fpsAccum = 0;
        }
    }

    function onResize() {
        const container = renderer.domElement.parentElement;
        const w = Math.max(container.clientWidth, 100);
        const h = container.clientHeight || window.innerHeight;
        renderer.setSize(w, h);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
    }

    // ----- Init -----
    function init() {
        // Build panel DOM first
        buildPanel();

        const canvas = document.getElementById(canvasId);
        const container = canvas.parentElement;
        const w = container.clientWidth;
        const h = container.clientHeight || window.innerHeight;

        renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(w, h);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.6;

        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);

        camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
        camera.position.set(0, 1.0, 3.5);

        controls = new OrbitControls(camera, canvas);
        controls.target.set(0, 0.9, 0);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.minDistance = 0.5;
        controls.maxDistance = 15;
        controls.update();

        // Lighting
        const keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
        keyLight.position.set(2, 4, -5);
        scene.add(keyLight);
        const fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
        fillLight.position.set(-3, 3, -4);
        scene.add(fillLight);
        const backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
        backLight.position.set(0, 4, 5);
        scene.add(backLight);
        scene.add(new THREE.AmbientLight(0xffffff, 0.8));

        // Grid
        scene.add(new THREE.GridHelper(4, 20, 0x333355, 0x222244));

        window.addEventListener('resize', onResize);

        // Load data
        loadMorphs();
        loadMesh().then(() => animate());
        connectWebSocket();
    }

    return { init };
}
