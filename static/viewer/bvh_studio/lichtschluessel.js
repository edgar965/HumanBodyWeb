import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Studioanzeige } from './studioanzeige.js';

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
     * @param {Object<string, any>} [wahl]  `mitVorgaben`: echte Vorgabewerte statt
     *               `null` (siehe Klassendoku); alles Weitere geht als Feld in
     *               `data` (z. B. `trackPosition`)
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

    /**
     * Ein Keyframe am Abspielkopf (oder am angegebenen Bild) — für ALLE
     * Lichtspuren zugleich, nicht nur die gerade gewählte (Edgar, 23.09.2026:
     * „das Event soll für alle Lichter gelten" — mit nur der gewählten Spur
     * blieben die übrigen Lichter auf ihrem alten Stand stehen, obwohl sie im
     * 3D-Fenster längst anders standen). `spurnummer` entscheidet nur, OB
     * überhaupt eine Lichtspur gemeint ist (Aufrufer prüfen das meist schon
     * selbst) — jede Spur erhält danach IHREN EIGENEN aktuellen Zustand.
     */
    static einzeln(spurnummer, bild) {
        if (!Lichtschluessel._spur(spurnummer)) return;
        const lichtspuren = Lichtschluessel._alle();
        if (lichtspuren.length === 0) return;
        pushUndo('Licht Keyframe');
        const stelle = bild != null ? bild : state.playheadFrame;
        const nummer = Lichtschluessel._naechsteNummer(lichtspuren);
        for (const s of lichtspuren) {
            s.clips.push(Lichtschluessel.bauen(s, stelle, `Licht ${nummer}`));
            s.clips.sort((a, b) => a.startFrame - b.startFrame);
        }
        Lichtschluessel._nachtragen();
        Protokoll.info('BVH Studio',
                       `Licht-Keyframe für ${lichtspuren.length} Lichter `
                       + `gespeichert bei Frame ${stelle}`);
    }

    /**
     * Zwei Keyframes am GLEICHEN Bild — vor und nach dem Schnitt, für ALLE
     * Lichtspuren (siehe `einzeln`).
     *
     * Damit lässt sich das Licht an einer Stelle hart umschalten. In der
     * Zeitleiste werden sie oben/unten versetzt gezeichnet (`trackPosition`).
     */
    static paar(spurnummer, bild) {
        if (!Lichtschluessel._spur(spurnummer)) return;
        const lichtspuren = Lichtschluessel._alle();
        if (lichtspuren.length === 0) return;
        pushUndo('Lichteigenschaft-Pair');
        const stelle = bild != null ? bild : state.playheadFrame;
        const nummer = Lichtschluessel._naechsteNummer(lichtspuren);
        for (const s of lichtspuren) {
            s.clips.push(Lichtschluessel.bauen(s, stelle,
                                               `Licht ${nummer} (vor)`,
                                               { trackPosition: 'upper',
                                                 fade: false }));
            s.clips.push(Lichtschluessel.bauen(s, stelle,
                                               `Licht ${nummer + 1} (nach)`,
                                               { trackPosition: 'lower' }));
            s.clips.sort(Lichtschluessel._reihenfolge);
        }
        Lichtschluessel._nachtragen();
        fn.serverLog?.('light_kf_pair_added', `frame=${stelle}`);
    }

    /** Alle Lichtspuren des Projekts mit angeschlossenem Licht. */
    static _alle() {
        return state.project.tracks.filter(t => t.type === 'light' && t.light);
    }

    /** Höchste vorhandene Keyframe-Zahl über alle Spuren + 1 — hält die
     *  Namen synchron, auch wenn eine Spur schon eigene (ältere) Keyframes
     *  hatte, die eine andere noch nicht kennt. */
    static _naechsteNummer(lichtspuren) {
        return Math.max(0, ...lichtspuren.map(s => s.clips.length)) + 1;
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

    /** Dauer, Zeitleiste, Eigenschaften — siehe `Studioanzeige`. */
    static _nachtragen() {
        Studioanzeige.nachtragen();
    }
}
