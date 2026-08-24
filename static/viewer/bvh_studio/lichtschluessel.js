import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Lichtschluessel — Keyframes einer Lichtspur anlegen.
 *
 * Herausgelöst aus `spur_lichter.js` (321 Zeilen). Dort stand der Aufbau eines
 * Licht-Keyframes DREIMAL fast gleich (Standardpaar, Paar am Schnitt, einzelner
 * Keyframe) — je fünfzehn Zeilen mit denselben neun Feldern. Wer ein Feld
 * ergänzte, musste drei Stellen finden.
 *
 * DIE VORGABEN UNTERSCHIEDEN SICH — UND ZWAR ABSICHTLICH
 * ======================================================
 * Beim Standardpaar (Anlegen einer Spur) sind `angle`, `penumbra` und `distance`
 * `null`, wenn das Licht sie nicht hat; bei den vom Nutzer gesetzten Keyframes
 * stehen echte Vorgaben (30°, 0,3, 50). Grund: Das Standardpaar friert den
 * IST-Zustand ein, ein neuer Keyframe soll bearbeitbare Werte haben — ein `null`
 * im Regler wäre nicht ziehbar. Deshalb `mitVorgaben`.
 *
 * `fade` heißt „zum nächsten Keyframe überblenden". Beim Paar am Schnitt ist der
 * obere (vor dem Schnitt) auf `false`: Genau das macht den harten Wechsel.
 */
export class Lichtschluessel {

    static VORGABE_WINKEL = Math.PI / 6;
    static VORGABE_RAND = 0.3;
    static VORGABE_REICHWEITE = 50;
    /** Wenn das Projekt keine Länge hat: zehn Sekunden. */
    static VORGABE_DAUER = 10;

    /**
     * Ein Keyframe-Clip aus dem aktuellen Zustand des Lichts.
     *
     * @param spur         die Lichtspur
     * @param bild         Startbild
     * @param name         Anzeigename
     * @param mitVorgaben  echte Vorgabewerte statt `null` (siehe Klassendoku)
     * @param zusatz       weitere Felder für `data` (z. B. `trackPosition`)
     */
    static bauen(spur, bild, name, { mitVorgaben = true, ...zusatz } = {}) {
        const licht = spur.light;
        const ziel = licht.target?.position || { x: 0, y: 0, z: 0 };
        const schluessel = new Clip(null, name, 0, state.project.fps);
        schluessel.type = 'light_kf';
        schluessel.startFrame = bild;
        schluessel.data = {
            position: { x: licht.position.x, y: licht.position.y,
                        z: licht.position.z },
            target: { x: ziel.x, y: ziel.y, z: ziel.z },
            color: '#' + licht.color.getHexString(),
            intensity: licht.intensity,
            angle: Lichtschluessel._wert(licht.angle, mitVorgaben,
                                         Lichtschluessel.VORGABE_WINKEL),
            penumbra: Lichtschluessel._wert(licht.penumbra, mitVorgaben,
                                            Lichtschluessel.VORGABE_RAND),
            distance: Lichtschluessel._wert(licht.distance, mitVorgaben,
                                            Lichtschluessel.VORGABE_REICHWEITE),
            fade: true,
            visible: !spur.muted,
            ...zusatz,
        };
        return schluessel;
    }

    static _wert(wert, mitVorgaben, vorgabe) {
        return wert ?? (mitVorgaben ? vorgabe : null);
    }

    // ------------------------------------------------------------- Standardpaar

    /**
     * Zwei Keyframes: einer bei 0, einer am Ende der Zeitleiste.
     *
     * Ohne Keyframe ist das Licht AUS — das Paar hält es über die ganze Dauer im
     * gewünschten Zustand. Namen sind schlicht durchnummeriert.
     */
    static standardpaar(spur) {
        if (!spur.light) return;
        const endbild = Math.max(
            Math.round((state.project.duration || Lichtschluessel.VORGABE_DAUER)
                       * state.project.fps), 10);
        spur.clips.push(Lichtschluessel.bauen(spur, 0, '1',
                                              { mitVorgaben: false }));
        if (endbild > 0) {
            spur.clips.push(Lichtschluessel.bauen(spur, endbild, '2',
                                                  { mitVorgaben: false }));
        }
    }

    // -------------------------------------------------------- Vom Nutzer gesetzt

    /** Ein einzelner Keyframe am Abspielkopf (oder am angegebenen Bild). */
    static einzeln(spurnummer, bild) {
        const spur = Lichtschluessel._spur(spurnummer);
        if (!spur) return;
        pushUndo('Licht Keyframe');
        const stelle = bild != null ? bild : state.playheadFrame;
        spur.clips.push(Lichtschluessel.bauen(
            spur, stelle, `Licht ${spur.clips.length + 1}`));
        spur.clips.sort((a, b) => a.startFrame - b.startFrame);
        Lichtschluessel._nachtragen();
        Protokoll.info('BVH Studio',
                       `Licht-Keyframe gespeichert bei Frame ${stelle}`);
    }

    /**
     * Zwei Keyframes am GLEICHEN Bild — vor und nach dem Schnitt.
     *
     * Damit lässt sich das Licht an einer Stelle hart umschalten. In der
     * Zeitleiste werden sie oben/unten versetzt gezeichnet (`trackPosition`).
     */
    static paar(spurnummer, bild) {
        const spur = Lichtschluessel._spur(spurnummer);
        if (!spur) return;
        pushUndo('Lichteigenschaft-Pair');
        const stelle = bild != null ? bild : state.playheadFrame;
        const nummer = spur.clips.length + 1;
        spur.clips.push(Lichtschluessel.bauen(spur, stelle,
                                             `Licht ${nummer} (vor)`,
                                             { trackPosition: 'upper',
                                               fade: false }));
        spur.clips.push(Lichtschluessel.bauen(spur, stelle,
                                             `Licht ${nummer + 1} (nach)`,
                                             { trackPosition: 'lower' }));
        spur.clips.sort(Lichtschluessel._reihenfolge);
        Lichtschluessel._nachtragen();
        fn.serverLog?.('light_kf_pair_added',
                       `track=${spur.name} frame=${stelle}`);
    }

    /** Nach Bild, bei gleichem Bild der obere zuerst. */
    static _reihenfolge(a, b) {
        if (a.startFrame !== b.startFrame) return a.startFrame - b.startFrame;
        const rang = clip => (clip.data?.trackPosition === 'upper' ? 0 : 1);
        return rang(a) - rang(b);
    }

    static _spur(spurnummer) {
        const spur = state.project.tracks[spurnummer];
        if (!spur || spur.type !== 'light' || !spur.light) return null;
        return spur;
    }

    static _nachtragen() {
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
    }
}
