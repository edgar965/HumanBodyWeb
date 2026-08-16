/**
 * Formregler — die Schieber der formabhaengigen Parameter (Tutu, Spirale,
 * Helix, Rock, Flaeche, Rhombus).
 *
 * WARUM eine Tabelle (Umbau 16.08.2026): Dieselben 31 Regler standen ZWEIMAL in
 * modellgenerator_ui.js — einmal als 31 `_tutuSlider(...)`-Aufrufe zum Anbinden
 * und einmal als 31-zeiliges Feld `shapeSliders` zum Nachziehen beim
 * Knochenwechsel. Zwei Listen derselben Sache laufen auseinander, sobald jemand
 * einen Regler nur in einer davon eintraegt. Jetzt eine Liste, zwei Schleifen.
 *
 * Die Kennung des Wertefelds ist ausnahmslos `<id>-val` — das muss nicht
 * mitgefuehrt werden.
 */
import { fn } from '../../gemeinsam/registrierung.js';
import { Modellbauzustand } from './zustand.js';

/** [Kennung, Eigenschaft, Vorgabewert, Nachkommastellen] */
export const FORMREGLER = [
    // Tutu
    ['mg-tutu-thickness', 'tutuThickness', 0.01, 3],
    ['mg-tutu-droop', 'tutuDroop', 0.03, 3],
    ['mg-tutu-droop-start', 'tutuDroopStart', 0.7, 2],
    ['mg-tutu-offset', 'tutuOffset', 0, 3],
    // Spiral-Tutu
    ['mg-spiral-winds', 'spiralWinds', 3, 0],
    ['mg-spiral-start-r', 'spiralStartR', 0.15, 3],
    ['mg-spiral-end-r', 'spiralEndR', 0.35, 3],
    ['mg-spiral-pos-top', 'spiralPosTop', 0.05, 3],
    ['mg-spiral-pos-bottom', 'spiralPosBottom', -0.15, 3],
    ['mg-spiral-thickness', 'tutuThickness', 0.008, 3],
    ['mg-spiral-droop', 'tutuDroop', 0.02, 3],
    // Helix-Band
    ['mg-helix-winds', 'spiralWinds', 3, 1],
    ['mg-helix-start-r', 'spiralStartR', 0.15, 3],
    ['mg-helix-end-r', 'spiralEndR', 0.35, 3],
    ['mg-helix-ribbon-w', 'ribbonWidth', 0.04, 3],
    ['mg-helix-pos-top', 'spiralPosTop', 0.05, 3],
    ['mg-helix-pos-bottom', 'spiralPosBottom', -0.15, 3],
    ['mg-helix-thickness', 'tutuThickness', 0.005, 3],
    ['mg-helix-droop', 'tutuDroop', 0.015, 3],
    // Rock
    ['mg-skirt-radius-top', 'skirtRadiusTop', 0.08, 3],
    ['mg-skirt-radius-bottom', 'skirtRadiusBottom', 0.25, 3],
    ['mg-skirt-pos-top', 'skirtPosTop', 0.02, 3],
    ['mg-skirt-pos-bottom', 'skirtPosBottom', -0.15, 3],
    ['mg-skirt-thickness', 'skirtThickness', 0.005, 3],
    // Flaeche
    ['mg-plane-width', 'planeWidth', 0.15, 3],
    ['mg-plane-height', 'planeHeight', 0.22, 3],
    // Rhombus / Kegelstumpf
    ['mg-rhombus-top-w', 'rhombusTopWidth', 0.10, 3],
    ['mg-rhombus-top-d', 'rhombusTopDepth', 0.10, 3],
    ['mg-rhombus-bot-w', 'rhombusBotWidth', 0.20, 3],
    ['mg-rhombus-bot-d', 'rhombusBotDepth', 0.20, 3],
    ['mg-rhombus-height', 'rhombusHeight', 0.20, 3],
];

/** Welche Parametergruppe zu welcher Form gehoert. */
const FELDGRUPPEN = [
    ['mg-overlap-row', 'double_oval'],
    ['mg-tutu-params', 'tutu'],
    ['mg-spiral-tutu-params', 'spiral_tutu'],
    ['mg-helix-ribbon-params', 'helix_ribbon'],
    ['mg-skirt-params', 'skirt'],
    ['mg-plane-params', 'plane'],
    ['mg-rhombus-params', 'rhombus'],
];

export class Formregler {
    /** Alle Regler einmalig an den Zustand haengen. */
    static binden(neuAufbauen) {
        for (const [id, eigenschaft, , stellen] of FORMREGLER) {
            const regler = document.getElementById(id);
            if (!regler) continue;
            const anzeige = document.getElementById(id + '-val');
            regler.addEventListener('input', () => {
                const v = parseFloat(regler.value);
                if (anzeige) anzeige.textContent = v.toFixed(stellen);
                const teil = Modellbauzustand.teil();
                if (!teil) return;
                teil[eigenschaft] = v;
                neuAufbauen();
            });
            regler.addEventListener('change', () => fn.markDirty?.(eigenschaft));
        }
    }

    /** Reglerstellungen auf ein Knochenteil nachziehen. */
    static nachziehen(teil) {
        for (const [id, eigenschaft, vorgabe, stellen] of FORMREGLER) {
            const regler = document.getElementById(id);
            const anzeige = document.getElementById(id + '-val');
            const v = teil[eigenschaft] ?? vorgabe;
            if (regler) regler.value = v;
            if (anzeige) {
                anzeige.textContent = stellen === 0 ? String(Math.round(v))
                                                    : v.toFixed(stellen);
            }
        }
    }

    /** Nur die Parametergruppe der gewaehlten Form zeigen. */
    static gruppeZeigen(form) {
        for (const [id, zuForm] of FELDGRUPPEN) {
            const el = document.getElementById(id);
            if (el) el.style.display = (form === zuForm) ? '' : 'none';
        }
    }
}
