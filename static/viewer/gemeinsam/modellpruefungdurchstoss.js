import * as THREE from 'three';

/**
 * Modellpruefungdurchstoss — sticht der Körper durch die Kleidung? Klasse des Modell Checks (`Modellpruefung`, 02.11.2026, Sitzung roomguest-f0; Edgar: „sind diese
 * Testmethoden für die Figur auch in dem generischen Code … Modell Check? wenn nicht, dann tu das“). Anlass Foto-Genesis, Probejob EdgarTrip--versatz: die Knöchelhaut lag
 * außerhalb des Sockenbunds, im Bild ein Hautring in der Socke (Socken „falsch“ 2.009 Pixel, Zeile 1 852; `KoerperKI_Fotos/fotoauswendig.py`, DICKE_M).
 *
 * Je Körperpunkt zwei Strahlen längs seiner Normale (`Modellpruefung.normalen`, nach außen) gegen jedes Kleidungsnetz: trifft der Strahl nach innen höchstens AUSSEN_M
 * tief Stoff (der Stoff liegt unter der Haut) und der Strahl nach außen bis OBEN_M keinen, liegt der Punkt außerhalb des Stücks — sichtbar, wenn mehr als TIEFE_M.
 * Doppellagiger Stoff (Futter) zählt so nicht, und Haut neben dem Saum auch nicht (dort liegt innen kein Stoff). Gesucht über ein Gitter der Dreiecke (Zelle ZELLE_M,
 * die Zellen längs der Strecke), Strahl gegen Dreieck nach Möller/Trumbore (beides aus dem Gedächtnis, nicht gegen den Text geprüft).
 *
 *     const d = Modellpruefungdurchstoss.pruefen(koerper, lage, netze, nrm);
 *     // lage, nrm: Float32Array (3 n) Welt (`Modellpruefung.normalen`); netze: die sichtbaren Netze (Kleidung sucht `kleider`)
 *     // → {geprueft, stuecke: [{name, zahl, tief_mm, punkte: [Körperpunkt …]}], zu: [Stücke über PUNKTE_MAX], punkte: [alle Körperpunkte mit Befund]}
 * Grenze PUNKTE_MAX GESETZT wie `Modellpruefung.HAND_PUNKTE_MAX`, noch an keinem Daz-Modell geeicht; Edgar Foto-Genesis (Charakter, 02.11.2026): Socken 178 Punkte.
 */
export class Modellpruefungdurchstoss {

    static ZELLE_M = 0.015;                 // Edgar Foto-Genesis (104.480 Körperpunkte, 4 Stücke): 30 mm 1,86 s, 20 mm 0,89 s, 15 mm 0,65 s, gleicher Befund (02.11.2026)
    static AUSSEN_M = 0.015;
    static OBEN_M = 0.03;
    static TIEFE_M = 0.001;
    static PUNKTE_MAX = 20;

    /** Kleidungsnetze unter den sichtbaren Netzen: Katalogstücke der Art „kleidung“, Eigenkleider, gebackene Eigenschalen, Eigenröcke — ohne Haar und Requisiten. */
    static kleider(netze) {
        return netze.filter((o) => o.userData?.art === 'kleidung' || o.userData?.eigenkleid || o.userData?.eigenGebacken || /^eigenrock_/.test(o.name || ''));
    }

    static pruefen(koerper, lage, netze, nrm) {
        const M = Modellpruefungdurchstoss, stuecke = [], n = lage.length / 3, kleider = M.kleider(netze.filter((o) => o !== koerper));
        for (const o of kleider) {
            const { pos, idx } = M.weltnetz(o), gitter = M.gitter(pos, idx), kiste = new THREE.Box3().setFromArray(pos).expandByScalar(M.OBEN_M);
            const punkte = [];
            let tief = 0;
            const p = new THREE.Vector3();
            for (let i = 0; i < n; i++) {
                if (!kiste.containsPoint(p.set(lage[3 * i], lage[3 * i + 1], lage[3 * i + 2]))) continue;
                const innen = M.innen(p, nrm, i, pos, idx, gitter);
                if (innen > M.TIEFE_M) { punkte.push(i); tief = Math.max(tief, innen); }
            }
            if (punkte.length) stuecke.push({ name: o.name || o.uuid, zahl: punkte.length, tief_mm: Math.round(1000 * tief), punkte });
        }
        stuecke.sort((a, b) => b.zahl - a.zahl);
        return { geprueft: kleider.length, stuecke, zu: stuecke.filter((s) => s.zahl > M.PUNKTE_MAX), punkte: [...new Set(stuecke.flatMap((s) => s.punkte))] };
    }

