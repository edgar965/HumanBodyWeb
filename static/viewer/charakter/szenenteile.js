import { state, TONE_MAPPINGS } from './state.js';
import { Szeneneinstellungen } from '../gemeinsam/szeneneinstellungen.js';

/**
 * Die Teile DIESER Seite, fertig fuer `Szeneneinstellungen`.
 *
 * WARUM (28.08.2026, zweite Runde des Befunds `doppelcode`): Nachdem die
 * Rechnung nach `gemeinsam/szeneneinstellungen.js` gewandert war, stand
 * stattdessen das Zusammensuchen der Teile dreimal da — in `lighting.js`,
 * `session.js` und `szenenzustand.js`, je sieben gleiche Zeilen. Das Werkzeug
 * hat es sofort wieder gemeldet, und zu Recht: Kommt ein viertes Licht dazu,
 * muss es an drei Stellen nachgetragen werden.
 *
 * Beachten: Das Umgebungslicht heisst auf DIESER Seite `ambientLight`, auf den
 * Betrachter-Seiten `ambient`. Deshalb steht die Zuordnung hier und nicht in
 * der gemeinsamen Klasse.
 *
 * @param woher Name fuers Protokoll — die drei Aufrufer sollen im Log
 *              unterscheidbar bleiben.
 */
export function szenenteile(woher) {
    return new Szeneneinstellungen({
        keyLight: state.keyLight,
        fillLight: state.fillLight,
        backLight: state.backLight,
        ambient: state.ambientLight,
        renderer: state.renderer,
        scene: state.scene,
        camera: state.camera,
        controls: state.controls,
        tonwerte: TONE_MAPPINGS,
        woher,
    });
}
