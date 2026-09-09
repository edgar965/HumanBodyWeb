import { Gedaechtniswahl } from '../gemeinsam/gedaechtniswahl.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Reitergedächtnis — die letzten Einstellungen stehen beim nächsten Aufruf.
 *
 * AUFTRAG (Edgar, 09.09.2026): „merke dir die letzten Einstellungen auf allen
 * Tabs, z.B. GarmentCode, so dass sie beim nächsten Aufruf angeklickt sind."
 *
 * WAS gemerkt wird, entscheidet `Gedaechtniswahl` (Positivliste, Begründung
 * dort). Hier steht das WIE:
 *
 * `localStorage`, NICHT `sessionStorage` und nicht die Servereinstellungen.
 * `Figurmerker` liegt im sessionStorage — richtig, denn dort geht es um die
 * Figuren DIESER Sitzung. „Beim nächsten Aufruf" heißt aber: neues Fenster,
 * neuer Tag. Und die Servereinstellungen sind Vorgaben, die man in Hilfe →
 * Einstellungen setzt; ein Regler, der bei jedem Zug dorthin schreibt,
 * verwischt den Unterschied zwischen „so ist es eingestellt" und „so habe ich
 * gerade geschoben". Dieselbe Begründung wie beim `Bereichsgedaechtnis`.
 *
 * EIN DELEGIERTER HÖRER, KEINE BINDUNG JE FELD. Die 71 GarmentCode-Regler
 * entstehen erst, wenn der Server sie liefert, und werden bei jedem Wechsel
 * des Kleidungsstücks neu gebaut. Ein Hörer am Reiter fängt auch, was später
 * dazukommt — eine Bindung je Feld hätte genau diese Felder verpasst.
 *
 * JEDER ABLAGEZUGRIFF IST UMSCHLOSSEN. In einem privaten Fenster wirft schon
 * das Lesen; dann läuft die Seite ohne Gedächtnis weiter (die harmlose
 * Richtung).
 */
export class Reitergedaechtnis {

    static SCHLUESSEL = 'hb_reiter_einstellungen';
    /** Wo der zuletzt offene Reiter steht. */
    static REITER_SCHLUESSEL = 'letzter_reiter';

    static _zettel = null;

    // ----------------------------------------------------------- Ablage

    static _alle() {
        if (Reitergedaechtnis._zettel) return Reitergedaechtnis._zettel;
        try {
            const roh = localStorage.getItem(Reitergedaechtnis.SCHLUESSEL);
            const gelesen = roh ? JSON.parse(roh) : {};
            Reitergedaechtnis._zettel =
                (gelesen && typeof gelesen === 'object') ? gelesen : {};
        } catch (fehler) {
            Reitergedaechtnis._zettel = {};
        }
        return Reitergedaechtnis._zettel;
    }

    static _speichern() {
        try {
            localStorage.setItem(Reitergedaechtnis.SCHLUESSEL,
                                 JSON.stringify(Reitergedaechtnis._alle()));
            return true;
        } catch (fehler) {
            Protokoll.debug('reitergedaechtnis', 'nicht speicherbar', fehler);
            return false;
        }
    }

    static setzen(schluessel, wert) {
        Reitergedaechtnis._alle()[schluessel] = wert;
        return Reitergedaechtnis._speichern();
    }

    static holen(schluessel, ersatz = null) {
        const wert = Reitergedaechtnis._alle()[schluessel];
        return wert === undefined ? ersatz : wert;
    }

    /** Alles vergessen — für Tests und einen Neuanfang. */
    static leeren() {
        Reitergedaechtnis._zettel = {};
        Reitergedaechtnis._speichern();
    }

    // ------------------------------------------------------- Der Reiter

    static reiterMerken(name) {
        if (name) Reitergedaechtnis.setzen(
            Reitergedaechtnis.REITER_SCHLUESSEL, name);
    }

    static letzterReiter() {
        return Reitergedaechtnis.holen(Reitergedaechtnis.REITER_SCHLUESSEL);
    }

    // -------------------------------------------------------- Die Felder

    /**
     * Kennung eines Feldes: seine `id`. Kein Ersatz, und das mit Absicht.
     *
     * Die 71 GarmentCode-Regler haben keine `id`, sondern einen `data-pfad`
     * an ihrer Zeile — und sie werden NICHT hier gemerkt, sondern von
     * `garmentcodeRegler` selbst (`gcWerte`). Der Grund: Das Modul fuehrt
     * die abweichenden Werte in `this.werte` und schickt genau die an den
     * Server. Wer daneben die DOM-Werte merkte, haette zwei Buchfuehrungen
     * fuer dieselbe Zahl — sie laufen auseinander, sobald ein Preset oder
     * ein Vorlagenwechsel nur eine von beiden anfasst.
     */
    static kennung(feld) {
        return feld.id || null;
    }

