/**
 * Kleidungsstueck in zwei Stufen an den Koerper anpassen — Anmeldung.
 *
 * Stufe 1 (Hülle aus einem Knochenmodell) steckt in `Kleiderhuelle`, Stufe 2
 * (Anpassen am Server) in `Kleideranpassung`. Vorher standen hier zwei
 * Funktionen mit 111 und 103 Zeilen, letztere fast Zeile für Zeile gleich mit
 * `_doGarmentFit` im Assets-Reiter.
 */
import { state } from './state.js';
import { Kleiderhuelle } from './kleiderhuelle.js';
import { Kleideranpassung } from './kleideranpassung.js';

async function _doKleiderStage1() {
    return Kleiderhuelle.bauen();
}

/**
 * Stufe 2 und 3: Das Stück an die Hülle (`rig_hull`) oder an den Körper
 * (`body_refine`) anpassen.
 */
async function _doKleiderFit(fitMode) {
    const modus = fitMode || 'rig_hull';
    return new Kleideranpassung({
        vorsilbe: 'kleider',
        schluessel: 'kld_',
        kennung: state._selectedKleiderId,
        modus,
        // Nur der Hüllenmodus schickt die Punkte aus Stufe 1 mit.
        huelle: modus === 'rig_hull',
    }).ausfuehren();
}

export { _doKleiderStage1, _doKleiderFit };
