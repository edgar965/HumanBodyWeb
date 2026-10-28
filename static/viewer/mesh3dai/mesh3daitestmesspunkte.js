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

/** MediaPipe FaceLandmarker (Nummern = Index der 478 Punkte): Lippen, linkes Auge, linke Braue, rechtes Auge, rechte Braue, Gesichtsumriss, Nase — gelesen aus
 * `FaceLandmarksConnections` (`mediapipe/tasks/python/vision/face_landmarker.py`, `ProjektTemp/_wegwerf/regler_ki/mediapipe_konturen.py`). Edgar 27.10.2026: „Hier fehlen auch die Linien
 * zwischen den Features“. */
const MEDIAPIPE_KONTUREN = [[61, 146], [146, 91], [91, 181], [181, 84], [84, 17], [17, 314], [314, 405], [405, 321], [321, 375], [375, 291], [61, 185], [185, 40], [40, 39], [39, 37],
    [37, 0], [0, 267], [267, 269], [269, 270], [270, 409], [409, 291], [78, 95], [95, 88], [88, 178], [178, 87], [87, 14], [14, 317], [317, 402], [402, 318], [318, 324], [324, 308],
    [78, 191], [191, 80], [80, 81], [81, 82], [82, 13], [13, 312], [312, 311], [311, 310], [310, 415], [415, 308],
    [263, 249], [249, 390], [390, 373], [373, 374], [374, 380], [380, 381], [381, 382], [382, 362], [263, 466], [466, 388], [388, 387], [387, 386], [386, 385], [385, 384], [384, 398], [398, 362],
    [276, 283], [283, 282], [282, 295], [295, 285], [300, 293], [293, 334], [334, 296], [296, 336],
    [33, 7], [7, 163], [163, 144], [144, 145], [145, 153], [153, 154], [154, 155], [155, 133], [33, 246], [246, 161], [161, 160], [160, 159], [159, 158], [158, 157], [157, 173], [173, 133],
    [46, 53], [53, 52], [52, 65], [65, 55], [70, 63], [63, 105], [105, 66], [66, 107],
    [10, 338], [338, 297], [297, 332], [332, 284], [284, 251], [251, 389], [389, 356], [356, 454], [454, 323], [323, 361], [361, 288], [288, 397], [397, 365], [365, 379], [379, 378],
    [378, 400], [400, 377], [377, 152], [152, 148], [148, 176], [176, 149], [149, 150], [150, 136], [136, 172], [172, 58], [58, 132], [132, 93], [93, 234], [234, 127], [127, 162],
    [162, 21], [21, 54], [54, 103], [103, 67], [67, 109], [109, 10],
    [168, 6], [6, 197], [197, 195], [195, 5], [5, 4], [4, 1], [1, 19], [19, 94], [94, 2], [98, 97], [97, 2], [2, 326], [326, 327], [327, 294], [294, 278], [278, 344], [344, 440],
    [440, 275], [275, 4], [4, 45], [45, 220], [220, 115], [115, 48], [48, 64], [64, 98]];

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

    /** @param {HTMLElement} karte `#mesh3dai-gesichtspunkte` mit `data-kennung` (und `data-nur-deltas`: Feld 3 nur die roten Linien Eingang – Ergebnis, ohne Pfeilspitze) */
    static gesichtStarten(karte) {
        if (!karte) return null;
        const basis = `/api/mesh3dai/test/${karte.dataset.kennung}/messpunkte/`;
        const anzeige = new Ai2d3dmesspunkte(karte, karte.dataset.kennung, [{ adresse: `${basis}bild/gesicht_vorlage/1/` }],
            { daten: `${basis}gesicht/`, seite: nr => `${basis}bild/gesicht_ergebnis/${nr}/` },
            { farbe: Mesh3daitestmesspunkte.FARBE, nurRot: true, gerippe: MEDIAPIPE_KONTUREN });
        anzeige.zeigen(0);
        return anzeige;
    }
}
