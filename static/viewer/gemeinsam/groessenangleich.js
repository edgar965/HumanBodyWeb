/**
 * Groessenangleich — der Faktor, mit dem eine Figur auf die Höhe einer
 * anderen kommt.
 *
 * WARUM EIGENES MODUL (06.09.2026): Die Rechnung ist die einzige Stelle mit
 * Entscheidungen (was ist Messrauschen, was eine kaputte Messung), und sie
 * lässt sich nur prüfen, wenn sie ohne Three.js auskommt. `figurplatzierung.js`
 * misst und wendet an, hier steht, was daraus folgt.
 */
export class Groessenangleich {

    /** Darunter ist der Unterschied Messrauschen und nicht der Rede wert. */
    static RAUSCHEN = 0.02;

    /** Außerhalb dieser Grenzen ist nicht die Figur schuld, sondern die Messung. */
    static KLEINSTER = 0.2;
    static GROESSTER = 5;

    /**
     * @param eigen  gemessene Höhe der neuen Figur in Metern
     * @param soll   Höhe, auf die sie kommen soll
     * @returns Skalierungsfaktor; 1 heißt „unverändert lassen"
     */
    static faktor(eigen, soll) {
        const a = Number(eigen), b = Number(soll);
        if (!isFinite(a) || !isFinite(b) || a <= 0 || b <= 0) return 1;
        const faktor = b / a;
        if (faktor < Groessenangleich.KLEINSTER || faktor > Groessenangleich.GROESSTER) return 1;
        if (Math.abs(faktor - 1) < Groessenangleich.RAUSCHEN) return 1;
        return faktor;
    }

    /** Ob `faktor` etwas ändern würde — für Anzeigen und Tests. */
    static greift(eigen, soll) {
        return Groessenangleich.faktor(eigen, soll) !== 1;
    }
}
