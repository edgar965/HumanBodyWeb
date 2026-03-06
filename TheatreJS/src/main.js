import * as THREE from 'three';
import studio from '@theatre/studio';
import { createScene } from './scene-setup.js';
import { setupTheatre, createCameraSheet, createLightSheet } from './theatre-bridge.js';
import { loadGLBFromFile, loadCharacterModel, loadCharacterFromPreset, loadBVHFromText } from './asset-loader.js';
import { VideoExporter } from './video-export.js';
import {
    fetchSceneList, fetchScene, saveScene,
    fetchModelList, fetchModel,
    fetchAnimationList, fetchBVH,
} from './scene-manager.js';
import { PRESETS, applyPreset } from './presets.js';

// Wait for DOM before initialising
window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('theatre-canvas');
    if (!canvas) {
        console.error('theatre-canvas not found');
        return;
    }

    // 1. Theatre Studio overlay
    studio.initialize();

    // 2. Three.js scene (ballet stage)
    const { scene, camera, renderer, controls, lights } = createScene(canvas);

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
    const activeMixers = [];
    const clock = new THREE.Clock();

    // ── Modal helpers ──

    function openModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add('open');
    }

    function closeModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove('open');
    }

    // Close modals via X button
    document.querySelectorAll('[data-close-modal]').forEach((btn) => {
        btn.addEventListener('click', () => {
            btn.closest('.theatre-modal-overlay')?.classList.remove('open');
        });
    });

    // Close modals via backdrop click
    document.querySelectorAll('.theatre-modal-overlay').forEach((overlay) => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.classList.remove('open');
        });
    });

    // ── Menu: Scene Load ──

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
                    item.className = 'modal-list-item';
                    item.innerHTML = `
                        <span>${s.label || s.name}</span>
                        <span class="item-meta">${s.character_count || 0} Character(s)</span>
                    `;
                    item.addEventListener('click', () => handleSceneLoad(s.name));
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

            // Load characters from scene
            if (sceneData.characters && Array.isArray(sceneData.characters)) {
                for (const charDef of sceneData.characters) {
                    await loadCharacterFromPreset(scene, charDef, charDef.name || name);
                }
            }
        } catch (err) {
            console.error('Scene load error:', err);
            alert('Scene laden fehlgeschlagen: ' + err.message);
        }
    }

    // ── Menu: Scene Save ──

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
                // Collect scene state
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

        // Enter key to save
        sceneSaveInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sceneSaveBtn.click();
        });
    }

    // ── Menu: Model Load ──

    const menuModelLoad = document.getElementById('menu-model-load');
    if (menuModelLoad) {
        menuModelLoad.addEventListener('click', async () => {
            const body = document.getElementById('model-list-body');
            body.innerHTML = '<div class="loading-msg">Lade Modelle...</div>';
            openModal('modal-model-load');

            try {
                const models = await fetchModelList();
                if (models.length === 0) {
                    body.innerHTML = '<div class="loading-msg">Keine Modelle gefunden.</div>';
                    return;
                }
                body.innerHTML = '';
                for (const m of models) {
                    const item = document.createElement('div');
                    item.className = 'modal-list-item';
                    item.innerHTML = `<span>${m.label || m.name}</span>`;
                    item.addEventListener('click', () => handleModelLoad(m.name));
                    body.appendChild(item);
                }
            } catch (err) {
                body.innerHTML = `<div class="loading-msg">Fehler: ${err.message}</div>`;
            }
        });
    }

    async function handleModelLoad(name) {
        closeModal('modal-model-load');
        try {
            const preset = await fetchModel(name);
            await loadCharacterFromPreset(scene, preset, name);
            console.log('Model loaded:', name);
        } catch (err) {
            console.error('Model load error:', err);
            alert('Modell laden fehlgeschlagen: ' + err.message);
        }
    }

    // ── Menu: Animation Load ──

    const menuAnimLoad = document.getElementById('menu-anim-load');
    if (menuAnimLoad) {
        menuAnimLoad.addEventListener('click', async () => {
            const body = document.getElementById('anim-list-body');
            body.innerHTML = '<div class="loading-msg">Lade Animationen...</div>';
            openModal('modal-anim-load');

            try {
                const categories = await fetchAnimationList();
                const catNames = Object.keys(categories);
                if (catNames.length === 0) {
                    body.innerHTML = '<div class="loading-msg">Keine Animationen gefunden.</div>';
                    return;
                }
                body.innerHTML = '';
                for (const catName of catNames) {
                    const anims = categories[catName];
                    const catDiv = document.createElement('div');
                    catDiv.className = 'anim-category';

                    const header = document.createElement('div');
                    header.className = 'anim-category-header';
                    header.innerHTML = `<i class="fas fa-chevron-right"></i> ${catName} (${anims.length})`;
                    header.addEventListener('click', () => {
                        catDiv.classList.toggle('open');
                    });
                    catDiv.appendChild(header);

                    const itemsDiv = document.createElement('div');
                    itemsDiv.className = 'anim-category-items';

                    for (const anim of anims) {
                        const item = document.createElement('div');
                        item.className = 'anim-item';
                        item.innerHTML = `
                            <span>${anim.name}</span>
                            <span class="frame-count">${anim.frames || '?'} frames</span>
                        `;
                        item.addEventListener('click', () => handleAnimLoad(anim.category, anim.name));
                        itemsDiv.appendChild(item);
                    }

                    catDiv.appendChild(itemsDiv);
                    body.appendChild(catDiv);
                }
            } catch (err) {
                body.innerHTML = `<div class="loading-msg">Fehler: ${err.message}</div>`;
            }
        });
    }

    async function handleAnimLoad(category, name) {
        closeModal('modal-anim-load');
        try {
            const bvhText = await fetchBVH(category, name);
            const { mixer } = loadBVHFromText(bvhText, scene, `${category}/${name}`);
            activeMixers.push(mixer);
            console.log('Animation loaded:', category, name);
        } catch (err) {
            console.error('Animation load error:', err);
            alert('Animation laden fehlgeschlagen: ' + err.message);
        }
    }

    // ── Menu: GLB Import ──

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

    // ── Menu: Settings (Presets) ──

    const presetButtons = document.querySelectorAll('[data-preset]');
    presetButtons.forEach((btn) => {
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

    // ── Toolbar: Add Light ──

    const btnAddLight = document.getElementById('btn-add-light');
    let extraLightCount = 0;

    if (btnAddLight) {
        btnAddLight.addEventListener('click', () => {
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

    // ── Toolbar: Export Video ──

    const btnExport = document.getElementById('btn-export-video');
    if (btnExport) {
        btnExport.addEventListener('click', async () => {
            if (exporter.isRecording) {
                btnExport.innerHTML = '<i class="fas fa-file-video"></i> Export Video';
                btnExport.classList.remove('recording');
                await exporter.stopAndDownload();
            } else {
                exporter.start(30);
                btnExport.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
                btnExport.classList.add('recording');
            }
        });
    }

    // ── Render loop ──

    function animate() {
        requestAnimationFrame(animate);
        const delta = clock.getDelta();

        // Update all active BVH animation mixers
        for (const mixer of activeMixers) {
            mixer.update(delta);
        }

        controls.update();
        renderer.render(scene, camera);
    }
    animate();
});
