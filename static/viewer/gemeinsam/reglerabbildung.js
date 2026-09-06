/**
 * Reglerabbildung — ein gemeinsamer Reglerwert, übersetzt in beide Welten.
 *
 * UMA formt über Knochen, HumanBody über einzelne Punkte. Ein Eintrag der
 * gemeinsamen Tabelle (`/api/character/regler/gemeinsam/`) nennt beides:
 * `uma` sind DNA-Namen, `humanbody` Morphnamen. Hier steht die Umrechnung.
 *
 *     gemeinsam  -100 .. +100, Mitte 0
 *     UMA           0 .. 1,    Mitte 0,5      wert  ->  0.5 + wert/200
 *     HumanBody    -1 .. +1,   Mitte 0        wert  ->  wert/100
 *
 * DIESELBEN FORMELN STEHEN IN PYTHON (`humanbody_core.regler.Reglertabelle`),
 * weil UMA im Browser rechnet und HumanBody auf dem Server. Beide Seiten
 * werden mit denselben Beispielwerten geprüft (`test_reglertabelle.py` und
 * `test_js_reglerabbildung.py`), damit sie nicht auseinanderlaufen.
 *
 * Einträge mit `einheit` (heute nur die Größe in cm) sind ausgenommen: Deren
 * Umrechnung hängt an der Figur — die sichtbare Höhe einer UMA-Figur wird
 * gemessen, nicht gerechnet. 06.09.2026.
 */
export class Reglerabbildung {

    static MIN = -100;
    static MAX = 100;

    /** {DNA-Name: 0..1} für einen gemeinsamen Wert. */
    static umaWerte(eintrag, wert) {
        const roh = 0.5 + Reglerabbildung._geklemmt(wert) * (eintrag.richtung ?? 1) / 200;
        const werte = {};
        for (const name of eintrag.uma || []) werte[name] = Math.max(0, Math.min(1, roh));
        return werte;
    }

    /** {Morphname: -1..1} für einen gemeinsamen Wert. */
    static humanbodyWerte(eintrag, wert) {
        const roh = Reglerabbildung._geklemmt(wert) / 100;
        const werte = {};
        for (const name of eintrag.humanbody || []) werte[name] = roh;
        return werte;
    }

    /**
     * Stand einer UMA-Figur als gemeinsamer Wert; `null`, wenn ihre Rasse
     * keinen der DNA-Namen führt — dann gehört der Regler nicht auf die Seite.
     */
    static ausUma(eintrag, dna) {
        const werte = (eintrag.uma || []).filter(n => n in dna).map(n => dna[n]);
        if (!werte.length) return null;
        const mittel = werte.reduce((a, b) => a + b, 0) / werte.length;
        return (mittel - 0.5) * 200 * (eintrag.richtung ?? 1);
    }

    /**
     * Stand einer HumanBody-Figur als gemeinsamer Wert. Ein nicht gesetzter
     * Morph zählt als 0 mit, sonst zeigte ein Sammelregler mit drei Zielen zu
     * viel, wenn nur eines gestellt ist.
     */
    static ausHumanbody(eintrag, morphs) {
        const namen = eintrag.humanbody || [];
        if (!namen.length) return null;
        const summe = namen.reduce((a, n) => a + (morphs[n] || 0), 0);
        return summe / namen.length * 100;
    }

    /**
     * Kennt die Figur diesen Regler überhaupt? Der Latin-Körpertyp führt keine
     * Gesichtsmorphs, männliche Typen keine Brustposition, und nicht jede
     * UMA-Rasse hat jeden DNA-Namen — solche Zeilen bleiben weg, statt sich
     * ziehen zu lassen und nichts zu tun.
     */
    static gilt(eintrag, { dna, morphnamen }) {
        if (dna) return (eintrag.uma || []).some(n => n in dna);
        if (eintrag.meta) return true;
        // Ohne Morphnamen ist es ein Nur-UMA-Eintrag (Gruppe „Nur UMA") — bei
        // einer HumanBody-Figur gibt es dafür nichts zu stellen. Die Prüfung
        // muss VOR `every` stehen: `[].every(…)` ist true, und der Regler
        // stünde sonst ausgerechnet dort, wo er nichts bewirkt.
        const namen = eintrag.humanbody || [];
        return namen.length > 0 && namen.every(n => morphnamen.has(n));
    }

    static _geklemmt(wert) {
        return Math.max(Reglerabbildung.MIN, Math.min(Reglerabbildung.MAX, Number(wert) || 0));
    }
}
