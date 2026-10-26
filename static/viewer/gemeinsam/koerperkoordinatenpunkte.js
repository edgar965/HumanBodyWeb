import { Koerperkoordinatenkarte } from './koerperkoordinatenkarte.js';

/**
 * Koerperkoordinatenpunkte — die Körperkoordinaten JE PUNKT eines Netzes (Stufe K2a, 25.10.2026): Kette, Anteil, Höhe, Winkel wie in `G9koerperkoordinaten`.
 *
 * Das ist der EINGANG aller stückunabhängigen Rechnungen der eigenen Kleider: der Shader (Attribut `kkKoord`, `EigenkleidGLSL`: Sitz, Säume, Ausschnitt) und die
 * Brücke über Mulden (`Eigenkleidbruecke`) — `{kette: Uint8Array, anteil, hoehe, winkel: Float32Array}` mit einer Zeile je Punkt. Für die Haut kommen sie aus der
 * Karte an der UV des Punkts (`ausKarte`, dieselbe Regel wie `texelFetch`); ein getragenes Daz-Stück bekäme sie später aus seiner Bindung an die Haut (nächster
 * Hautpunkt) — dieselben Felder, kein Umbau.
 *
 * NAHTDOPPEL: Ein Punkt an einer UV-Naht steht mehrfach im Netz (gleiche Lage, andere UV, oft andere Kachel). Las jedes Doppel die Karte selbst, bekam die eine
 * Hälfte „Rumpf“, die andere „Bein“ — mit anderem Sitz riss die Schale entlang der Naht auf (im Chrome gesehen an Mann1: helle Zickzacklinien am Gesäß, schwarze
 * Dreiecke am Kreuz). Deshalb tragen alle Punkte gleicher Lage die Werte des ERSTEN (`verschweissen`).
 *
 * Welche Kachel ein Punkt hat, sagt die Gruppe eines seiner Dreiecke (Material `userData.kachel`); nur Gruppen, deren Name `haut` trifft und deren Kachel die
 * Karte führt — alle anderen Punkte bleiben Kette 0 (`keine`).
 */
export class Koerperkoordinatenpunkte {

    static HAUT = /^(Head|Body|Arms|Legs)$/;

    /**
     * @param position  Float32Array (3N) — Ruhelage (für die Nahtdoppel)
     * @param uv        Float32Array (2N) — die UV der Punkte
     * @param index     Uint32Array — Dreiecke (der volle Index, auch unter einem angesetzten Stück)
     * @param gruppen   `[{start, count, materialIndex}]`
     * @param materialien die Materialien (mit `userData.gruppe`, `userData.kachel`)
     */
    static ausKarte(karte, position, uv, index, gruppen, materialien, haut = Koerperkoordinatenpunkte.HAUT) {
        const n = uv.length / 2;
        const zeile = new Int16Array(n).fill(-1);
        for (const g of gruppen) {
            const m = materialien[g.materialIndex];
            const z = haut.test(m?.userData?.gruppe || '') ? karte.zeile.get(Number(m.userData.kachel)) : undefined;
            if (z === undefined) continue;
            for (let i = g.start; i < g.start + g.count; i++) zeile[index[i]] = z;
        }
        const aus = { kette: new Uint8Array(n), anteil: new Float32Array(n), hoehe: new Float32Array(n), winkel: new Float32Array(n) };
        for (let p = 0; p < n; p++) {
            if (zeile[p] < 0) continue;
            const [k, a, h, w] = Koerperkoordinatenkarte.lesen(karte, zeile[p], uv[2 * p], uv[2 * p + 1]);
            aus.kette[p] = k;
            aus.anteil[p] = a;
            aus.hoehe[p] = h;
            aus.winkel[p] = w;
        }
        Koerperkoordinatenpunkte._naegel(aus, position, index, gruppen, materialien);
        aus.verschweisst = Koerperkoordinatenpunkte.verschweissen(aus, position);
        return aus;
    }

    static NAEGEL = /^Toenails$/;
    static OHNE = -0.5;

    /**
     * Zehennägel (eigene Gruppe, nicht in der Karte) bekommen die Kette ihres Fußes (10 links = +x, 11 rechts), Anteil wie jeder Fußpunkt (`OHNE`), Höhe am
     * Bildrand (1,5): Socken decken sie mit (25.10.2026 nachts — im Chrome gesehen an DamiraAlt: die Nägel standen rosa in der weißen Socke, die Schale hatte
     * dort Löcher). Für Oberteil und Hose ändert das nichts: Fußpunkte schneiden beide weg.
     */
    static _naegel(aus, position, index, gruppen, materialien) {
        for (const g of gruppen) {
            if (!Koerperkoordinatenpunkte.NAEGEL.test(materialien[g.materialIndex]?.userData?.gruppe || '')) continue;
            for (let i = g.start; i < g.start + g.count; i++) {
                const p = index[i];
                if (aus.kette[p]) continue;
                aus.kette[p] = position[3 * p] > 0 ? 10 : 11;
                aus.anteil[p] = Koerperkoordinatenpunkte.OHNE;
                aus.hoehe[p] = 1.5;
            }
        }
    }

