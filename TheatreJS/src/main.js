import * as THREE from 'three';
// BVHLoader only needed for non-skinned fallback (asset-loader.js has its own)
import studio from '@theatre/studio';
import { createScene } from './scene-setup.js';
import { setupTheatre, createCameraSheet, createLightSheet, getAllTheatreObjects } from './theatre-bridge.js';
import { loadGLBFromFile, loadBVHFromText } from './asset-loader.js';
import { VideoExporter } from './video-export.js';
// Nur noch fetchBVH: Szenen-, Modell- und Animationslisten holt der
// Figurenlader bzw. Seitenlisten (studio/). Die sechs anderen Importe standen
// hier, nachdem ihre Aufrufer in Module gewandert waren.
import { fetchBVH } from './scene-manager.js';
import { PRESETS, applyPreset } from './presets.js';
import { fetchRetargetedClip, fetchRetargetedClipFromText, detectBVHFormat } from './retarget_hybrid.js';
import { buildRigifySkeleton } from './rigify_skeleton_builder.js';
import { KeyframeUI } from './keyframe-ui.js';
import { Skinner } from './studio/skinner.js';
import { Lichtpanel } from './studio/panels/lichtpanel.js';
import { Kleiderpanel } from './studio/panels/kleiderpanel.js';
import { Figurpanel } from './studio/panels/figurpanel.js';
import { Bildexport } from './studio/bildexport.js';
import { Auswahl } from './studio/auswahl.js';
import { Figurenlader } from './studio/figurenlader.js';
import { Seitenlisten } from './studio/seitenlisten.js';
import { Abspieler } from './studio/abspieler.js';
import { Kamerabahn } from './studio/kamerabahn.js';
import { Animationslauf } from './studio/animationslauf.js';
import { Bedienleiste } from './studio/bedienleiste.js';

// Theatre.js ignores the getProject({ state }) param if localStorage exists.
// Clear stale localStorage so our state.json (with correct sequence length) takes effect.
// Force-clear if the stored state has an outdated sequence length (e.g. 300).
try {
    const stored = localStorage.getItem('theatre-0.4.persistent');
    if (stored) {
        const hasUserKeyframes = stored.includes('"keyframes":[{');
        if (!hasUserKeyframes) {
            localStorage.removeItem('theatre-0.4.persistent');
            console.log('[Theatre Studio] Cleared stale localStorage (no user keyframes)');
        }
    }
} catch (_) { /* ignore */ }

// Theatre Studio MUST be initialized at module level (before DOMContentLoaded)
studio.initialize().then(() => {
    console.log('[Theatre Studio] initialized successfully');
    // Force Studio visible (it remembers hide state in localStorage)
    studio.ui.restore();
    // Wait for render() setTimeout to create DOM element
    setTimeout(() => {
        const root = document.getElementById('theatrejs-studio-root');
        if (root) {
            root.style.setProperty('z-index', '900', 'important');

            // Fix: position:fixed so context menus are positioned correctly
            root.style.setProperty('position', 'fixed', 'important');
            root.style.setProperty('top', '0', 'important');
            root.style.setProperty('left', '0', 'important');
            root.style.setProperty('width', '100vw', 'important');
            root.style.setProperty('height', '100vh', 'important');
            root.style.setProperty('pointer-events', 'none', 'important');

            if (root.shadowRoot) {
                const sr = root.shadowRoot;
                const style = document.createElement('style');
                style.textContent = `
                    :host { font-size: 13px !important; }
                    svg { transform: scale(1.3); }
                    [data-testid] { min-height: 28px; }

                    /* Re-enable pointer events only on the Sequence Editor (bottom timeline) */
                    [data-testid="SequenceEditor"],
                    [data-testid="GlobalToolbar"] {
                        pointer-events: auto !important;
                    }

                    /* Outline panel: shift right to clear sidebar */
                    div[class] > div[class]:nth-child(3) {
                        left: 220px !important;
                        pointer-events: auto !important;
                    }
                    /* Detail panel (properties): shift left to clear right panel */
                    div[class] > div[class]:nth-child(4) {
                        pointer-events: auto !important;
                    }

                    /* Context menus + popovers must be clickable */
                    [data-radix-popper-content-wrapper],
                    [data-radix-menu-content],
                    [role="menu"],
                    [role="dialog"] {
                        pointer-events: auto !important;
                        z-index: 99999 !important;
                    }
                `;
                sr.prepend(style);
            }
            console.log('[Theatre Studio] UI visible, position:fixed, context menu fix active');
        }
    }, 100);
}).catch(err => {
    console.error('[Theatre Studio] initialize() FAILED:', err);
});
window.studio = studio;

