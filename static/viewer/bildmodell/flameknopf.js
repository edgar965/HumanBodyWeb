import { Gvhmrknopf } from './gvhmrknopf.js';
import { Flamefenster } from './flamefenster.js';

/**
 * Flameknopf — „Kopf (FLAME)" an jeder Kopfbild-Zeile und -Kachel (20.09.2026).
 *
 * Das Gegenstück zu „SMPL (GVHMR)" für Kopfbilder: GVHMR erfindet auf einem
 * Kopfausschnitt einen Körper, der Kopf kommt aus PyMAF-X/FLAME. Ein Klick öffnet
 * das `Flamefenster` und startet den Einzelschritt `flame` (`Bildmodellflame`),
 * wenn noch kein FLAME-Kopf liegt; danach baut derselbe Lauf das Modell neu —
 * der Kopf-Fit stellt die Gesichtsregler auf diesen Kopf.
 */
export class Flameknopf extends Gvhmrknopf {

    static _fenster = null;
    static FENSTER = Flamefenster;
    static ART = {
        schritt: 'flame', feld: 'flame', endpunkt: 'flame3d', name: 'FLAME',
        ansehen: 'Kopf ansehen', rechnen: 'Kopf (FLAME)',
        titelAnsehen: 'Ausgabefenster: FLAME-Kopf aus PyMAF-X in 3D, Zahlen, „Neu rechnen"',
        titelRechnen: 'FLAME-Kopf für dieses Kopfbild rechnen (PyMAF-X, ~10 s), danach das Modell neu '
            + 'mit Kopf-Fit — Ausgabefenster mit dem Kopf in 3D',
    };

    /** Nur an Kopfbildern. */
    static passt(b) { return !b.video && Gvhmrknopf.kopfbild(b); }
}
