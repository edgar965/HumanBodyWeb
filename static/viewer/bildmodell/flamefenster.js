import { Gvhmrfenster } from './gvhmrfenster.js';

/**
 * Flamefenster — das Ausgabefenster „FLAME-Kopf" für EIN Kopfbild (20.09.2026).
 *
 * Edgar: „warum gibt es beim Kopf keine Button zum Lauf und Erzeugung eines 3D
 * Modells?" — dasselbe Fenster wie `Gvhmrfenster` (`bildmodell_gvhmr_dialog.html`
 * mit `dialog_id=flame-dialog`), nur ohne Rig und Fotokamera: links das Kopfbild,
 * rechts der FLAME-Kopf aus PyMAF-X (5.023 Punkte, `flame3d/`), Zahlen, „Neu rechnen"
 * (Einzelschritt `flame`, danach die Kette bis zur Vorschau — Kopf-Fit inklusive).
 */
export class Flamefenster extends Gvhmrfenster {

    static MERKER = 'bildmodell.flame.groesse';
    static FARBE = 0xd9c6b9;
    static ART = {
        schritt: 'flame', feld: 'flame', endpunkt: 'flame3d', dialog: 'flame-dialog', rig: false,
        name: 'FLAME', ordner: 'schaetzung/',
        start: 'FLAME startet — PyMAF-X auf dem Kopfbild, danach das Modell mit Kopf-Fit …',
        neu: 'FLAME wird neu gerechnet …', kette: 'Modell mit FLAME-Kopf',
    };
}
