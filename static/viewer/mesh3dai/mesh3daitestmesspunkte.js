/**
 * Mesh3daitestmesspunkte — Zeile „Messpunkte des Körpers“ der Testseite (24.10.2026 nachts, Edgar zu randy_tropical: „mach im Job eine zweite Zeile mit den Messungen, so wie hier“ — Vorbild
 * die Testzeile von `/2d-3d-AI/test/edgartrip/`). Dieselbe Anzeige (`Ai2d3dmesspunkte`), die Daten aus der Kostüm-Prüfung (`Kostuemmesspunkte`): Eingang und Figur mit Stücken aus vier
 * Richtungen in EINER Kamera, ViTPose und Randpunkte auf beiden. Die Knöpfe wählen die Richtung (statt des Fotos bei 2d-3d-AI).
 */
import { Ai2d3dmesspunkte } from '../ai2d3d/ai2d3dmesspunkte.js';

export class Mesh3daitestmesspunkte {
    /** Reihenfolge wie `Kostuembild.ANSICHTEN` — die Bilder heißen `vorlage_<n>` / `ergebnis_<n>` mit n ab 1. */
    static ANSICHTEN = ['vorne', 'hinten', 'links', 'rechts'];

    /** @param {HTMLElement} karte `#mesh3dai-messpunkte` mit `data-kennung` und Knöpfen `[data-messansicht]` */
    static starten(karte) {
        if (!karte) return null;
        const basis = `/api/mesh3dai/test/${karte.dataset.kennung}/messpunkte/`;
        const fotos = Mesh3daitestmesspunkte.ANSICHTEN.map((_a, i) => ({ adresse: `${basis}bild/vorlage/${i + 1}/` }));
        const anzeige = new Ai2d3dmesspunkte(karte, karte.dataset.kennung, fotos, { daten: basis, seite: nr => `${basis}bild/ergebnis/${nr}/` });
        const knoepfe = [...karte.querySelectorAll('[data-messansicht]')];
        const waehlen = i => {
            knoepfe.forEach((b, j) => b.setAttribute('aria-pressed', String(i === j)));
            anzeige.zeigen(i);
        };
        knoepfe.forEach((b, i) => b.addEventListener('click', () => waehlen(i)));
        waehlen(0);
        return anzeige;
    }
}