    // -------------------------------------------- GarmentCode-Reglerwerte

    /** Wo die Reglerabweichungen EINER Vorlage liegen. */
    static gcSchluessel(vorlage) {
        return `garmentcode/werte:${vorlage}`;
    }

    /** Die Reglerwerte einer Vorlage merken (`{pfad: wert}`). */
    static gcWerteMerken(vorlage, werte) {
        if (!vorlage) return false;
        return Reitergedaechtnis.setzen(
            Reitergedaechtnis.gcSchluessel(vorlage), werte || {});
    }

    /** Die gemerkten Reglerwerte einer Vorlage — `{}` wenn keine. */
    static gcWerte(vorlage) {
        const werte = vorlage
            ? Reitergedaechtnis.holen(Reitergedaechtnis.gcSchluessel(vorlage))
            : null;
        return (werte && typeof werte === 'object') ? werte : {};
    }

    static _beschreibung(feld) {
        const pane = feld.closest?.('.tab-pane');
        return {
            reiter: Gedaechtniswahl.reiterName(pane?.id),
            kennung: Reitergedaechtnis.kennung(feld),
            art: feld.type,
        };
    }

    /** Der Wert eines Feldes, wie er in die Ablage geht. */
    static wertVon(feld) {
        return feld.type === 'checkbox' ? !!feld.checked : feld.value;
    }

    /** Ein Feld merken — liefert `false`, wenn es nicht dazugehört. */
    static feldMerken(feld) {
        const beschreibung = Reitergedaechtnis._beschreibung(feld);
        if (!Gedaechtniswahl.merkbar(beschreibung)) return false;
        return Reitergedaechtnis.setzen(
            Gedaechtniswahl.schluessel(beschreibung.reiter,
                                       beschreibung.kennung),
            Reitergedaechtnis.wertVon(feld));
    }

    /**
     * Gemerkte Werte in einen Bereich zurückschreiben.
     *
     * Nur wo sich der Wert unterscheidet, und mit `input`+`change`: Die
     * Module hängen an beiden Ereignissen, und ein Setzen ohne Ereignis
     * bliebe ein Wert, den nur die Anzeige kennt.
     *
     * @returns Anzahl der gesetzten Felder
     */
    static anwenden(bereich = document) {
        let gesetzt = 0;
        for (const feld of bereich.querySelectorAll('input, select, textarea')) {
            const beschreibung = Reitergedaechtnis._beschreibung(feld);
            if (!Gedaechtniswahl.merkbar(beschreibung)) continue;
            const wert = Reitergedaechtnis.holen(
                Gedaechtniswahl.schluessel(beschreibung.reiter,
                                           beschreibung.kennung));
            if (wert === null || wert === undefined) continue;
            if (Reitergedaechtnis._setzenAmFeld(feld, wert)) gesetzt += 1;
        }
        return gesetzt;
    }

    static _setzenAmFeld(feld, wert) {
        if (feld.type === 'checkbox') {
            if (feld.checked === !!wert) return false;
            feld.checked = !!wert;
        } else {
            if (feld.value === String(wert)) return false;
            feld.value = String(wert);
        }
        feld.dispatchEvent(new Event('input', { bubbles: true }));
        feld.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
    }

    /**
     * Loslegen: Hörer setzen und die gemerkten Werte anwenden.
     *
     * `change` UND `input`: Ein Schieber feuert `input` beim Ziehen und
     * `change` am Ende; eine Auswahl nur `change`. Gemerkt wird bei beiden,
     * die Ablage kostet nichts Nennenswertes (ein `JSON.stringify` auf
     * wenige Dutzend Werte).
     */
    static starten() {
        for (const pane of document.querySelectorAll('.tab-pane')) {
            if (!Gedaechtniswahl.REITER.includes(
                    Gedaechtniswahl.reiterName(pane.id))) continue;
            for (const art of ['change', 'input']) {
                pane.addEventListener(art, (ereignis) => {
                    const feld = ereignis.target;
                    if (feld?.tagName) Reitergedaechtnis.feldMerken(feld);
                });
            }
        }
        return Reitergedaechtnis.anwenden();
    }
}
