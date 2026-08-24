import * as THREE from 'three';
import { state } from './state.js';
import { VIEWER_TONE_MAPPINGS } from './scene_settings.js';

/**
 * Smpllicht — Beleuchtung, Belichtung und Kamera des Reiters „Szene".
 *
 * Herausgelöst aus `smpl.js` (393 Zeilen). Dort stand das Setzen der Lampen
 * ZWEIMAL Zeile für Zeile: einmal für die vier Vorgaben (`_applyLightPreset`)
 * und einmal für die gespeicherten Einstellungen (`_applySmplSceneSettings`) —
 * gleiche Felder, gleiche Reihenfolge, doppelt gepflegt.
 *
 * Eine Lampenangabe ist immer `{intensity, color, pos}`; `pos` fehlt beim
 * Umgebungslicht, weil es keine Richtung hat.
 *
 * Die Regler zählen in ganzen Zahlen: Stärke und Belichtung in Prozent
 * (Teiler 100), die Position in Metern (unverändert), das Sichtfeld in Grad.
 */
export class Smpllicht {

    /** Reglername -> Feld in `state`. */
    static GRUPPEN = [['key', 'keyLight'], ['fill', 'fillLight'],
                      ['back', 'backLight']];

    static ACHSEN = ['x', 'y', 'z'];

    /** Die vier Beleuchtungsvorgaben der Auswahlliste. */
    static VORGABEN = {
        studio: {
            key: { intensity: 3.0, color: '#ffffff', pos: [2, 4, -5] },
            fill: { intensity: 2.0, color: '#eeeeff', pos: [-3, 3, -4] },
            back: { intensity: 2.5, color: '#ffeedd', pos: [0, 4, 5] },
            ambient: { intensity: 0.8, color: '#ffffff' }, exposure: 1.6,
        },
        outdoor: {
            key: { intensity: 4.0, color: '#fff5e0', pos: [5, 8, -2] },
            fill: { intensity: 1.5, color: '#8899cc', pos: [-4, 2, -3] },
            back: { intensity: 1.0, color: '#ffeedd', pos: [-2, 3, 4] },
            ambient: { intensity: 1.2, color: '#ddeeff' }, exposure: 1.8,
        },
        dramatic: {
            key: { intensity: 4.5, color: '#ffddaa', pos: [4, 3, -3] },
            fill: { intensity: 0.5, color: '#4444aa', pos: [-3, 1, -2] },
            back: { intensity: 3.0, color: '#ff8844', pos: [0, 3, 5] },
            ambient: { intensity: 0.3, color: '#222244' }, exposure: 1.4,
        },
        neutral: {
            key: { intensity: 2.5, color: '#ffffff', pos: [3, 5, -4] },
            fill: { intensity: 2.5, color: '#ffffff', pos: [-3, 5, -4] },
            back: { intensity: 2.0, color: '#ffffff', pos: [0, 4, 5] },
            ambient: { intensity: 1.0, color: '#ffffff' }, exposure: 1.6,
        },
    };

    /** Der Stand des Knopfs „Beleuchtung zurücksetzen". */
    static GRUNDSTAND = { vorgabe: 'studio', belichtung: 1.6,
                          hintergrund: 0x1a1a2e, sichtfeld: 35 };

    // ------------------------------------------------------------------ Setzen

    /** Eine Lampenangabe auf eine Lampe legen. */
    static lampe(licht, angabe) {
        if (!angabe) return;
        licht.intensity = angabe.intensity;
        licht.color.set(angabe.color);
        if (angabe.pos) licht.position.set(...angabe.pos);
    }

    /** Beleuchtung setzen — Vorgabe wie gespeicherter Stand, gleiche Felder. */
    static beleuchtung(angaben) {
        if (!angaben) return;
        for (const [name, feld] of Smpllicht.GRUPPEN) {
            Smpllicht.lampe(state[feld], angaben[name]);
        }
        Smpllicht.lampe(state.ambient, angaben.ambient);
        if (angaben.exposure !== undefined) {
            state.renderer.toneMappingExposure = angaben.exposure;
        }
    }