    /** Tiefe des Stoffs unter dem Punkt (m), 0 wenn darüber Stoff liegt oder darunter keiner. Nur die Zellen, durch die die Strecke p − AUSSEN_M·n … p + OBEN_M·n läuft
     *  (Amanatides/Woo; mit allen 27 Nachbarzellen von 30 mm 6,0 s für Edgar Foto-Genesis, gleicher Befund). */
    static innen(p, nrm, i, pos, idx, gitter) {
        const M = Modellpruefungdurchstoss, z = M.ZELLE_M, d = [nrm[3 * i], nrm[3 * i + 1], nrm[3 * i + 2]], L = M.AUSSEN_M + M.OBEN_M;
        const s = [p.x - M.AUSSEN_M * d[0], p.y - M.AUSSEN_M * d[1], p.z - M.AUSSEN_M * d[2]], c = s.map((w) => Math.floor(w / z));
        const schritt = d.map((w) => (w > 0 ? 1 : -1)), tdelta = d.map((w) => (w ? Math.abs(z / w) : Infinity));
        const tmax = d.map((w, a) => (w ? ((c[a] + (w > 0 ? 1 : 0)) * z - s[a]) / w : Infinity));
        let innen = Infinity;
        for (;;) {
            for (const t of gitter.get(M.schluessel(c[0], c[1], c[2])) || []) {
                const h = M.strahl(p, d[0], d[1], d[2], pos, idx, t);
                if (h > 0 && h < M.OBEN_M) return 0;
                if (h < 0 && -h < M.AUSSEN_M) innen = Math.min(innen, -h);
            }
            const a = tmax[0] < tmax[1] ? (tmax[0] < tmax[2] ? 0 : 2) : (tmax[1] < tmax[2] ? 1 : 2);
            if (tmax[a] > L) break;
            c[a] += schritt[a];
            tmax[a] += tdelta[a];
        }
        return innen < Infinity ? innen : 0;
    }

    /** Abstand längs der Geraden p + h·d bis zum Dreieck t (negativ = nach innen), NaN ohne Treffer. */
    static strahl(p, dx, dy, dz, pos, idx, t) {
        const a = 3 * idx[3 * t], b = 3 * idx[3 * t + 1], c = 3 * idx[3 * t + 2];
        const e1x = pos[b] - pos[a], e1y = pos[b + 1] - pos[a + 1], e1z = pos[b + 2] - pos[a + 2];
        const e2x = pos[c] - pos[a], e2y = pos[c + 1] - pos[a + 1], e2z = pos[c + 2] - pos[a + 2];
        const px = dy * e2z - dz * e2y, py = dz * e2x - dx * e2z, pz = dx * e2y - dy * e2x;
        const det = e1x * px + e1y * py + e1z * pz;
        if (Math.abs(det) < 1e-12) return NaN;
        const tx = p.x - pos[a], ty = p.y - pos[a + 1], tz = p.z - pos[a + 2];
        const u = (tx * px + ty * py + tz * pz) / det;
        if (u < 0 || u > 1) return NaN;
        const qx = ty * e1z - tz * e1y, qy = tz * e1x - tx * e1z, qz = tx * e1y - ty * e1x;
        const v = (dx * qx + dy * qy + dz * qz) / det;
        if (v < 0 || u + v > 1) return NaN;
        return (e2x * qx + e2y * qy + e2z * qz) / det;
    }

    /** Gestellte Punkte (Welt) und Dreiecke eines Netzes. */
    static weltnetz(o) {
        const g = o.geometry, m = g.attributes.position.count, pos = new Float32Array(3 * m), q = new THREE.Vector3();
        for (let i = 0; i < m; i++) { o.getVertexPosition(i, q).applyMatrix4(o.matrixWorld); pos.set([q.x, q.y, q.z], 3 * i); }
        return { pos, idx: g.index ? g.index.array : Uint32Array.from({ length: m }, (_, i) => i) };
    }

    /** Zelle → Dreiecke, deren Kiste die Zelle berührt. */
    static gitter(pos, idx) {
        const M = Modellpruefungdurchstoss, z = M.ZELLE_M, aus = new Map();
        for (let t = 0; t < idx.length / 3; t++) {
            const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
            for (let k = 0; k < 3; k++) for (let a = 0; a < 3; a++) { const w = pos[3 * idx[3 * t + k] + a]; lo[a] = Math.min(lo[a], w); hi[a] = Math.max(hi[a], w); }
            for (let x = Math.floor(lo[0] / z); x <= Math.floor(hi[0] / z); x++) for (let y = Math.floor(lo[1] / z); y <= Math.floor(hi[1] / z); y++) {
                for (let w = Math.floor(lo[2] / z); w <= Math.floor(hi[2] / z); w++) {
                    const s = M.schluessel(x, y, w);
                    if (!aus.has(s)) aus.set(s, []);
                    aus.get(s).push(t);
                }
            }
        }
        return aus;
    }

    static schluessel(x, y, z) {
        return ((x + 512) * 1024 + (y + 512)) * 1024 + (z + 512);
    }
}
