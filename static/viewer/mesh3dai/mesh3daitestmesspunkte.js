/**
 * Mesh3daitestmesspunkte — Zeilen „Messpunkte des Körpers“ und „Gesichtspunkte“ der Testseite (24.10.2026 nachts, Edgar zu randy_tropical: „mach im Job eine zweite Zeile mit den Messungen,
 * so wie hier“ — Vorbild die Testzeile von `/2d-3d-AI/test/edgartrip/`). Dieselbe Anzeige (`Ai2d3dmesspunkte`), die Daten aus der Kostüm-Prüfung:
 *  Körper     `Kostuemmesspunkte`: Eingang und Figur mit Stücken aus vier Richtungen in EINER Kamera, ViTPose (23 Punkte, Gerippe) und Randpunkte auf beiden; Knöpfe wählen die Richtung
 *  Gesicht    `Kostuemgesichtszeile` (27.10.2026): MediaPipe (478 Punkte) auf dem Eingang gegen dieselben Punkte am Käfig der Figur, Kamera frontal auf den Kopf
 * Farben (27.10.2026, Edgar: „Blau Eingang, Schwarz Ausgang und Rot beim letzten Bild zwischen den Linien Eingang und Ausgang … orange Linien brauche ich nicht mehr“): `FARBE`, Feld 3 nur rot.
 */
import { Ai2d3dmesspunkte } from '../ai2d3d/ai2d3dmesspunkte.js';

/** ViTPose (COCO-WholeBody, Nummern der Zeile = Index + 1): Kopf, Rumpf, Arme, Beine, Füße. */
const VITPOSE_GERIPPE = [[1, 2], [1, 3], [2, 4], [3, 5], [6, 7], [6, 12], [7, 13], [12, 13], [6, 8], [8, 10], [7, 9], [9, 11], [12, 14], [14, 16], [13, 15], [15, 17],
    [16, 18], [16, 19], [16, 20], [17, 21], [17, 22], [17, 23]];

export class Mesh3daitestmesspunkte {
    /** Reihenfolge wie `Kostuembild.ANSICHTEN` — die Bilder heißen `vorlage_<n>` / `ergebnis_<n>` mit n ab 1. */
    static ANSICHTEN = ['vorne', 'hinten', 'links', 'rechts'];
    static FARBE = { ergebnis: '#000000', ergebnis_linie: '#000000' };

    /** @param {HTMLElement} karte `#mesh3dai-messpunkte` mit `data-kennung` und Knöpfen `[data-messansicht]` */
    static starten(karte) {
        if (!karte) return null;
        const basis = `/api/mesh3dai/test/${karte.dataset.kennung}/messpunkte/`;
        const fotos = Mesh3daitestmesspunkte.ANSICHTEN.map((_a, i) => ({ adresse: `${basis}bild/vorlage/${i + 1}/` }));
        const anzeige = new Ai2d3dmesspunkte(karte, karte.dataset.kennung, fotos, { daten: basis, seite: nr => `${basis}bild/ergebnis/${nr}/` },
            { farbe: Mesh3daitestmesspunkte.FARBE, nurRot: true, gerippe: VITPOSE_GERIPPE });
        const knoepfe = [...karte.querySelectorAll('[data-messansicht]')];
        const waehlen = i => {
            knoepfe.forEach((b, j) => b.setAttribute('aria-pressed', String(i === j)));
            anzeige.zeigen(i);
        };
        knoepfe.forEach((b, i) => b.addEventListener('click', () => waehlen(i)));
        waehlen(0);
        return anzeige;
    }

    /** @param {HTMLElement} karte `#mesh3dai-gesichtspunkte` mit `data-kennung` (und `data-nur-deltas`: Feld 3 nur die Pfeile Eingang → Ergebnis) */
    static gesichtStarten(karte) {
        if (!karte) return null;
        const basis = `/api/mesh3dai/test/${karte.dataset.kennung}/messpunkte/`;
        const anzeige = new Ai2d3dmesspunkte(karte, karte.dataset.kennung, [{ adresse: `${basis}bild/gesicht_vorlage/1/` }],
            { daten: `${basis}gesicht/`, seite: nr => `${basis}bild/gesicht_ergebnis/${nr}/` }, { farbe: Mesh3daitestmesspunkte.FARBE, nurRot: true });
        anzeige.zeigen(0);
        return anzeige;
    }
}
