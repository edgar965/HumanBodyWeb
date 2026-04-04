/**
 * Viewer — Morph UI (body type, meta sliders, morph categories).
 */
import { state, API } from './state.js';
import { fn } from './registry.js';
import { wsSend, sendMorphThrottled } from './websocket.js';
import { getSkinMat, syncSkinUI, applySkinColor } from './scene_settings.js';

export async function loadMorphs() {
    try {
        const resp = await fetch(`${API}/morphs/`);
        const data = await resp.json();
        state.skinColors = data.skin_colors || {};

        // Body type dropdown
        const select = document.getElementById('body-type-select');
        data.body_types.forEach(bt => {
            const opt = document.createElement('option');
            opt.value = bt;
            opt.textContent = bt.replace('_', ' ');
            select.appendChild(opt);
        });
        select.addEventListener('change', () => {
            wsSend({ type: 'body_type', value: select.value });
            const parts = select.value.split('_');
            const ethnicity = parts[1] || parts[0];
            const colors = data.skin_colors[ethnicity];
            const skinMat = getSkinMat();
            if (colors && skinMat) {
                skinMat.color.setRGB(
                    Math.pow(colors[0], 1/2.2),
                    Math.pow(colors[1], 1/2.2),
                    Math.pow(colors[2], 1/2.2)
                );
                syncSkinUI(skinMat);
            }
            if (select.value.startsWith('Male_')) {
                fn.removeAllCloth();
            }
        });

        // Meta sliders
        const metaSliders = ['age', 'mass', 'tone', 'height'];
        metaSliders.forEach(name => {
            const slider = document.getElementById(`meta-${name}`);
            const valSpan = document.getElementById(`meta-${name}-val`);
            if (!slider) return;
            const meta = data.meta_sliders?.[name];
            if (meta) {
                slider.min = meta.min;
                slider.max = meta.max;
                slider.value = meta.default;
                valSpan.textContent = meta.default;
            }
            slider.addEventListener('input', () => {
                const displayVal = parseInt(slider.value);
                valSpan.textContent = displayVal;
                const min = parseInt(slider.min), max = parseInt(slider.max);
                const neutral = (min + max) / 2;
                const half = (max - min) / 2;
                const internal = half ? (displayVal - neutral) / half : 0;
                wsSend({ type: 'meta', name: name, value: internal });
            });
        });

        // Skin color + material controls
        const skinColorInput = document.getElementById('skin-color-viewer');
        if (skinColorInput) {
            skinColorInput.addEventListener('input', e => {
                const mat = getSkinMat();
                if (mat) mat.color.set(e.target.value);
            });
        }
        const skinRoughSlider = document.getElementById('skin-roughness-viewer');
        const skinRoughVal = document.getElementById('skin-roughness-viewer-val');
        if (skinRoughSlider) {
            skinRoughSlider.addEventListener('input', () => {
                const v = parseFloat(skinRoughSlider.value) / 100;
                skinRoughVal.textContent = v.toFixed(2);
                const mat = getSkinMat();
                if (mat) mat.roughness = v;
            });
        }
        const skinMetalSlider = document.getElementById('skin-metalness-viewer');
        const skinMetalVal = document.getElementById('skin-metalness-viewer-val');
        if (skinMetalSlider) {
            skinMetalSlider.addEventListener('input', () => {
                const v = parseFloat(skinMetalSlider.value) / 100;
                skinMetalVal.textContent = v.toFixed(2);
                const mat = getSkinMat();
                if (mat) mat.metalness = v;
            });
        }

        // Group morphs by category
        state.morphCategories = {};
        data.morphs.forEach(m => {
            if (!state.morphCategories[m.category]) state.morphCategories[m.category] = [];
            state.morphCategories[m.category].push(m);
        });

        const panel = document.getElementById('morphs-panel');
        panel.innerHTML = '';

        data.categories.sort().forEach(cat => {
            const morphs = state.morphCategories[cat];
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

                const label = document.createElement('label');
                label.textContent = m.name.split('_').slice(1).join(' ') || m.name;
                label.title = m.name;

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

                row.appendChild(label);
                row.appendChild(slider);
                row.appendChild(valSpan);
                body.appendChild(row);
            });

            div.appendChild(body);
            panel.appendChild(div);
        });

        // Reset button
        document.getElementById('reset-morphs').addEventListener('click', () => {
            panel.querySelectorAll('input[type="range"]').forEach(s => {
                s.value = 0;
                s.nextElementSibling.textContent = '0';
            });
            metaSliders.forEach(name => {
                const slider = document.getElementById(`meta-${name}`);
                const valSpan = document.getElementById(`meta-${name}-val`);
                if (!slider) return;
                const meta = data.meta_sliders?.[name];
                if (meta) {
                    slider.value = meta.default;
                    valSpan.textContent = meta.default;
                }
            });
            const skinMat = getSkinMat();
            if (skinMat) {
                const parts = select.value.split('_');
                const ethnicity = parts[1] || parts[0];
                const colors = data.skin_colors[ethnicity];
                if (colors) {
                    skinMat.color.setRGB(
                        Math.pow(colors[0], 1/2.2),
                        Math.pow(colors[1], 1/2.2),
                        Math.pow(colors[2], 1/2.2)
                    );
                } else {
                    skinMat.color.setHex(0xd4a574);
                }
                skinMat.roughness = 0.55;
                skinMat.metalness = 0.0;
                syncSkinUI(skinMat);
            }
            if (skinRoughSlider) { skinRoughSlider.value = 55; skinRoughVal.textContent = '0.55'; }
            if (skinMetalSlider) { skinMetalSlider.value = 0; skinMetalVal.textContent = '0.00'; }
            wsSend({ type: 'reset', body_type: select.value });
        });

        applySkinColor();

    } catch (e) {
        console.error('Failed to load morphs:', e);
    }
}

fn.loadMorphs = loadMorphs;