    // ------------------------------------------------------------- Anzeige

    static anzeigenAuffrischen() {
        for (const [name, feld] of Smpllicht.GRUPPEN) {
            Smpllicht._gruppeAnzeigen(name, state[feld]);
        }
        Smpllicht._setzen('scene-ambient-intensity',
                          Math.round(state.ambient.intensity * 100),
                          state.ambient.intensity.toFixed(2));
        Smpllicht._farbe('scene-ambient-color', state.ambient.color);
        const wahl = document.getElementById('scene-tonemapping');
        if (wahl) wahl.value = Smpllicht.tonwertname();
        Smpllicht._setzen('scene-exposure',
                          Math.round(state.renderer.toneMappingExposure * 100),
                          state.renderer.toneMappingExposure.toFixed(2));
        if (state.scene.background) {
            Smpllicht._farbe('scene-background', state.scene.background);
        }
        Smpllicht._setzen('scene-fov', state.camera.fov,
                          Math.round(state.camera.fov) + '°');
    }

    static _gruppeAnzeigen(name, licht) {
        Smpllicht._setzen(`scene-${name}-intensity`,
                          Math.round(licht.intensity * 100),
                          licht.intensity.toFixed(2));
        Smpllicht._farbe(`scene-${name}-color`, licht.color);
        for (const achse of Smpllicht.ACHSEN) {
            Smpllicht._setzen(`scene-${name}-pos-${achse}`, licht.position[achse],
                              licht.position[achse].toFixed(1));
        }
    }

    static _setzen(kennung, wert, text) {
        const regler = document.getElementById(kennung);
        if (regler) regler.value = wert;
        const anzeige = document.getElementById(`${kennung}-val`);
        if (anzeige) anzeige.textContent = text;
    }

    static _farbe(kennung, farbe) {
        const feld = document.getElementById(kennung);
        if (feld) feld.value = '#' + farbe.getHexString();
    }

    // ----------------------------------------------------------------- Binden

    static bedienungBinden() {
        if (!document.getElementById('tab-szene')) return;
        const wahl = document.getElementById('scene-light-preset');
        wahl?.addEventListener('change', () => {
            Smpllicht.beleuchtung(Smpllicht.VORGABEN[wahl.value]);
            Smpllicht.anzeigenAuffrischen();
        });
        for (const [name, feld] of Smpllicht.GRUPPEN) {
            Smpllicht._gruppeBinden(name, state[feld]);
        }
        Smpllicht._reglerBinden('scene-ambient-intensity', 100,
                                w => { state.ambient.intensity = w; },
                                w => w.toFixed(2));
        Smpllicht._farbeBinden('scene-ambient-color', state.ambient);
        Smpllicht._tonwertBinden();
        Smpllicht._reglerBinden('scene-exposure', 100,
                                w => { state.renderer.toneMappingExposure = w; },
                                w => w.toFixed(2));
        document.getElementById('scene-background')?.addEventListener(
            'input', ereignis => state.scene.background.set(ereignis.target.value));
        Smpllicht._sichtfeldBinden();
        document.getElementById('scene-reset-lighting')
            ?.addEventListener('click', () => Smpllicht.zuruecksetzen(wahl));
        Smpllicht.anzeigenAuffrischen();
    }

    static _gruppeBinden(name, licht) {
        Smpllicht._reglerBinden(`scene-${name}-intensity`, 100,
                                w => { licht.intensity = w; },
                                w => w.toFixed(2));
        Smpllicht._farbeBinden(`scene-${name}-color`, licht);
        for (const achse of Smpllicht.ACHSEN) {
            Smpllicht._reglerBinden(`scene-${name}-pos-${achse}`, 1,
                                    w => { licht.position[achse] = w; },
                                    w => w.toFixed(1));
        }
    }

