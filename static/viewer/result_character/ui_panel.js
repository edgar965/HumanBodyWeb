/**
 * Result Character — Anmeldung des Bedienfelds.
 *
 * Der Aufbau steckt in `Bedienfeld` (bedienfeld.js), die Bausteine in
 * bauteile.js. Hier bleibt der Name, den die anderen Module kennen. Vorher
 * standen an dieser Stelle 211 Zeilen in einer Funktion.
 */
import { fn } from '../gemeinsam/registrierung.js';
import { Bedienfeld } from './bedienfeld.js';

export { el } from './bauteile.js';

export function buildControlPanel(behaelter, daten) {
    return new Bedienfeld(behaelter, daten).bauen();
}

fn.buildControlPanel = buildControlPanel;
