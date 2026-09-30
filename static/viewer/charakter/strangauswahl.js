import * as THREE from 'three';
import { Umfaerbung } from '../gemeinsam/umfaerbung.js';

/**
 * Strangauswahl — gewähltes Stranghaar SICHTBAR machen, auch wenn es dunkel ist.
 *
 * Edgar, 30.09.2026: „G9 Force pixie hair ist nicht auswählbar im 3D View, es wählt immer
 * das ganze Modell bei Klick". Im Chrome nachgeklickt: Pixie WIRD gewählt (die Zeile in der
 * Garderobe ist markiert) — man sieht es nur nicht. Stranghaar hat keine Fläche, die Aura
 * (`auswahlaura.js`) findet dort keinen Umriss; übrig blieb die Grundfarbe, und die
 * MULTIPLIZIERT die Strähnenfarben. Gemessen an Pixie: Strähnen im Mittel
 * [0,062  0,036  0,026], mal der Auswahlfarbe [1,9  1,35  0,7] = [0,118  0,049  0,018] —
 * immer noch fast schwarz. Wer nichts sieht, klickt noch einmal, und der zweite Klick auf
 * das gewählte Stück wählt es ab (`_doSubMeshClick` schaltet um): Die Figur leuchtet auf.
 *
 * DIE RECHNUNG (dasselbe Prinzip wie `Umfaerbung`): Der Faktor richtet sich nach der
 * TATSÄCHLICHEN Farbe des Haars — Zielfarbe ÷ Mittel der Punktfarben. Dann liegt das Haar
 * im Mittel genau auf der Auswahlfarbe, die Strähnen behalten ihr Hell und Dunkel. Das
 * Mittel wird einmal je Netz gemessen, jede 97. Farbe genügt.
 *
 * MIT EIGENER HAARFARBE (`Umfaerbung`) GEHT DAS NICHT: Dort legt der Shader den FARBTON fest
 * (`Wahlfarbe × Helligkeit ÷ Mittel`), die Grundfarbe geht nur noch in die Helligkeit ein —
 * „Orange ÷ Kupfer" hätte das Haar sogar abgedunkelt (Helligkeit des Faktors unter 1). Dann
 * hellt die Auswahl das Haar deutlich auf (`HELLER_*`), im Farbton der gewählten Farbe.
 *
 * Die Zielfarben sind die der Aura: Auswahl dunkles Orange, Hover helles Orange
 * (`auswahlanzeige.md`), damit Stranghaar genauso aussieht wie jede andere Auswahl.
 */
export class Strangauswahl {

    static AUSWAHL = new THREE.Color(0xb84400);
    static HOVER = new THREE.Color(0xffe8c8);
    /** Mit eigener Haarfarbe: so viel heller (Umfaerbung deckelt das Verhältnis bei 4). */
    static HELLER_AUSWAHL = 2.6;
    static HELLER_HOVER = 1.6;
    /** Unter diesem Mittel wird nicht weiter geteilt (fast schwarzes Haar). */
    static BODEN = 0.02;
    /** Höchster Faktor je Kanal — Glanzlichter auf sehr dunklem Haar liefen sonst aus. */
    static DECKEL = 24;
    static SCHRITT = 97;

    /**
     * Den Faktor für `material.color` setzen.
     * @param netz das Strang-Netz (für das Mittel der Punktfarben)
     * @param material sein Material
     * @param ziel `Strangauswahl.AUSWAHL`, `Strangauswahl.HOVER` — oder null (zurück auf 1)
     */
    static setzen(netz, material, ziel) {
        if (!ziel) { material.color.setRGB(1, 1, 1); return; }
        if (Umfaerbung.farbe(material)) {
            const k = ziel === Strangauswahl.AUSWAHL ? Strangauswahl.HELLER_AUSWAHL
                                                     : Strangauswahl.HELLER_HOVER;
            material.color.setRGB(k, k, k);
            return;
        }
        const mittel = Strangauswahl.mittel(netz);
        material.color.setRGB(
            Strangauswahl._faktor(ziel.r, mittel.r),
            Strangauswahl._faktor(ziel.g, mittel.g),
            Strangauswahl._faktor(ziel.b, mittel.b));
    }

    static _faktor(ziel, mittel) {
        return Math.min(Strangauswahl.DECKEL, ziel / Math.max(Strangauswahl.BODEN, mittel));
    }

    /** Das Mittel der Punktfarben (linear), gemerkt je Netz und Fassung des Attributs. */
    static mittel(netz) {
        const gemerkt = netz.userData._strangmittel;
        const farben = netz.geometry?.attributes?.color;
        if (gemerkt && gemerkt.fassung === farben?.version) return gemerkt.farbe;
        const farbe = new THREE.Color(1, 1, 1);
        if (farben?.count) {
            let r = 0, g = 0, b = 0, n = 0;
            for (let i = 0; i < farben.count; i += Strangauswahl.SCHRITT) {
                r += farben.getX(i); g += farben.getY(i); b += farben.getZ(i); n += 1;
            }
            farbe.setRGB(r / n, g / n, b / n);
        }
        netz.userData._strangmittel = { farbe, fassung: farben?.version };
        return farbe;
    }
}
