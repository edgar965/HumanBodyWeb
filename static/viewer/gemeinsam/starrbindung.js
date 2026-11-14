/**
 * Starrbindung — ein starres Stück hängt je Insel ganz an EINEM Knochen (12.11.2026, Bauart „starr“, `bauart.js`).
 *
 * Anlass (Konzept `Docu/konzepte/2026-11-12_genesis-zuerst-konzept.md`, Abschnitte 3b und 10a): Die Laserwaffe des Fallout Rangers hängt in
 * ihrer `.dsf` an spine1 bis spine4 und l_shoulder und lief im Stoffschwung; im Tanz verformte sie sich (Kantendehnung p99 je Bild 1,31 bis
 * 1,71, gemessen im Chrome mit der `Kleidungsprobe`). Edgar entschied „mit deinen Empfehlungen“: Starr wird ein Stück über die Bauart am
 * Eintrag der Garderobe, nicht über neue Gewichte in der Stückdatei.
 *
 * DIE REGEL: Je zusammenhängender Insel des Netzes zählt jeder Knochen die Summe seiner Gewichte über alle Punkte der Insel; der größte
 * gewinnt, jeder Punkt der Insel hängt danach mit Gewicht 1 an ihm. Ein Paar Ohrringe oder zwei Armbänder bleiben so zwei Inseln an zwei
 * Knochen. Punkte an derselben Stelle (Nahtkopien der UV, `G9netzteilung`) gehören zu derselben Insel — sonst zerfiele ein Helm entlang
 * seiner UV-Nähte in Teile an verschiedenen Knochen.
 *
 * NICHT für Schuhe: Sie sind starr je Fuß, ihre Gewichte (Fuß, Zehen) bringt Daz mit, und die Fußhaltung kommt über `griffdeltas`
 * (12.11.2026). Nicht für Ersatzstücke (Originalaugen) und verschweißte Stücke (Scham), die gehören zur Figur.
 */
export class Starrbindung {

    /** Nahtkopien gleicher Lage zusammenlegen: Raster in Metern. */
    static LAGE_M = 1e-6;

    /** Soll dieses Netz starr gebunden werden? */
    static gilt(netz, bauart) {
        const u = netz?.userData || {};
        return bauart === 'starr' && !u.schuh && !u.hautTiefe && !(u.ersetzt?.length);
    }

    /**
     * Die Attribute `skinIndex`/`skinWeight` eines gebundenen Netzes je Insel auf einen Knochen setzen.
     * @returns {{inseln, knochen}|null} Zahl der Inseln und der gewählten Knochen (Spalten im Skelett), null ohne Gewichte
     */
    static anwenden(netz) {
        const g = netz?.geometry;
        const si = g?.getAttribute?.('skinIndex'), sw = g?.getAttribute?.('skinWeight');
        if (!si || !sw || !g.index) return null;
        const n = si.count;
        const insel = Starrbindung.gruppen(Starrbindung.inseln(g.index.array, g.attributes.position.array, n), g.attributes.position.array);
        const summen = new Map();
        for (let i = 0; i < n; i++) {
            for (let k = 0; k < 4; k++) {
                const w = sw.array[4 * i + k];
                if (!(w > 0)) continue;
                const schluessel = insel[i] * 4096 + Math.round(si.array[4 * i + k]);
                summen.set(schluessel, (summen.get(schluessel) || 0) + w);
            }
        }
        const bester = new Map();                                   // Insel → [Knochen, Summe]
        for (const [schluessel, summe] of summen) {
            const i = Math.floor(schluessel / 4096), b = schluessel % 4096;
            const bisher = bester.get(i);
            if (!bisher || summe > bisher[1]) bester.set(i, [b, summe]);
        }
        for (let i = 0; i < n; i++) {
            const b = bester.get(insel[i]);
            if (!b) continue;                                       // Insel ganz ohne Gewicht: bleibt, wie sie war
            si.array[4 * i] = b[0]; si.array[4 * i + 1] = 0; si.array[4 * i + 2] = 0; si.array[4 * i + 3] = 0;
            sw.array[4 * i] = 1; sw.array[4 * i + 1] = 0; sw.array[4 * i + 2] = 0; sw.array[4 * i + 3] = 0;
        }
        si.needsUpdate = true;
        sw.needsUpdate = true;
        const knochen = [...new Set([...bester.values()].map((b) => b[0]))];
        netz.userData.starrbindung = { inseln: bester.size, knochen };
        return netz.userData.starrbindung;
    }

