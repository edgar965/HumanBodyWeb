import { Genesis9haut } from './genesis9haut.js';
import { Genesis9hautebenenwerte } from './genesis9hautebenenwerte.js';

/**
 * Genesis9mimikfalten — die Falten der Mimik auf der Kopfhaut (17.10.2026, Edgar: „mach alles was offen ist"; Tabelle 11 in `genesis9-alter.md`).
 *
 * Daz' 27 FACS-Details (`FACSDetails_facs_bs_<Ausdruck>_HD2`) sind HD-Morphs mit Verschiebungen von 0,1 bis 0,8 mm — bei 3,3 mm Kantenlänge der Ansichtsstufe keine Geometrie, nur Licht. Der Server hat sie zu
 * einem Atlas aus Normalen gebacken (`G9mimikfalten`: 27 Zellen à 512², 6 Spalten × 5 Zeilen, Kopfkachel 1001); hier summiert der Shader `Σ Gewicht · Normale` über die Zellen, deren Kanal in dieser Stellung einen
 * Wert hat (`hdwerte` der Netzantwort: der Wert des HD-Kanals, also Mimik mal `FACSDetailStrength`). Ohne Ausdruck sind alle Gewichte 0, dann kommt weder Programm noch Atlas.
 *
 * Geteilt mit den übrigen Hautebenen (`Genesis9hautebenen`): derselbe Zusatz am Kopfmaterial, derselbe Weg der Karten (`Genesis9hautkarten`, Produkt `mimik`). Die Rechnung der Gewichte steht ohne Three.js in
 * `Genesis9hautebenenwerte` (`mimikAktiv`, `mimikGewichte`); dieses Modul hält nur, was Three braucht.
 */
export class Genesis9mimikfalten {

    /** Steigung bei Gewicht 1 und Regler 100 % (die Karte trägt Steigungen bis 0,22; nach Augenmaß wie `Genesis9hautebenen.STAERKE`, im Bild nicht abgestimmt). */
    static STAERKE = 3.0;
    /** Gruppe des Materials, auf dem die Mimikfalten liegen (die Zellen sind Kachel 1001, die Mundhöhle teilt sie nicht mit). */
    static GRUPPE = 'Head';

    /** Die Uniforms des Zusatzes — Platzhalter, bis der Atlas da ist; `uHtMimikW` bleibt dasselbe Feld (der Shader hält es fest). */
    static uniforms() {
        return {
            uHtMimikAtlas: { value: Genesis9haut.platzhalter(128, 128, 128) },
            uHtMimikW: { value: new Float32Array(Genesis9hautebenenwerte.MIMIK_ANZAHL) },
            uHtMimikStaerke: { value: 0 },
        };
    }
}
