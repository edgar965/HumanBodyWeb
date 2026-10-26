import { Koerperkoordinatenpunkte } from './koerperkoordinatenpunkte.js';

/**
 * Dazschnittkoord — die Körperkoordinaten JE PUNKT eines Daz-Stücks (Stufe K2c, 25.10.2026): die der Haut, an die der Punkt gebunden ist.
 *
 * HAUT: je Körperpunkt aus der Karte der eigenen Stücke (`Koerperkoordinatenpunkte.ausKarte`, an UV-Nähten verschweißt) — einmal je Körpergeometrie (`haut`).
 * BINDUNG AN DIE HAUT: die `NACHBARN` nächsten Körperpunkte in Ruhe (Würfelraster `ZELLE_M`), gewichtet nach 1 / Abstand; der nächste, über dessen Fläche der
 * Stoffpunkt liegt (Abstand entlang seiner Normale ≥ −`INNEN_M`), führt — an der Achsel läge der nächste sonst leicht auf der falschen Seite.
 * NICHT die Bindung des Servers (`G9oberflaechenbindung`, Attribute `bindung`/`bary`/`bindabstand`): Im Chrome gemessen (25.10.2026, Basic Wear T Shirt auf
 * DamiraAlt, Stufe 1, jeder 97. Punkt) lag der aus ihr nachgebaute Ort im Median 4,5 mm, aber p90 38 mm und p99 135 mm neben dem Stoffpunkt — ungeprüft schnitt
 * ein V-Ausschnitt Löcher in den Bauch (Bauchpunkte auf Halspunkten gebunden). Geprüft und nur dort genommen, wo sie passte (57.529 von 82.809 Punkten), zeichnete
 * die Mischung beider Quellen eine Sägezahnkante; mit den nächsten Hautpunkten allein war die Kante glatt (Bildvergleich im Chrome). Warum die Bindung an
 * diesen Punkten nicht passt, ist NICHT geklärt (Vermutung: die Punkte wurden nach dem Binden verschoben — Lagen, Kollision).
 * MISCHEN wie die Karte (`G9koerperkoordinaten.kachel`): Kette des führenden Punkts; Höhe über alle, Anteil und Winkel (Kreismittel) nur über die Punkte DIESER
 * Kette — stetig im Stoff, kein erfundener Wert an einer Kettengrenze.
 *
 * LÄNGEN dieser Figur: Rumpf aus Höhe und y der Rumpfpunkte ausgeglichen (wie `Eigenkleidbruecke.rumpfLaenge`), Arm und Bein im Verhältnis der Grundfigur.
 */
export class Dazschnittkoord {

    static ZELLE_M = 0.015;
    static INNEN_M = 0.004;
    static NACHBARN = 4;
    /** Suchwürfel ±1, ±2, ±4 Zellen (bis 6 cm); weiter weg bekommt ein Punkt keine Koordinaten und wird nie geschnitten. */
    static RINGE = [1, 2, 4];
    static _haut = new WeakMap();

    /** Ruhelage eines Netzes (ohne Gelenkkorrekturen einer laufenden Bewegung, wie `Hautverdeckung.lage`). */
    static lage(geo) {
        const p = geo.attributes.position.array, r = geo.userData?.felder?.ruhe;
        return r?.length === p.length ? r : p;
    }

    /** `{koord, laengen, pos, normal, raster}` der Haut — einmal je Körpergeometrie. */
    static haut(koerper, karte) {
        const geo = koerper.geometry;
        let aus = Dazschnittkoord._haut.get(geo);
        if (aus) return aus;
        const voll = geo.userData?.indexVoll;
        const index = voll?.index || geo.index.array, gruppen = voll?.gruppen || geo.groups;
        const pos = Dazschnittkoord.lage(geo);
        const koord = Koerperkoordinatenpunkte.ausKarte(karte, pos, geo.attributes.uv.array, index, gruppen, [koerper.material].flat());
        const rumpf = Dazschnittkoord.rumpflaenge(pos, koord);
        const skala = rumpf > 0.2 && rumpf < 1.5 ? rumpf / karte.laengen[0] : 1;
        aus = { koord, laengen: karte.laengen.map(l => l * skala), pos, normal: geo.attributes.normal?.array || null, raster: Dazschnittkoord._raster(pos, koord),
                ansatz: Koerperkoordinatenpunkte.ansatz(koord) };                 // Halsansatz je Umfangswinkel, wie bei den eigenen Stücken (25.10. nachts)
        Dazschnittkoord._haut.set(geo, aus);
        return aus;
    }