    /** Inseln, deren Kisten höchstens so weit auseinander liegen, sind EIN starres Teil. */
    static NAH_M = 0.03;

    /**
     * Inseln zu starren Gruppen zusammenfassen (12.11.2026, im Chrome gemessen: die Laserwaffe des Fallout Rangers besteht aus 175 Inseln, je Insel
     * gewählt hingen sie an fünf Knochen — die Teile wären gegeneinander gewandert; der Helm aus 22 an fünf). Inseln, deren Kisten sich bis `NAH_M`
     * nähern, gehören zusammen; ein Paar Ohrringe (15 cm auseinander) bleibt getrennt. → je Punkt die Nummer seiner Gruppe.
     */
    static gruppen(insel, pos) {
        const kisten = new Map();
        for (let i = 0; i < insel.length; i++) {
            let k = kisten.get(insel[i]);
            if (!k) { k = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity]; kisten.set(insel[i], k); }
            for (let a = 0; a < 3; a++) { const w = pos[3 * i + a]; if (w < k[a]) k[a] = w; if (w > k[a + 3]) k[a + 3] = w; }
        }
        const namen = [...kisten.keys()], liste = namen.map((n) => kisten.get(n)), eltern = namen.map((_, i) => i), d = Starrbindung.NAH_M;
        const wurzel = (i) => { while (eltern[i] !== i) { eltern[i] = eltern[eltern[i]]; i = eltern[i]; } return i; };
        for (let a = 0; a < liste.length; a++) {
            for (let b = a + 1; b < liste.length; b++) {
                const A = liste[a], B = liste[b];
                if (A[0] - d <= B[3] && B[0] - d <= A[3] && A[1] - d <= B[4] && B[1] - d <= A[4] && A[2] - d <= B[5] && B[2] - d <= A[5]) {
                    const x = wurzel(a), y = wurzel(b); if (x !== y) eltern[x] = y;
                }
            }
        }
        const gruppe = new Map(namen.map((n, i) => [n, namen[wurzel(i)]]));
        return Int32Array.from(insel, (n) => gruppe.get(n));
    }

    /** Je Punkt die Nummer seiner Insel (über Dreiecke und über gleiche Lage verbunden). */
    static inseln(index, pos, n) {
        const eltern = new Int32Array(n);
        for (let i = 0; i < n; i++) eltern[i] = i;
        const wurzel = (i) => {
            while (eltern[i] !== i) { eltern[i] = eltern[eltern[i]]; i = eltern[i]; }
            return i;
        };
        const vereinen = (a, b) => { const x = wurzel(a), y = wurzel(b); if (x !== y) eltern[x] = y; };
        for (let k = 0; k + 2 < index.length; k += 3) {
            vereinen(index[k], index[k + 1]);
            vereinen(index[k + 1], index[k + 2]);
        }
        const lage = new Map(), r = 1 / Starrbindung.LAGE_M;
        for (let i = 0; i < n; i++) {
            const schluessel = `${Math.round(pos[3 * i] * r)},${Math.round(pos[3 * i + 1] * r)},${Math.round(pos[3 * i + 2] * r)}`;
            const erster = lage.get(schluessel);
            if (erster === undefined) lage.set(schluessel, i);
            else vereinen(i, erster);
        }
        const aus = new Int32Array(n);
        for (let i = 0; i < n; i++) aus[i] = wurzel(i);
        return aus;
    }
}
