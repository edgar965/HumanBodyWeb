/**
 * Result Character — Control panel builder (toggle bar, tabs, morphs, cloth, assets).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';

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
// Build Control Panel
// =====================================================================

export function buildControlPanel(container, data) {
    container.innerHTML = '';

    // --- Toggle buttons bar ---
    const toggleBar = el('div', 'rc-toggle-bar');

    const modelBtn = el('button', 'rc-toggle-btn active');
    modelBtn.innerHTML = '<i class="fas fa-user"></i> Model';
    modelBtn.addEventListener('click', () => {
        if (state.bodyMesh) state.bodyMesh.visible = !state.bodyMesh.visible;
        modelBtn.classList.toggle('active', state.bodyMesh && state.bodyMesh.visible);
    });
    toggleBar.appendChild(modelBtn);

    const rigBtn = el('button', 'rc-toggle-btn');
    rigBtn.innerHTML = '<i class="fas fa-bone"></i> Rig';
    rigBtn.addEventListener('click', () => {
        state.rigVisible = !state.rigVisible;
        if (state.rigVisible) {
            if (!state.skeletonHelper && state.rigifySkeleton) {
                state.skeletonHelper = new THREE.SkeletonHelper(state.rigifySkeleton.rootBone);
                state.skeletonHelper.material.depthTest = false;
                state.skeletonHelper.material.depthWrite = false;
                state.skeletonHelper.material.color.set(0x00ffaa);
                state.skeletonHelper.material.linewidth = 2;
                state.skeletonHelper.renderOrder = 999;
                state.scene.add(state.skeletonHelper);
            }
            if (state.skeletonHelper) state.skeletonHelper.visible = true;
        } else {
            if (state.skeletonHelper) state.skeletonHelper.visible = false;
        }
        rigBtn.classList.toggle('active', state.rigVisible);
        if (typeof window.setBvhOverlayVisible === 'function') {
            window.setBvhOverlayVisible(state.rigVisible);
        }
    });
    toggleBar.appendChild(rigBtn);

    const clothBtn = el('button', 'rc-toggle-btn active');
    clothBtn.innerHTML = '<i class="fas fa-tshirt"></i> Kleider';
    clothBtn.addEventListener('click', () => {
        state.clothesVisible = !state.clothesVisible;
        for (const m of Object.values(state.clothMeshes)) {
            if (m) m.visible = state.clothesVisible;
        }
        for (const m of Object.values(state.garmentMeshes)) {
            if (m) m.visible = state.clothesVisible;
        }
        clothBtn.classList.toggle('active', state.clothesVisible);
    });
    toggleBar.appendChild(clothBtn);

    const hairBtn = el('button', 'rc-toggle-btn active');
    hairBtn.innerHTML = '<i class="fas fa-hat-wizard"></i> Haar';
    hairBtn.addEventListener('click', () => {
        if (state.hairMesh) {
            state.hairMesh.visible = !state.hairMesh.visible;
            hairBtn.classList.toggle('active', state.hairMesh.visible);
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

        // Resize handle
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
    }

    // 3D viewport fullscreen toggle + resize
    const charContainer = document.getElementById('resultCharacter');
    const charViewport = document.getElementById('characterViewport');
    const fsBtn = document.getElementById('btnViewportFullscreen');
    const resizeHandle = document.getElementById('viewportResizeHandle');

    if (fsBtn && charContainer && charViewport) {
        let isFullscreen = true;
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
            window.dispatchEvent(new Event('resize'));
        });

        if (resizeHandle) {
            resizeHandle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const startY = e.clientY;
                const startH = charViewport.offsetHeight;
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
            if (p.name === state.currentPresetName) opt.selected = true;
            presetSelect.appendChild(opt);
        });
    }).catch(() => {});
    presetSelect.addEventListener('change', () => fn.reloadForPreset(presetSelect.value));
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
        fn.wsSend({ type: 'reset', body_type: state.currentBodyType });
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
            const presetVal = state.currentMorphs[m.name] || 0;
            slider.value = Math.round(presetVal * 100);

            const valSpan = el('span', 'rc-slider-val');
            valSpan.textContent = slider.value;

            slider.addEventListener('input', () => {
                valSpan.textContent = slider.value;
                const v = parseInt(slider.value) / 100.0;
                state.currentMorphs[m.name] = v;
                fn.sendMorphThrottled(m.name, v);
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
        fn.loadCloth(`tpl_${p.template}`, p);
    });
    updateBtn.addEventListener('click', () => {
        const p = getTplParams();
        const key = `tpl_${p.template}`;
        if (state.clothMeshes[key]) fn.loadCloth(key, p);
    });
    deleteBtn.addEventListener('click', () => {
        const tpl = tplSelect.value || 'TPL_TSHIRT';
        fn.removeClothRegion(`tpl_${tpl}`);
    });
    removeAllBtn.addEventListener('click', () => fn.removeAllCloth());

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

fn.buildControlPanel = buildControlPanel;
