import { Anatomiehaut } from './anatomiehaut.js';
import { Anatomielage } from './anatomielage.js';
import { Dreiecksabstand } from './dreiecksabstand.js';
import { Hautstellengitter } from './hautstellengitter.js';
import { Strahldreieck } from './strahldreieck.js';

/**
 * Genesis9hautebenenstueck — die Hautebenen auch auf dem Anatomie-Stück (18.10.2026).
 *
 * Edgar, 18.10.2026 (DamiraAlt: Hautton 35, Sommersprossen, Altersflecken): „textur noch kaputt. Lädt eigene Textur, und nicht die von dem Modell" — „das soll für alle
 * Modelle funktionieren, und hat auch schon mal funktioniert". Das Stück backt die Karten der Haut darunter (`Anatomiebacken`) — aber nur die rohen Karten. Was die
 * Hautebenen im Shader daraus machen (`Genesis9hautebenen`, seit 17.10.2026: Ton, Röte, Farbton, Punkte, Flecken), lag nur auf den Materialien des Körpers
 * (`Genesis9hautebenen.materialien` = `bodyMesh.material`). Ohne Hautebenen passte das Stück, mit ihnen stand es als eigene Farbe in der Haut.
 *
 * HIER: `ziele` nennt die Materialien, die die Ebenen bekommen — die des Körpers (Vorbild = sie selbst) und die der Anatomie-Stücke, die die Karten der Haut zeigen
 * (Vorbild = das Körpermaterial, aus dem ihre Karte gebacken ist, `anatomieGebacken.vorbild`: dessen Kachel, Gruppe, Gebietskarte). Ton und Farbe hängen an keiner UV;
 * Punkte und Gebiete lesen im Shader die UV der KACHEL (`vMapUv`), auf dem Stück wäre das sein eigener Atlas. Deshalb bekommt das Stück je Punkt die Kachel-UV der
 * Haut darunter (`uvHaut`: Punkt im Hautdreieck der Vorbildgruppe, durch die Kartenmatrix des Vorbilds wie `vMapUv`) und der Shader nimmt sie (`HT_UV_HAUT`,
 * `Genesis9hautebenenGLSL`). Gerechnet wird je Körpernetz, Vorbild und Stückform einmal.
 */
export class Genesis9hautebenenstueck {

    /** Kantenlänge des Suchgitters (m) und Rand um das Stück, in dem Hautdreiecke zählen. */
    static ZELLE_M = 0.01;
    static RAND_M = 0.03;
    /** Der Strahl entlang der Normale gilt bis zu so viel × dem nächsten Abstand (+ 1 mm) — wie beim Bake (`Anatomiezuordnung`). */
    static STRAHL_FAKTOR = 2.5;

    /** `[{m, v}]`: die Hautmaterialien des Körpers (`v = m`) und die der Anatomie-Stücke mit den Karten der Haut (`v` = Körpermaterial, aus dem sie gebacken sind). */
    static ziele(inst, koerpermaterialien) {
        const aus = (koerpermaterialien || []).map(m => ({ m, v: m }));
        for (const { netz } of Anatomiehaut.stuecke(inst)) {
            const vorbild = netz.userData.anatomieGebacken?.vorbild;
            if (!vorbild) continue;
            const mats = Anatomiehaut.materialien(netz).filter(m => m.map && m.map === m.userData.anatomieHaut?.hautKarte);
            if (!mats.length || !Genesis9hautebenenstueck.uvSetzen(inst, netz, vorbild)) continue;
            for (const m of mats) {
                Genesis9hautebenenstueck.umstellen(m);
                aus.push({ m, v: vorbild });
            }
        }
        return aus;
    }

    /** Der Shader des Stücks liest Punkte und Gebiete über `uvHaut` (`HT_UV_HAUT`); `defines` gehören zum Programmschlüssel von Three. */
    static umstellen(m) {
        if (m.defines && 'HT_UV_HAUT' in m.defines) return;
        m.defines = { ...(m.defines || {}), HT_UV_HAUT: '' };
        m.needsUpdate = true;
    }

    /** `uvHaut` am Stück setzen (oder lassen, wenn Körpernetz, Vorbild und Stückform gleich sind) — false, wenn keine Haut der Vorbildgruppe in der Nähe liegt. */
    static uvSetzen(inst, netz, vorbild) {
        const koerper = inst?.bodyMesh, geo = koerper?.geometry, st = netz.geometry, pos = st?.attributes?.position;
        if (!geo?.attributes?.uv || !pos) return false;
        const schluessel = `${geo.uuid}|${vorbild.uuid}|${pos.version}|${pos.count}|${Anatomielage.kennung(st)}`;
        if (st.userData.uvHautSchluessel === schluessel && st.attributes.uvHaut) return true;
        const uv = Genesis9hautebenenstueck.rechnen(koerper, vorbild, Anatomielage.lage(st), st.attributes.normal?.array || null);    // Lage wie gezeigt
        if (!uv) return false;
        st.setAttribute('uvHaut', new pos.constructor(uv, 2));        // dieselbe Attributklasse wie `position` — ohne Three-Import, in Node prüfbar
        st.userData.uvHautSchluessel = schluessel;
        return true;
    }

