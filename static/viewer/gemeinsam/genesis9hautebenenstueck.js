import { Anatomiehaut } from './anatomiehaut.js';
import { Anatomielage } from './anatomielage.js';
import { Dreiecksabstand } from './dreiecksabstand.js';
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
        const gitter = Genesis9hautebenenstueck._gitter(hp, ecken);
        vorbild.map?.updateMatrix?.();
        const e = vorbild.map?.matrix?.elements || [1, 0, 0, 0, 1, 0, 0, 0, 1];
        const aus = new Float32Array((stueck.length / 3) * 2), ab = new Float64Array(3);
        for (let i = 0, j = 0; i < stueck.length; i += 3, j += 2) {
            const t = Genesis9hautebenenstueck._stelle(stueck, normalen, i, hp, ecken, gitter, ab);
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

    /** Das Hautdreieck unter dem Stückpunkt `i` (Nummer; Gewichte von b und c in `ab[1]`, `ab[2]`) — Kandidaten aus den Zellen ringsum (3 × 3 × 3), ohne Treffer alle. */
    static _stelle(stueck, normalen, i, hp, ecken, gitter, ab) {
        const x = stueck[i], y = stueck[i + 1], z = stueck[i + 2], Z = Genesis9hautebenenstueck.ZELLE_M;
        const kand = new Set(), cx = Math.floor(x / Z), cy = Math.floor(y / Z), cz = Math.floor(z / Z);
        for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
            for (const t of gitter.get(`${cx + dx},${cy + dy},${cz + dz}`) || []) kand.add(t);
        }
        const liste = kand.size ? [...kand] : Array.from({ length: ecken.length / 3 }, (_, t) => t), hilf = new Float64Array(3);
        const ecke = (t, k) => 3 * ecken[3 * t + k];
        let bt = -1, beste = Infinity;
        for (const t of liste) {
            const a = ecke(t, 0), b = ecke(t, 1), c = ecke(t, 2);
            Dreiecksabstand.naechster(x, y, z, hp[a], hp[a + 1], hp[a + 2], hp[b], hp[b + 1], hp[b + 2], hp[c], hp[c + 1], hp[c + 2], hilf);
            if (hilf[0] < beste) { beste = hilf[0]; bt = t; ab[1] = hilf[1]; ab[2] = hilf[2]; }
        }
        // Lieber der Strahl: der nächste Punkt einer Fläche aus Facetten hängt an Kanten und Ecken (Nachbarpunkte bekämen dieselbe Stelle), der Strahl geht stetig.
        const nx = normalen?.[i] || 0, ny = normalen?.[i + 1] || 0, nz = normalen?.[i + 2] || 0, nl = Math.hypot(nx, ny, nz);
        if (!(nl > 1e-9)) return bt;
        let grenze = Genesis9hautebenenstueck.STRAHL_FAKTOR * Math.sqrt(beste) + 0.001;
        for (const t of liste) {
            const a = ecke(t, 0), b = ecke(t, 1), c = ecke(t, 2);
            if (Strahldreieck.trifft(x, y, z, nx / nl, ny / nl, nz / nl, hp[a], hp[a + 1], hp[a + 2], hp[b], hp[b + 1], hp[b + 2], hp[c], hp[c + 1], hp[c + 2], hilf)
                && hilf[0] < grenze) { grenze = hilf[0]; bt = t; ab[1] = hilf[1]; ab[2] = hilf[2]; }
        }
        return bt;
    }
}
