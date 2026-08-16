/**
 * Modellzustand sichern und Voreinstellungen laden.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026).
 */

import { Seitenzustand } from './seitenzustand.js';
import { loadBVHAnimation } from './wiedergabe.js';


// =========================================================================
// Save Model (Seitenzustand.scene + model state from localStorage)
// =========================================================================
export let currentPresetName = '';

export function gatherModelState() {
    // Model body/cloth/hair from localStorage (set by Konfiguration page)
    let model = {};
    const saved = localStorage.getItem('humanbody_current_model');
    if (saved) {
        try { model = JSON.parse(saved); } catch (e) { /* ignore */ }
    }
    // Scene settings from localStorage
    const sceneSaved = localStorage.getItem('humanbody_scene_settings');
    if (sceneSaved) {
        try { model.scene = JSON.parse(sceneSaved); } catch (e) { /* ignore */ }
    }
    return model;
}

export function getCSRFToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

export async function saveModel(name) {
    const data = gatherModelState();
    data.name = name;
    try {
        const resp = await fetch('/api/character/model/save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ name, data }),
        });
        const result = await resp.json();
        if (result.ok) {
            currentPresetName = name;
            console.log(`Model saved: ${result.filename}`);
            return true;
        } else {
            alert('Fehler beim Speichern: ' + (result.error || 'Unbekannt'));
            return false;
        }
    } catch (e) {
        alert('Fehler beim Speichern: ' + e.message);
        return false;
    }
}

export async function loadDefaultPresetName() {
    try {
        const resp = await fetch('/api/settings/humanbody/');
        if (resp.ok) {
            const s = await resp.json();
            if (s.animations) currentPresetName = s.animations;
            // Apply rig visibility from settings
            if (s.show_rig_animations) {
                Seitenzustand.rigVisible = true;
                const rigToggle = document.getElementById('rig-toggle');
                if (rigToggle) rigToggle.classList.add('active');
            }
            // Auto-play default animation
            if (s.default_anim_animations) {
                const waitForMesh = async () => {
                    const maxWait = 15000;
                    const start = Date.now();
                    while (!Seitenzustand.bodyMesh && Date.now() - start < maxWait) {
                        await new Promise(r => setTimeout(r, 200));
                    }
                    if (Seitenzustand.bodyMesh) {
                        await new Promise(r => setTimeout(r, 1000));
                        loadBVHAnimation(s.default_anim_animations, 'Default', 0);
                    }
                };
                waitForMesh();
            }
        }
    } catch (e) { /* ignore */ }
}

export function initSaveButtons() {
    loadDefaultPresetName();
    const saveBtn = document.getElementById('save-model-btn');
    const saveAsBtn = document.getElementById('save-model-as-btn');

    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            if (!currentPresetName) {
                saveAsBtn?.click();
                return;
            }
            const ok = await saveModel(currentPresetName);
            if (ok) {
                saveBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!';
                setTimeout(() => { saveBtn.innerHTML = '<i class="fas fa-save"></i> Speichern'; }, 1500);
            }
        });
    }

    if (saveAsBtn) {
        saveAsBtn.addEventListener('click', async () => {
            const name = prompt('Modell-Name:', currentPresetName || 'Mein Modell');
            if (!name || !name.trim()) return;
            const ok = await saveModel(name.trim());
            if (ok) {
                saveAsBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!';
                setTimeout(() => { saveAsBtn.innerHTML = '<i class="fas fa-file-export"></i> Speichern unter'; }, 1500);
            }
        });
    }
}
