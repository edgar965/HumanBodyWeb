/**
 * Zusatzdaten — `userData` vor einem glTF-Export beiseiteräumen.
 *
 * `GLTFExporter` kopiert jedes `userData` als `extras` ins glTF-JSON. Bei
 * Genesis 9 hängen dort App-interne Daten, die kein Zielwerkzeug braucht:
 *
 * - `object.userData` / `material.userData` — `gruppe`, `kachel`, `regler` …
 *   (Fund 26.09.2026: eine 510-MB-GLB, davon 425 MB reiner JSON-Text).
 * - `geometry.userData` — der eigentliche Brocken, und lange übersehen:
 *   `figurhaut.js` legt dort `indexVoll` ab, den VOLLEN Index als TypedArray
 *   (Millionen Einträge), dazu Masken über alle Punkte. `JSON.stringify`
 *   schreibt eine TypedArray als {"0":123,"1":124,…} aus — rund 29 Bytes je
 *   Eintrag, gemessen. Schlimmer noch: `GLTFExporter` serialisiert die
 *   Geometrie-Zusatzdaten INNERHALB der Materialgruppen-Schleife
 *   (`GLTFExporter.js:1941`), also je Zone erneut. Sieben Hautzonen mal 4,5
 *   Mio Einträge sprengen V8s String-Grenze: „RangeError: Invalid string
 *   length".
 *
 * `Netzattribute.tauschen` hilft hier NICHT: `geometry.clone()` übernimmt
 * `userData` als geteilte Referenz.
 */
export class Zusatzdaten {

    /**
     * Alle `userData` unter `objekte` leeren (Objekt, Werkstoffe, Geometrie).
     * @returns Funktion, die den vorigen Stand zurückstellt
     */
    static leeren(objekte) {
        const eintraege = [];
        const beiseite = (halter) => {
            if (halter?.userData && Object.keys(halter.userData).length) {
                eintraege.push([halter, halter.userData]);
                halter.userData = {};
            }
        };
        const proObjekt = (obj) => {
            beiseite(obj);
            beiseite(obj.geometry);
            const werkstoffe = Array.isArray(obj.material) ? obj.material : obj.material ? [obj.material] : [];
            werkstoffe.forEach(beiseite);
        };
        objekte.forEach((obj) => obj.traverse(proObjekt));
        return () => eintraege.forEach(([halter, wert]) => { halter.userData = wert; });
    }
}
