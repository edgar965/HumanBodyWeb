import { Hautmaskegeometrie as G } from './hautmaskegeometrie.js';

/**
 * Saumschnitt — die Haut endet an der Stoffkante, nicht ein Zahn darunter.
 *
 * BEFUND (Edgar, 13.09.2026, mit Bild vom Bund der Hose von oben: „der
 * Innensaum der Kleider ist eckig, der soll so sein wie die Außenhaut"):
 * Entlang des Bundes standen schwarze Zacken, 5 mm hoch, ein Zahn je
 * Hautdreieck. Nicht die Hose — ihr Bundring ist glatt (z-Abweichung vom
 * Nachbarmittel p90 0,25 mm, gemessen an `hose_rig.json`) —, sondern der
 * `Hauteinzug`: Die verdeckte Ecke jedes Randdreiecks der Haut wanderte 1 cm
 * nach innen. Das Dreieck kippt damit in den Körper; von oben zeigt es der
 * Kamera seine Rückseite (Haut ist einseitig), und durch das Loch sieht man
 * die Innenseite der Hose. Mit dem Einzug auf null war der Saum glatt.
 *
 * DER WEG: Eine verdeckte Ecke, die zu einem gezeichneten Randdreieck gehört
 * und nah an einer Stoffkante liegt, wandert nicht nach innen, sondern
 * ENTLANG DER HAUT unter die Kante — auf den nächsten Kantenpunkt projiziert
 * in die Tangentialebene, dazu `UNTERKANTE_M` nach innen. Das Dreieck bleibt
 * in der Hautfläche und endet, wo der Stoff anfängt; seine Kante folgt dem
 * Bundring, der glatt ist. Hinter der Kante bleibt seit dem Abend des
 * 13.09.2026 ein Band versenkter Haut (`Saumband`) — der Schnitt legt nur
 * die erste Reihe unter die Kante, damit die Haut genau am Stoff endet.
 *
 * Nur nahe Kanten (`SCHNAPP_M`): An einer anliegenden Kante reicht die Maske
 * bis zum Rand, die verdeckten Ecken liegen eine Hautkante (4–6 mm) davor.
 * An einer LOCKEREN Kante bleiben zwei Stoffringe Haut frei (`Hautmaske`),
 * die Maskengrenze liegt dort 2 cm hinter dem Rand — und der alte Einzug
 * nach innen bleibt richtig, der Stoff verdeckt ihn.
 *
 * Ohne Three.js, damit `test_js_saumschnitt` es in Node prüft.
 */
export class Saumschnitt {

    /**
     * Näher als das an einer Stoffkante: an die Kante statt nach innen.
     * 15 mm: Am Bauch (Hautkanten bis 8 mm, Bund 5–10 mm über der Haut)
     * lagen 37 von 348 Randecken 10–16 mm von der Kante — jede ein Zahn.
     * Lockere Kanten halten zwei Stoffringe (16–22 mm) Abstand zur Maske.
     */
    static SCHNAPP_M = 0.015;
    /** So weit unter die Kante (entlang der Normale nach innen). */
    static UNTERKANTE_M = 0.001;

    /**
     * Die offenen Kanten aller Stücke als Strecken, hintereinander
     * (ax ay az bx by bz je Kante). Strecken, nicht Punkte: Die Bundpunkte
     * liegen 11 mm auseinander — an den nächsten PUNKT gezogen sammelten
     * sich die Hautecken dort in Fächern, und wer zwischen zwei Punkten
     * lag, war „zu weit weg" (48 von 348 Randecken über 10 mm, obwohl die
     * Kante 6 mm entfernt lief).
     * @param stoffe  [{punkte, dreiecke}] in der Lage des Körpers
     */
    static kanten(stoffe) {
        const teile = [];
        for (const s of stoffe || []) {
            const P = s?.punkte, T = s?.dreiecke;
            if (!P?.length || !T?.length) continue;
            const n = P.length / 3;
            const zaehler = new Map();
            for (let k = 0; k + 2 < T.length; k += 3) {
                for (const [a, b] of [[T[k], T[k + 1]], [T[k + 1], T[k + 2]], [T[k + 2], T[k]]]) {
                    const key = a < b ? a * n + b : b * n + a;
                    zaehler.set(key, (zaehler.get(key) || 0) + 1);
                }
            }
            for (const [key, c] of zaehler) {
                if (c !== 1) continue;
                const a = Math.floor(key / n), b = key % n;
                teile.push(P[3 * a], P[3 * a + 1], P[3 * a + 2], P[3 * b], P[3 * b + 1], P[3 * b + 2]);
            }
        }
        return Float32Array.from(teile);
    }

