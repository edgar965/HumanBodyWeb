import { Dazachsen } from './dazachsen.js';

/**
 * Genesis9drehknochen — Daz' Twist-Knochen folgen ihrem Glied per Formel.
 *
 * Edgar (20.09.2026 nachts, Dance1_smplx Bild 95): „der Arm ist kaputt".
 * Der Retarget traf Richtung und Beugung des Arms auf 0,1 Grad — aber
 * SMPL-X dreht den Unterarm dort um 110–140 Grad um seine Achse, und die
 * ganze Verdrehung sass am Ellbogengelenk: Bonbonpapier zwischen Oberarm-
 * und Unterarmhaut. In Daz nehmen die Twist-Knochen (Kinder des Glieds)
 * einen Teil am Gelenk zurück (`Genesis9/drehknochen.py`):
 *
 *     l_forearmtwist1?rotation/x = l_forearm?rotation/x × −0,83
 *     l_forearmtwist2?rotation/x = l_forearm?rotation/x × −0,28
 *
 * Die Bewegung steuert die Twist-Knochen nicht an (`g9_zuordnung.py`) —
 * hier werden sie je Bild aus dem Daz-Winkel ihres Glieds gestellt, im
 * Takt der Gelenkkorrekturen (`genesis9gelenke.js`), bevor die deren
 * Winkel lesen. Die Formeln kommen mit den Achsen des Servers (`dreh`).
 */
export class Genesis9drehknochen {

    static ACHSE = { x: 0, y: 1, z: 2 };
    static _winkel = [0, 0, 0];
    static _grad = [0, 0, 0];

    /**
     * `[{k, von, quelle, achse, faktor}]` — je Twist-Knochen sein Eintrag aus
     * `Dazachsen.vorbereiten` (`k`) und der seines Glieds (`von`).
     * @param alle    `{name: {bone, A, B, …}}` (Dazachsen.vorbereiten)
     * @param achsen  `{name: {o, r, dreh?: {von, quelle, achse, faktor}}}` vom Server
     */
    static vorbereiten(alle, achsen) {
        const aus = [];
        for (const [name, a] of Object.entries(achsen || {})) {
            const d = a?.dreh;
            if (!d || !alle[name] || !alle[d.von]) continue;
            aus.push({
                k: alle[name], von: alle[d.von],
                quelle: Genesis9drehknochen.ACHSE[d.quelle] ?? 0,
                achse: Genesis9drehknochen.ACHSE[d.achse] ?? 0,
                faktor: Number(d.faktor) || 0,
            });
        }
        return aus;
    }

    /** Ein Bild: jeden Twist-Knochen aus dem Winkel seines Glieds stellen. */
    static takt(liste) {
        if (!liste?.length) return 0;
        const grad = Genesis9drehknochen._grad;
        for (const e of liste) {
            const w = Dazachsen.winkel(e.von, Genesis9drehknochen._winkel);
            grad[0] = grad[1] = grad[2] = 0;
            grad[e.achse] = w[e.quelle] * e.faktor;
            Dazachsen.quaternion(e.k, grad, e.k.bone.quaternion);
        }
        return liste.length;
    }
}