    /** Punkte gleicher Lage (auf 0,01 mm) bekommen die Werte des ersten mit Kette > 0; → Zahl der angeglichenen Punkte. */
    static verschweissen(koord, position) {
        const erster = new Map();
        let zahl = 0;
        const schluessel = p => `${Math.round(position[3 * p] * 1e5)},${Math.round(position[3 * p + 1] * 1e5)},${Math.round(position[3 * p + 2] * 1e5)}`;
        for (let p = 0; p < koord.kette.length; p++) {
            if (!koord.kette[p]) continue;
            const s = schluessel(p);
            const q = erster.get(s);
            if (q === undefined) { erster.set(s, p); continue; }
            if (koord.kette[p] !== koord.kette[q] || koord.anteil[p] !== koord.anteil[q] || koord.hoehe[p] !== koord.hoehe[q]) zahl++;
            for (const feld of ['kette', 'anteil', 'hoehe', 'winkel']) koord[feld][p] = koord[feld][q];
        }
        return zahl;
    }

    /**
     * Normalen gleicher Lage gemittelt (3N) — das Attribut `kkNormal`. Die Haut trägt an UV-Nähten getrennte Normalen; die Schale schiebt entlang der Normale, also
     * klaffte sie dort um Sitz × Winkel auf (im Chrome gesehen an Mann1: dunkle Treppe in der Leiste, die Naht Body/Legs entlang, auch ohne Brücke).
     */
    static normalen(position, normal) {
        const n = position.length / 3, summe = new Map(), aus = new Float32Array(3 * n);
        const schluessel = p => `${Math.round(position[3 * p] * 1e5)},${Math.round(position[3 * p + 1] * 1e5)},${Math.round(position[3 * p + 2] * 1e5)}`;
        for (let p = 0; p < n; p++) {
            const s = schluessel(p), v = summe.get(s) || [0, 0, 0];
            v[0] += normal[3 * p]; v[1] += normal[3 * p + 1]; v[2] += normal[3 * p + 2];
            summe.set(s, v);
        }
        for (let p = 0; p < n; p++) {
            const v = summe.get(schluessel(p)), l = Math.hypot(v[0], v[1], v[2]) || 1;
            aus.set([v[0] / l, v[1] / l, v[2] / l], 3 * p);
        }
        return aus;
    }

    static ANSATZ_FAECHER = 36;

    /**
     * Rumpfhöhe des HALSANSATZES unter dem Umfangswinkel jedes Rumpf-, Hals- und Kopfpunkts (N, sonst 0) — das Attribut `kkAnsatz` (25.10.2026 nachts).
     * Der Ausschnitt maß seine Tiefe von h = 0, der waagrechten Ebene durch das Halsgelenk `neck1`. Der Halsansatz (unterster Halspunkt, Kette 6, je Fach des
     * Umfangswinkels) liegt aber darüber — gemessen an DamiraAlt: vorn h = −0,034, seitlich −0,092, hinten −0,082 (× Rumpflänge 0,563 m: 1,9 / 5,2 / 4,6 cm).
     * Außerhalb der Ausschnittbreite schnitt die Ebene deshalb über den Trapezmuskel: oben auf den Schultern lag Haut frei, mit Saumband drumherum. Jetzt zählt
     * die Tiefe ab diesem Ansatz (`EigenkleidschnittGLSL.kkHals`). Je Fach das Maximum der Höhe, leere Fächer vom Nachbarn, dreifach gemittelt, zwischen den
     * Fachmitten linear.
     */
    static ansatz(koord) {
        const n = koord.kette.length, f = Koerperkoordinatenpunkte.ANSATZ_FAECHER, max = new Float64Array(f).fill(NaN), aus = new Float32Array(n);
        for (let p = 0; p < n; p++) {
            if (koord.kette[p] !== 6) continue;
            const b = Math.floor(koord.winkel[p] * f) % f;
            max[b] = Number.isNaN(max[b]) ? koord.hoehe[p] : Math.max(max[b], koord.hoehe[p]);
        }
        if (max.every(Number.isNaN)) return aus;
        for (let schritt = 0; schritt < f && max.some(Number.isNaN); schritt++) {
            const alt = max.slice();
            for (let b = 0; b < f; b++) if (Number.isNaN(alt[b])) max[b] = [alt[(b + 1) % f], alt[(b + f - 1) % f]].find(v => !Number.isNaN(v)) ?? NaN;
        }
        const glatt = max.map((v, b) => (max[(b + f - 1) % f] + v + max[(b + 1) % f]) / 3);
        for (let p = 0; p < n; p++) {
            const k = koord.kette[p];
            if (k !== 1 && k !== 6 && k !== 7) continue;
            const x = koord.winkel[p] * f - 0.5, b0 = ((Math.floor(x) % f) + f) % f, t = x - Math.floor(x);
            aus[p] = glatt[b0] * (1 - t) + glatt[(b0 + 1) % f] * t;
        }
        return aus;
    }

    /** Die vier Größen als ein Feld (4N: Kette, Anteil, Höhe, Winkel) — das Attribut `kkKoord`. */
    static alsFeld(koord) {
        const n = koord.kette.length, feld = new Float32Array(4 * n);
        for (let p = 0; p < n; p++) feld.set([koord.kette[p], koord.anteil[p], koord.hoehe[p], koord.winkel[p]], 4 * p);
        return feld;
    }
}
