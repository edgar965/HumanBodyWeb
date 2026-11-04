import { Mesh3daifigurbewegungsleiste } from '../mesh3dai/mesh3daifigurbewegungsleiste.js';
import { Ai2d3dzeile1bewegung } from './ai2d3dzeile1bewegung.js';

/**
 * Ai2d3dbewegung — die Abspielleiste unter den Genesis-Feldern der Jobseite (31.10.2026, Edgar: „diese Play-Leiste (die es bei /mesh-3D-AI/test/venus/ gibt) soll auch bei den Jobs von
 * /2d-3d-AI/test/edgartrip/ sein, sowohl in der ersten Zeile (für das Genesis-Modell) als auch 2. Zeile bei Genesis-Modell, damit ich die Animation sehen kann“).
 *
 * Derselbe Code wie auf der Mesh3D-AI-Testseite: `Mesh3daifigurbewegung` (Genesis9Modell in der Ruhelage, Retarget wie die Charakter-Seite, Mischer) und `Mesh3daifigurbewegungsleiste`
 * (Knöpfe, Schieber, Standardanimation je Job über `/api/2d3dai/<job>/standardanimation/`). Zeile 2 spielt die Figur der Exportleiste (`Ai2d3dexportfigur`: Regler, Haut aus den Fotos,
 * Stücke aus den Fotos) — Export und Bewegung sind eine Figur. Zeile 1 spielt dieselbe Figur mit Kleidern und Haar (31.10.2026 nachts, Edgar: „bei animation ist das Modell in der
 * 1. Zeile ohne Kleider und Haaren“) und der Form der Zeile 1 (`Ai2d3dzeile1bewegung`: Versatz der Ruhelage aus `KoerperKI_Fotos.Zeile1versatz`).
 */
export class Ai2d3dbewegung {

    /** @param seite `Ai2d3dseite` @param figur `Ai2d3dexportfigur` mit dem Feld der Zeile 2 */
    static leisten(seite, figur) {
        // die Leiste im Feld „Genesis-Modell“ — seit 04.11.2026 bei PSHuman-Jobs in der dritten Zeile (`_ai2d3d_genesisfeld.html`), sonst in der Körperzeile
        const zeile2 = document.querySelector('[data-feld="genesis"]')?.closest('section')?.querySelector('[data-figurbewegung]') ?? null;
        if (zeile2) new Mesh3daifigurbewegungsleiste(zeile2, figur.bewegung).wahlLaden(zeile2.dataset.adresse);
        const zeile1 = document.querySelector('#ai2d3d-meshzeile [data-figurbewegung]');
        if (zeile1 && seite.meshzeile) {
            const bewegung = new Ai2d3dzeile1bewegung(seite.meshzeile.figurfeld, () => figur.koerperQuelle());
            new Mesh3daifigurbewegungsleiste(zeile1, bewegung).wahlLaden(zeile1.dataset.adresse);
        }
    }
}