    /** Rumpflänge (m): Steigung von y über der Rumpfhöhe der Rumpfpunkte (Kette 1), negativ genommen; null bei zu wenigen Punkten. */
    static rumpflaenge(pos, koord) {
        let m = 0, sh = 0, sy = 0, shh = 0, shy = 0;
        for (let p = 0; p < koord.kette.length; p++) {
            if (koord.kette[p] !== 1) continue;
            const h = koord.hoehe[p], y = pos[3 * p + 1];
            m++; sh += h; sy += y; shh += h * h; shy += h * y;
        }
        return m > 10 ? -(m * shy - sh * sy) / (m * shh - sh * sh) : null;
    }

    static _zelle(x, y, z) {
        const g = Dazschnittkoord.ZELLE_M;
        return `${Math.floor(x / g)},${Math.floor(y / g)},${Math.floor(z / g)}`;
    }

    /** Würfelraster der Hautpunkte mit Kette. */
    static _raster(pos, koord) {
        const raster = new Map();
        for (let k = 0; k < pos.length / 3; k++) {
            if (!koord.kette[k]) continue;
            const s = Dazschnittkoord._zelle(pos[3 * k], pos[3 * k + 1], pos[3 * k + 2]);
            const liste = raster.get(s);
            if (liste) liste.push(k); else raster.set(s, [k]);
        }
        return raster;
    }

    /**
     * `{koord: Float32Array 4N (Kette, Anteil, Höhe, Winkel), lage: Float32Array 2N (x in Ruhe, Rumpfhöhe des Halsansatzes unter diesem Umfangswinkel —
     * `Koerperkoordinatenpunkte.ansatz`, gemischt wie der Anteil), naechste, ohne, quelle, ms}` eines Teils. Ab dem Halsansatz misst der Ausschnitt; ab der Ebene
     * durch das Halsgelenk (h = 0) schnitt er außerhalb seiner Breite über den Trapezmuskel (bei DamiraAlt seitlich 5,2 cm, gemessen von K2a).
     */
    static teil(netz, haut) {
        const t0 = performance.now();
        const pos = Dazschnittkoord.lage(netz.geometry), n = pos.length / 3;
        const koord = new Float32Array(4 * n), lage = new Float32Array(2 * n);
        const ecken = new Int32Array(Dazschnittkoord.NACHBARN), abstand = new Float64Array(Dazschnittkoord.NACHBARN), gewichte = new Float64Array(Dazschnittkoord.NACHBARN);
        let gefunden = 0;
        for (let p = 0; p < n; p++) {
            lage[2 * p] = pos[3 * p];
            let zahl = 0;
            for (const ring of Dazschnittkoord.RINGE) {                     // weiter weg nur, wenn nah nichts liegt (lose Röcke, Kragen)
                zahl = Dazschnittkoord._naechste(pos[3 * p], pos[3 * p + 1], pos[3 * p + 2], haut, ecken, abstand, ring);
                if (zahl) break;
            }
            if (!zahl) continue;
            gefunden++;
            for (let i = 0; i < zahl; i++) gewichte[i] = 1 / (abstand[i] + 1e-4);
            gewichte[0] *= 1.5;                                            // der führende Punkt (über seiner Fläche) bestimmt die Kette
            Dazschnittkoord._mischen(haut.koord, ecken, gewichte, zahl, koord, 4 * p);
            let sw = 0, sa = 0;
            for (let i = 0; i < zahl; i++) {
                if (haut.koord.kette[ecken[i]] !== koord[4 * p]) continue;
                sw += gewichte[i]; sa += gewichte[i] * haut.ansatz[ecken[i]];
            }
            lage[2 * p + 1] = sw > 0 ? sa / sw : 0;
        }
        return { koord, lage, naechste: gefunden, ohne: n - gefunden, quelle: `nächste Hautpunkte: ${gefunden} von ${n}`, ms: Math.round(performance.now() - t0) };
    }

