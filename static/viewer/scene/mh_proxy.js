/**
 * Scene Editor — MakeHuman-Kleidung: Anmeldung beim Seitengerüst.
 *
 * Die Bedienung steckt in `MhProxyBedienung` (mhproxy_bedienung.js). Hier
 * bleibt nur, was die Seite braucht: eine Aufrufstelle und die Einträge in
 * `fn`. Vorher standen 243 Zeilen Verdrahtung in `loadMHProxyUI()`.
 */
import './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _selectedMHMesh } from './utils.js';
import './skeleton.js';
import { _doMHProxyFit, _fitMHProxyOnInst, _initPropMHControls,
         _syncPropMHControls } from './mhproxy_anpassen.js';
import { _renderMHList } from './mhproxy_liste.js';
import { MhProxyBedienung } from './mhproxy_bedienung.js';

/** Die eine Bedienung der Seite — steht auch dem Rest zur Verfügung. */
let bedienung = null;

async function loadMHProxyUI() {
    if (!bedienung) bedienung = new MhProxyBedienung();
    return bedienung.verdrahten();
}

export { loadMHProxyUI, _selectedMHMesh };

fn.loadMHProxyUI = loadMHProxyUI;
fn._doMHProxyFit = _doMHProxyFit;
fn._fitMHProxyOnInst = _fitMHProxyOnInst;
fn._syncPropMHControls = _syncPropMHControls;
fn._initPropMHControls = _initPropMHControls;