    /** Ein Regler: Wert durch `teiler`, dann setzen und anzeigen. */
    static _reglerBinden(kennung, teiler, setzen, formatieren) {
        const regler = document.getElementById(kennung);
        if (!regler) return;
        regler.addEventListener('input', () => {
            const wert = parseFloat(regler.value) / teiler;
            setzen(wert);
            const anzeige = document.getElementById(`${kennung}-val`);
            if (anzeige) anzeige.textContent = formatieren(wert);
        });
    }

    static _farbeBinden(kennung, ziel) {
        const feld = document.getElementById(kennung);
        feld?.addEventListener('input', () => ziel.color.set(feld.value));
    }

    static _tonwertBinden() {
        const wahl = document.getElementById('scene-tonemapping');
        wahl?.addEventListener('change', () => {
            if (VIEWER_TONE_MAPPINGS[wahl.value] !== undefined) {
                state.renderer.toneMapping = VIEWER_TONE_MAPPINGS[wahl.value];
            }
        });
    }

    static _sichtfeldBinden() {
        const regler = document.getElementById('scene-fov');
        regler?.addEventListener('input', () => {
            state.camera.fov = parseFloat(regler.value);
            state.camera.updateProjectionMatrix();
            const anzeige = document.getElementById('scene-fov-val');
            if (anzeige) anzeige.textContent = regler.value + '°';
        });
    }

    static zuruecksetzen(wahl) {
        const grund = Smpllicht.GRUNDSTAND;
        Smpllicht.beleuchtung(Smpllicht.VORGABEN[grund.vorgabe]);
        state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        state.renderer.toneMappingExposure = grund.belichtung;
        state.scene.background.set(grund.hintergrund);
        state.camera.fov = grund.sichtfeld;
        state.camera.updateProjectionMatrix();
        Smpllicht.anzeigenAuffrischen();
        if (wahl) wahl.value = grund.vorgabe;
    }

    // ------------------------------------------------------------ Einstellungen

    /** Der Name des eingestellten Tonwertverfahrens. */
    static tonwertname() {
        for (const [name, wert] of Object.entries(VIEWER_TONE_MAPPINGS)) {
            if (state.renderer.toneMapping === wert) return name;
        }
        return 'ACESFilmic';
    }

    static _angabe(licht, mitPosition = true) {
        const angabe = { intensity: licht.intensity,
                         color: '#' + licht.color.getHexString() };
        if (mitPosition) {
            angabe.pos = [licht.position.x, licht.position.y, licht.position.z];
        }
        return angabe;
    }

    /** Der Stand der Szene, so wie er gespeichert wird. */
    static einstellungen() {
        const beleuchtung = { ambient: Smpllicht._angabe(state.ambient, false) };
        for (const [name, feld] of Smpllicht.GRUPPEN) {
            beleuchtung[name] = Smpllicht._angabe(state[feld]);
        }
        return {
            lighting: beleuchtung,
            renderer: {
                toneMapping: Smpllicht.tonwertname(),
                exposure: state.renderer.toneMappingExposure,
                background: '#' + (state.scene.background
                    ? state.scene.background.getHexString() : '1a1a2e'),
            },
            camera: { fov: state.camera.fov },
        };
    }

    static einstellungenAnwenden(stand) {
        if (!stand || typeof stand !== 'object') return;
        Smpllicht.beleuchtung(stand.lighting);
        const bild = stand.renderer;
        if (bild) {
            if (VIEWER_TONE_MAPPINGS[bild.toneMapping] !== undefined) {
                state.renderer.toneMapping = VIEWER_TONE_MAPPINGS[bild.toneMapping];
            }
            if (bild.exposure !== undefined) {
                state.renderer.toneMappingExposure = bild.exposure;
            }
            if (bild.background) state.scene.background.set(bild.background);
        }
        if (stand.camera?.fov) {
            state.camera.fov = stand.camera.fov;
            state.camera.updateProjectionMatrix();
        }
        Smpllicht.anzeigenAuffrischen();
    }
}
