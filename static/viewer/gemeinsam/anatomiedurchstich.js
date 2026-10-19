/**
 * Anatomiedurchstich — welche Punkte eines Anatomie-Stücks außen durch den Stoff stechen (19.10.2026, für `Anatomieverdeckung`).
 *
 * Edgar, 19.10.2026: „GC Hosen fitten nicht wenn die Scham aktiviert ist", dann „mach das auch für männliche Genitalien mit Matt0" und „checke alle
 * Hosen, alle Wäsche, Unterhosen, Bikinis, Röcke, Anzüge auf die Genitalien". Gemessen im Chrome (sichtbare Pixel des grün gefärbten Genitals, drei
 * Ansichten, gegen dieselben Ansichten ohne Stück): an Damira0 deckt die Hose das Stück, seit die Lagenrechnung es an seiner gezeigten Lage sieht
 * (`G9stueckstarr.nachgezogen`, 0 Pixel); an Matt0 hängt der Penis bis 58 mm vor der Haut, und die Hose umschließt ihn nicht — bei GC Pants Wool
 * blieben 13–28 % sichtbar, die Eichel unter dem Bund. Daz bringt für das männliche Geograft keinen Morph für Kleidung mit (Morphs gelesen:
 * DefaultPose, PenileLength/Width, TestesAsymmetry, Uncircumcised, Realism).
 *
 * HIER: Ein Punkt liegt außen, wenn die Strecke von ihm zum ANKER (Mitte der Randpunkte des Stücks, am Ansatz in der Haut) eine Stofffläche kreuzt
 * — dann steht der Stoff zwischen ihm und dem Körper. Was drinnen liegt (die Beule unter der Hose, die Lippen unter dem Slip), kreuzt keinen Stoff
 * und bleibt. Ohne Three.js und ohne DOM (Node-Tests).
 *
 * ZWEITE STRECKE, ENTLANG DER NORMALE (19.10.2026): Am weiblichen Stück (flach auf der Haut) lief die Strecke zum Anker von einem Punkt am Rand seitlich
 * durch den Beinausschnitt, obwohl der Stoff direkt hinter ihm lag — Damira0 mit `asian_female_shorts`: 11.769 Pixel des Stücks vor dem Stoff, der Stoff
 * 2,5 / 5,1 / 8,7 mm dahinter (p10 / p50 / p90, Tiefenvergleich im Chrome). Jetzt zählt auch die Strecke INNEN entlang der Normale des Punkts nach innen.
 *
 * DURCHBROCHENER STOFF ZÄHLT NICHT (19.10.2026, `Stoffdeckung`): Unter Spitze sah man die Löcher der ausgeblendeten Dreiecke — Matt0 mit
 * `mh_punkduck_strappy_lace_thong`: 4.826 Dreiecke weg, das Glied voller schwarzer Flecken. Hinter den Stoff drücken statt ausblenden ließ die Fläche
 * zu, zeigte unter Spitze aber die zusammengeschobene Eichel verschmiert, und unter der Wollhose blieben 13.636 / 9.230 / 15.979 Pixel sichtbar statt
 * 4 / 14 / 37 (gemessen im Chrome, drei Ansichten). Also: ausblenden unter blickdichtem Stoff, unter durchbrochenem nichts tun.
 */
export class Anatomiedurchstich {

    /** Kantenlänge (m) der Gitterzellen über den Stoffdreiecken. */
    static ZELLE = 0.01;
    /** Stoffdreiecke so weit (m) um den Kasten aus Stück und Anker zählen mit. */
    static RAND = 0.01;
    /** Ein Treffer gilt erst so weit (Anteil der Strecke) vom Punkt und vom Anker entfernt — eine Fläche durch den Punkt selbst zählt nicht. */
    static EPS = 1e-3;
    /** Länge (m) der zweiten Strecke: vom Punkt entlang seiner Normale nach innen (der Stoff lag bis 8,7 mm hinter dem Stück, p90). */
    static INNEN = 0.015;
    /**
     * Ein Punkt ist bedeckt, wenn entlang seiner Normale nach außen binnen so viel Metern Stoff liegt. Gefragt wird nur an den Nachbarn eines äußeren Punkts — sie
     * liegen ein Dreieck (3–5 mm) neben dem Durchstich. Mit 6 cm traf der Strahl an `asian_female_unterw_sche_underwear` (Damira0) einen fernen Träger, das
     * Dreieck fiel, und seitlich sah man durch das Hautloch (30.318 Lochpixel).
     */
    static VORN = 0.02;
    /** Lage eines Punkts (`lagen`): frei (kein Stoff davor oder dahinter), außen (Stoff dahinter), bedeckt (Stoff davor). */
    static FREI = 0;
    static AUSSEN = 1;
    static BEDECKT = 2;

