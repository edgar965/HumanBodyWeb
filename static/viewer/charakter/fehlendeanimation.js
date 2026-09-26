import { Figurmerker } from './figurmerker.js';

/**
 * Fehlendeanimation — eine Animation, die eine Figur (gerade angeklickt oder
 * aus `Figurmerker` geholt) auf der Platte nicht mehr findet: 404 vom
 * Retarget.
 *
 * WARUM (Edgar, 24.09.2026): „Falls es Animationen gibt im Studio oder
 * Charakter die es nicht mehr auf der Platte gibt, dann Fehlermeldung, mit
 * Abfrage ob die gelöscht werden sollen." Bisher stand nur „Fehler: ..." in
 * der Zeile unter der Leiste, ohne dass etwas aufgeräumt wurde — der nächste
 * Play-Versuch derselben Figur landete wieder in derselben 404.
 *
 * „Löschen" heisst hier: die GEMERKTE Auswahl vergessen (`Figurmerker`), bei
 * ALLEN Figuren, die dieselbe Datei gewählt hatten — auf dieser Seite gibt es
 * keine andere gespeicherte Referenz (eine Szene selbst speichert keine
 * Animation, siehe `figurablage.js`; anders als im BVH Studio, wo Clips in
 * `.studio.json`-Projekten liegen, siehe `bvh_studio/clipfehlt.js`).
 */
export class Fehlendeanimation {

    /**
     * @param {(Error & {status?: number})|null} fehler
     * @param {{url: string, name?: string}} quelle
     * @param {(text: string) => void} meldung
     * @returns {boolean} true, wenn als „Datei fehlt" behandelt (der Fehler
     *   ist damit verbraucht — der Aufrufer soll seine eigene Fehlermeldung
     *   NICHT mehr zusätzlich zeigen).
     */
    static behandeln(fehler, quelle, meldung) {
        if (fehler?.status !== 404) return false;
        const bezeichner = Fehlendeanimation._bezeichner(quelle);
        const loeschen = confirm(
            `„${bezeichner}" gibt es nicht mehr auf der Platte.\n\n`
            + 'Gemerkte Auswahl bei allen Figuren löschen, die sie gewählt hatten?');
        if (loeschen) {
            const anzahl = Figurmerker.animationVergessen(quelle.url);
            meldung(`${bezeichner} gibt es nicht mehr — Auswahl bei `
                    + `${anzahl} Figur${anzahl === 1 ? '' : 'en'} gelöscht`);
        } else {
            meldung(`${bezeichner} gibt es nicht mehr auf der Platte`);
        }
        return true;
    }

    static _bezeichner(quelle) {
        const treffer = (quelle.url || '').match(/\/api\/character\/bvh\/([^/]+)\/([^/]+)\/?/);
        if (treffer) return `${decodeURIComponent(treffer[1])}/${decodeURIComponent(treffer[2])}`;
        return quelle.name || quelle.url || '?';
    }
}
