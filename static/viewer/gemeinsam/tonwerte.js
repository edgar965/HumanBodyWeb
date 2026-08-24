/**
 * Tonwerte — die Zuordnung Name → Three.js-Tonemapping.
 *
 * WARUM DIESES MODUL (Umbau 17.08.2026): Diese Tabelle stand VIERMAL im
 * Projekt, und die vierte hieß anders — `VIEWER_TONE_MAPPINGS` in
 * `viewer/scene_settings.js`, inhaltlich identisch. Damit war sie gleich zwei
 * Befunde: `doppelcode` (Kriterium 6) und ein abweichender Name für dieselbe
 * Sache (Kriterium 7).
 *
 * Die Namen sind das DRAHTFORMAT: Sie stehen so in `humanbody_scene_settings`
 * im localStorage und in den gespeicherten Szenen-JSONs (`renderer.toneMapping`).
 * Wer hier einen Schlüssel umbenennt, macht alle gespeicherten Szenen auf
 * dieses Feld hin wirkungslos — ohne Fehlermeldung, weil der Leser bei einem
 * unbekannten Namen still auf ACESFilmic zurückfällt.
 *
 * `THREE` kommt als Parameter: Jede Seite hält ihre eigene Instanz über eine
 * eigene Importmap. Ein zweiter Import derselben Bibliothek wären zwei
 * Instanzen mit verschiedenen Konstanten.
 */

/** Die fünf Namen, in der Reihenfolge, in der sie im Auswahlfeld stehen. */
export const TONWERTNAMEN = ['ACESFilmic', 'Linear', 'Reinhard', 'Cineon', 'None'];

/** {Name: Three-Konstante} für die Three-Instanz dieser Seite. */
export function tonwerte(THREE) {
    return {
        ACESFilmic: THREE.ACESFilmicToneMapping,
        Linear:     THREE.LinearToneMapping,
        Reinhard:   THREE.ReinhardToneMapping,
        Cineon:     THREE.CineonToneMapping,
        None:       THREE.NoToneMapping,
    };
}