    /** Je Punkt 1, wenn er außen durch einen Stoff sticht (`lagen` ohne die Unterscheidung frei/bedeckt). */
    static aussen(pos, anker, stoffe, normalen = null, weite = 0) {
        return Anatomiedurchstich.lagen(pos, anker, stoffe, normalen, weite).map((l) => (l === Anatomiedurchstich.AUSSEN ? 1 : 0));
    }

    /**
     * Je Punkt des Stücks seine Lage zum Stoff: AUSSEN, wenn die Strecke INNEN entlang der Normale nach innen einen Stoff kreuzt oder — nur jenseits von `weite` —
     * die Strecke zum Anker; sonst BEDECKT, wenn die Strecke VORN entlang der Normale nach außen einen kreuzt; sonst FREI. Ohne Normalen gilt jeder innere Punkt
     * als bedeckt.
     *
     * DIE STRECKE ZUM ANKER NUR FÜR, WAS ÜBER DEN ANSATZ HINAUS HÄNGT (19.10.2026, `weite`): Am flachen Stück der Frau liegt kein Punkt weiter vom Anker als der fernste Randpunkt
     * (Damira0: Rand bis 1,33 R, Punkte bis 1,33 R, R = 62,8 mm). Dort lag ein mittig einschneidender String zwischen den Lippen und dem Anker, die Lippen galten als
     * außen und fielen samt Nachbarn — seitlich sah man durchs Hautloch (`asian_female_unterw_sche_underwear`, 30.318 Lochpixel).
     * @param pos       Punkte des Stücks (xyz, so wie gezeigt — `Anatomielage`)
     * @param anker     `[x, y, z]`
     * @param stoffe    `[{pos, index}]` — Punkte (wie gezeigt) und voller Dreiecksindex je Stück
     * @param normalen  Punktnormalen des Stücks (xyz, nach außen) oder null
     * @param weite     Abstand zum Anker (m), ab dem die Strecke zum Anker zählt (`weite`: der fernste Randpunkt); 0 = für jeden Punkt
     */
    static lagen(pos, anker, stoffe, normalen = null, weite = 0) {
        const D = Anatomiedurchstich, n = pos.length / 3, aus = new Uint8Array(n).fill(D.BEDECKT);
        const g = D._gitter(stoffe, D._kasten(pos, anker, D.RAND + (normalen ? D.VORN : 0)));
        if (!g) return aus.fill(D.FREI);
        for (let i = 0; i < n; i++) {
            const x = pos[3 * i], y = pos[3 * i + 1], z = pos[3 * i + 2];
            const L = normalen ? Math.hypot(normalen[3 * i], normalen[3 * i + 1], normalen[3 * i + 2]) : 0;
            const strecke = (laenge) => [x + laenge / L * normalen[3 * i], y + laenge / L * normalen[3 * i + 1], z + laenge / L * normalen[3 * i + 2]];
            const haengt = Math.hypot(x - anker[0], y - anker[1], z - anker[2]) > weite;
            if ((haengt && D._kreuzt(x, y, z, anker, g)) || (L > 1e-9 && D._kreuzt(x, y, z, strecke(-D.INNEN), g))) aus[i] = D.AUSSEN;
            else if (L > 1e-9) aus[i] = D._kreuzt(x, y, z, strecke(D.VORN), g) ? D.BEDECKT : D.FREI;
        }
        return aus;
    }

    /** Die Mitte der Randpunkte (Kanten mit einem Dreieck; Punkte an UV-Nähten auf 0,01 mm zusammengelegt) — null ohne Rand. */
    static anker(pos, index) {
        const rand = Anatomiedurchstich._rand(pos, index);
        if (!rand.size) return null;
        const m = [0, 0, 0];
        for (const i of rand) for (let c = 0; c < 3; c++) m[c] += pos[3 * i + c] / rand.size;
        return m;
    }