// Wait for DOM before initialising
window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('theatre-canvas');
    if (!canvas) {
        console.error('theatre-canvas not found');
        return;
    }

    // 2. Three.js scene (ballet stage)
    const { scene, camera, renderer, controls, lights, lightIcons, transformControls } = createScene(canvas);

    // DEBUG: Expose for console debugging
    window.scene = scene;
    window.camera = camera;
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
    // Auswahl (Figur / Licht / Kleidung) in einer Klasse — vorher zwei
    // Closure-Variablen, an fuenfzehn Stellen gesetzt und gelesen.
    const auswahl = new Auswahl(transformControls);
    window.auswahl = auswahl;
    const loadedCharacters = [];   // Track all loaded character groups
    // `reloadDebounceTimer` stand hier mit dem Kommentar "Debounce for character
    // reload" — und wurde nie benutzt: Jede Schieberbewegung loeste sofort eine
    // Anfrage aus. Die Entprellung steckt jetzt in Figurpanel, wo sie hingehoert.

    // Skelett, Gewichte und die Umwandlung zu SkinnedMesh stecken in einer
    // eigenen Klasse (studio/skinner.js). Vorher standen hier 290 Zeilen mit
    // fuenf Closure-Variablen, an denen sechs Funktionen gemeinsam schrieben.
    const skinner = new Skinner(scene, loadedCharacters);
    skinner.laden();
    window.skinner = skinner;

    // Licht-Eigenschaften: studio/panels/lichtpanel.js (vorher 162 Zeilen hier,
    // davon rund 90 Inline-Stile — die stehen jetzt als .pnl-* in theatre.html).
    // Die Deklaration gehoert VOR den Klick-Zuhoerer weiter unten: `const` in
    // einem Block gilt erst ab seiner Zeile.
    const lichtpanel = new Lichtpanel(lights);
    window.lichtpanel = lichtpanel;   // wie window.scene/lights: fuer Konsole und UI-Tests

    // Kleidungs-Eigenschaften: studio/panels/kleiderpanel.js (vorher 184
    // Zeilen hier). Dort steht auch, warum elf Regler jetzt zugeklappt und
    // als 'noch nicht angebunden' beschriftet sind.
    const kleiderpanel = new Kleiderpanel();
    window.kleiderpanel = kleiderpanel;

    // Figur-Eigenschaften: studio/panels/figurpanel.js (vorher 320 Zeilen in
    // vier Funktionen). Dort steht auch, warum das Netz jetzt entprellt
    // nachgeladen wird — vorher eine Anfrage à 5,2 MB je Schieberbewegung.
    const figurpanel = new Figurpanel();
    window.figurpanel = figurpanel;

    // Figuren laden (Vorgabe, Szene) und Bühnenzustand speichern:
    // studio/figurenlader.js — der Kern stand vorher dreimal in dieser Datei.
    const figurenlader = new Figurenlader(scene, loadedCharacters, skinner, auswahl);
    window.figurenlader = figurenlader;

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
                auswahl.lichtWaehlen(clickedIcon);
                console.log('✓ Licht ausgewählt:', clickedIcon.userData.light);
                lichtpanel.zeigen(clickedIcon.userData.light, clickedIcon);
                return;
            }
        }

        // Try character meshes (all loaded characters)
        // Filter out SkinnedMeshes without bound skeleton (causes bones error)
        let charIntersects;
        try {
            charIntersects = raycaster.intersectObjects(loadedCharacters, true);
        } catch (e) {
            return; // SkinnedMesh without skeleton, skip
        }
        if (charIntersects.length > 0) {
            const clickedMesh = charIntersects[0].object;

            // Check if it's a garment (higher priority than character)
            if (clickedMesh.userData.isGarment) {
                auswahl.kleidungWaehlen(clickedMesh);
                console.log('✓ Garment ausgewählt:', clickedMesh.name);
                kleiderpanel.zeigen(clickedMesh);
                return;
            }

            // Otherwise find the character group (walk up the hierarchy)
            let clickedChar = clickedMesh;
            while (clickedChar.parent && !clickedChar.userData.isCharacter) {
                clickedChar = clickedChar.parent;
            }

            if (clickedChar.userData.isCharacter) {
                auswahl.figurWaehlen(clickedChar);
                console.log('✓ Character ausgewählt:', clickedChar.userData.presetName);
                figurpanel.zeigen(clickedChar);
                return;
            }
        }

        // Nothing clicked - deselect
        auswahl.leeren();
        lichtpanel.verbergen();
    });

    // 3. Theatre project + sheet
    const { project, sheet } = setupTheatre();

    // Expose to window for Studio UI
    window.theatreProject = project;
    window.theatreSheet = sheet;

    // 4. Register camera & spotlights as animatable Theatre objects
    const cameraObj = createCameraSheet(sheet, camera);
    createLightSheet(sheet, 'Spot Left', lights.spotLeft);
    createLightSheet(sheet, 'Spot Right', lights.spotRight);
    createLightSheet(sheet, 'Back Light', lights.backLight);

    // Sync OrbitControls camera position back to Theatre.js
    // so the Detail Panel shows the actual camera position.
    controls.addEventListener('change', () => {
        if (window.isPlaying) return; // sequence drives camera during playback
        studio.transaction(({ set }) => {
            set(cameraObj.props.position.x, camera.position.x);
            set(cameraObj.props.position.y, camera.position.y);
            set(cameraObj.props.position.z, camera.position.z);
        });
    });

    // 5. Initialize Keyframe UI for Camera/Light animation
    const theatreObjects = getAllTheatreObjects();
    window.theatreObjects = theatreObjects; // Expose for Playwright tests & debugging
    const keyframeUI = new KeyframeUI(project, sheet, theatreObjects);
    window.keyframeUI = keyframeUI; // Expose for debugging

    // Open the Sequence Editor panel by selecting the sheet.
    // Tracks are pre-defined in theatre-state.json (Camera + 3 Lights).
    project.ready.then(() => {
        studio.setSelection([sheet]);
    });

    // 6. Video exporter
    const exporter = new VideoExporter(renderer.domElement);

    // 6. Track active mixers for BVH animation playback
    // `activeMixer` und `currentAction` liegen jetzt in Animationslauf;
    // window.activeMixer wird dort weiter gepflegt (Playwright liest es).
    const clock = new THREE.Clock();

    // Menüleiste, Reiter, Werkzeugknöpfe: studio/bedienleiste.js. Vorher 128
    // Zeilen hier — darunter dreimal derselbe Umschalter und fuenfmal das
    // Zuklappen aller Menues.
    const bedienleiste = new Bedienleiste(
        { scene, lightIcons, transformControls },
        { PRESETS, applyPreset, camera, lights, controls }).verdrahten();
    window.bedienleiste = bedienleiste;

    // Rig-Anzeige umschalten. Der Aufbau des SkeletonHelper stand hier ein
    // zweites Mal, mit denselben fuenf Materialzeilen wie beim Umwandeln zu
    // SkinnedMesh — beides liegt jetzt in Skinner.rigAufbauen().
    const btnToggleRig = document.getElementById('btn-toggle-rig');
    if (btnToggleRig) {
        btnToggleRig.addEventListener('click', () => {
            btnToggleRig.classList.toggle('active', skinner.rigUmschalten());
        });
    }

    // Kamera-Keyframes: studio/kamerabahn.js. Vorher 94 Zeilen in drei
    // Menue-Zuhoerern — dreimal derselbe Menue-Vorspann, zweimal dieselbe
    // Suche nach dem Theatre-Zustand im localStorage.
    const kamerabahn = new Kamerabahn(sheet.sequence, cameraObj, camera, studio).verdrahten();
    window.kamerabahn = kamerabahn;

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

    // Toggle Theatre.js Studio panel
    const btnToggleStudio = document.getElementById('btn-toggle-studio');
    let studioVisible = true;
    if (btnToggleStudio) {
        btnToggleStudio.addEventListener('click', () => {
            studioVisible = !studioVisible;
            if (studioVisible) {
                studio.ui.restore();
            } else {
                studio.ui.hide();
            }
            btnToggleStudio.classList.toggle('active', studioVisible);
        });
    }

    // ── Tools menu handlers ──
    // Expose as global function so it can be called from menu AND from console
    window.rebuildTimeline = function() {
        const seq = sheet.sequence;
        const objs = window.theatreObjects || {};

        // Set sequence length
        try {
            studio.transaction(({ set }) => { set(seq.pointer.length, 10); });
        } catch(e) { console.warn('Set length failed:', e); }

        // Move playhead to 0, write all current values as keyframes
        seq.position = 0;
        const objEntries = Object.entries(objs);
        for (const [name, obj] of objEntries) {
            const vals = obj.value;
            if (!vals) continue;
            try {
                studio.transaction(({ set }) => {
                    for (const [key, val] of Object.entries(vals)) {
                        if (key === 'color') {
                            set(obj.props[key], val);
                        } else if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
                            for (const [subKey, subVal] of Object.entries(val)) {
                                set(obj.props[key][subKey], subVal);
                            }
                        } else {
                            set(obj.props[key], val);
                        }
                    }
                });
                console.log('✓ Timeline:', name, 'OK');
            } catch(e) {
                console.error('✗ Timeline:', name, e.message);
            }
        }

        studio.setSelection([sheet]);
        console.log('✓ Timeline rebuilt:', objEntries.length, 'objects');
    };

    window.clearTimeline = function() {
        for (const key of Object.keys(localStorage)) {
            if (key.includes('theatre') || key.includes('Theatre') || key.includes('HumanBody Theatre')) {
                localStorage.removeItem(key);
            }
        }
        if (window.keyframeUI) window.keyframeUI.keyframes = [];
        window.location.reload();
    };

    // Menuepunkte des Werkzeug-Menues. Das Zuklappen aller Menues kommt aus
    // Bedienleiste — es stand in dieser Datei fuenfmal ausgeschrieben.
    for (const [id, tun] of [['menu-tracks-rebuild', () => window.rebuildTimeline()],
                             ['menu-tracks-clear', () => window.clearTimeline()]]) {
        document.getElementById(id)?.addEventListener('click', (ereignis) => {
            ereignis.stopPropagation();
            Bedienleiste.menuesZuklappen();
            tun();
        });
    }

    // Modalfenster, Szenen- und Modell-Listen: studio/seitenlisten.js.
    // Das Laden einer Figur stand hier dreimal mit denselben fuenf Zeilen —
    // jetzt Figurenlader.ausVorgabe() (studio/figurenlader.js).
    Seitenlisten.modalfensterVerdrahten();
    const listen = new Seitenlisten(figurenlader,
                                    (kategorie, name) => animationslauf.laden(kategorie, name));
    listen.modelle();

    document.getElementById('menu-scene-load')
        ?.addEventListener('click', () => listen.szenen());

    // Szene speichern
    const sceneSaveBtn = document.getElementById('scene-save-btn');
    const sceneSaveInput = document.getElementById('scene-save-name');
    document.getElementById('menu-scene-save')?.addEventListener('click', () => {
        Seitenlisten.oeffnen('modal-scene-save');
        if (sceneSaveInput) { sceneSaveInput.value = ''; sceneSaveInput.focus(); }
    });
    if (sceneSaveBtn && sceneSaveInput) {
        sceneSaveBtn.addEventListener('click', async () => {
            const name = sceneSaveInput.value.trim();
            if (!name) return;
            sceneSaveBtn.disabled = true;
            sceneSaveBtn.textContent = 'Speichere …';
            try {
                await figurenlader.speichern(name, { camera, controls, lights });
                Seitenlisten.schliessen('modal-scene-save');
            } catch (fehler) {
                console.error('Szene speichern fehlgeschlagen:', fehler);
                alert('Szene speichern fehlgeschlagen: ' + fehler.message);
            }
            sceneSaveBtn.disabled = false;
            sceneSaveBtn.textContent = 'Speichern';
        });
        sceneSaveInput.addEventListener('keydown', (ereignis) => {
            if (ereignis.key === 'Enter') sceneSaveBtn.click();
        });
    }

    // Der Knopf im linken Bereich schaltet nur auf den Modelle-Reiter.
    document.getElementById('menu-model-load')?.addEventListener('click', () => {
        document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        document.querySelector('[data-tab="tab-models"]')?.classList.add('active');
        document.getElementById('tab-models')?.classList.add('active');
    });

    // REIHENFOLGE: Der Abspieler steht VOR dem Animationslauf, weil dessen
    // Konstruktor ihn als Wert bekommt. Umgekehrt greift der Abspieler auf den
    // Lauf nur ueber Pfeilfunktionen zu — die werden erst beim Abspielen
    // ausgefuehrt, da ist er längst da. Andere Reihenfolge = 
    // "Cannot access 'animationslauf' before initialization".
    const abspieler = new Abspieler(sheet.sequence, {
        mixer: () => animationslauf.mixer,
        aktion: () => animationslauf.aktion,
        stoppen: () => animationslauf.anhalten(),
    }).verdrahten();
    window.abspieler = abspieler;

    // Animation laden und anhalten: studio/animationslauf.js. Vorher 107
    // Zeilen, die Mixer und Aktion als Closure-Variablen fuehrten — dieselben
    // zwei Werte, die Abspieler, Export und Render-Schleife brauchen.
    const animationslauf = new Animationslauf(
        { scene, sheet, studio }, skinner, auswahl, abspieler);
    window.animationslauf = animationslauf;

    // Animationsbaum aufbauen — braucht `animationslauf`, der direkt darueber
    // angelegt wird.
    listen.animationen();

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

    // ── Export MP4 ──
    const QUALITY_BITRATES = { low: 2_000_000, medium: 5_000_000, high: 8_000_000, ultra: 15_000_000 };
    const RESOLUTION_MAP = { '720p': [1280, 720], '1080p': [1920, 1080], '1440p': [2560, 1440], '4k': [3840, 2160] };

    const menuExportMp4 = document.getElementById('menu-export-mp4');
    const modalExportMp4 = document.getElementById('modal-export-mp4');
    const exportStartBtn = document.getElementById('export-mp4-start');
    const exportStatus = document.getElementById('export-mp4-status');

    if (menuExportMp4 && modalExportMp4) {
        // Open modal
        menuExportMp4.addEventListener('click', () => {
            // Pre-fill settings from server if available
            const vs = window._theatreVideoSettings || {};
            const resEl = document.getElementById('export-mp4-resolution');
            const fpsEl = document.getElementById('export-mp4-fps');
            const qualEl = document.getElementById('export-mp4-quality');
            const fmtEl = document.getElementById('export-mp4-format');
            if (resEl && vs.resolution) resEl.value = vs.resolution;
            if (fpsEl && vs.fps) fpsEl.value = String(vs.fps);
            if (qualEl && vs.quality) qualEl.value = vs.quality;
            if (fmtEl && vs.format) fmtEl.value = vs.format;

            modalExportMp4.classList.add('open');
            exportStatus.style.display = 'none';

            if (exporter.isRecording) {
                exportStartBtn.innerHTML = '<i class="fas fa-stop" style="color:#e74c3c;"></i> Aufnahme stoppen & exportieren';
            } else {
                exportStartBtn.innerHTML = '<i class="fas fa-circle" style="color:#e74c3c;"></i> Aufnahme starten';
            }
        });

        // Start/Stop recording
        exportStartBtn.addEventListener('click', async () => {
            if (exporter.isRecording) {
                // Stop and export
                exportStartBtn.disabled = true;
                exportStatus.style.display = 'block';
                exportStatus.textContent = 'Aufnahme gestoppt. Verarbeite...';

                const fmt = document.getElementById('export-mp4-format').value;
                const filename = document.getElementById('export-mp4-filename').value || 'theatre-export';
                const ext = fmt === 'webm' ? '.webm' : '.mp4';
                const outName = filename.endsWith(ext) ? filename : filename.replace(/\.\w+$/, '') + ext;

                try {
                    if (fmt === 'mp4') {
                        exportStatus.textContent = 'Konvertiere zu MP4 (ffmpeg)...';
                        await exporter.stopAndUpload('/api/theatre/convert-video/', outName);
                    } else {
                        await exporter.stopAndDownload(outName);
                    }
                    exportStatus.style.background = 'rgba(46,204,113,0.15)';
                    exportStatus.style.color = '#2ecc71';
                    exportStatus.textContent = 'Export erfolgreich: ' + outName;
                } catch (err) {
                    exportStatus.style.background = 'rgba(231,76,60,0.15)';
                    exportStatus.style.color = '#e74c3c';
                    exportStatus.textContent = 'Fehler: ' + err.message;
                }
                exportStartBtn.disabled = false;
                exportStartBtn.innerHTML = '<i class="fas fa-circle" style="color:#e74c3c;"></i> Aufnahme starten';
            } else {
                // Start recording
                const fps = parseInt(document.getElementById('export-mp4-fps').value) || 30;
                const quality = document.getElementById('export-mp4-quality').value || 'high';
                const resolution = document.getElementById('export-mp4-resolution').value || '1080p';
                const bitrate = QUALITY_BITRATES[quality] || 8_000_000;
                const [w, h] = RESOLUTION_MAP[resolution] || [1920, 1080];

                exporter.start({ fps, bitrate, width: w, height: h, renderer, camera });

                exportStatus.style.display = 'block';
                exportStatus.style.background = 'rgba(231,76,60,0.15)';
                exportStatus.style.color = '#e74c3c';
                exportStatus.textContent = `Aufnahme läuft (${resolution}, ${fps}fps)... Spiele die Animation ab und klicke dann "Stoppen".`;
                exportStartBtn.innerHTML = '<i class="fas fa-stop" style="color:#e74c3c;"></i> Aufnahme stoppen & exportieren';

                // Close modal so user can interact with the scene
                modalExportMp4.classList.remove('open');
            }
        });
    }


    // ── Auto-load defaults from settings ──
    async function loadDefaults() {
        try {
            const resp = await fetch('/api/settings/theatre/');
            if (!resp.ok) return;
            const cfg = await resp.json();

            // Store video export settings for exporter
            window._theatreVideoSettings = {
                format: cfg.video_format || 'mp4',
                resolution: cfg.video_resolution || '1080p',
                fps: cfg.video_fps || 30,
                quality: cfg.video_quality || 'high',
            };

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
                    // Dritte Fundstelle derselben fuenf Zeilen — jetzt ueber
                    // Figurenlader.modell() wie die anderen beiden.
                    await figurenlader.modell(cfg.model);
                    console.log('✓ Auto-loaded model:', cfg.model);

                    // Load animation if model loaded successfully
                    if (cfg.animation) {
                        const [category, name] = cfg.animation.split('/');
                        if (category && name) {
                            await animationslauf.laden(category, name);
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

        // Laufende BVH-Animation weiterdrehen und die Anzeige nachziehen.
        if (animationslauf.mixer && abspieler.laeuft) {
            animationslauf.mixer.update(delta * abspieler.tempo);
            if (animationslauf.aktion
                    && animationslauf.aktion.time >= abspieler.dauer) {
                animationslauf.aktion.time = 0;
            }
            abspieler.zeitVerfolgen();
        }

        // Sync light icons with lights (wenn bewegt via TransformControls)
        if (auswahl.licht()) {
            const light = auswahl.licht();
            light.position.copy(auswahl.lichtsymbol.position);
            auswahl.lichtsymbol.lookAt(light.target.position);
        }

        controls.update();
        // Temporarily hide SkinnedMeshes without skeleton to prevent render errors
        const hiddenMeshes = [];
        scene.traverse((child) => {
            if (child.isSkinnedMesh && !child.skeleton) {
                child.visible = false;
                hiddenMeshes.push(child);
            }
        });
        renderer.render(scene, camera);
        // Restore visibility so garments/meshes become visible once skeleton is bound
        for (const mesh of hiddenMeshes) {
            mesh.visible = true;
        }
    }
    animate();

    // ── Global API for server-side rendering (Playwright) ──
    window.__theatreSetTime = (t) => {
        abspieler.zeitSetzen(t);
        renderer.render(scene, camera);
    };
    window.__theatreGetDuration = () => abspieler.dauer || 0;
    window.__theatreReady = false;

    // ── URL-Parameter Autoplay ──
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('autoplay') === '1') {
        // Wait for scene to load, then start playing
        setTimeout(() => {
            const playBtn = document.getElementById('btnPlayPause');
            if (playBtn && !abspieler.laeuft) playBtn.click();
            window.__theatreReady = true;
        }, 3000);
    }

    // ── Export Tab UI ──
    const exportCrf = document.getElementById('export-crf');
    const exportCrfVal = document.getElementById('export-crf-val');
    if (exportCrf && exportCrfVal) {
        exportCrf.addEventListener('input', () => { exportCrfVal.textContent = exportCrf.value; });
    }

    const exportRes = document.getElementById('export-resolution');
    const exportCustom = document.getElementById('export-custom-res');
    if (exportRes && exportCustom) {
        exportRes.addEventListener('change', () => {
            exportCustom.style.display = exportRes.value === 'custom' ? 'flex' : 'none';
        });
    }

    // Show/hide server-only options based on method
    const exportMethodSel = document.getElementById('export-method');
    const exportRegionSection = document.getElementById('export-region-section');
    if (exportMethodSel) {
        exportMethodSel.addEventListener('change', () => {
            if (exportRegionSection) exportRegionSection.style.display = exportMethodSel.value === 'server' ? '' : 'none';
        });
    }

    // Update export info whenever Export tab is shown
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            if (tab.getAttribute('data-tab') === 'tab-export') {
                const nameEl = document.getElementById('export-anim-name');
                const durEl = document.getElementById('export-anim-dur');
                if (nameEl) nameEl.textContent = animationslauf.name || '—';
                const dauer = abspieler.dauer;
                if (durEl) durEl.textContent = dauer ? dauer.toFixed(1) : '—';
                // Endzeit vorbelegen, solange sie leer ist
                const endInput = document.getElementById('export-end');
                if (endInput && (!endInput.value || endInput.value === '0') && dauer) {
                    endInput.value = dauer.toFixed(1);
                }
            }
        });
    });

    // Video-Export: studio/bildexport.js (vorher 250 Zeilen hier). Er braucht
    // genau die Faehigkeiten des Abspielers — Dauer, Zeit setzen, pausieren,
    // fortsetzen — und bekommt ihn deshalb direkt, statt dieselben Zugriffe
    // ein zweites Mal auszuschreiben.
    const bildexport = new Bildexport(
        { renderer, scene, camera, canvas },
        {
            dauer: () => abspieler.dauer || 10,
            zeitSetzen: (zeit) => abspieler.zeitSetzen(zeit),
            laeuft: () => abspieler.laeuft,
            pausieren: () => { if (abspieler.laeuft) abspieler.umschalten(); },
            fortsetzen: () => { if (!abspieler.laeuft) abspieler.umschalten(); },
        }).verdrahten();
    window.bildexport = bildexport;
});
