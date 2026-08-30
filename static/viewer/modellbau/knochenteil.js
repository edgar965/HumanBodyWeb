/**
 * Knochenteil — welche Form und Dicke ein einzelner Knochen im Modell bekommt.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): In `modellvorgaben.js` standen DREI
 * fast gleiche Blöcke, die je einen Eintrag bauen — sichtbare Körperknochen,
 * versteckte Finger/Gesichtsknochen und Rig-Knochen. Gleiche Form, gleiche
 * Rundung, gleiche Obergrenze; unterschiedlich waren nur vier Zahlen. Genau so
 * laufen Fassungen auseinander: Wer die Obergrenze anhebt, findet zwei der
 * drei Stellen.
 *
 * DIE ZAHLEN SIND NICHT BELIEBIG und stehen deshalb beim Aufrufer, nicht hier:
 *
 *     Skelettknochen   Faktor 0,20   Mindestmaß 0,010   Ersatzlänge 0,10 / 0,05
 *     Rig-Knochen      Faktor 0,15   Mindestmaß 0,005   Ersatzlänge 0,05
 *
 * Rig-Knochen sind feiner, weil auch Steuerknochen dazugehören, die neben den
 * DEF-Knochen liegen — mit dem gröberen Maß verdecken sie einander.
 *
 * DIE ERSATZLÄNGE greift, wenn zu einem Knochen keine Weltmatrix vorliegt.
 * Ohne sie käme `undefined` in die Rechnung und der Radius wäre `NaN`; das
 * Teil verschwindet dann aus der Anzeige, ohne dass etwas rot wird.
 *
 * OBERGRENZE 0,05 für alle: Ein dickerer Zylinder ragt bei kurzen Knochen aus
 * dem Körper heraus — sichtbar als Beule, nicht als Fehler.
 */
export class Knochenteil {
    /** Kein Teil wird dicker als das, egal wie lang der Knochen ist. */
    static OBERGRENZE = 0.05;

    /** Alle Teile sind Zylinder, solange niemand von Hand etwas anderes wählt. */
    static FORM = 'cylinder';

    /**
     * Radius aus der Knochenlänge — nach oben und unten gekappt.
     *
     * Auf vier Nachkommastellen gerundet: Die Zahl geht als Zustand in die
     * gespeicherte Modelldatei, und `0.030000000000000002` dort wäre nur
     * Rauschen im Vergleich zweier Stände.
     */
    static radius(laenge, faktor, mindestmass) {
        const roh = Math.min(Knochenteil.OBERGRENZE,
                             Math.max(mindestmass, laenge * faktor));
        return parseFloat(roh.toFixed(4));
    }

    /**
     * Ein Eintrag für `bone_parts`.
     *
     * @param {Object} weltmatrix Eintrag aus `computeBoneWorldTransforms` —
     *     fehlt er, greift `ersatzlaenge`
     * @param {Object} mass {faktor, mindestmass, ersatzlaenge}
     * @param {Object} aussehen {farbe, sichtbar}
     */
    static bauen(weltmatrix, { faktor, mindestmass, ersatzlaenge },
                 { farbe, sichtbar }) {
        const laenge = weltmatrix ? weltmatrix.length : ersatzlaenge;
        return {
            shape: Knochenteil.FORM,
            radius: Knochenteil.radius(laenge, faktor, mindestmass),
            color: farbe,
            visible: sichtbar,
        };
    }
}