    /**
     * `Float32Array` (2 je Stückpunkt): die Kachel-UV der Haut unter jedem Stückpunkt — oder null ohne Haut der Vorbildgruppe in der Nähe. Die Stelle ist ein Punkt IM
     * Hautdreieck (Gewichte der Ecken), gesucht wie beim Bake: der Strahl entlang der Normale des Stücks, sonst der nächste Punkt. Die erste Fassung nahm die UV des
     * nächsten Hautpunkts — gemessen an DamiraAlt (18.10.2026, Chrome): 218 verschiedene UV auf 4.231 Stückpunkten (Kante im Mittel 1,84 mm); die Sommersprossen
     * (Zellen von 0,006 / `uHtMeterUV`, rund 6 mm) fielen auf dem Stück aus, die größeren Muttermale nicht.
     */
    static rechnen(koerper, vorbild, stueck, normalen = null) {
        const geo = koerper.geometry, material = [koerper.material].flat();
        const voll = geo.userData?.indexVoll, index = voll ? voll.index : geo.index?.array, gruppen = voll ? voll.gruppen : geo.groups;
        const hp = Anatomielage.lage(geo), huv = geo.attributes.uv.array;
        const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
        for (let i = 0; i < stueck.length; i += 3) {
            for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], stueck[i + k]); hi[k] = Math.max(hi[k], stueck[i + k]); }
        }
        const R = Genesis9hautebenenstueck.RAND_M;
        const drin = p => [0, 1, 2].every(k => hp[3 * p + k] >= lo[k] - R && hp[3 * p + k] <= hi[k] + R);
        const ecken = [];
        for (const gr of gruppen || []) {
            if (material[gr.materialIndex] !== vorbild || !index) continue;
            for (let n = gr.start; n + 2 < gr.start + gr.count; n += 3) {
                const a = index[n], b = index[n + 1], c = index[n + 2];
                if (drin(a) || drin(b) || drin(c)) ecken.push(a, b, c);
            }
        }
        if (!ecken.length) return null;
        const gitter = Genesis9hautebenenstueck._gitter(hp, ecken), vor = Genesis9hautebenenstueck._vorauswahl(hp, ecken);
        vorbild.map?.updateMatrix?.();
        const e = vorbild.map?.matrix?.elements || [1, 0, 0, 0, 1, 0, 0, 0, 1];
        const aus = new Float32Array((stueck.length / 3) * 2), ab = new Float64Array(3);
        for (let i = 0, j = 0; i < stueck.length; i += 3, j += 2) {
            const t = Genesis9hautebenenstueck._stelle(stueck, normalen, i, hp, ecken, gitter, ab, vor);
            const a = ecken[3 * t], b = ecken[3 * t + 1], c = ecken[3 * t + 2], w1 = 1 - ab[1] - ab[2];
            const u = w1 * huv[2 * a] + ab[1] * huv[2 * b] + ab[2] * huv[2 * c];
            const v = w1 * huv[2 * a + 1] + ab[1] * huv[2 * b + 1] + ab[2] * huv[2 * c + 1];
            aus[j] = e[0] * u + e[3] * v + e[6];                       // wie Three: vMapUv = (mapTransform · (uv, 1)).xy
            aus[j + 1] = e[1] * u + e[4] * v + e[7];
        }
        return aus;
    }

    /** Suchgitter: Zelle (`ZELLE_M`) → die Dreiecke (Nummer in `ecken` / 3), deren Kasten sie berührt. */
    static _gitter(hp, ecken) {
        const Z = Genesis9hautebenenstueck.ZELLE_M, gitter = new Map();
        for (let t = 0; 3 * t < ecken.length; t++) {
            const o = [0, 1, 2].map(k => 3 * ecken[3 * t + k]);
            const von = [0, 1, 2].map(k => Math.floor(Math.min(hp[o[0] + k], hp[o[1] + k], hp[o[2] + k]) / Z));
            const bis = [0, 1, 2].map(k => Math.floor(Math.max(hp[o[0] + k], hp[o[1] + k], hp[o[2] + k]) / Z));
            for (let x = von[0]; x <= bis[0]; x++) for (let y = von[1]; y <= bis[1]; y++) for (let z = von[2]; z <= bis[2]; z++) {
                const s = `${x},${y},${z}`;
                if (!gitter.has(s)) gitter.set(s, []);
                gitter.get(s).push(t);
            }
        }
        return gitter;
    }

    /**
     * Für die Vorauswahl in `_stelle` je Dreieck: `kaesten` `[x0, y0, z0, x1, y1, z1]`, je Achse um 2 · `Strahldreieck.RAND` · Ausdehnung größer, und `kugeln`
     * `[Mitte xyz, Radius]` um den Schwerpunkt, Radius × (1 + 4 · RAND). Ein Strahltreffer darf so weit neben dem Dreieck liegen (Gewichte ab −RAND, zwei davon
     * negativ) — Kasten und Kugel enthalten also jeden Treffer und jeden nächsten Punkt; `mitten` (der Schwerpunkt liegt im Dreieck) gibt eine obere Schranke.
     */
    static _vorauswahl(hp, ecken) {
        const T = ecken.length / 3, kaesten = new Float64Array(6 * T), kugeln = new Float64Array(4 * T), r = Strahldreieck.RAND;
        for (let t = 0; t < T; t++) {
            const a = 3 * ecken[3 * t], b = 3 * ecken[3 * t + 1], c = 3 * ecken[3 * t + 2];
            for (let d = 0; d < 3; d++) {
                const lo = Math.min(hp[a + d], hp[b + d], hp[c + d]), hi = Math.max(hp[a + d], hp[b + d], hp[c + d]), mehr = 2 * r * (hi - lo) + 1e-9;
                kaesten[6 * t + d] = lo - mehr;
                kaesten[6 * t + 3 + d] = hi + mehr;
                kugeln[4 * t + d] = (hp[a + d] + hp[b + d] + hp[c + d]) / 3;
            }
            let rad = 0;
            for (const e of [a, b, c]) rad = Math.max(rad, Math.hypot(hp[e] - kugeln[4 * t], hp[e + 1] - kugeln[4 * t + 1], hp[e + 2] - kugeln[4 * t + 2]));
            kugeln[4 * t + 3] = rad * (1 + 4 * r) + 1e-9;
        }
        return { kaesten, kugeln, gitter: T ? new Hautstellengitter(kaesten, Genesis9hautebenenstueck.ZELLE_M) : null };
    }

    /** Abstand² vom Punkt zum Kasten des Dreiecks `t` (`_kaesten`) — keine Stelle des Dreiecks liegt näher. */
    static _kastenAbstand2(k, t, x, y, z) {
        const o = 6 * t;
        const dx = Math.max(k[o] - x, 0, x - k[o + 3]), dy = Math.max(k[o + 1] - y, 0, y - k[o + 4]), dz = Math.max(k[o + 2] - z, 0, z - k[o + 5]);
        return dx * dx + dy * dy + dz * dz;
    }

    /** Spielraum der Vorauswahl gegen Rundung: übersprungen wird erst, wenn der Kasten um diesen Faktor (Abstand²) weiter liegt. */
    static GENAU = 1 + 1e-9;

    /**
     * Das Hautdreieck unter dem Stückpunkt `i` (Nummer; Gewichte von b und c in `ab[1]`, `ab[2]`) — Kandidaten aus den Zellen ringsum (3 × 3 × 3), ohne Treffer alle.
     *
     * VORAUSWAHL ÜBER DIE KÄSTEN (21.11.2026, Ladezeit /foto-genesis/test/zauberer_kleidungsregeln_kopie_48/, Edgar: „ladezeit ewig! fixe"): Am Glied von „Daz
     * Anatomie Mann" (Zauberer) lagen 3.798 von 6.979 Stückpunkten mehr als eine Zelle vor der Haut — jeder prüfte alle 3.668 Hautdreiecke, zweimal (28 Mio.
     * Prüfungen, 5,1 s auf dem Hauptfaden, im Tab gemessen; im Profil der längste Block beim Laden, 6,2 s). Jetzt wird ein Dreieck übersprungen, dessen Kasten
     * (`_vorauswahl`) weiter liegt als der beste nächste Punkt bisher (höchstens der Abstand zur nächsten Dreiecksmitte), bzw. dessen Kugel die Strahlgerade verfehlt
     * oder jenseits der Strahlgrenze liegt: kein Punkt und kein Treffer des Dreiecks kann dann gewinnen. Fern der Haut (keine Zelle ringsum hat ein Dreieck) kommen
     * die Kandidaten aus `Hautstellengitter` (Würfel um die Schranke, Zellen entlang der Strahlstrecke), aufsteigend wie beim Durchlauf über alle. Reihenfolge und
     * Vergleiche bleiben, wie sie waren — dasselbe Dreieck, dieselben Gewichte (im Tab bitgleich gegen die alte Fassung, 13.958 Werte, mit Gegenproben).
     * @param vor  `_vorauswahl(hp, ecken)` oder null (dann ohne Vorauswahl)
     */
    static _stelle(stueck, normalen, i, hp, ecken, gitter, ab, vor = null) {
        const x = stueck[i], y = stueck[i + 1], z = stueck[i + 2], Z = Genesis9hautebenenstueck.ZELLE_M, G = Genesis9hautebenenstueck.GENAU;
        const kand = new Set(), cx = Math.floor(x / Z), cy = Math.floor(y / Z), cz = Math.floor(z / Z);
        for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
            for (const t of gitter.get(`${cx + dx},${cy + dy},${cz + dz}`) || []) kand.add(t);
        }
        const ka = vor?.kaesten, ku = vor?.kugeln, fern = !kand.size && vor?.gitter, hilf = new Float64Array(3);
        let liste = kand.size ? [...kand] : null, anzahl = liste ? liste.length : ecken.length / 3;
        let schranke = Infinity;                                       // Abstand² zur nächsten Dreiecksmitte: so weit liegt der nächste Punkt höchstens
        if (fern) {                                                    // fern der Haut: nur die Dreiecke in der Kugel, die den nächsten sicher enthält (`Hautstellengitter`)
            schranke = fern.schranke(x, y, z, (t) => {
                const a = 3 * ecken[3 * t], b = 3 * ecken[3 * t + 1], c = 3 * ecken[3 * t + 2];
                return Dreiecksabstand.naechster(x, y, z, hp[a], hp[a + 1], hp[a + 2], hp[b], hp[b + 1], hp[b + 2], hp[c], hp[c + 1], hp[c + 2], hilf)[0];
            });
            anzahl = fern.kugel(x, y, z, Math.sqrt(schranke * G + 1e-18) * G + 1e-12, ka);
            liste = fern.liste;
        } else if (ku) {
            for (let j = 0; j < anzahl; j++) {
                const o = 4 * (liste ? liste[j] : j), dx = ku[o] - x, dy = ku[o + 1] - y, dz = ku[o + 2] - z, d2 = dx * dx + dy * dy + dz * dz;
                if (d2 < schranke) schranke = d2;
            }
        }
        let bt = -1, beste = Infinity;
        for (let j = 0; j < anzahl; j++) {
            const t = liste ? liste[j] : j;
            if (ka && Genesis9hautebenenstueck._kastenAbstand2(ka, t, x, y, z) > (beste < schranke ? beste : schranke) * G + 1e-18) continue;
            const a = 3 * ecken[3 * t], b = 3 * ecken[3 * t + 1], c = 3 * ecken[3 * t + 2];
            Dreiecksabstand.naechster(x, y, z, hp[a], hp[a + 1], hp[a + 2], hp[b], hp[b + 1], hp[b + 2], hp[c], hp[c + 1], hp[c + 2], hilf);
            if (hilf[0] < beste) { beste = hilf[0]; bt = t; ab[1] = hilf[1]; ab[2] = hilf[2]; }
        }
        // Lieber der Strahl: der nächste Punkt einer Fläche aus Facetten hängt an Kanten und Ecken (Nachbarpunkte bekämen dieselbe Stelle), der Strahl geht stetig.
        const nx = normalen?.[i] || 0, ny = normalen?.[i + 1] || 0, nz = normalen?.[i + 2] || 0, nl = Math.hypot(nx, ny, nz);
        if (!(nl > 1e-9)) return bt;
        const mx = nx / nl, my = ny / nl, mz = nz / nl;
        let grenze = Genesis9hautebenenstueck.STRAHL_FAKTOR * Math.sqrt(beste) + 0.001;
        if (fern) anzahl = fern.strecke(x, y, z, mx, my, mz, grenze * G + 1e-12);     // nur die Zellen entlang der Strahlstrecke; `liste` ist dieselbe Ablage
        for (let j = 0; j < anzahl; j++) {
            const t = liste ? liste[j] : j;
            if (ku) {
                const o = 4 * t, dx = ku[o] - x, dy = ku[o + 1] - y, dz = ku[o + 2] - z, s = dx * mx + dy * my + dz * mz, rad = ku[o + 3];
                if (dx * dx + dy * dy + dz * dz - s * s > rad * rad * G + 1e-14) continue;    // die Gerade verfehlt die Kugel
                if (Math.abs(s) - rad > grenze * G + 1e-12) continue;                         // jeder Treffer läge jenseits der Grenze
            }
            const a = 3 * ecken[3 * t], b = 3 * ecken[3 * t + 1], c = 3 * ecken[3 * t + 2];
            if (Strahldreieck.trifft(x, y, z, mx, my, mz, hp[a], hp[a + 1], hp[a + 2], hp[b], hp[b + 1], hp[b + 2], hp[c], hp[c + 1], hp[c + 2], hilf)
                && hilf[0] < grenze) { grenze = hilf[0]; bt = t; ab[1] = hilf[1]; ab[2] = hilf[2]; }
        }
        return bt;
    }
}
