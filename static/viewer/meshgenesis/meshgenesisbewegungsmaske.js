import { Hautverdeckung } from '../gemeinsam/hautverdeckung.js';

/**
 * Meshgenesisbewegungsmaske — die bewegte Figur erst zeigen, wenn die Haut unter ihren Kleidern verdeckt ist (19.11.2026, Edgar zur Goldprinzessin im Tanz: „Haut kommt durch das
 * Oberteil. Hast du das mit ‚HautGibtNach‘ aktiviert?“ — ja, 30 mm; die Haut kam aus einem anderen Grund).
 *
 * Die Maske der bewegten Figur rechnet der Browser beim ersten Abspielen eines Tests (`Hautverdeckung` im Worker, danach auf dem Server abgelegt, `Hautmaskenvorrat`: laut dort 2,8 s im
 * Leerlauf, 7–14 s bei Last). So lange stand die Haut vor dem Stoff — an goldprinzessin_mesh_genesis_50 war Edgar der Erste (13:08, Hauptfaden 4,9 s blockiert, feine Stufe nach 9,9 s).
 * Gemessen beim Neuladen mit sofortigem Abspielen: grobe Stufe nach 2 s, feine Stufe nach 6,8 s ohne Maske (Figur spielt schon), Maske nach 7,0 s (aus der Ablage); in derselben Haltung wie
 * Edgars Bild danach keine Haut im Oberteil (gesehen im Chrome). Solange eine Maske geplant ist oder im Worker rechnet, zeigt das Feld die stille Figur (sie trägt die Maske des Servers)
 * mit einem Hinweis; die Bewegung läuft im Hintergrund weiter und erscheint, sobald die Maske steht — auch nach dem Wechsel auf die feine Stufe.
 */
export class Meshgenesisbewegungsmaske {
    static TEXT = 'Haut unter der Kleidung wird gerechnet – die Bewegung erscheint gleich';
    static WARTEN_MS = 250;

    /** true, wenn die Figur ohne durchscheinende Haut gezeigt werden kann: Kleider aus, oder keine Maske geplant und keine im Worker. */
    static fertig(modell, kleiderAn) {
        if (!modell) return false;
        if (!kleiderAn) return true;
        return !Hautverdeckung._ausstehend.has(modell) && !modell._maskeRechnet;
    }

    /**
     * Vor `einhaengen` (`Meshgenesisfigurbewegung`): false = noch nicht zeigen — dann legt das Feld die stille Figur ein (`Meshgenesisansicht._fuellen`), hier steht der Hinweis, und
     * alle `WARTEN_MS` wird geprüft, bis die Maske steht (dann füllt sich das Feld neu, mit der bewegten Figur).
     */
    static zeigen(bewegung, inhalt, kleiderAn) {
        clearTimeout(bewegung._maskeUhr);
        bewegung._maskeStand = Meshgenesisbewegungsmaske.fertig(bewegung.modell, kleiderAn);
        if (bewegung._maskeStand) return true;
        inhalt.userData.hinweis = Meshgenesisbewegungsmaske.TEXT;
        const warten = () => {
            if (!bewegung.aktiv || !bewegung.modell) return;
            if (Meshgenesisbewegungsmaske.fertig(bewegung.modell, bewegung._kleiderAn)) bewegung.ansicht.neuZeigen();
            else bewegung._maskeUhr = setTimeout(warten, Meshgenesisbewegungsmaske.WARTEN_MS);
        };
        bewegung._maskeUhr = setTimeout(warten, Meshgenesisbewegungsmaske.WARTEN_MS);
        return false;
    }

    /** Je Bild der Bewegung: eine neue Stufe hat die Maske verworfen (neuer Körper, Plan läuft) — zurück zur stillen Figur, bis sie wieder steht. */
    static nachBild(bewegung) {
        if (bewegung.aktiv && bewegung._maskeStand && !Meshgenesisbewegungsmaske.fertig(bewegung.modell, bewegung._kleiderAn)) bewegung.ansicht.neuZeigen();
    }
}