    /**
     * Abstand (m) des fernsten Randpunkts vom Anker — ab dort zählt die Strecke zum Anker (`lagen`); 0 ohne Rand. Gemessen 19.10.2026: Daz Anatomie Mann an
     * Matt0 — 3.228 von 6.979 Punkten jenseits (R = 67,9 mm, Rand bis 1,28 R), Daz Anatomie Frau an Damira0 — 0 Punkte. Die Strecke zum Anker für JEDEN Punkt des
     * Manns ließ über dem Bund der hoch drapierten Foto-Hose `eigen_foto_01123809_hose` die Schamhaut fallen (69.605 Lochpixel von vorn, `gc_elvs_bootyshorts2a`
     * 20.468): die Strecke ins Becken kreuzte den Stoff, davor lag nichts.
     */
    static weite(pos, index, anker) {
        let w = 0;
        for (const i of Anatomiedurchstich._rand(pos, index)) w = Math.max(w, Math.hypot(pos[3 * i] - anker[0], pos[3 * i + 1] - anker[1], pos[3 * i + 2] - anker[2]));
        return w;
    }

    /** Die Randpunkte (Nummern) — Punkte an Kanten mit nur einem Dreieck. */
    static _rand(pos, index) {
        const id = new Map(), wer = new Int32Array(pos.length / 3);
        for (let i = 0; i < wer.length; i++) {
            const s = `${Math.round(pos[3 * i] * 1e5)},${Math.round(pos[3 * i + 1] * 1e5)},${Math.round(pos[3 * i + 2] * 1e5)}`;
            if (!id.has(s)) id.set(s, i);
            wer[i] = id.get(s);
        }
        const kanten = new Map();
        for (let k = 0; k + 2 < index.length; k += 3) for (let e = 0; e < 3; e++) {
            const a = wer[index[k + e]], b = wer[index[k + (e + 1) % 3]];
            if (a === b) continue;
            const key = a < b ? `${a}_${b}` : `${b}_${a}`;
            kanten.set(key, (kanten.get(key) || 0) + 1);
        }
        const rand = new Set();
        for (const [key, z] of kanten) if (z === 1) for (const i of key.split('_')) rand.add(Number(i));
        return rand;
    }

    /**
     * Je Dreieck des Index 1, wenn eine Ecke außen liegt und keine frei (`lagen`) — dahinter oder davor liegt dann überall Stoff, ein Loch sieht man nicht.
     * Gemessen im Chrome (Damira0): mit „eine Ecke außen" allein blieben an der Zwickelkante von `asian_female_shorts` dunkle Kerben (Lochpixel 12.118 / 2.729 / 0);
     * mit „alle drei Ecken außen" (743 / 0 / 0) stachen an `rainy_hose` Zacken durch (Genital sichtbar 23.198 / 9.624 / 43.224 statt 600 / 336 / 790).
     */
    static dreiecke(index, lagen) {
        const D = Anatomiedurchstich, aus = new Uint8Array(index.length / 3);
        for (let t = 0; t < aus.length; t++) {
            const a = lagen[index[3 * t]], b = lagen[index[3 * t + 1]], c = lagen[index[3 * t + 2]];
            aus[t] = (a === D.AUSSEN || b === D.AUSSEN || c === D.AUSSEN) && a !== D.FREI && b !== D.FREI && c !== D.FREI ? 1 : 0;
        }
        return aus;
    }

    static _kasten(pos, anker, rand) {
        const lo = [...anker], hi = [...anker];
        for (let i = 0; i + 2 < pos.length; i += 3) for (let c = 0; c < 3; c++) { lo[c] = Math.min(lo[c], pos[i + c]); hi[c] = Math.max(hi[c], pos[i + c]); }
        return { lo: lo.map(w => w - rand), hi: hi.map(w => w + rand) };
    }