    /** Die Mitten der Strecken (xyz je Strecke) — für das Suchgitter. */
    static mitten(kanten) {
        const aus = new Float32Array(kanten.length / 2);
        for (let k = 0; k < kanten.length / 6; k++) {
            aus[3 * k] = 0.5 * (kanten[6 * k] + kanten[6 * k + 3]);
            aus[3 * k + 1] = 0.5 * (kanten[6 * k + 1] + kanten[6 * k + 4]);
            aus[3 * k + 2] = 0.5 * (kanten[6 * k + 2] + kanten[6 * k + 5]);
        }
        return aus;
    }

    /** Je Punkt 1, wenn er verdeckt ist UND an einem gezeichneten Dreieck hängt. */
    static randecken(maske, dreiecke) {
        const aus = new Uint8Array(maske.length);
        for (let k = 0; k + 2 < dreiecke.length; k += 3) {
            const a = dreiecke[k], b = dreiecke[k + 1], c = dreiecke[k + 2];
            const m = maske[a] + maske[b] + maske[c];
            if (m === 0 || m === 3) continue;
            if (maske[a]) aus[a] = 1;
            if (maske[b]) aus[b] = 1;
            if (maske[c]) aus[c] = 1;
        }
        return aus;
    }

    /**
     * Der Einzug einer verdeckten Randecke: Verschiebung (xyz) unter den
     * nächsten Punkt der nächsten Stoffkante, oder null, wenn keine Kante
     * binnen `SCHNAPP_M` liegt.
     *
     * @param px,py,pz   der Punkt
     * @param nx,ny,nz   seine Normale nach außen
     * @param kanten     Strecken, `Saumschnitt.kanten`
     * @param gitter     `Hautmaskegeometrie.punktgitter(mitten(kanten), ZELLE_M)`
     */
    static verschiebung(px, py, pz, nx, ny, nz, kanten, gitter) {
        const q = Saumschnitt.naechsterKantenpunkt(px, py, pz, kanten, gitter);
        if (!q) return null;
        let dx = q[0] - px, dy = q[1] - py, dz = q[2] - pz;
        // In die Tangentialebene: der Anteil entlang der Normale fällt weg.
        const entlang = dx * nx + dy * ny + dz * nz;
        dx -= entlang * nx; dy -= entlang * ny; dz -= entlang * nz;
        const u = Saumschnitt.UNTERKANTE_M;
        return [dx - u * nx, dy - u * ny, dz - u * nz];
    }

    /** Der nächste Punkt auf einer Kantenstrecke binnen `SCHNAPP_M` — oder null. */
    static naechsterKantenpunkt(px, py, pz, kanten, gitter) {
        const h = Saumschnitt.ZELLE_M;
        const ci = Math.floor(px / h), cj = Math.floor(py / h), ck = Math.floor(pz / h);
        let best = Saumschnitt.SCHNAPP_M * Saumschnitt.SCHNAPP_M, treffer = null;
        for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
            const L = gitter.get(G.zelle(ci + a, cj + b, ck + c));
            if (!L) continue;
            for (let l = 0; l < L.length; l++) {
                const k = 6 * L[l];
                const ax = kanten[k], ay = kanten[k + 1], az = kanten[k + 2];
                const ex = kanten[k + 3] - ax, ey = kanten[k + 4] - ay, ez = kanten[k + 5] - az;
                const e2 = ex * ex + ey * ey + ez * ez;
                let t = e2 > 0 ? ((px - ax) * ex + (py - ay) * ey + (pz - az) * ez) / e2 : 0;
                t = t < 0 ? 0 : (t > 1 ? 1 : t);
                const qx = ax + t * ex, qy = ay + t * ey, qz = az + t * ez;
                const d2 = (qx - px) * (qx - px) + (qy - py) * (qy - py) + (qz - pz) * (qz - pz);
                if (d2 < best) { best = d2; treffer = [qx, qy, qz]; }
            }
        }
        return treffer;
    }

    /** Zellgröße des Kantengitters: Streckenmitten, Suche eine Zelle weit —
     *  reicht für `SCHNAPP_M` plus eine halbe Stoffkante (bis 2,5 cm). */
    static ZELLE_M = 0.025;
}
