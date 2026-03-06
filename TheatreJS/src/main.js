import * as THREE from 'three';
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
                    await loadCharacterFromPreset(scene, charDef, charDef.name || name);
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
                        await loadCharacterFromPreset(scene, preset, m.name);
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
            const { mixer, action, duration } = loadBVHFromText(bvhText, scene, `${category}/${name}`);

            // Replace current mixer
            if (activeMixer) activeMixer.stopAllAction();
            activeMixer = mixer;
            currentAction = action;

            // Update player UI
            updatePlayerDuration(duration);
            isPlaying = false;
            currentTime = 0;
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
                    await loadCharacterFromPreset(scene, modelData, cfg.model);
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

        controls.update();
        renderer.render(scene, camera);
    }
    animate();
});
