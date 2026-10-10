/**
 * Stucknormalen — die Normalen am Rand eines verschweißten Ersatzstücks gehen in die der Haut über (09.10.2026).
 *
 * WARUM (Chrome, „cute girl", Naht ohne Spalt, Edgar: „ich kann es nicht glauben, dass wir einen Tag an einer Naht arbeiten"): Der Rand
 * des Stücks liegt auf den Ringecken der Haut — und trotzdem blieb an der Naht eine Linie. Im Bild (linke Naht, Zeile quer über sie,
 * 16 Pixel breite Fenster) sprang die Farbe von 226/203/186 (Haut) auf 210/182/165 (Stück): 16 bis 21 Stufen in einem Fenster.
 * Mit abgeschalteten Normalenkarten (`normalScale` 0 an Haut und Stück) blieb der Sprung (226/204/188 → 210/182/165): er kommt nicht
 * aus den feinen Poren, sondern aus der Beleuchtung. Der Server rechnet die Normalen des Stücks aus dem Stück allein — am Rand sieht
 * jede Normale nur ihre Seite. Gemessen an den 98 Ringecken, Stück gegen Haut am selben Ort: Winkel im Median 19°, 90. Perzentil 73°,
 * größter 82° (Chrome, 09.10.2026).
 *
 * HIER: Die Normale eines Stückpunkts nahe am Rand wird zur Normale der Haut an den Ringecken gemischt, mit dem Weg über das Netz
 * als Maß: am Rand ganz die der Haut (dort sind beide dasselbe Netz), nach `BAND_M` ganz die eigene des Stücks (Hermite). Die Haut
 * liefert je Randpunkt die Normale ihres Ringpunkts; innen zählen die Randpunkte in der Nähe des nächsten, gewichtet mit 1/Abstand².
 * Das Maß ist der Weg über das Netz, nicht der Raumabstand — sonst bekäme auch die Gegenseite einer Falte (innere Lippen nahe dem
 * Damm) die Normale der Haut.
 *
 * Gerechnet wird aus der Normale, wie der Server sie lieferte (`ruhe`): ein zweiter Lauf (neue Maske) ergibt dasselbe, nicht eine
 * Mischung aus der Mischung. Ohne Three.js und ohne DOM (Node-Test `test_js_stucknormalen.py`).
 */
export class Stucknormalen {

    /** So weit (m) über das Netz vom Rand geht die Normale der Haut ins Stück (`weg` aus `Stuecknaht` reicht mit 14 mm weiter). */
    static BAND_M = 0.010;
    /** Randpunkte, die höchstens so viel (m) weiter weg liegen als der nächste, zählen mit. */
    static WEITE_M = 0.006;
    /** Dämpfung der Gewichte 1/(d + EPS)² — ein Punkt auf dem Rand hat Abstand 0. */
    static EPS_M = 1e-4;

    /**
     * Die Normalen des Stücks in `normalen` (in place) aus `ruhe` und den Normalen der Haut neu setzen.
     * @param punkte        Punkte des Stücks (Ruhelage), xyz
     * @param normalen      Normalen des Stücks, xyz — Ziel
     * @param ruhe          Normalen des Stücks, wie der Server sie lieferte
     * @param naht          Ergebnis von `Stuecknaht.verschiebung`: `weg` und `randpunkte`
     * @param ringPunkte    Hautpunkt je Ringecke (`ring.punkte`)
     * @param hautNormalen  Normalen der Haut, xyz
     * @returns Zahl der geänderten Punkte
     */
    static angleichen(punkte, normalen, ruhe, naht, ringPunkte, hautNormalen) {
        normalen.set(ruhe);
        const { weg, randpunkte } = naht;
        if (!weg || !randpunkte.ids.length) return 0;
        const { ids, ecke } = randpunkte, k = ids.length, n = punkte.length / 3;
        const abstand = new Float64Array(k);
        let geaendert = 0;
        for (let p = 0; p < n; p++) {
            if (!(weg[p] < Stucknormalen.BAND_M)) continue;
            const px = punkte[3 * p], py = punkte[3 * p + 1], pz = punkte[3 * p + 2];
            let nah = Infinity;
            for (let r = 0; r < k; r++) {
                const q = ids[r];
                abstand[r] = Math.hypot(punkte[3 * q] - px, punkte[3 * q + 1] - py, punkte[3 * q + 2] - pz);
                if (abstand[r] < nah) nah = abstand[r];
            }
            let sx = 0, sy = 0, sz = 0;
            for (let r = 0; r < k; r++) {
                if (abstand[r] > nah + Stucknormalen.WEITE_M) continue;
                const h = 3 * ringPunkte[ecke[r]], d = abstand[r] + Stucknormalen.EPS_M, w = 1 / (d * d);
                sx += w * hautNormalen[h]; sy += w * hautNormalen[h + 1]; sz += w * hautNormalen[h + 2];
            }
            const ls = Math.hypot(sx, sy, sz);
            if (!(ls > 0)) continue;
            const t = weg[p] / Stucknormalen.BAND_M, f = 1 - t * t * (3 - 2 * t);
            const x = ruhe[3 * p] * (1 - f) + sx / ls * f, y = ruhe[3 * p + 1] * (1 - f) + sy / ls * f, z = ruhe[3 * p + 2] * (1 - f) + sz / ls * f;
            const l = Math.hypot(x, y, z);
            if (!(l > 0)) continue;
            normalen[3 * p] = x / l; normalen[3 * p + 1] = y / l; normalen[3 * p + 2] = z / l;
            geaendert++;
        }
        return geaendert;
    }
}
