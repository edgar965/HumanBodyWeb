/**
 * Mesh3daianatomiehuelle — trägt ein gezeigtes Stück der KI die Anatomie, wird das Anatomie-Stück der bewegten Figur nicht gezeichnet (31.10.2026, seit 08.11.2026 nach der Regel des Servers).
 *
 * Edgar (31.10.2026, Testjob edgar, DanceKurz): „während der Animation [kommt] das Geschlechtsteil aus der hose“ — das Daz-Stück liegt tiefer als der Schritt der Hose aus dem Eingang.
 * Bis 08.11.2026 entschieden das drei Regeln auf verschiedenen Daten: der Server (`Kleideranatomie`, Hautmaske), hier waagrechte Strahlen vom Ansatz, und auf 2d-3d-AI jede gewählte Hose
 * (`Ai2d3dtestfigur.hose`, weil kein Strahl die Hose aus den Fotos traf). Edgar: „mach empfehlung“ — jetzt nur noch DIE Regel des Servers (`Kleideranatomie.getragen`: ein Stück einer
 * tragenden Art verdeckt mindestens 20 % der Anatomie-Dreiecke). Die Kleiderliste trägt das Ergebnis je Weg als `traegt_anatomie` (`Mesh3daitestkikleider.zeilen`); die stehende Figur
 * liest dieselbe Entscheidung aus der Maske des Stücks (dort steht dann die ganze Anatomie). Ausgeblendet zählt das Stück in der Hautverdeckung nicht mehr (`Hautverdeckung.zaehlt`):
 * die Haut darunter bekommt kein Loch; wer `anwenden` ruft, plant die Hautverdeckung neu, wenn sich etwas geändert hat.
 */
import { Hautverdeckung } from '../gemeinsam/hautverdeckung.js';

export class Mesh3daianatomiehuelle {
    /** Die Anatomie-Stücke der Figur (starr an die Haut gesetzt, `userData.hautTiefe` — wie `Kleidersichtbarkeit.istKoerperteil`, ohne ersetzende Augen). */
    static stuecke(modell) {
        return Object.values(modell?.clothMeshes || {}).filter(netz => netz?.userData?.hautTiefe > 0 && !(netz.userData.ersetzt?.length > 0));
    }

    /** Trägt ein gewähltes Stück der Kleiderliste (`…/kleider/<g>/`) die Anatomie? Entschieden hat der Server (`traegt_anatomie` am gewählten Weg). */
    static getragen(liste) {
        return (liste?.stuecke || []).some(st => st.wahl && st.wahl !== 'aus' && st[st.wahl]?.traegt_anatomie === true);
    }

    /** `anwenden`, dann die Hautverdeckung planen — mit `nurGeaendert` nur, wenn sich eine Sichtbarkeit geändert hat (neue Stufe der Figur). */
    static planen(modell, nurGeaendert = false) {
        if (Mesh3daianatomiehuelle.anwenden(modell) || !nurGeaendert) Hautverdeckung.planen(modell);
    }

    /** Sichtbarkeit der Anatomie-Stücke setzen (`modell.anatomieGetragen()`: Kleider an und ein Stück trägt sie, `Mesh3daifigurbewegung`); → true, wenn sich eine geändert hat. */
    static anwenden(modell) {
        const stuecke = Mesh3daianatomiehuelle.stuecke(modell);
        if (!stuecke.length) return false;
        const verdeckt = modell.anatomieGetragen?.() === true;
        let geaendert = false;
        for (const netz of stuecke) {
            const vorher = netz.userData.anatomieHuelle;
            netz.visible = !verdeckt;
            netz.userData.anatomieHuelle = verdeckt;
            if (vorher !== verdeckt) geaendert = true;
        }
        return geaendert;
    }
}
