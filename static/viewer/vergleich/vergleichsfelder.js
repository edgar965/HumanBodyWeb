/**
 * Vergleichsfelder — die Bedienelemente einer Vergleichsspalte.
 *
 * WARUM eine Klasse (Umbau 16.08.2026, Anforderung 10): Elf DOM-Verweise lagen
 * als lose Variablen in der Closure von `createViewer` — `statusSpan`,
 * `vertexSpan`, `fpsSpan`, `bodyTypeSelect`, `metaSliderEls`, `morphsPanel`,
 * `skinColorInput`, `skinRoughSlider`, `skinRoughVal`, `skinMetalSlider`,
 * `skinMetalVal`. Sie werden an einer Stelle gefuellt und an sechs gelesen; als
 * Datensatz gehoeren sie zusammen.
 */
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Vergleichsfelder {
    constructor() {
        /** Statusleiste unten. */
        this.status = null;
        this.vertexzahl = null;
        this.bildrate = null;
        /** Auswahl der Koerperart. */
        this.koerperart = null;
        /** {name: {slider, val}} der vier Grundregler. */
        this.grundregler = {};
        /** Behaelter der Morph-Liste. */
        this.morphliste = null;
        /** Hautregler. */
        this.hautfarbe = null;
        this.rauheit = null;
        this.rauheitWert = null;
        this.metall = null;
        this.metallWert = null;
    }

    /** Kurzmeldung in der Statusleiste. */
    melden(text, klasse) {
        if (!this.status) { Protokoll.warnung('vergleich', text); return; }
        this.status.textContent = text;
        this.status.className = klasse;
    }

    zahl(feld, wert) {
        if (this[feld]) this[feld].textContent = wert;
    }
}
