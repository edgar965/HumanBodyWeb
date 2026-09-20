import { Bereichsgriff } from './bereichsgriff.js';

/**
 * Hoehengriff — ein Feld lässt sich an der Unterkante ziehen.
 *
 * ANLASS (Edgar, 20.09.2026, Szene → Genesis 9 → „Form (Daz-Regler)"): „mach
 * unten an der Stelle einen Griff, mit dem ich die Ansicht der Tool-Seite
 * nach unten verschieben kann, merke dir die Position des Griffs". Die
 * Reglerliste ist ein `.anim-tree` mit 300 px Höhe und eigenem Rollbalken;
 * darunter war der Reiter leer.
 *
 * Was er tut: Ziehen setzt die Höhe des Felds — `height` UND `max-height`,
 * weil `.anim-tree` eine Höchstgrenze mitbringt, die sonst weiter gälte.
 * Die Höhe überlebt das Neuladen (`localStorage`, je Browser), Doppelklick
 * stellt die Vorgabe wieder her.
 *
 * Dieselbe Mechanik wie `Bereichsgriff` (Breite), nur die Achse ist eine
 * andere: senkrechter Mausweg, `row-resize`, und KEIN `resize`-Ereignis —
 * eine Liste im Seitenfeld ändert an der Leinwand nichts.
 *
 * Verwendung:
 *
 *     new Hoehengriff({ griff: el, bereich: liste, min: 120, max: 1600,
 *                       vorgabe: 300, schluessel: 'scene_x_hoehe' }).verdrahten();
 */
export class Hoehengriff extends Bereichsgriff {

    static CURSOR = 'row-resize';

    /** Die Höhe — im Erbe heißt das Maß `breite`. */
    get hoehe() { return this.breite; }

    _koordinate(e) { return e.clientY; }

    _anwenden(px) {
        this.bereich.style.height = px;
        this.bereich.style.maxHeight = px;
    }

    _nachziehen() {}
}
