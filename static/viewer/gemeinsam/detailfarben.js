/**
 * Detailfarben — Farben und Glanz der Materialgruppen des HumanBody-Netzes.
 *
 * Herausgelöst aus `koerperdetails.js` (12.09.2026, 308 Zeilen — die Datei
 * durfte nicht wachsen), als Edgar nach den Lippen fragte: „wahrscheinlich
 * fehlen noch viele andere Sachen, schau mal nach und füge alle ein". Das
 * Netz gibt her (Index = Materialgruppe, `koerpermaterialien.js`): Haut (0,
 * dazu 1 „Censor" — dieselbe Haut), Wimpern (2), Pupille (3), Sklera (4),
 * Hornhaut (5), Iris (6), Zunge (7), Zähne (8), Nägel Hand (9), Nägel Fuß
 * (10) — und seit heute die Lippen (11), die `Lippengruppe` aus der Haut
 * abspaltet. Pupille (schwarz) und Hornhaut (durchsichtig) bleiben fest.
 *
 * HAUT: leer heißt „Farbe der Körperart" (`Hautfarbe.ausKoerperart`, aus
 * der Ethnie); nur eine gesetzte Farbe überschreibt sie. GLANZ ist die
 * Umkehr der Rauheit (1 − roughness), 0..1.
 *
 * Ohne Three.js: die Materialien kommen als Objekte mit `color.set` und
 * `roughness` herein — so läuft es in Node (`test_js_koerperdetails.py`).
 */
export class Detailfarben {

    /** Vorgaben = die festen Farben aus `koerpermaterialien.js`; Haut leer = Körperart. */
    static VORGABE = Object.freeze({
        haut: '', haut_glanz: 0.45,
        iris: '#4a7a9b', sklera: '#f4f0e8', wimpern: '#111111', brauen: '#3a2a1e',
        lippen: '#b5707a', lippen_glanz: 0.6, zaehne: '#f0ece0', zunge: '#b55a6a',
        naegel_hand: '#e0a88a', naegel_fuss: '#e0a88a',
    });

    /** Farbfeld → Materialgruppen. `brauen` fehlt: eigenes Netz (`augenbrauenbau.js`). */
    static FARBEN = [
        ['haut', [0, 1]], ['wimpern', [2]], ['sklera', [4]], ['iris', [6]], ['zunge', [7]],
        ['zaehne', [8]], ['naegel_hand', [9]], ['naegel_fuss', [10]], ['lippen', [11]],
    ];

    /** Glanzfeld → Materialgruppen. */
    static GLANZ = [['haut_glanz', [0, 1]], ['lippen_glanz', [11]]];

    static istFarbe(wert) {
        return /^#[0-9a-fA-F]{6}$/.test(String(wert));
    }

    /**
     * Farben und Glanz auf die Materialliste des Körpers setzen.
     * @returns Zahl der gesetzten Farben (leere Haut zählt nicht — sie bleibt, was sie ist)
     */
    static faerben(materialien, details) {
        if (!Array.isArray(materialien)) return 0;
        let gesetzt = 0;
        for (const [name, gruppen] of Detailfarben.FARBEN) {
            if (!Detailfarben.istFarbe(details[name])) continue;
            for (const g of gruppen) {
                const material = materialien[g];
                if (!material?.color?.set) continue;
                material.color.set(details[name]);
                gesetzt += 1;
            }
        }
        for (const [name, gruppen] of Detailfarben.GLANZ) {
            const glanz = Number(details[name]);
            if (!Number.isFinite(glanz)) continue;
            for (const g of gruppen) {
                if (materialien[g]) materialien[g].roughness = 1 - glanz;
            }
        }
        return gesetzt;
    }
}
