import { Knopfmeldung } from '../gemeinsam/knopfmeldung.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Smpllicht } from './smpl_licht.js';

/**
 * Smpleinstellungen — die gespeicherten Vorgaben des SMPL-Reiters.
 *
 * Herausgelöst aus `smpl_koerper.js`. Gespeichert wird ein Objekt mit sechs
 * Körperfeldern und der kompletten Szene (`Smpllicht.einstellungen()`).
 *
 * Die Regler zählen wieder in Prozent: Deckkraft und Versatz gehen durch 100,
 * die zehn Formwerte ebenfalls. Ein `null` im gespeicherten Stand heißt „nicht
 * gesetzt" und lässt den Regler stehen — 0 wäre etwas anderes.
 */
export class Smpleinstellungen {

    static ENDPUNKT = '/api/settings/smpl/';
    static SPEICHERN = '/api/settings/smpl/save/';

    /** Feld im Stand, Regler-Kennung, Teiler, Anzeigeform. */
    static REGLER = [
        ['opacity', 'smpl-body-opacity', 100, wert => wert.toFixed(2)],
        ['xoffset', 'smpl-body-xoffset', 100, wert => wert.toFixed(2) + ' m'],
    ];

    /** Den gespeicherten Stand holen und auf die Bedienung legen. */
    static async laden(formwerteSetzen) {
        let stand;
        try {
            stand = await Serverabruf.json(Smpleinstellungen.ENDPUNKT);
        } catch (fehler) {
            Protokoll.warnung('smpl', 'Vorgaben nicht ladbar', fehler);
            return;
        }
        const geschlecht = document.getElementById('smpl-body-gender');
        if (geschlecht && stand.gender) geschlecht.value = stand.gender;
        formwerteSetzen(stand.betas);
        for (const [feld, kennung, teiler, form] of Smpleinstellungen.REGLER) {
            Smpleinstellungen._setzen(kennung, stand[feld], teiler, form);
        }
        const farbe = document.getElementById('smpl-body-color');
        if (farbe && stand.color) farbe.value = stand.color;
        const gitter = document.getElementById('smpl-body-wireframe');
        if (gitter && stand.wireframe != null) gitter.checked = stand.wireframe;
        if (stand.scene) Smpllicht.einstellungenAnwenden(stand.scene);
    }

    static _setzen(kennung, wert, teiler, formatieren) {
        const regler = document.getElementById(kennung);
        if (!regler || wert == null) return;
        regler.value = Math.round(wert * teiler);
        const anzeige = document.getElementById(`${kennung}-val`);
        if (anzeige) anzeige.textContent = formatieren(wert);
    }

    /** Den aktuellen Stand speichern und den Knopf quittieren lassen. */
    static async speichern(stand) {
        const knopf = document.getElementById('smpl-save-settings');
        try {
            if (knopf) {
                knopf.disabled = true;
                knopf.innerHTML =
                    '<i class="fas fa-spinner fa-spin"></i> Speichern...';
            }
            const antwort = await Serverabruf.senden(
                Smpleinstellungen.SPEICHERN, stand);
            if (!antwort.ok) throw new Error(antwort.error || 'Save failed');
            // `Knopfmeldung` nimmt Text UND Farbe zurueck; hier muss zusaetzlich
            // die Sperre des Knopfs fallen.
            Knopfmeldung.fertig(knopf);
            setTimeout(() => { if (knopf) knopf.disabled = false; },
                       Zeiten.BESTAETIGUNG_MS);
        } catch (fehler) {
            Protokoll.fehler('smpl', 'Einstellungen nicht speicherbar', fehler);
            if (knopf) knopf.disabled = false;
            Knopfmeldung.fehler(knopf, 'Fehler!');
        }
    }
}
