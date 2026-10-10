import { Protokoll } from './protokoll.js';

/**
 * Normalenarbeit — die Normalen der Gelenkkorrekturen auf einem Worker rechnen lassen (Hauptfaden-Seite von
 * `normalenarbeiter.js`, Rechnung in `normalenrechnung.js`; 09.10.2026).
 *
 * WARUM (Edgar: „auf /Charakter/ ruckelt die Bedienung mit Damira, vergrößern, verkleinern, die Animation"): Bei laufender
 * Animation verschieben die JCMs über die Hälfte der Körperpunkte jedes Bild; die Normalen davon stehen mit 25–70 ms je Bild
 * auf dem Hauptfaden (Zeitmesser um `Genesis9normalen.nachziehen`, Chrome-Tab, Damira tanzt: 78 % der Gelenkkorrekturen).
 *
 * EIN Auftrag je Geometrie zur Zeit. Kommt ein neues Bild, während einer rechnet, wird NICHT gestapelt: der Auftrag merkt sich
 * nur „neu" und schickt nach der Antwort die dann aktuelle Lage. Die Normalen hängen so ein bis drei Bilder hinter den
 * Punkten her — bei einer stehenden Figur gar nicht, denn das letzte Bild löst immer noch einen letzten Auftrag aus.
 *
 * Was beim Eintreffen geschrieben wird, bestimmt der Stand JETZT (`stand.marke`): ein Punkt, der inzwischen wieder in der Ruhe
 * steht, bekommt nichts. Rechnet ein spätes Bild synchron (`Genesis9normalen.nachziehen`, wenige Punkte), trägt das einen neuen
 * `stempel` — die Antwort eines Auftrags von vorher ist dann überholt und wird verworfen, sonst überschriebe sie die frischeren
 * Normalen.
 *
 * Schalter: Einstellungen → Charakter → „Normalen der Gelenkkorrekturen im Worker" (`ui_prefs.normalen_worker`, Vorgabe AUS;
 * gelesen von `Starteinstellungen`, wirkt nach dem Neuladen). Aus = die Rechnung von vorher, je Punkt auf dem Hauptfaden.
 *
 * Fehlt der Pfad (die Seite hat kein `<meta name="normalenarbeiter">`, etwa das Studio), gibt es keinen Worker und der
 * Hauptfaden rechnet wie vorher. Fällt der Worker aus, ebenso — mit einer Warnung im Log, und er wird nicht wieder versucht.
 */
export class Normalenarbeit {

    /** Die Einstellung; `Genesis9normalen` fragt sie, bevor es die schnelle Rechnung (Worker, Durchlauf über alle Dreiecke) nimmt. */
    static eingeschaltet = false;
    static ausgefallen = false;
    static _arbeiter = null;
    /** Geometrie -> Eintrag; die Geometrie darf verschwinden. */
    static _eintraege = new WeakMap();
    /** Kennung -> Eintrag (für die Antworten; Einträge verschwinden mit `dispose`). */
    static _nachKennung = new Map();
    static _zaehler = 0;

    /** Der Pfad des Workers aus der Vorlage (mit Fassung); null, wenn die Seite keinen kennt. */
    static pfad() {
        return typeof document !== 'undefined' ? document.querySelector('meta[name="normalenarbeiter"]')?.content || null : null;
    }

    static einschalten(an) {
        Normalenarbeit.eingeschaltet = an === true || an === '1' || an === 1;
    }

    static verfuegbar() {
        return Normalenarbeit.eingeschaltet && !Normalenarbeit.ausgefallen && typeof Worker !== 'undefined' && !!Normalenarbeit.pfad();
    }

    /**
     * Ein Bild für `geo` anmelden. @returns true, wenn der Worker die Normalen liefert; false = der Aufrufer rechnet selbst.
     * @param v     `Genesis9normalen.vorbereiten` (Gruppen, Ruhenormalen)
     * @param stand `geo.userData.felder` (Marken, berührte Punkte, Ruhelage)
     */
    static anfordern(geo, v, stand) {
        if (!Normalenarbeit.verfuegbar()) return false;
        const eintrag = Normalenarbeit._eintrag(geo, v, stand);
        if (!eintrag) return false;
        eintrag.neu = true;
        if (!eintrag.laeuft) Normalenarbeit._senden(eintrag);
        return true;
    }

    /** Ein synchroner Zug hat gerechnet: Antworten von vorher sind überholt. */
    static ueberholt(geo) {
        const eintrag = Normalenarbeit._eintraege.get(geo);
        if (eintrag) eintrag.stempel += 1;
    }

