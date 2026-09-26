/**
 * Genesis9lipsync — Lippensynchronisation in der SZENE: eine Tondatei, die
 * Mundformen von Rhubarb, die Visemes der Genesis-9-Figuren im Takt der
 * laufenden Animation.
 *
 * WARUM (18.09.2026 abends, Offen-Punkt „Lipsync in der Szene — die Szene
 * hat keine Tonspur"): Das BVH Studio hatte Tonspur und Lippensync
 * (`studio/audiospur.js`, `mimikgenesis9.js`), die Szene nur die
 * Animation. Hier bekommt der Reiter Animation einen Abschnitt
 * (`_szene_lipsync.html`): Tondatei wählen → Upload wie im Studio
 * (`/api/studio/audio-upload/`) → Rhubarb (`POST /api/studio/lipsync/`,
 * `{cues: [{start, end, form}]}`) → je Bild an der Zeit der laufenden
 * Aktion (`state.currentAction.time`) die Reglergewichte
 * (`Lipsynckurve.gewichte` mit `Lipsyncformen.GENESIS9`) auf JEDE
 * Genesis-9-Figur der Szene (`Mimikgenesis9.setzen`: Felder + Kiefer- und
 * Lippenknochen). Der Ton läuft in einem `<audio>` mit, an die Aktion
 * gekoppelt: bei Wiedergabe spielt er ab ihrer Zeit, bei Pause hält er, und
 * driftet er mehr als `DRIFT_S`, wird er nachgestellt.
 *
 * Ohne Animation (keine Aktion) läuft die Zeit des Tons selbst — so lässt
 * sich eine Figur auch im Stand sprechen lassen.
 */
import { state } from '../state.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Lipsynckurve, Lipsyncformen } from '../../gemeinsam/lipsynckurve.js';
import { Mimikgenesis9 } from '../../studio/mimikgenesis9.js';

export class Genesis9lipsync {

    static HOCHLADEN = '/api/studio/audio-upload/';
    static CUES = '/api/studio/lipsync/';
    static DRIFT_S = 0.2;
    static FELDER = { datei: 'scene-lipsync-datei', status: 'scene-lipsync-status',
                      ton: 'scene-lipsync-ton', weg: 'scene-lipsync-weg' };

    static cues = null;
    static audioUrl = null;
    static _audio = null;
    static _gesetzt = new Set();       // Figuren, die gerade Gewichte tragen

    /** Einmal je Seite: Hörer an die Felder des Reiters. */
    static einrichten(dokument = document) {
        const datei = dokument.getElementById(Genesis9lipsync.FELDER.datei);
        datei?.addEventListener('change', () => {
            const d = datei.files?.[0];
            if (d) Genesis9lipsync.laden(d).catch(f => Genesis9lipsync.melden(`Fehler: ${f.message}`));
        });
        dokument.getElementById(Genesis9lipsync.FELDER.weg)
            ?.addEventListener('click', () => Genesis9lipsync.entfernen());
    }

    static melden(text) {
        const feld = document.getElementById(Genesis9lipsync.FELDER.status);
        if (feld) feld.textContent = text;
    }

    /** Tondatei hochladen, Mundformen holen, Ton bereitstellen. */
    static async laden(datei) {
        Genesis9lipsync.melden(`Lade ${datei.name} …`);
        const formular = new FormData();
        formular.append('audio', datei);
        const hoch = await Serverabruf.formular(Genesis9lipsync.HOCHLADEN, formular);
        if (!hoch?.ok || !hoch.url) throw new Error(hoch?.error || 'Upload fehlgeschlagen');
        Genesis9lipsync.melden('Erkenne Mundformen (Rhubarb) …');
        const antwort = await Serverabruf.senden(Genesis9lipsync.CUES, { audioUrl: hoch.url });
        if (!antwort?.ok) throw new Error(antwort?.fehler || 'Rhubarb fehlgeschlagen');
        Genesis9lipsync.setzen(antwort.cues, hoch.url);
        Genesis9lipsync.melden(`${datei.name}: ${antwort.cues.length} Mundformen, ${antwort.dauer.toFixed(1)} s`);
        return antwort.cues;
    }

    /** Cues (und Ton) übernehmen — auch für Proben ohne Upload. */
    static setzen(cues, audioUrl = null) {
        Genesis9lipsync.cues = Array.isArray(cues) && cues.length ? cues : null;
        Genesis9lipsync.audioUrl = audioUrl;
        Genesis9lipsync._audio?.pause();
        Genesis9lipsync._audio = null;
        if (audioUrl) {
            const a = new Audio(audioUrl);
            a.preload = 'auto';
            Genesis9lipsync._audio = a;
        }
    }

    static entfernen() {
        Genesis9lipsync.setzen(null);
        for (const inst of Genesis9lipsync._gesetzt) Mimikgenesis9.setzen(inst, {});
        Genesis9lipsync._gesetzt.clear();
        Genesis9lipsync.melden('—');
    }

    /** Die Zeit, an der der Mund steht: die laufende Aktion, sonst der Ton. */
    static zeit() {
        const aktion = state.currentAction;
        if (aktion && state.mixer) return aktion.time;
        return Genesis9lipsync._audio ? Genesis9lipsync._audio.currentTime : null;
    }

    /** Aus der Szenenschleife, nach dem Mischer. */
    static takt() {
        if (!Genesis9lipsync.cues) return null;
        const t = Genesis9lipsync.zeit();
        if (t === null) return null;
        Genesis9lipsync._ton(t);
        const gewichte = Lipsynckurve.gewichte(Genesis9lipsync.cues, t, Lipsyncformen.GENESIS9);
        for (const inst of state.characters.values()) {
            if (inst?.quelle !== 'genesis9' || !inst.bodyMesh) continue;
            if (Mimikgenesis9.setzen(inst, gewichte)) Genesis9lipsync._gesetzt.add(inst);
        }
        return gewichte;
    }

    /** Den Ton an die Aktion koppeln (nur mit Kästchen „Ton"). */
    static _ton(t) {
        const a = Genesis9lipsync._audio;
        if (!a) return;
        const an = document.getElementById(Genesis9lipsync.FELDER.ton)?.checked ?? true;
        const laeuft = !!(state.playing && state.currentAction && state.mixer);
        if (!an || !laeuft) {
            if (!a.paused && state.currentAction) a.pause();
            return;
        }
        if (Math.abs(a.currentTime - t) > Genesis9lipsync.DRIFT_S) a.currentTime = t;
        if (a.paused) a.play().catch(fehler => Protokoll.debug('Lipsync', `Ton: ${fehler.message}`));
    }
}

window.__lipsync = Genesis9lipsync;
