/**
 * Hautmaskeersatz — die Haut vor und auf einem ERSATZSTÜCK (die Scham aus einer .blend, 09.10.2026).
 *
 * BEFUND (Edgar: „die hat im moment zwei mal Geschlechtsorgane", dann in der Szene gemessen): Das Stück liegt zum großen
 * Teil 5–25 mm HINTER der Genesis-Fläche (die Figur überbrückt die Furche) und war deshalb komplett verdeckt — die
 * gezeigte Furche war die Körperhaut. Die Maske eines Stoffs trifft den Stoff mit einem Strahl entlang der Körpernormale,
 * und zwar nur die Dreiecke um den NÄCHSTEN Stoffpunkt (`hautmaske.js`); bei einer Haut, die ein Stück überbrückt, liegt der
 * nächste Stoffpunkt nicht dort, wo der Strahl landet. Gemessen am Stück „cute girl Scham": 111 verdeckte Körperpunkte mit
 * Strahl, auch bei Tiefen von 45, 60 und 90 mm unverändert — die Tiefe war nicht das Problem, die Trefferliste war es.
 *
 * Hier gilt die einfachere Frage: Liegt an der Normale des Körperpunkts — von `tiefe` hinein bis `abstand` darüber, in einem
 * Zylinder vom Radius `RADIUS_M` — ein PUNKT des Stücks? Dann fällt die Haut dort weg. Ohne Dreiecke, ohne Nachbarschaft,
 * und ein Ersatzstück ist dicht genug (2 mm), dass ein Zylinder von 4 mm keine Lücke lässt. Reichweite: eine Gitterzelle
 * (`Hautmaskegeometrie.ZELLE_M`, 30 mm) um den Körperpunkt.
 */
import { Hautmaskegeometrie as G } from './hautmaskegeometrie.js';

export class Hautmaskeersatz {

    /** Radius (m) des Zylinders um die Körpernormale — etwa ein Punktabstand der Stufe 1 (4 mm). */
    static RADIUS_M = 0.004;
    /** Ringe Haut (Dreiecksschichten), die am Rand des Stücks stehen bleiben. */
    static RINGE = 2;

    /**
     * Setzt `maske[i] = 1` für jeden Körperpunkt, an dessen Normale ein Punkt des Stücks liegt. `davor`: die Maske VOR
     * diesem Stück (Kopie) — was dieses Stück (mit dem Strahltest davor) neu verdeckt, kommt in `ersatz` (Körperpunkte,
     * deren Haut ganz entfällt statt als Saumband versenkt zu bleiben, `hautverdeckung.js`).
     */
    static maskieren(basis, maske, stoff, abstand, tiefe, davor, ersatz) {
        const { koerper, normalen } = basis;
        const P = stoff.punkte, h = G.ZELLE_M;
        const gitter = G.punktgitter(P, h);
        const huelle = G.huelle(P, Math.max(abstand, tiefe));
        const r2 = Hautmaskeersatz.RADIUS_M ** 2;
        for (let i = 0; i < maske.length; i++) {
            if (maske[i]) continue;
            const px = koerper[3 * i], py = koerper[3 * i + 1], pz = koerper[3 * i + 2];
            if (px < huelle[0] || px > huelle[3] || py < huelle[1] || py > huelle[4]
                || pz < huelle[2] || pz > huelle[5]) continue;
            const nx = normalen[3 * i], ny = normalen[3 * i + 1], nz = normalen[3 * i + 2];
            if (Hautmaskeersatz._trifft(P, gitter, h, [px, py, pz], [nx, ny, nz], abstand, tiefe, r2)) maske[i] = 1;
        }
        if (ersatz) for (let i = 0; i < maske.length; i++) if (maske[i] && !davor[i]) ersatz[i] = 1;
    }

    /**
     * Die Körperpunkte, deren Haut ganz entfällt: Ersatz-Punkte ohne Dreieck mit einer gezeichneten Ecke. Ein Ring bleibt
     * stehen (eingezogen wie das Saumband) — der Stückrand ist gezackt, und bis dorthin entfernt klafft ein Loch
     * (gesehen 09.10.2026: dunkle Zacken oben und an den Seiten der Scham).
     */
    static innen(ersatz, maske, dreiecke) {
        const innen = Uint8Array.from(ersatz);
        let gezeichnet = maske;
        for (let r = 0; r < Hautmaskeersatz.RINGE; r++) {
            const neu = Uint8Array.from(innen);
            for (let k = 0; k + 2 < dreiecke.length; k += 3) {
                const a = dreiecke[k], b = dreiecke[k + 1], c = dreiecke[k + 2];
                if (r === 0 ? (gezeichnet[a] && gezeichnet[b] && gezeichnet[c]) : (innen[a] && innen[b] && innen[c])) continue;
                neu[a] = 0; neu[b] = 0; neu[c] = 0;
            }
            innen.set(neu);
        }
        return innen;
    }

    /** Liegt in den 27 Zellen um `p` ein Stückpunkt im Zylinder um die Normale `n`? */
    static _trifft(P, gitter, h, p, n, abstand, tiefe, r2) {
        const ci = Math.floor(p[0] / h), cj = Math.floor(p[1] / h), ck = Math.floor(p[2] / h);
        for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
            const liste = gitter.get(G.zelle(ci + a, cj + b, ck + c));
            if (!liste) continue;
            for (let l = 0; l < liste.length; l++) {
                const j = liste[l];
                const vx = P[3 * j] - p[0], vy = P[3 * j + 1] - p[1], vz = P[3 * j + 2] - p[2];
                const t = vx * n[0] + vy * n[1] + vz * n[2];
                if (t < -tiefe || t > abstand) continue;
                if (vx * vx + vy * vy + vz * vz - t * t <= r2) return true;
            }
        }
        return false;
    }
}