    static _eintrag(geo, v, stand) {
        let eintrag = Normalenarbeit._eintraege.get(geo);
        if (eintrag) return eintrag;
        const arbeiter = Normalenarbeit._starten();
        if (!arbeiter) return null;
        eintrag = { netz: ++Normalenarbeit._zaehler, geo, v, stand, laeuft: false, neu: false, folge: 0, stempel: 0 };
        Normalenarbeit._eintraege.set(geo, eintrag);
        Normalenarbeit._nachKennung.set(eintrag.netz, eintrag);
        // Das Netz einmal: Kopien, die übertragen werden (ein Ausschnitt eines großen Puffers würde ganz mitgeklont).
        const index = geo.index.array.slice(), gruppe = v.gruppe.slice(), ruhePos = stand.ruhe.slice();
        arbeiter.postMessage({ typ: 'netz', netz: eintrag.netz, index, gruppe, ruhePos, anzahlGruppen: v.gerechnet.length },
                             [index.buffer, gruppe.buffer, ruhePos.buffer]);
        geo.addEventListener('dispose', () => Normalenarbeit._frei(eintrag));
        return eintrag;
    }

    static _senden(eintrag) {
        const { geo, v, stand } = eintrag;
        const pos = geo.getAttribute('position').array.slice();
        const ruheNormalen = v.ruhe.slice();
        const punkte = stand.beruehrt.slice(0, stand.anzahl);
        eintrag.laeuft = true;
        eintrag.neu = false;
        eintrag.folge += 1;
        Normalenarbeit._arbeiter.postMessage(
            { typ: 'rechnen', netz: eintrag.netz, folge: eintrag.folge, stempel: eintrag.stempel,
              pos, ruheNormalen, punkte, anzahl: punkte.length },
            [pos.buffer, ruheNormalen.buffer, punkte.buffer]);
    }

    static _starten() {
        if (Normalenarbeit._arbeiter) return Normalenarbeit._arbeiter;
        try {
            const arbeiter = new Worker(Normalenarbeit.pfad(), { type: 'module' });
            arbeiter.onmessage = (ereignis) => Normalenarbeit._angekommen(ereignis.data);
            arbeiter.onerror = (ereignis) => {
                ereignis.preventDefault?.();
                Normalenarbeit._ausfall(`Worker: ${ereignis.message || 'abgebrochen'}`);
            };
            Normalenarbeit._arbeiter = arbeiter;
        } catch (fehler) {
            Normalenarbeit._ausfall(`nicht gestartet: ${fehler.message}`);
        }
        return Normalenarbeit._arbeiter;
    }

    static _angekommen(daten) {
        if (daten?.typ === 'fehler') {
            Normalenarbeit._ausfall(daten.meldung);
            return;
        }
        if (daten?.typ !== 'fertig') return;
        const eintrag = Normalenarbeit._nachKennung.get(daten.netz);
        if (!eintrag) return;
        eintrag.laeuft = false;
        if (daten.stempel === eintrag.stempel) Normalenarbeit._schreiben(eintrag, daten.punkte, daten.normalen);
        if (eintrag.neu) Normalenarbeit._senden(eintrag);
    }

    /** Die Normalen der Punkte, die JETZT noch berührt sind, ins Attribut — die übrigen stehen schon in der Ruhe. */
    static _schreiben(eintrag, punkte, normalen) {
        const normal = eintrag.geo.getAttribute('normal');
        const marke = eintrag.stand.marke, aus = normal.array;
        for (let j = 0; j < punkte.length; j++) {
            const q = punkte[j];
            if (!marke[q]) continue;
            aus[3 * q] = normalen[3 * j]; aus[3 * q + 1] = normalen[3 * j + 1]; aus[3 * q + 2] = normalen[3 * j + 2];
        }
        normal.needsUpdate = true;
    }

    static _frei(eintrag) {
        Normalenarbeit._nachKennung.delete(eintrag.netz);
        Normalenarbeit._eintraege.delete(eintrag.geo);
        Normalenarbeit._arbeiter?.postMessage({ typ: 'frei', netz: eintrag.netz });
    }

    /** Der Worker fällt aus: Hauptfaden rechnet wieder selbst, der nächste Zug holt alles nach. */
    static _ausfall(grund) {
        if (Normalenarbeit.ausgefallen) return;
        Normalenarbeit.ausgefallen = true;
        Normalenarbeit._arbeiter?.terminate();
        Normalenarbeit._arbeiter = null;
        for (const eintrag of Normalenarbeit._nachKennung.values()) eintrag.laeuft = false;
        Protokoll.warnung('Normalenarbeit', `Normalen der Gelenkkorrekturen ohne Worker, der Hauptfaden rechnet selbst: ${grund}`);
    }
}
