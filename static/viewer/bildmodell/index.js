import { Bildmodellauftrag } from './auftrag.js';
import { Optionenformular } from './optionenformular.js';
import { Laufansicht } from './laufansicht.js';
import { Bilderansicht } from './bilderansicht.js';
import { Ergebnisansicht } from './ergebnisansicht.js';
import { Ansicht3d } from './ansicht3d.js';
import { Personenformular } from './personenformular.js';
import { Proportionenansicht } from './proportionen.js';

/**
 * Bildmodellseite — Einstieg der Auftragsseite „Modell aus Dateien".
 *
 * Liest Zustand und Optionenkatalog aus `#bildmodell-daten`, baut die
 * Teile (Lauf, Optionen, Bilder, Ergebnis, 3D) und lässt den Auftrag
 * nachfragen, solange er läuft. Die 3D-Ansicht kommt zuletzt und fängt
 * ihre Fehler selbst (ohne WebGL bleibt der Rest der Seite bedienbar).
 */
export class Bildmodellseite {

    static aufbauen() {
        const roh = document.getElementById('bildmodell-daten');
        const daten = roh ? JSON.parse(roh.textContent) : { zustand: {}, katalog: { schritte: [] } };
        const auftrag = new Bildmodellauftrag(daten.zustand);
        const formular = new Optionenformular(daten.katalog, daten.zustand.optionen);
        const ergebnis = new Ergebnisansicht(auftrag);
        const lauf = new Laufansicht(auftrag, formular, () => ergebnis.festgehalten());
        const bilder = new Bilderansicht(auftrag);
        const ansicht = new Ansicht3d(auftrag);
        const person = new Personenformular(auftrag, daten.katalog, formular, () => ergebnis.festgehalten());
        const proportionen = new Proportionenansicht(auftrag, daten.katalog);
        auftrag.verfolgen();
        window.__bildmodell = { auftrag, formular, lauf, bilder, ergebnis, ansicht, person, proportionen };
        return window.__bildmodell;
    }
}
