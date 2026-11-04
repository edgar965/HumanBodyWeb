import * as THREE from 'three';
import { Gezeichneterpunkt } from './gezeichneterpunkt.js';

/**
 * Modellpruefungdeckung — wo am Körper Stoff sein muss: die Punkte der Klasse „deckung“ des Modell Checks (`Modellpruefung`; aus `modellpruefung.js` abgeteilt
 * 02.11.2026 abends). Rot im Deckungsbild wird nur, was hier 1 ist und frei liegt.
 *   muss                Körperpunkte: Eigen-Schale Kante ≥ 3 cm im Stoff und anliegend (≤ 12 mm); weggeschnittene Armhaut nahe der Wurzel, die unter dem Schultergelenk
 *                       und hinter der Ebene quer zum Oberarm liegt (gestreckte Achsel); Kleid bis 6 cm unter der Taillennaht; Rumpf und Beine über dem Saum eines
 *                       Eigenrocks in der Nähe.
 *   anatomieUnterStoff  Punkte des Daz-Anatomie-Stücks, wo Stoff sein muss oder Kleidung näher als ANATOMIE_STOFF_M liegt. Bis 02.11.2026 abends war das Stück immer
 *                       rot und ohne seinen Hauteinzug gezeichnet (`Gezeichneterpunkt`) — an Damira mit Hose stach es so in jedem Prüfbild durch, an einer nackten
 *                       Figur war es rot, ohne dass Stoff hingehört (Edgar: „bei Modell Check wird die Scham rot markiert, obwohl sie OK ist“).
 */
export class Modellpruefungdeckung {

    static MUSS_INNEN_M = 0.03;
    static ANLIEGEN_M = 0.012;
    static ACHSEL_ANTEIL = 0.15;
    static ACHSEL_UNTER_M = 0.03;
    static ACHSEL_HINTER_M = 0.03;
    static ROCK_RADIUS_M = 0.12;
    static ROCK_SAUM_M = 0.04;
    static ROCK_BUND_M = 0.03;
    static ANATOMIE_STOFF_M = 0.03;

