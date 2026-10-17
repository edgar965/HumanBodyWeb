import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Posenaufnahme } from './posenaufnahme.js';
import { _selectedInst } from './utils.js';

/**
 * Posenspeichern — der Bereich „Aktuelle Pose speichern" im Reiter „Posen".
 *
 * Edgar, 17.10.2026: die Stellung der gewählten Figur als neue Pose ablegen.
 * Name eintippen, „Speichern": Der Server legt sie unter `poseData/eigene/`
 * ab (`Posenablage`), die Liste zeigt sie danach gewählt. Die Kategorie
 * bestimmt der Server — `rest_poses` und `charmorph` kommen aus CharMorph und
 * MB-Lab und werden nie beschrieben.
 *
 * Eine Pose desselben Namens wird nicht überschrieben (409): Wer „t-pose2"
 * meinte und „t-pose" tippt, soll keine gute Pose verlieren.
 */
export class Posenspeichern {

    static ENDPUNKT = '/api/character/pose-manage/';

    static _gebunden = false;

    /**
     * Knopf und Eingabefeld anmelden — einmal; `loadPoseUI` läuft nach jeder
     * Aktion erneut, und jeder Lauf hängte sonst einen weiteren Zuhörer an.
     *
     * @param status    (text, ok) schreibt unter die Liste
     * @param neuLaden  (id) baut die Liste neu und wählt die Pose `id`
     */
    static binden({ status, neuLaden }) {
        if (Posenspeichern._gebunden) return;
        const knopf = document.getElementById('pose-save-btn');
        const feld = document.getElementById('pose-save-name');
        if (!knopf || !feld) return;
        Posenspeichern._gebunden = true;
        const los = () => Posenspeichern.speichern(feld, status, neuLaden);
        knopf.addEventListener('click', los);
        feld.addEventListener('keydown', (ereignis) => {
            if (ereignis.key === 'Enter') {
                ereignis.preventDefault();
                los();
            }
        });
    }

    static async speichern(feld, status, neuLaden) {
        const name = feld.value.trim();
        if (!name) {
            status('Bitte einen Namen für die Pose eingeben.', false);
            feld.focus();
            return false;
        }
        const aufnahme = Posenaufnahme.aufnehmen(_selectedInst());
        if (!aufnahme.ok) {
            status(aufnahme.grund, false);
            return false;
        }
        let antwort;
        try {
            antwort = await Serverabruf.senden(Posenspeichern.ENDPUNKT,
                { action: 'save', name, bones: aufnahme.drehungen });
        } catch (fehler) {
            // Der Server sagt, warum (Name vergeben, Zeichen nicht erlaubt …) —
            // im Feld `error` seiner Antwort; `message` wäre „409 Conflict bei …".
            Protokoll.warnung('Pose', 'Speichern abgelehnt:', fehler);
            status(fehler.daten?.error || fehler.message || String(fehler), false);
            return false;
        }
        feld.value = '';
        status(Posenspeichern._text(antwort), true);
        await neuLaden(antwort.id);
        return true;
    }

    static _text(antwort) {
        const weg = (antwort.uebersprungen || []).length;
        return `„${antwort.name}" gespeichert in „${antwort.category}" (${antwort.knochen} Knochen)`
            + (weg ? ` — ${weg} Knochen ohne Entsprechung ausgelassen.` : '.');
    }
}
