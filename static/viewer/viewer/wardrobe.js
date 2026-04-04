/**
 * Viewer — Wardrobe UI (GLB asset toggles).
 */
import { state } from './state.js';
import { fn } from './registry.js';

export async function loadWardrobe() {
    try {
        const resp = await fetch('/api/character/wardrobe/');
        const data = await resp.json();
        const panel = document.getElementById('wardrobe-panel');
        panel.innerHTML = '';

        if (!data.assets || data.assets.length === 0) {
            panel.innerHTML += '<div style="color:var(--text-muted);font-size:0.8rem;">No assets available</div>';
            return;
        }

        const cats = {};
        data.assets.forEach(a => {
            if (!cats[a.category]) cats[a.category] = [];
            cats[a.category].push(a);
        });

        Object.keys(cats).sort().forEach(cat => {
            const label = document.createElement('div');
            label.style.cssText = 'font-size:0.78rem;color:var(--text-muted);margin:8px 0 4px;';
            label.textContent = cat;
            panel.appendChild(label);

            const grid = document.createElement('div');
            grid.className = 'asset-grid';

            cats[cat].forEach(asset => {
                const btn = document.createElement('div');
                btn.className = 'asset-btn';
                if (asset.has_glb === false) btn.classList.add('disabled');
                btn.textContent = asset.name.replace(/_/g, ' ');
                btn.title = asset.name;
                btn.dataset.asset = asset.name;
                btn.dataset.url = asset.glb_url;

                btn.addEventListener('click', () => {
                    if (btn.classList.contains('disabled')) return;
                    toggleAsset(asset.name, asset.glb_url, btn);
                });

                grid.appendChild(btn);
            });
            panel.appendChild(grid);
        });
    } catch (e) {
        console.error('Failed to load wardrobe:', e);
    }
}

function toggleAsset(name, url, btn) {
    if (state.loadedAssets[name]) {
        state.scene.remove(state.loadedAssets[name]);
        state.loadedAssets[name] = null;
        btn.classList.remove('active');
        fn.updateEquippedList();
    } else {
        btn.textContent = 'Loading...';
        state.gltfLoader.load(url, (gltf) => {
            const model = gltf.scene;
            state.scene.add(model);
            state.loadedAssets[name] = model;
            btn.classList.add('active');
            btn.textContent = name.replace(/_/g, ' ');
            fn.updateEquippedList();
        }, undefined, (err) => {
            console.error(`Failed to load ${name}:`, err);
            btn.textContent = name.replace(/_/g, ' ');
        });
    }
}

fn.loadWardrobe = loadWardrobe;
