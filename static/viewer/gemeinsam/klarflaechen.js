/**
 * Klarflächen — fast durchsichtige Schalen ohne Farbkarte weglassen, für
 * Formate, die keine Durchsichtigkeit kennen (OBJ, PLY, STL).
 *
 * FUND 26.09.2026 (Edgar, nachdem die Hautflecken behoben waren: die Augen
 * blieben weiß): Ein Genesis-9-Auge besteht aus vier Zonen — Augapfel mit der
 * Iriskarte, und davor Hornhaut und Tränenfilm. Die beiden vorderen tragen
 * KEINE Farbkarte, nur `Kd 1 1 1` und `d 0.12`; im Browser sieht man durch
 * sie hindurch auf die Iris.
 *
 * Die `.mtl` schreibt dieses `d` korrekt mit — aber MeshLab (und mancher
 * andere Leser) stellt Durchsichtigkeit gar nicht dar und zeichnet die Schale
 * als WEISSE Kugel über der Iris. Gemessen an Damira1: die Hornhaut reicht
 * bis Z = 0,0862, der Augapfel nur bis Z = 0,0836 — sie liegt also 2,6 mm
 * davor und deckt ihn vollständig zu.
 *
 * Eine Schale ohne Farbkarte trägt zum Bild nichts bei außer Verdeckung.
 * Deshalb bleibt sie in diesen Formaten draußen — und der Nutzer erfährt es
 * (Rückgabe `weggelassen`, im Exportdialog als Warnung).
 *
 * ABSICHTLICH ENG: nur ohne Farbkarte UND unter `GRENZE` Deckkraft. Ein
 * halbdurchsichtiger Schleier mit Karte bleibt drin — sonst verschwände
 * Kleidung, die man sehen will.
 */
export class Klarflaechen {

    /** Bis zu dieser Deckkraft gilt eine Fläche als Schale, nicht als Stoff. */
    static GRENZE = 0.25;

    /**
     * @param objekte Netze (nach `Gruppennetze.zerlegen`, also je Netz EIN Material)
     * @returns {{netze: Array, weggelassen: string[]}}
     */
    static entfernen(objekte) {
        const netze = [];
        const weggelassen = [];
        for (const obj of objekte) {
            const mat = Array.isArray(obj.material) ? null : obj.material;
            if (mat && Klarflaechen.istSchale(mat)) {
                weggelassen.push(obj.name || mat.name || 'ohne Namen');
                continue;
            }
            netze.push(obj);
        }
        return { netze, weggelassen };
    }

    /** Fast durchsichtig und ohne eigene Farbe — also eine reine Schale. */
    static istSchale(mat) {
        if (!mat || mat.map) return false;
        const deckkraft = mat.opacity === undefined ? 1 : mat.opacity;
        return mat.transparent === true && deckkraft <= Klarflaechen.GRENZE;
    }
}
