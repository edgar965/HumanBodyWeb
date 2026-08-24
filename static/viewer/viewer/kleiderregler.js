import { setSlider, sliderVal } from './utils.js';
import { state } from './state.js';

/**
 * Kleiderregler — die Regler des Kleidungs-Reiters lesen und füllen.
 *
 * Herausgelöst aus `garment_liste.js` (229 Zeilen). Dort stand dreimal
 * dieselbe Liste von 21 Reglern: einmal zum Speichern, einmal zum Füllen aus
 * dem gespeicherten Stand, einmal für die Vorgaben. Wer einen Regler ergänzte,
 * musste alle drei treffen — der Grund, warum `minDist`, `crotchFloor`, `lift`
 * und `crotchDepth` in der einen Liste standen und in der anderen fehlten.
 *
 * **Die Einheiten stehen NUR hier.** Der Regler zählt in ganzen Zahlen, der
 * Zustand rechnet in Metern und 0…1:
 *
 *     Abstand (offset)  Regler 0…50   -> 0,000…0,050 m   (Teiler 1000)
 *     Steifigkeit       Regler 0…100  -> 0,00…1,00       (Teiler 100)
 *     Mindestabstand    Regler in mm  -> mm              (Teiler 1)
 *     Verschiebung      Regler in cm  -> m               (Teiler 100)
 */
export class Kleiderregler {

    /** Zustandsfeld, Regler-Kennung, Teiler, Anzeigeform, Vorgabe (Reglereinheit). */
    static SCHIEBER = [
        ['offset', 'garment-offset', 1000, w => (w / 1000).toFixed(3), null],
        ['stiffness', 'garment-stiffness', 100, w => (w / 100).toFixed(2), null],
        ['minDist', 'garment-min-dist', 1, w => w + ' mm', 3],
        ['crotchFloor', 'garment-crotch-floor', 1, w => w + ' mm', 0],
        ['lift', 'garment-lift', 1, w => w + ' mm', 0],
        ['crotchDepth', 'garment-crotch-depth', 1, w => w + ' mm', 0],
        ['roughness', 'garment-roughness', 100, w => (w / 100).toFixed(2), 80],
        ['metalness', 'garment-metalness', 100, w => (w / 100).toFixed(2), 0],
        ['posX', 'garment-pos-x', 100, w => (w / 100).toFixed(2) + ' m', 0],
        ['posY', 'garment-pos-y', 100, w => (w / 100).toFixed(2) + ' m', 0],
        ['posZ', 'garment-pos-z', 100, w => (w / 100).toFixed(2) + ' m', 0],
        ['scaleX', 'garment-scale-x', 100, w => (w / 100).toFixed(2), 100],
        ['scaleY', 'garment-scale-y', 100, w => (w / 100).toFixed(2), 100],
        ['scaleZ', 'garment-scale-z', 100, w => (w / 100).toFixed(2), 100],
        ['regionTop', 'garment-region-top', 100, w => (w / 100).toFixed(2) + ' m', 0],
        ['regionUpper', 'garment-region-upper', 100, w => (w / 100).toFixed(2) + ' m', 0],
        ['regionMid', 'garment-region-mid', 100, w => (w / 100).toFixed(2) + ' m', 0],
        ['regionLower', 'garment-region-lower', 100, w => (w / 100).toFixed(2) + ' m', 0],
        ['regionBottom', 'garment-region-bottom', 100, w => (w / 100).toFixed(2) + ' m', 0],
    ];

    static FARBE = 'garment-color';
    static ERSATZFARBE = '#4d5980';

    /** Die Reglerstellungen als Zustand — genau die Felder von `SCHIEBER`. */
    static lesen() {
        const zustand = {};
        for (const [feld, kennung, teiler] of Kleiderregler.SCHIEBER) {
            zustand[feld] = sliderVal(kennung) / teiler;
        }
        zustand.color = document.getElementById(Kleiderregler.FARBE)?.value
            || Kleiderregler.ERSATZFARBE;
        return zustand;
    }

    /** Den Zustand eines Kleidungsstücks merken. */
    static speichern(gid) {
        state.garmentState[gid] = Kleiderregler.lesen();
    }

    /** Die Regler auf einen gespeicherten Zustand stellen. */
    static fuellen(zustand) {
        for (const [feld, kennung, teiler, form, vorgabe] of Kleiderregler.SCHIEBER) {
            const wert = zustand[feld] ?? (vorgabe === null ? 0 : vorgabe / teiler);
            setSlider(kennung, Math.round(wert * teiler), form);
        }
        setSlider(Kleiderregler.FARBE, zustand.color);
    }

    /**
     * Die Regler auf die Vorgaben eines Katalogeintrags stellen.
     *
     * Abstand und Steifigkeit kommen aus dem Katalog, wenn er sie führt; fehlen
     * sie, bleibt der Regler stehen (`vorgabe === null`). Alles andere hat feste
     * Vorgaben.
     */
    static vorgaben(eintrag) {
        for (const [feld, kennung, teiler, form, vorgabe] of Kleiderregler.SCHIEBER) {
            if (vorgabe !== null) {
                setSlider(kennung, vorgabe, form);
            } else if (eintrag?.[feld] !== undefined) {
                setSlider(kennung, Math.round(eintrag[feld] * teiler), form);
            }
        }
        Kleiderregler.katalogfarbe(eintrag);
    }

    /** Die Katalogfarbe (`[r,g,b]` in 0…1) ins Farbfeld. */
    static katalogfarbe(eintrag) {
        const feld = document.getElementById(Kleiderregler.FARBE);
        if (!feld || !eintrag?.color) return;
        feld.value = '#' + eintrag.color
            .map(anteil => Math.round(anteil * 255).toString(16).padStart(2, '0'))
            .join('');
    }
}
