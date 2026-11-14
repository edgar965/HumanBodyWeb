/**
 * Bauart — wie ein Stück sich bewegt und wie tief die Haut darunter nachgibt (12.11.2026).
 *
 * Edgar, 12.11.2026: „könnte die Haut (also das mesh) nachgeben, wenn es zu solchen kleinigkeiten kommt? … man könnte doch einen Parameter
 * setzen bis zu dem das mesh eingedrückt werden kann bei den animationen oder Ruhelage, oder schuhe?“ Danach: „mach alles, mit deinen
 * Empfehlungen“ — Empfehlung im Konzept `Docu/konzepte/2026-11-12_genesis-zuerst-konzept.md`, Abschnitt 3b und Entscheidung 4:
 *
 *   starr      Hut, Helm, Waffe, Schuh: das Stück behält seine Form (ein Knochen je Insel, `Starrbindung`), nie Stoffschwung;
 *              die Haut darunter zieht am tiefsten ein.
 *   anliegend  Hemd, Hose, Panzer: Häutung mit den Gewichten des Stücks, die Haut zieht bis zur eingestellten Tiefe ein, erst darüber
 *              schiebt die Hautbindung den Stoff hinaus (`Oberflaechenbindung`).
 *   lose       Rock, Robe, Mantel: Stoffschwung.
 *
 * Die Bauart steht am Eintrag der Garderobe (Server: `G9bauart`, Datei `Genesis9/bauarten.json` für die am Stück gesetzten Werte) und kommt
 * mit der Antwort des Stücks (`daten.bauart`, `daten.nachgeben_mm`). Fehlt sie (Antwort aus einem Vorrat von vorher), folgt sie hier aus
 * dem, was das Netz trägt — dieselbe Einteilung wie auf dem Server.
 *
 * DIE TIEFE (`nachgebenM`) IST DIE OBERGRENZE DES HAUTEINZUGS (`Hauteinzugrechnung`, `Saumband.tiefe`): verdeckte Haut zieht an der
 * Stoffkante 1 mm ein, je Meter Abstand von der gezeichneten Haut einen Meter mehr, höchstens diese Tiefe, und nie tiefer als ein Teil der
 * Körperdicke (`Hautdicke`, die dafür je Punkt bis `Tiefe / ANTEIL` sucht). Bis zum 12.11.2026 galt für jedes Stück 10 mm
 * (`Saumband.TIEFE_M`). Liegt ein Körperpunkt unter mehreren Stücken, gilt das tiefste (`Hautmaske.verdeckt`).
 */
export class Bauart {

    static ARTEN = ['starr', 'anliegend', 'lose'];

    /**
     * Obergrenze des Hauteinzugs je Bauart (Millimeter), Vorgabe, am Stück 1–50 mm überschreibbar. Edgar, 12.11.2026 abends: „Mach default
     * bei jedem Teil von mindestens 20 mm für Schuhe, eher mehr für T-shirts und Hosen, mach Vorschlag“. Starr 20 mm (an Olesia1 stachen
     * unter den Sneakern 395 Hautpunkte bis 15 mm hinaus, Modell-Check „Durchstoß“); anliegend und lose 30 mm — Vorschlag, nicht an einem
     * Durchstich gemessen: Hemd und Hose ziehen sich in Beugung und Spagat weiter in den Körper als ein Schuh, der starr bleibt.
     */
    static NACHGEBEN_MM = { starr: 20, anliegend: 30, lose: 30 };

    /** Die Bauart eines Netzes: vom Server, sonst aus dem, was das Netz trägt. */
    static von(netz) {
        const u = netz?.userData || {};
        if (Bauart.ARTEN.includes(u.bauart)) return u.bauart;
        if (u.stoff) return 'lose';                                       // Stoffschwung (`Genesis9/stoff.py`)
        if (u.art === 'requisit' || u.schuh) return 'starr';
        return 'anliegend';                                               // auch Ersatzstücke (`hautTiefe`): sie gehören zur Figur
    }

    /** Die Tiefe, bis zu der die Haut unter diesem Netz nachgibt (Meter): am Stück gesetzt, sonst die der Bauart. */
    static nachgebenM(netz) {
        const roh = netz?.userData?.nachgebenMm, mm = Number(roh);
        if (roh != null && roh !== '' && Number.isFinite(mm) && mm >= 0) return mm / 1000;     // `Number(null)` ist 0 — ohne Angabe gilt die Bauart (12.11.2026)
        return Bauart.NACHGEBEN_MM[Bauart.von(netz)] / 1000;
    }

    /** Was die Serverantwort eines Stücks über die Bauart sagt, ans Netz schreiben. */
    static eintragen(netz, daten) {
        netz.userData.bauart = Bauart.ARTEN.includes(daten?.bauart) ? daten.bauart : null;
        const mm = Number(daten?.nachgeben_mm);
        netz.userData.nachgebenMm = daten?.nachgeben_mm != null && Number.isFinite(mm) ? mm : null;
        netz.userData.schuh = !!daten?.schuh;
    }
}
