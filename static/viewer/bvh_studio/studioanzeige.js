/**
 * Studioanzeige — das Feld oben rechts, das den Projektnamen zeigt.
 *
 * WARUM eine Klasse (Umbau 16.08.2026): Der Blink-Zeitgeber lag als loses
 * `let _studioInfoFlashTimer` auf Modulebene von project.js. Beim Aufteilen der
 * Datei waere er auf der falschen Seite liegen geblieben — genau der Fehler, der
 * in timeline.js einen ReferenceError beim Seitenaufbau erzeugt hat. Als
 * Klassenfeld gibt es genau einen Ort dafuer.
 *
 * In den statischen Methoden steht absichtlich `Studioanzeige.` statt `this.` —
 * so darf `fn.updateStudioInfo = Studioanzeige.aktualisieren` als lose
 * Funktionsreferenz weitergegeben werden, ohne `bind`.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Studioanzeige {
    /** Laufender Zeitgeber einer Kurzmeldung, sonst null. */
    static _blinker = null;

    static _feld() {
        return document.getElementById('studio-info');
    }

    /** Projektnamen anzeigen. Waehrend einer Kurzmeldung nichts tun. */
    static aktualisieren() {
        const el = Studioanzeige._feld();
        if (!el || Studioanzeige._blinker) return;
        el.textContent = `Projekt: ${state.project?.name || 'Untitled'}`;
    }

    /**
     * Dauer, Zeitleiste und Eigenschaften nachziehen — in dieser Reihenfolge.
     *
     * BEFUND `doppelcode` (30.08.2026): Stand als `_nachtragen` zeichengleich
     * in `clipbearbeitung.js` und `lichtschluessel.js`. Nach JEDER Aenderung an
     * einem Clip oder einem Licht muessen dieselben drei Ansichten neu.
     *
     * DIE REIHENFOLGE IST NICHT BELIEBIG: Die Zeitleiste zeichnet sich auf die
     * Gesamtdauer. Wer sie vor `updateDuration` zeichnet, bekommt eine Leiste
     * in der alten Laenge, in der der letzte Clip abgeschnitten ist — das
     * sieht aus wie ein verlorener Clip und ist nur eine falsche Skala.
     *
     * UEBER `fn` UND NICHT PER IMPORT: Die drei Funktionen liegen in Modulen,
     * die ihrerseits Clip- und Lichtbearbeitung rufen; ein Import waere ein
     * Ringschluss.
     */
    static nachtragen() {
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
    }

    /** Kurzmeldung zeigen (Speichern, Laden, Rueckgaengig), danach zurueck. */
    static melden(text, ms = 2500) {
        const el = Studioanzeige._feld();
        if (!el) { Protokoll.warnung('studioanzeige', text); return; }
        el.textContent = text;
        if (Studioanzeige._blinker) clearTimeout(Studioanzeige._blinker);
        Studioanzeige._blinker = setTimeout(() => {
            Studioanzeige._blinker = null;
            Studioanzeige.aktualisieren();
        }, ms);
    }
}

fn.updateStudioInfo = Studioanzeige.aktualisieren;
fn.flashStudioInfo = Studioanzeige.melden;
