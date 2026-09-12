/**
 * Zeilenwahl — Kästchen je Zeile, Bereich mit Shift, „alle" im Kopf.
 *
 * Edgar (12.09.2026): „Checkbox auswählen, Multi-Select mit Shift und
 * Batch-Delete" für die Auftragstabelle. Die Kästchen gab es, den Bereich
 * nicht: Wer zwanzig Aufträge löschen wollte, klickte zwanzigmal.
 *
 * WIE DER BEREICH GEHT: Ein Klick merkt sich sein Kästchen. Ein Shift-Klick
 * setzt alle Kästchen ZWISCHEN dem gemerkten und dem geklickten auf den
 * Zustand des geklickten — an oder aus, je nachdem, was der Klick gerade
 * getan hat. „Zwischen" heißt in der SICHTBAREN Reihenfolge: djangoBase hängt
 * die Zeilen beim Sortieren um, und die Kästchen werden jedes Mal frisch aus
 * dem Tabellenkörper gelesen. Detailzeilen (Fortschritt) haben kein Kästchen
 * und zählen nicht.
 *
 * DAS KOPFKÄSTCHEN zeigt drei Zustände: leer, alle, teils (`indeterminate`).
 * Ein Klick darauf wählt alle, wenn nicht alle gewählt sind, sonst keines.
 *
 * Die Klasse hängt an der TABELLE, nicht am Dokument: Die Foto-Aufträge haben
 * ihre eigenen Kästchen (`fotoauftragsliste.js`), die hier nichts angehen.
 */
export class Zeilenwahl {

    /** Die Kästchen der Zeilen. */
    static KASTEN = 'input.job-check';
    /** Das Kästchen im Kopf. */
    static ALLE = 'select-all';
    /** Klasse einer gewählten Zeile (`auftragstabelle.css`). */
    static GEWAEHLT = 'gewaehlt';

    /**
     * @param {HTMLTableElement} tabelle
     * @param {(anzahl: number) => void} [beiAenderung] wird nach jeder
     *        Änderung mit der Zahl der gewählten Zeilen gerufen
     */
    constructor(tabelle, beiAenderung) {
        this.tabelle = tabelle;
        this.beiAenderung = beiAenderung || (() => {});
        /** @type {HTMLInputElement|null} zuletzt angeklicktes Kästchen */
        this.letztes = null;
    }

    binden() {
        if (!this.tabelle) return this;
        this.tabelle.addEventListener('click', ereignis => this._klick(ereignis));
        // Shift+Klick würde sonst den Text zwischen den Zeilen markieren —
        // und djangoBase verwirft einen Sortierklick, solange etwas
        // markiert ist. Das Kästchen schaltet trotzdem (das tut der Klick,
        // nicht der Mausdruck).
        this.tabelle.addEventListener('mousedown', ereignis => {
            if (ereignis.shiftKey && ereignis.target.matches(Zeilenwahl.KASTEN)) {
                ereignis.preventDefault();
            }
        });
        // Beim `click` hat der Browser das Kopfkästchen schon umgeschaltet;
        // `nachziehen` stellt es danach aus den Zeilen. KEIN preventDefault:
        // Das ließe den Browser den Haken nach dem Handler zurücksetzen —
        // über alles hinweg, was der Handler gesetzt hat.
        this.kopf()?.addEventListener('click', () => {
            const alle = this.kaesten();
            const voll = alle.length > 0 && alle.every(k => k.checked);
            this.alleSetzen(!voll);
            this.nachziehen();
        });
        this.nachziehen();
        return this;
    }

    /** Das Kopfkästchen — steht im `<thead>` der Tabelle. */
    kopf() {
        return this.tabelle.querySelector('#' + Zeilenwahl.ALLE);
    }

    /** Die Kästchen des Körpers in der sichtbaren Reihenfolge. */
    kaesten() {
        return [...this.tabelle.querySelectorAll('tbody ' + Zeilenwahl.KASTEN)];
    }

    /** Die Kennungen (Werte) der gewählten Zeilen. */
    kennungen() {
        return this.kaesten().filter(k => k.checked).map(k => k.value);
    }

    anzahl() {
        return this.kennungen().length;
    }

    alleSetzen(an) {
        this.kaesten().forEach(k => { k.checked = an; });
        this.letztes = null;
    }

    _klick(ereignis) {
        const kasten = ereignis.target.closest(Zeilenwahl.KASTEN);
        if (!kasten) return;
        const kaesten = this.kaesten();
        if (ereignis.shiftKey && this.letztes && this.letztes !== kasten) {
            Zeilenwahl.bereich(kaesten, this.letztes, kasten)
                .forEach(k => { k.checked = kasten.checked; });
        }
        this.letztes = kasten;
        this.nachziehen();
    }

    /**
     * Die Elemente von `von` bis `bis` (beide einschließlich), in der
     * Reihenfolge der Liste — egal, welches der beiden vorn steht. Ist eines
     * nicht (mehr) in der Liste — die Zeile wurde gelöscht —, gibt es keinen
     * Bereich, und nur das geklickte Kästchen ändert sich.
     * @template T
     * @param {T[]} liste
     * @param {T} von
     * @param {T} bis
     * @returns {T[]}
     */
    static bereich(liste, von, bis) {
        const a = liste.indexOf(von);
        const b = liste.indexOf(bis);
        if (a < 0 || b < 0) return [];
        return liste.slice(Math.min(a, b), Math.max(a, b) + 1);
    }

    /**
     * Zustand des Kopfkästchens aus der Zahl der gewählten Zeilen.
     * @returns {{checked: boolean, indeterminate: boolean}}
     */
    static kopfstand(gewaehlt, gesamt) {
        return { checked: gesamt > 0 && gewaehlt === gesamt,
                 indeterminate: gewaehlt > 0 && gewaehlt < gesamt };
    }

    /** Zeilen markieren, Kopfkästchen stellen, Zähler melden. */
    nachziehen() {
        const kaesten = this.kaesten();
        kaesten.forEach(k => {
            k.closest('tr')?.classList.toggle(Zeilenwahl.GEWAEHLT, k.checked);
        });
        const gewaehlt = kaesten.filter(k => k.checked).length;
        const kopf = this.kopf();
        if (kopf) {
            const stand = Zeilenwahl.kopfstand(gewaehlt, kaesten.length);
            kopf.checked = stand.checked;
            kopf.indeterminate = stand.indeterminate;
        }
        this.beiAenderung(gewaehlt);
    }
}
