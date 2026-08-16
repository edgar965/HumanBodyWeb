/**
 * Photo To 3D — Anmeldung der Ausrichtungsvorschau.
 *
 * Das Zeichnen steckt in `Ausrichtungsvorschau`, das Vergrößern in
 * `Zoomfenster`, die Umrisskurve in `kontur.js`. Vorher standen hier 152 Zeilen
 * `renderAlignmentPreview()` und 95 Zeilen Zoomdialog.
 */
import { fn } from '../gemeinsam/registrierung.js';
import { Ausrichtungsvorschau } from './ausrichtungsvorschau.js';
import { Zoomfenster } from './zoomfenster.js';

export { drawSmoothContour, drawSmoothContourTransformed } from './kontur.js';

export async function renderAlignmentPreview() {
    const vorschau = new Ausrichtungsvorschau();
    vorschau.beiKlick = leinwand => Zoomfenster.zeigen(leinwand);
    return vorschau.zeichnen();
}

fn.renderAlignmentPreview = renderAlignmentPreview;
