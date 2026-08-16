/**
 * Leinwand des Ausricht-Assistenten — Anmeldung.
 *
 * Das Zeichnen steckt in `Assistentenbild`, die Punktumrechnung in
 * `wizard_umrechnung.js`. Vorher standen hier 141 Zeilen `renderWizardCanvas()`
 * plus eine zweite Kopie der Umrechnung.
 */
import { Assistentenbild } from './assistentenbild.js';

export { transformPtGlobal, inverseTransformPt } from './wizard_umrechnung.js';

export function renderWizardCanvas() {
    return new Assistentenbild().zeichnen();
}