    /**
     * Die bis zu `NACHBARN` nächsten Hautpunkte im Würfel ±`ring` Zellen nach `ecken`/`abstand` (aufsteigend), der nächste ÜBER seiner Fläche an Stelle 0.
     * → Anzahl (0 = keiner in Reichweite).
     */
    static _naechste(x, y, w, haut, ecken, abstand, ring) {
        const g = Dazschnittkoord.ZELLE_M, hp = haut.pos, hn = haut.normal, m = Dazschnittkoord.NACHBARN;
        const cx = Math.floor(x / g), cy = Math.floor(y / g), cw = Math.floor(w / g);
        let zahl = 0, ueber = -1, ueberD = Infinity;
        for (let i = -ring; i <= ring; i++) for (let j = -ring; j <= ring; j++) for (let l = -ring; l <= ring; l++) {
            const liste = haut.raster.get(`${cx + i},${cy + j},${cw + l}`);
            if (!liste) continue;
            for (const k of liste) {
                const dx = x - hp[3 * k], dy = y - hp[3 * k + 1], dw = w - hp[3 * k + 2], d = Math.sqrt(dx * dx + dy * dy + dw * dw);
                if (d < ueberD && (!hn || dx * hn[3 * k] + dy * hn[3 * k + 1] + dw * hn[3 * k + 2] >= -Dazschnittkoord.INNEN_M)) { ueberD = d; ueber = k; }
                if (zahl === m && d >= abstand[m - 1]) continue;
                let s = Math.min(zahl, m - 1);
                while (s > 0 && abstand[s - 1] > d) { ecken[s] = ecken[s - 1]; abstand[s] = abstand[s - 1]; s--; }
                ecken[s] = k; abstand[s] = d;
                if (zahl < m) zahl++;
            }
        }
        if (ueber >= 0 && ecken[0] !== ueber) {                            // der Punkt über seiner Fläche führt
            let s = 0;
            while (s < zahl && ecken[s] !== ueber) s++;
            if (s === zahl) s = zahl - 1;                                   // nicht unter den nächsten: verdrängt den letzten
            for (; s > 0; s--) { ecken[s] = ecken[s - 1]; abstand[s] = abstand[s - 1]; }
            ecken[0] = ueber; abstand[0] = ueberD;
        }
        return zahl;
    }

    /** Werte mehrerer Hautpunkte mischen wie die Karte (siehe Kopf) nach `aus[o … o+3]`; `ecken[0]` führt. */
    static _mischen(h, ecken, gewichte, zahl, aus, o) {
        const kette = h.kette[ecken[0]];
        let sw = 0, sh = 0, swk = 0, st = 0, ss = 0, sc = 0;
        for (let i = 0; i < zahl; i++) {
            const k = ecken[i], w = gewichte[i];
            sw += w; sh += w * h.hoehe[k];
            if (h.kette[k] !== kette) continue;
            swk += w; st += w * h.anteil[k];
            ss += w * Math.sin(2 * Math.PI * h.winkel[k]); sc += w * Math.cos(2 * Math.PI * h.winkel[k]);
        }
        aus[o] = kette;
        aus[o + 1] = swk > 0 ? st / swk : h.anteil[ecken[0]];
        aus[o + 2] = sw > 0 ? sh / sw : h.hoehe[ecken[0]];
        aus[o + 3] = ((Math.atan2(ss, sc) / (2 * Math.PI)) % 1 + 1) % 1;
    }
}