    /** Gitter über die Stoffdreiecke, die den Kasten berühren: `{lo, n, zellen: Map(zelle → [Dreieck]), ecken: [[a, b, c]...]} ` oder null. */
    static _gitter(stoffe, kasten) {
        const z = Anatomiedurchstich.ZELLE, n = [0, 1, 2].map(k => Math.max(1, Math.ceil((kasten.hi[k] - kasten.lo[k]) / z)));
        const zellen = new Map(), dreiecke = [];
        for (const { pos, index } of stoffe) {
            for (let k = 0; k + 2 < index.length; k += 3) {
                const p = [index[k], index[k + 1], index[k + 2]].map(i => [pos[3 * i], pos[3 * i + 1], pos[3 * i + 2]]);
                const lo = [0, 1, 2].map(c => Math.min(p[0][c], p[1][c], p[2][c])), hi = [0, 1, 2].map(c => Math.max(p[0][c], p[1][c], p[2][c]));
                if ([0, 1, 2].some(c => hi[c] < kasten.lo[c] || lo[c] > kasten.hi[c])) continue;
                const nr = dreiecke.push(p.flat()) - 1;
                const von = [0, 1, 2].map(c => Math.max(0, Math.floor((lo[c] - kasten.lo[c]) / z))), bis = [0, 1, 2].map(c => Math.min(n[c] - 1, Math.floor((hi[c] - kasten.lo[c]) / z)));
                for (let x = von[0]; x <= bis[0]; x++) for (let y = von[1]; y <= bis[1]; y++) for (let w = von[2]; w <= bis[2]; w++) {
                    const zelle = (x * n[1] + y) * n[2] + w;
                    if (!zellen.has(zelle)) zellen.set(zelle, []);
                    zellen.get(zelle).push(nr);
                }
            }
        }
        return dreiecke.length ? { lo: kasten.lo, n, zellen, dreiecke, marke: new Int32Array(dreiecke.length), stempel: 0 } : null;
    }

    /** Kreuzt die Strecke vom Punkt zum Ziel `anker` ein Stoffdreieck? Gelaufen wird in halben Zellen durch das Gitter. */
    static _kreuzt(px, py, pz, anker, g) {
        const dx = anker[0] - px, dy = anker[1] - py, dz = anker[2] - pz, L = Math.hypot(dx, dy, dz);
        if (!(L > 1e-9)) return false;
        const schritt = 0.5 * Anatomiedurchstich.ZELLE / L, eps = Anatomiedurchstich.EPS;
        g.stempel++;
        for (let s = 0; s <= 1 + schritt; s += schritt) {
            const q = [px + s * dx, py + s * dy, pz + s * dz].map((v, c) => Math.floor((v - g.lo[c]) / Anatomiedurchstich.ZELLE));
            if (q.some((v, c) => v < 0 || v >= g.n[c])) continue;
            const liste = g.zellen.get((q[0] * g.n[1] + q[1]) * g.n[2] + q[2]);
            if (!liste) continue;
            for (const t of liste) {
                if (g.marke[t] === g.stempel) continue;
                g.marke[t] = g.stempel;
                const d = g.dreiecke[t];
                const w = Anatomiedurchstich._schnitt(px, py, pz, dx, dy, dz, d);
                if (w > eps && w < 1 - eps) return true;
            }
        }
        return false;
    }

    /** Möller–Trumbore: Parameter der Strecke `p + w · d` am Schnitt mit dem Dreieck `d` (9 Zahlen) — NaN ohne Schnitt. */
    static _schnitt(px, py, pz, dx, dy, dz, d) {
        const e1x = d[3] - d[0], e1y = d[4] - d[1], e1z = d[5] - d[2], e2x = d[6] - d[0], e2y = d[7] - d[1], e2z = d[8] - d[2];
        const hx = dy * e2z - dz * e2y, hy = dz * e2x - dx * e2z, hz = dx * e2y - dy * e2x, det = e1x * hx + e1y * hy + e1z * hz;
        if (Math.abs(det) < 1e-16) return NaN;
        const inv = 1 / det, sx = px - d[0], sy = py - d[1], sz = pz - d[2], u = (sx * hx + sy * hy + sz * hz) * inv;
        if (u < 0 || u > 1) return NaN;
        const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x, v = (dx * qx + dy * qy + dz * qz) * inv;
        if (v < 0 || u + v > 1) return NaN;
        return (e2x * qx + e2y * qy + e2z * qz) * inv;
    }
}
