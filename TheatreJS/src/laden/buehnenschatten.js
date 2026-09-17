/**
 * Buehnenschatten — was auf die Bühne kommt, wirft und empfängt Schatten.
 *
 * GLB-Dateien und gebaute Figuren bringen die Einstellung nicht mit; dieselbe
 * `traverse`-Schleife stand dreimal (`asset-loader.js`, `laden/vorgabefigur.js`,
 * `studio/figurwahl.js` — Befund `doppelcode`, 17.09.2026). Jetzt einmal.
 */
export class Buehnenschatten {

    /**
     * Schatten an allen Netzen der Gruppe einschalten.
     * @param {import('three').Object3D} gruppe
     * @returns {import('three').Object3D} dieselbe Gruppe
     */
    static an(gruppe) {
        gruppe.traverse(teil => {
            if (teil.isMesh) {
                teil.castShadow = true;
                teil.receiveShadow = true;
            }
        });
        return gruppe;
    }
}
