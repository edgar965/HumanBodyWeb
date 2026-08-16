/**
 * Viewer — Anmeldung des Morph-Felds.
 *
 * Der Aufbau steckt in `Morphbedienung` (morphbedienung.js). Vorher standen
 * hier 193 Zeilen in `loadMorphs()`.
 */
import { fn } from '../gemeinsam/registrierung.js';
import { Morphbedienung } from './morphbedienung.js';

export async function loadMorphs() {
    return Morphbedienung.laden();
}

fn.loadMorphs = loadMorphs;
