/**
 * Genesis9werte — die Zahlen einer Netzantwort an die Figur (25.11.2026 aus `Genesis9Modell.koerperAufbauen` herausgelöst; `Genesis9nachformen` braucht dieselben).
 */
export class Genesis9werte {

    /** Alles außer Netzen und Skelett. */
    static uebernehmen(inst, daten) {
        Genesis9werte.griffdeltas(inst, daten);
        inst.hoehe = daten.hoehe || 0;
        inst.punktzahl = daten.punktzahl || 0;
        inst.browserpunkte = daten.browserpunkte || daten.vertex_count || 0;
        inst.stufen = daten.stufen || 0;
        inst.morphwerte = daten.morphwerte || {};
        inst.gelenkregler = daten.gelenkregler || {};   // JCM-Schalter (`genesis9gelenke.js`)
        /** Wirksame HD-Morphkanäle (`Genesis9/hdmorphe.py`) — auf Stufe 1, mit Strg+Alt+H auch 2. */
        inst.hdkanaele = daten.hdkanaele || [];
        /** Wert je HD-Kanal dieser Stellung (17.10.2026): die Gewichte der Mimikfalten (`Genesis9mimikfalten`). */
        inst.hdwerte = daten.hdwerte || {};
        /** Das EINE Aussehen aus „Alter“ und „Wirkt älter / jünger“ (−1…1, `G9alterung`, 17.10.2026): Falten, Altersflecken und graues Haar folgen ihm (`Genesis9hautfalten.alter`). */
        inst.alterAussehen = Number.isFinite(Number(daten.alter_aussehen)) ? Number(daten.alter_aussehen) : null;
    }

    /** Die Fußhaltung getragener Schuhe je Knochen (12.11.2026, `Genesis9/griffkette.py` `deltas`): eine Animation setzt die Füße je Bild neu, `charakter/posenabsatz.js` legt diese
     *  Drehung danach wieder auf — dieselben Felder wie beim Absatz der HumanBody-Figuren. */
    static griffdeltas(inst, daten) {
        const deltas = daten.griffdeltas && Object.keys(daten.griffdeltas).length ? daten.griffdeltas : null;
        if (JSON.stringify(deltas) !== JSON.stringify(inst.absatzDeltas || null)) { inst.absatzDeltas = deltas; inst._absatzGemischt = {}; }
    }
}
