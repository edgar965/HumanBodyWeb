import { Posenanwendung } from './posenanwendung.js';

/**
 * Absatzdrehung — Fuss und Zehen einer Figur um die Ballenachse drehen.
 *
 * Der Rechenteil von `garmentcode_absatz.js`: Der Fuss dreht um den Kopf
 * von `DEF-foot` (die Ferse steigt), die Zehen drehen um den Kopf von
 * `DEF-toe` zurück, damit sie flach bleiben — und um die Sprengung des
 * Schuhs weiter (die Spitze steigt). Weltdrehung um die x-Achse der
 * Figur, in den Elternraum jedes Knochens übersetzt wie in
 * `Posenanwendung._oberschenkel`.
 *
 * DIE DREHRICHTUNG WIRD GEMESSEN, NICHT ANGENOMMEN: Eine Probedrehung
 * des Fusses muss den Zehenkopf senken. Hebt sie ihn, war es die andere
 * Seite der x-Achse — dann wird das Vorzeichen umgedreht. So hängt nichts
 * an der Frage, wohin die Figur in der Szene blickt; und die Probe ist
 * vom Winkel unabhängig, damit sie auch bei reiner Sprengung (Winkel 0)
 * greift.
 */
export class Absatzdrehung {

    static FUSS = ['DEF-foot.L', 'DEF-foot.R'];
    static ZEHEN = ['DEF-toe.L', 'DEF-toe.R'];
    /** Probedrehung für das Vorzeichen, Bogenmass. */
    static PROBE = 0.1;

    /**
     * Fuss und Zehen drehen (Bogenmass); liefert die Liste
     * `[knochen, lokale Drehung]`, mit der `zuruecknehmen` alles aufhebt.
     */
    static drehen(inst, skelett, winkel, sprengung) {
        const Quat = skelett.bones[0].quaternion.constructor;
        const Vec3 = skelett.bones[0].position.constructor;
        const gruppe = new Quat();
        inst.group.getWorldQuaternion(gruppe);
        const achse = new Vec3(1, 0, 0).applyQuaternion(gruppe).normalize();
        const vorzeichen = Absatzdrehung._vorzeichen(skelett, achse, Quat, Vec3);
        const drehungen = Absatzdrehung._anwenden(skelett, achse, vorzeichen * winkel,
            vorzeichen * sprengung, Quat);
        skelett.bones[0].updateWorldMatrix(true, true);
        return drehungen;
    }

    static zuruecknehmen(drehungen) {
        for (const [knochen, lokal] of drehungen) {
            knochen.quaternion.premultiply(lokal.clone().invert());
        }
    }

    /** +1, wenn eine positive Drehung um `achse` den Zehenkopf senkt, sonst -1. */
    static _vorzeichen(skelett, achse, Quat, Vec3) {
        const zehe = skelett.getBoneByName(Posenanwendung.jsName(Absatzdrehung.ZEHEN[0]));
        if (!zehe) return 1;
        const vorher = zehe.getWorldPosition(new Vec3()).y;
        const probe = Absatzdrehung._anwenden(skelett, achse, Absatzdrehung.PROBE, 0, Quat);
        skelett.bones[0].updateWorldMatrix(true, true);
        const nachher = zehe.getWorldPosition(new Vec3()).y;
        Absatzdrehung.zuruecknehmen(probe);
        skelett.bones[0].updateWorldMatrix(true, true);
        return nachher < vorher ? 1 : -1;
    }

    static _anwenden(skelett, achse, winkel, sprengung, Quat) {
        const drehungen = [];
        // Die Zehen drehen die Fussdrehung zurück (bleiben flach) und um
        // die Sprengung weiter (die Spitze steigt).
        const paare = [[Absatzdrehung.FUSS, winkel],
                       [Absatzdrehung.ZEHEN, -(winkel + sprengung)]];
        for (const [namen, grad] of paare) {
            for (const name of namen) {
                const knochen = skelett.getBoneByName(Posenanwendung.jsName(name));
                if (!knochen?.parent) continue;
                const welt = new Quat().setFromAxisAngle(achse, grad);
                const eltern = new Quat();
                knochen.parent.getWorldQuaternion(eltern);
                const lokal = eltern.clone().invert().multiply(welt).multiply(eltern);
                knochen.quaternion.premultiply(lokal);
                drehungen.push([knochen, lokal]);
            }
        }
        return drehungen;
    }
}