    /**
     * Je Körperpunkt 1, wo Stoff sein muss (siehe Kopf). `objekt`: Lage im Raum des Körpers (wie die Gelenke), `lage`: Welt (wie die Rocknetze); `glied`: je Punkt 1
     * an Arm, Hand, Fuß und Kopf (zählt unter dem Rock nicht); `netze`: die sichtbaren Netze der Figur (Eigenröcke).
     */
    static muss(gebacken, objekt, lage, glied, netze) {
        const D = Modellpruefungdeckung, n = lage.length / 3, muss = new Uint8Array(n);
        const kk = gebacken[0]?.userData.koord, kette = (i) => (kk ? Math.floor(kk[4 * i] + 0.5) : 0);
        for (const b of gebacken) {
            const { stoffseite: f, versatz, laengen: L, schulter } = b.userData, saumX = b.userData.saum[0], art = b.userData.eigenGebacken;
            for (let i = 0; i < n; i++) {
                if (f[i] >= D.MUSS_INNEN_M && versatz[i] < D.ANLIEGEN_M) muss[i] = 1;
                if (art === 'kleid' && kette(i) === 1) { const unter = (kk[4 * i + 2] - saumX) * L[0]; if (unter >= 0 && unter <= 0.06) muss[i] = 1; }
            }
            if (art !== 'oberteil' && art !== 'kleid') continue;
            for (let i = 0; i < n; i++) {
                const k = kette(i);
                if ((k !== 2 && k !== 3) || f[i] >= 0 || kk[4 * i + 1] >= D.ACHSEL_ANTEIL) continue;
                const x = objekt[3 * i], y = objekt[3 * i + 1], z = objekt[3 * i + 2], s = schulter[x >= 0 ? 'l' : 'r'];
                if (!s || y > s.a.y - D.ACHSEL_UNTER_M) continue;
                if ((x - s.a.x) * s.achse.x + (y - s.a.y) * s.achse.y + (z - s.a.z) * s.achse.z < -D.ACHSEL_HINTER_M) muss[i] = 1;
            }
        }
        const roecke = netze.filter((o) => /^eigenrock_/.test(o.name || ''));
        if (!roecke.length) return muss;
        const rp = [], q = new THREE.Vector3(), R = D.ROCK_RADIUS_M;
        for (const r of roecke) {
            const m = r.geometry.attributes.position.count, schritt = Math.max(1, Math.floor(m / 6000));
            for (let i = 0; i < m; i += schritt) { r.getVertexPosition(i, q).applyMatrix4(r.matrixWorld); rp.push(q.x, q.y, q.z); }
        }
        const zellen = new Map(), zelle = (x, z) => `${Math.floor(x / R)},${Math.floor(z / R)}`;
        for (let j = 0; j < rp.length; j += 3) { const k = zelle(rp[j], rp[j + 2]); if (!zellen.has(k)) zellen.set(k, []); zellen.get(k).push(j); }
        for (let i = 0; i < n; i++) {
            if (glied[i]) continue;
            if (kk && ![1, 4, 5].includes(kette(i))) continue;
            const x = lage[3 * i], y = lage[3 * i + 1], z = lage[3 * i + 2], cx = Math.floor(x / R), cz = Math.floor(z / R);
            let unten = Infinity, oben = -Infinity;
            for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) {
                for (const j of zellen.get(`${cx + a},${cz + b}`) || []) {
                    const dx = rp[j] - x, dz = rp[j + 2] - z;
                    if (dx * dx + dz * dz < R * R) { unten = Math.min(unten, rp[j + 1]); oben = Math.max(oben, rp[j + 1]); }
                }
            }
            if (unten < Infinity && y > unten + D.ROCK_SAUM_M && y < oben - D.ROCK_BUND_M) muss[i] = 1;
        }
        return muss;
    }

    /**
     * Je Anatomie-Netz `{lage: Float32Array 3m (Welt, wie gezeichnet — mit Einzug), unter: Uint8Array m, zahl}` — `unter` = 1, wo ein Körperpunkt mit `muss` oder ein Punkt von `kleider`
     * (Welt) näher als ANATOMIE_STOFF_M liegt. Nackt bleibt alles 0: dort ist die Scham kein Befund.
     */
    static anatomieUnterStoff(anatomie, lage, muss, kleider) {
        if (!anatomie.length) return [];
        const r = Modellpruefungdeckung.ANATOMIE_STOFF_M, q = new THREE.Vector3(), kiste = new THREE.Box3();
        const stuecke = anatomie.map((o) => {
            const m = o.geometry.attributes.position.count, pos = new Float32Array(3 * m);
            for (let i = 0; i < m; i++) { Gezeichneterpunkt.lage(o, i, q).applyMatrix4(o.matrixWorld); pos.set([q.x, q.y, q.z], 3 * i); kiste.expandByPoint(q); }
            return { lage: pos, unter: new Uint8Array(m), zahl: 0 };
        });
        kiste.expandByScalar(r);
        const zellen = new Map(), schl = (x, y, z) => `${Math.floor(x / r)},${Math.floor(y / r)},${Math.floor(z / r)}`;
        const rein = (x, y, z) => {
            if (x < kiste.min.x || y < kiste.min.y || z < kiste.min.z || x > kiste.max.x || y > kiste.max.y || z > kiste.max.z) return;
            const k = schl(x, y, z);
            if (!zellen.has(k)) zellen.set(k, []);
            zellen.get(k).push(x, y, z);
        };
        for (let i = 0; i < muss.length; i++) if (muss[i]) rein(lage[3 * i], lage[3 * i + 1], lage[3 * i + 2]);
        for (const o of kleider) {
            const m = o.geometry.attributes.position.count;
            for (let i = 0; i < m; i++) { Gezeichneterpunkt.lage(o, i, q).applyMatrix4(o.matrixWorld); rein(q.x, q.y, q.z); }
        }
        if (!zellen.size) return stuecke;
        for (const s of stuecke) {
            for (let i = 0; i < s.unter.length; i++) {
                const x = s.lage[3 * i], y = s.lage[3 * i + 1], z = s.lage[3 * i + 2], cx = Math.floor(x / r), cy = Math.floor(y / r), cz = Math.floor(z / r);
                suche: for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
                    const p = zellen.get(`${cx + a},${cy + b},${cz + c}`);
                    if (!p) continue;
                    for (let j = 0; j < p.length; j += 3) {
                        if ((p[j] - x) ** 2 + (p[j + 1] - y) ** 2 + (p[j + 2] - z) ** 2 < r * r) { s.unter[i] = 1; s.zahl++; break suche; }
                    }
                }
            }
        }
        return stuecke;
    }
}
