/**
 * Scene Editor — Kleider-Reiter: Anmeldung beim Seitengerüst.
 *
 * Die Bedienung steckt in `Kleiderbedienung` (kleiderbedienung.js). Vorher
 * standen hier 184 Zeilen in `loadKleiderUI()`.
 */
import './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import './skeleton.js';
import { _doKleiderFit, _doKleiderStage1 } from './kleider_anpassen.js';
import { _kleiderSelectById, _renderKleiderList,
         _selectedKleiderMesh } from './kleider_liste.js';
import { Kleiderbedienung } from './kleiderbedienung.js';

let bedienung = null;

async function loadKleiderUI() {
    if (!bedienung) bedienung = new Kleiderbedienung();
    return bedienung.verdrahten();
}

export { loadKleiderUI };

fn.loadKleiderUI = loadKleiderUI;
