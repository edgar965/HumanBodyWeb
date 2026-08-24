import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Keyframeablage — Schlüsselbilder als JSON aus- und wieder einlesen.
 *
 * Herausgelöst aus `keyframe-ui.js` (319 Zeilen). Die Datei enthält Dauer UND
 * Schlüsselbilder: Ohne die Dauer stünde die Zeitleiste nach dem Einlesen auf
 * zehn Sekunden, und alles dahinter wäre unerreichbar.
 */
export class Keyframeablage {

    static DATEINAME = 'theatre_keyframes.json';
    static VORGABE_DAUER = 10;

    /** Herunterladen. */
    static ausgeben(dauer, schluesselbilder) {
        const inhalt = JSON.stringify({ duration: dauer,
                                        keyframes: schluesselbilder }, null, 2);
        const adresse = URL.createObjectURL(
            new Blob([inhalt], { type: 'application/json' }));
        const verweis = document.createElement('a');
        verweis.href = adresse;
        verweis.download = Keyframeablage.DATEINAME;
        verweis.click();
        // Ohne das Freigeben bleibt der Blob bis zum Seitenwechsel im Speicher.
        URL.revokeObjectURL(adresse);
        Protokoll.debug('keyframe-ui', '✓ Keyframes exported');
    }

    /**
     * Dateiauswahl öffnen und den Inhalt an `beimLesen` geben.
     * @param {Function} beimLesen ({dauer, schluesselbilder})
     */
    static einlesen(beimLesen) {
        const feld = document.createElement('input');
        feld.type = 'file';
        feld.accept = '.json';
        feld.onchange = () => {
            const datei = feld.files[0];
            if (!datei) return;
            const leser = new FileReader();
            leser.onload = ereignis =>
                Keyframeablage._auswerten(ereignis.target.result, beimLesen);
            leser.readAsText(datei);
        };
        feld.click();
    }

    static _auswerten(inhalt, beimLesen) {
        try {
            const daten = JSON.parse(inhalt);
            beimLesen({
                dauer: daten.duration || Keyframeablage.VORGABE_DAUER,
                schluesselbilder: daten.keyframes || [],
            });
            Protokoll.debug('keyframe-ui', '✓ Keyframes imported:',
                            (daten.keyframes || []).length);
        } catch (fehler) {
            Protokoll.fehler('keyframe-ui', 'Import fehlgeschlagen', fehler);
            alert('Import failed: ' + fehler.message);
        }
    }
}
