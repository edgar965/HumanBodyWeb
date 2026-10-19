import { Anatomiezuordnung } from './anatomiezuordnung.js';
import { Anatomiemitte } from './anatomiemitte.js';

/**
 * Anatomiezuordnungsteil — die Zuordnung (`Anatomiezuordnung`) für einen ABSCHNITT der Stück-Dreiecke, und die Abschnitte wieder zusammen (19.10.2026).
 *
 * Gerechnet in mehreren Workern nebeneinander (`Anatomiezuordnungsarbeit`, `anatomiearbeiter.js`): auf ultrafein brauchte die Zuordnung am Stück 22,2 s (Damira0,
 * 1,18 Mio. Texel, 19.012 Hautdreiecke; mit den Vorfiltern 13,5 s), auf dem Hauptfaden in Häppchen. Jeder Abschnitt belegt seine Texel selbst; beim Zusammenführen
 * in der Reihenfolge der Abschnitte gehört ein Texel dem ersten Dreieck, das es belegt — genau wie in einem Lauf über alle Dreiecke, und die Einträge stehen in
 * derselben Reihenfolge. Was ein Texel bekommt, hängt nicht davon ab, welche Texel davor dran waren (die Schranke in `_strahl` begrenzt nur die Suche).
 * Ohne Three.js und ohne DOM: läuft im Worker.
 */
export class Anatomiezuordnungsteil {

    /**
     * Die Stück-Dreiecke `[von, bis)` wie `Anatomiezuordnung.rechnen` OHNE `Anatomiemitte` (der Weg für weit vor der Haut hängende Stücke braucht alle Dreiecke):
     * `{fern, anzahl, texel, btri, l2, l3, stri}` — `fern` zählt die Dreiecke, die `Anatomiemitte.fern` meldet (der Aufrufer entscheidet über alle).
     */
    static rechnen(stueck, haut, breite, hoehe, von, bis) {
        const gitter = Anatomiezuordnung._gitter(haut);
        const belegt = new Uint8Array(breite * hoehe);
        const liste = { n: 0, texel: new Uint32Array(65536), btri: new Int32Array(65536), l2: new Float32Array(65536), l3: new Float32Array(65536), stri: new Int32Array(65536) };
        const index = stueck.index, ab = new Float64Array(3);
        let fern = 0;
        for (let s = von; s < bis; s++) {
            const ecken = [index[3 * s], index[3 * s + 1], index[3 * s + 2]];
            const kand = Anatomiezuordnung._kandidaten(gitter, haut, stueck.pos, ecken, ab);
            if (Anatomiemitte.fern(kand)) fern++;
            if (kand) Anatomiezuordnung._rastern(stueck, ecken, s, kand, haut, breite, hoehe, belegt, liste, ab);
        }
        const n = liste.n;
        return { fern, anzahl: n, texel: liste.texel.slice(0, n), btri: liste.btri.slice(0, n), l2: liste.l2.slice(0, n), l3: liste.l3.slice(0, n), stri: liste.stri.slice(0, n) };
    }

    /** Die Abschnitte in ihrer Reihenfolge zusammen: wie `Anatomiezuordnung.rechnen` — `{anzahl, texel, btri, l2, l3, stri, belegt}`. */
    static zusammen(teile, breite, hoehe) {
        const belegt = new Uint8Array(breite * hoehe);
        const summe = teile.reduce((s, t) => s + t.anzahl, 0);
        const aus = { texel: new Uint32Array(summe), btri: new Int32Array(summe), l2: new Float32Array(summe), l3: new Float32Array(summe), stri: new Int32Array(summe) };
        let n = 0;
        for (const t of teile) {
            for (let i = 0; i < t.anzahl; i++) {
                const nr = t.texel[i];
                if (belegt[nr]) continue;
                belegt[nr] = 1;
                aus.texel[n] = nr; aus.btri[n] = t.btri[i]; aus.l2[n] = t.l2[i]; aus.l3[n] = t.l3[i]; aus.stri[n] = t.stri[i];
                n++;
            }
        }
        return { anzahl: n, texel: aus.texel.slice(0, n), btri: aus.btri.slice(0, n), l2: aus.l2.slice(0, n), l3: aus.l3.slice(0, n), stri: aus.stri.slice(0, n), belegt };
    }

    /** Die Haut nur mit den Punkten ihrer Dreiecke (der Körper hat auf ultrafein 410.202 Punkte, die Dreiecke am Stück nutzen einen Bruchteil) — Nummern der Dreiecke bleiben. */
    static knapp(haut) {
        const neu = new Int32Array(haut.pos.length / 3).fill(-1);
        const ecken = new Uint32Array(haut.ecken.length);
        let n = 0;
        for (let i = 0; i < ecken.length; i++) {
            const v = haut.ecken[i];
            if (neu[v] < 0) neu[v] = n++;
            ecken[i] = neu[v];
        }
        const pos = new haut.pos.constructor(3 * n);                  // derselbe Zahlentyp: dieselben Werte, dasselbe Ergebnis
        for (let v = 0; v < neu.length; v++) {
            const k = neu[v];
            if (k >= 0) { pos[3 * k] = haut.pos[3 * v]; pos[3 * k + 1] = haut.pos[3 * v + 1]; pos[3 * k + 2] = haut.pos[3 * v + 2]; }
        }
        return { pos, ecken };
    }
}
