/**
 * Modellzustand sichern und Voreinstellungen laden.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026).
 */

import { Seitenzustand } from './seitenzustand.js';
import { loadBVHAnimation } from './wiedergabe.js';
import { Knopfmeldung } from '../gemeinsam/knopfmeldung.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';


// =========================================================================
// Save Model (Seitenzustand.scene + model state from localStorage)
// =========================================================================
export let currentPresetName = '';

export function gatherModelState() {
    // Model body/cloth/hair from localStorage (set by Konfiguration page)
    let model = {};
    const saved = localStorage.getItem('humanbody_current_model');
    if (saved) {
        try {
            model = JSON.parse(saved);
        } catch (e) {
            Protokoll.debug('speichern', 'gespeichertes Modell nicht lesbar', e);
        }
    }
    // Scene settings from localStorage
    const sceneSaved = localStorage.getItem('humanbody_scene_settings');
    if (sceneSaved) {
        try {
            model.scene = JSON.parse(sceneSaved);
        } catch (e) {
            Protokoll.debug('speichern', 'gespeicherte Szeneneinstellungen nicht lesbar', e);
        }
    }
    return model;
}

export async function saveModel(name) {
    const data = gatherModelState();
    data.name = name;
    try {
        const result = await Serverabruf.senden('/api/character/model/save/',
                                                { name, data });
        if (result.ok) {
            currentPresetName = name;
            Protokoll.info('Animation', `Model saved: ${result.filename}`);
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

/** So lange wird auf das Netz gewartet, bevor die Startanimation entfällt. */
const NETZ_WARTEN_MS = 15000;

export async function loadDefaultPresetName() {
    const s = await Serverabruf.jsonOderNull('/api/settings/humanbody/');
    if (!s) return;
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
            const start = Date.now();
            while (!Seitenzustand.bodyMesh && Date.now() - start < NETZ_WARTEN_MS) {
                await new Promise(r => setTimeout(r, Zeiten.WARTESCHRITT_MS));
            }
            if (Seitenzustand.bodyMesh) {
                await new Promise(r => setTimeout(r, Zeiten.SEKUNDE_MS));
                loadBVHAnimation(s.default_anim_animations, 'Default', 0);
            }
        };
        waitForMesh();
    }
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
                Knopfmeldung.fertig(saveBtn);
            }
        });
    }

    if (saveAsBtn) {
        saveAsBtn.addEventListener('click', async () => {
            const name = prompt('Modell-Name:', currentPresetName || 'Mein Modell');
            if (!name || !name.trim()) return;
            const ok = await saveModel(name.trim());
            if (ok) {
                Knopfmeldung.fertig(saveAsBtn);
            }
        });
    }
}
