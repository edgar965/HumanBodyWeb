import { Posenanwendung } from './posenanwendung.js';
import { Posenabsatz } from './posenabsatz.js';

/**
 * Posenaufnahme — die Stellung einer Figur als Pose-Drehungen lesen.
 *
 * Edgar, 17.10.2026: „Aktuelle Pose speichern" im Reiter „Posen". Das ist die
 * UMKEHRUNG von `Posenanwendung.anwenden`: Dort wird auf jeden Knochen
 * `ruhelage * delta` gelegt (und bei vier Gliedwurzeln die Drehung des
 * Elternknochens herausgerechnet); hier wird aus dem Zustand der Knochen das
 * `delta` zurückgelesen, das genau diesen Zustand wieder ergäbe.
 *
 *     Knochen:   endlage  =  C * (ruhelage * delta)
 *     delta   =  ruhelage⁻¹ * C⁻¹ * endlage
 *     C       =  elternNachher⁻¹ * elternVorher       nur Oberarm und Oberschenkel
 *     C⁻¹     =  elternVorher⁻¹ * elternNachher       (`_gliederKorrigieren`)
 *
 * Alle anderen Knochen haben kein `C`. Die Ruhelage ist die gesicherte der
 * Figur (`figur._aPoseBones`) — dieselbe, auf die `anwenden` die Deltas legt;
 * mit einer anderen kämen beim Laden andere Stellungen heraus.
 *
 * EIN ABSATZSCHUH GEHÖRT NICHT IN DIE POSE: Seine Fußbeugung rechnet der
 * Server bei jedem Laden hinein (`Absatzpose.einrechnen`, rechts mit dem
 * Delta multipliziert). Ohne Abzug stünde sie doppelt in der Datei. Deshalb
 * wird `figur.absatzDeltas` hier rechts herausgenommen — dieselbe
 * Reihenfolge wie beim Einrechnen.
 *
 * Die Rechnung selbst (`berechnen`) kennt weder `state` noch das DOM und läuft
 * mit jedem Skelett, das Three.js-Knochen führt — so ist sie in Node prüfbar.
 */
export class Posenaufnahme {

    /** Unter dieser Abweichung von der Ruhelage gilt ein Knochen als unbewegt. */
    static UNBEWEGT = 1e-9;

    /**
     * Die Stellung der gewählten Figur. Liefert `{ok, drehungen}` oder
     * `{ok: false, grund}` — jeder Ausstieg nennt seinen Grund.
     */
    static aufnehmen(figur) {
        const befund = Posenanwendung.pruefen(figur);
        if (!befund.ok) return befund;
        if (!figur.isSkinned) {
            return { ok: false, grund: 'Figur hat kein Skelett zum Lesen.' };
        }
        const skelett = Posenanwendung.skelett(figur);
        if (!skelett) {
            return { ok: false, grund: 'Kein gehäutetes Netz an dieser Figur.' };
        }
        if (!figur._aPoseBones) {
            return { ok: false,
                     grund: 'Die Ruhelage der Figur ist noch nicht gesichert — '
                            + 'erst einmal eine Pose aus der Liste anklicken '
                            + '(z. B. a-pose), dann lässt sich jede Stellung speichern.' };
        }
        const absatz = Posenabsatz.aktiv(figur) ? figur.absatzDeltas : null;
        const drehungen = Posenaufnahme.berechnen(skelett, figur._aPoseBones, absatz);
        if (!Object.keys(drehungen).length) {
            return { ok: false,
                     grund: 'Die Figur steht in der Ruhelage — nichts zu speichern.' };
        }
        return { ok: true, drehungen };
    }

    /**
     * Die Deltas aller bewegten Knochen: `{Knochenname: [x, y, z, w]}`.
     *
     * @param skelett  Three.js-Skeleton
     * @param ruhe     {Knochenname: Quaternion} — die gesicherte Ruhelage
     * @param absatz   {DEF-Name mit Punkt: [x, y, z, w]} oder null
     */
    static berechnen(skelett, ruhe, absatz = null) {
        const knochen = skelett.bones;
        const Quat = knochen[0].quaternion.constructor;
        const endlagen = knochen.map((k) => k.quaternion.clone());

        // Die Elterndrehung der Gliedwurzeln, wie sie JETZT steht ...
        knochen[0].updateWorldMatrix(true, true);
        const nachher = Posenaufnahme._elterndrehungen(skelett, Quat);
        // ... und wie sie in der Ruhelage stand (kurz herstellen, danach zurück).
        for (const k of knochen) {
            if (ruhe[k.name]) k.quaternion.copy(ruhe[k.name]);
        }
        knochen[0].updateWorldMatrix(true, true);
        const vorher = Posenaufnahme._elterndrehungen(skelett, Quat);
        knochen.forEach((k, i) => k.quaternion.copy(endlagen[i]));
        knochen[0].updateWorldMatrix(true, true);

        const deltaAbsatz = Posenaufnahme._absatz(absatz, Quat);
        const drehungen = {};
        knochen.forEach((k, i) => {
            if (!ruhe[k.name]) return;
            const q = endlagen[i].clone();
            if (vorher[k.name]) {
                q.premultiply(vorher[k.name].clone().invert().multiply(nachher[k.name]));
            }
            const delta = ruhe[k.name].clone().invert().multiply(q);
            if (deltaAbsatz[k.name]) delta.multiply(deltaAbsatz[k.name].clone().invert());
            if (1 - Math.abs(delta.w) < Posenaufnahme.UNBEWEGT
                    && Math.abs(delta.x) + Math.abs(delta.y) + Math.abs(delta.z)
                        < Posenaufnahme.UNBEWEGT) {
                return;
            }
            drehungen[k.name] = [delta.x, delta.y, delta.z, delta.w];
        });
        return drehungen;
    }

    /** Weltdrehung der Eltern der Gliedwurzeln, nach Knochenname. */
    static _elterndrehungen(skelett, Quat) {
        const drehungen = {};
        for (const name of Posenanwendung.GLIEDWURZELN) {
            const k = skelett.getBoneByName(Posenanwendung.jsName(name));
            if (!k?.parent) continue;
            const welt = new Quat();
            k.parent.getWorldQuaternion(welt);
            drehungen[k.name] = welt;
        }
        return drehungen;
    }

    /** Die Absatzdeltas mit den Knochennamen von Three.js (Punkt -> Unterstrich). */
    static _absatz(absatz, Quat) {
        const aus = {};
        for (const [name, w] of Object.entries(absatz || {})) {
            aus[Posenanwendung.jsName(name)] = new Quat(w[0], w[1], w[2], w[3]);
        }
        return aus;
    }
}
