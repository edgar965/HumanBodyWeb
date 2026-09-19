import { Testzustand } from './testzustand.js';
import { createBoneLabels, createBoneViz } from './knochenbild.js';
import { Einpassung } from './einpassung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Zielskelett — eine Spalte der Vergleichsseite, die ein ZIEL des Retargets
 * zeigt (wie DEF): das Skelett kommt fertig vom Server, die Bewegung mit
 * `target=<platz>` umgerechnet (`Vergleichswiedergabe.ZIELE`).
 *
 * Herausgelöst aus `umaskelett.js` (19.09.2026), als Genesis 9 als zweites
 * solches Ziel dazukam (Edgar: „den Genesis Rig als neuen Rig hinzufügen, so
 * wie andere"). Was je Ziel anders ist, steht in der Unterklasse: `ADRESSE`,
 * `PLATZ`, `NAME` und `bauen(daten)` — UMA liest glTF-Knochen, Genesis 9
 * den Bauplan von `Knochenbau`. Der Ablauf ist derselbe: holen, bauen, in
 * die Spalte stellen, einpassen (`Einpassung`: alle Skelette 1,68 m),
 * Knochenbild und Nummern, Schild beschriften. Fehlt die Quelle, bleibt die
 * Spalte leer — mit dem Grund auf dem Schild.
 *
 * Ein Ziel bekommt keine `Anfangshaltung`: Es ist kein BVH-Format.
 */
export class Zielskelett {

    /** Serveradresse des Skeletts — je Unterklasse. */
    static ADRESSE = '';
    /** Schlüssel in `Testzustand.skeletons` und Klasse des Schilds. */
    static PLATZ = '';
    /** Wie das Ziel auf dem Schild und im Protokoll heißt. */
    static NAME = '';
    /** Schildtext, wenn der Server das Skelett nicht hat. */
    static FEHLT = 'keine Quelle';

    /** `{skeleton, rootBone, bones, boneByName, achsen?}` aus der Serverantwort — je
     *  Unterklasse; `achsen` = Knochenlängen entlang der eigenen Achse (Daz). */
    static bauen(daten) {   // eslint-disable-line no-unused-vars
        throw new Error(`${this.name}.bauen() ist nicht implementiert`);
    }

    /** Kurztext für das Schild nach dem Laden, z. B. der Dateiname. */
    static herkunft(daten) {   // eslint-disable-line no-unused-vars
        return '';
    }

    /** Vom Server holen und in die Spalte stellen; `null`, wenn es fehlt. */
    static async laden() {
        const platz = Testzustand.skeletons[this.PLATZ];
        let daten;
        try {
            daten = await Serverabruf.json(this.ADRESSE);
        } catch (fehler) {
            Protokoll.warnung('skelett_test', `${this.NAME}-Skelett nicht ladbar: ${fehler.message}`);
            this.beschriften(`${this.NAME} – ${this.FEHLT}`);
            return null;
        }
        const gebaut = this.bauen(daten);
        platz.rootBone = gebaut.rootBone;
        platz.boneByName = gebaut.boneByName;
        platz.skeleton = gebaut;
        platz.bones = gebaut.bones;
        const einpassung = new Einpassung(gebaut.rootBone, gebaut.bones);
        const massstab = einpassung.anwenden(this.PLATZ);
        createBoneViz(gebaut.bones, this.PLATZ, 1 / massstab, gebaut.achsen || null);
        createBoneLabels(gebaut.bones, this.PLATZ);
        const herkunft = this.herkunft(daten);
        this.beschriften(herkunft ? `${this.NAME} (${herkunft})` : this.NAME);
        Protokoll.debug('Viewer',
            `${this.NAME}-Skelett geladen: ${gebaut.bones.length} Knochen`
            + (herkunft ? ` aus ${herkunft}` : '') + ', ' + einpassung.beschreibung());
        return gebaut;
    }

    static beschriften(text) {
        const schild = document.querySelector(`.skeleton-label.${this.PLATZ}`);
        if (schild) schild.textContent = text;
    }
}
