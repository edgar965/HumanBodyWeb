import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Spurerzeugung } from './spurerzeugung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Spurauswahl } from './spurauswahl.js';

/**
 * Effektschluessel — ein Speed-Ereignis auf einer Effekte-Spur setzen.
 *
 * Herausgeloest analog zu `kameraschluessel.js`/`lichtschluessel.js`. Anders
 * als dort speichert der Schluessel keinen Zustand der Szene, sondern nur die
 * eingestellte Wiedergabegeschwindigkeit (`state.playbackSpeed`) — die
 * Interpolation zwischen zwei Schluesseln rechnet `effektespur.js`.
 */
export class Effektschluessel {

    /** Die Effekte-Spur zur Animationsspur `bvhIdx` — angelegt, falls nötig. */
    static spurZuAnimation(bvhIdx) {
        const vorhanden = state.project.tracks.find(
            t => t.type === 'effekte' && t._linkedAnimIdx === bvhIdx);
        if (vorhanden) return vorhanden;
        return Spurerzeugung.effekte(null, bvhIdx);
    }

    /** Speed-Ereignis auf einer BEKANNTEN Effekte-Spur setzen. */
    static setzenAufSpur(effekteIdx, bild, speed) {
        const spur = state.project.tracks[effekteIdx];
        if (!spur || spur.type !== 'effekte') return null;
        pushUndo('Speed-Ereignis');
        const stelle = Effektschluessel._platzieren(spur, bild, speed);
        Effektschluessel._nachAenderung(effekteIdx, spur);
        Protokoll.info('BVH Studio', `Speed-Ereignis ${speed}x bei Frame ${stelle}`);
        return spur.clips.find(c => c.type === 'speed_kf' && c.startFrame === stelle);
    }

    /**
     * Speed-Ereignis fuer eine Animationsspur setzen — legt ihre Effekte-Spur
     * an, falls sie noch keine hat (Taste G auf der Animationsspur).
     */
    static setzenFuerAnimation(bvhIdx, bild, speed) {
        const spur = Effektschluessel.spurZuAnimation(bvhIdx);
        return Effektschluessel.setzenAufSpur(state.project.indexOf(spur), bild, speed);
    }

    /** Abstand der Anfahrt-/Ausfahrt-Rampe vor/nach dem Standbild, in Bildern. */
    static RAMPE_BILDER = 2;

    /**
     * Standbild als BALKEN einfuegen: VIER Speed-Ereignisse — Tempo 1 kurz vor
     * dem Start, Tempo 0 am Start, Tempo 0 am Ende, Tempo 1 kurz nach dem Ende
     * (Edgar, 22.09.2026: „leicht versetzt, einmal 1 dann 0, am ende 0 dann
     * 1"). Dazwischen liegt (`effektespur.js`) automatisch ein Balken mit
     * Geschwindigkeit 0 (das eigentliche Standbild); die beiden kurzen
     * Rand-Balken (`RAMPE_BILDER` Bilder) bremsen/beschleunigen weich statt
     * hart zu schneiden — OHNE die Rand-Ereignisse spraenge das Tempo an
     * Start/Ende ohne Zwischenstufe von der impliziten Vorgabe (1 ausserhalb
     * jedes Balkens, `Effektespur.VORGABE_SPEED`) auf 0. Kein Splitten, kein
     * Trimmen noetig (Edgar, 22.09.2026: „Kontextmenü-Eintrag für 'Ereignis'
     * hinzufügen für Standbild usw.", ganz am Anfang bereits „Länge
     * veränderbar, Anfang und Ende trimmen brauche ich nicht") — die Laenge
     * aendert sich, indem man einen der mittleren Punkte zieht oder im
     * Eigenschaften-Feld sein „Frame" aendert.
     */
    static standbildEinfuegen(effekteIdx, bild, dauerBilder = null) {
        const spur = state.project.tracks[effekteIdx];
        if (!spur || spur.type !== 'effekte') return null;
        pushUndo('Standbild einfügen');
        const start = (bild != null) ? bild : state.playheadFrame;
        const dauer = dauerBilder || state.project.fps;
        const rampe = Effektschluessel.RAMPE_BILDER;
        // Eigene Namen statt der Vorgabe „Speed N" (22.09.2026, Edgar: „bei
        // Standbild einfügen fügt es Speed events hinzu???" — technisch stimmt
        // das (ein Standbild IST eine Kette von Speed-Ereignissen, siehe
        // Klassendoku), aber das Eigenschaften-Feld zeigte nur „Speed: Speed 1"
        // und verriet nirgends, dass hier ein Standbild entstanden ist).
        Effektschluessel._platzieren(spur, Math.max(0, start - rampe), 1, 'Standbild Anfahrt');
        Effektschluessel._platzieren(spur, start, 0, 'Standbild Start');
        Effektschluessel._platzieren(spur, start + dauer, 0, 'Standbild Ende');
        Effektschluessel._platzieren(spur, start + dauer + rampe, 1, 'Standbild Ausfahrt');
        Effektschluessel._nachAenderung(effekteIdx, spur);
        Protokoll.info('BVH Studio', `Standbild bei Frame ${start}, ${dauer} Bilder`);
        return spur.clips.find(c => c.type === 'speed_kf' && c.startFrame === start);
    }

    /** Ereignis in `spur.clips` setzen (neu oder vorhandenes Bild ueberschreiben) — ohne Nebenwirkungen. */
    static _platzieren(spur, bild, speed, name = null) {
        const stelle = (bild != null) ? bild : state.playheadFrame;
        const vorhandenes = spur.clips.find(c => c.type === 'speed_kf' && c.startFrame === stelle);
        if (vorhandenes) {
            vorhandenes.data.speed = speed;
            if (name) vorhandenes.name = name;
        } else {
            const schluessel = new Clip(null, name || `Speed ${spur.clips.length + 1}`, 0, state.project.fps);
            schluessel.type = 'speed_kf';
            schluessel.startFrame = stelle;
            schluessel.data = { speed };
            spur.clips.push(schluessel);
            spur.clips.sort((a, b) => a.startFrame - b.startFrame);
        }
        return stelle;
    }

    static _nachAenderung(effekteIdx, spur) {
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
        // Steckt die Effekte-Spur unter einer zugeklappten Modellspur, wäre
        // das Ereignis sonst unsichtbar (Edgar, 22.09.2026: „erscheint nicht").
        Spurauswahl.einblenden(effekteIdx, spur);
    }
}

fn.addSpeedKeyframe = (effekteIdx, bild) =>
    Effektschluessel.setzenAufSpur(effekteIdx, bild, state.playbackSpeed);
fn.addSpeedKeyframeAufAnimation = (bvhIdx, bild) =>
    Effektschluessel.setzenFuerAnimation(bvhIdx, bild, state.playbackSpeed);
fn.standbildEinfuegenEffekte = (effekteIdx, bild) =>
    Effektschluessel.standbildEinfuegen(effekteIdx, bild);
