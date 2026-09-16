/**
 * Hauttextur — MB-Lab-Albedo, Bump und Rauheit auf der Haut der Figur.
 *
 * WARUM (Edgar, 13.09.2026: „es fehlt auch die Einstellung der Hautfarbe,
 * Textur, usw. Schau nach was sonst noch fehlt im MBLab"): Die Figur trug
 * eine einfarbige Haut. MB-Lab liefert zu diesem Netz (die UVs passen, siehe
 * `core/dienste/lippenmaske.py`) je Ethnie eine Albedo (Poren, Röte, Lippen,
 * Brauenschatten), dazu eine Bump- und eine Rauheitskarte. Der Server gibt
 * sie unter `/api/character/textur/<datei>/` heraus (`core/api/hauttexturen.py`).
 *
 * Das Detail `haut_textur` nennt die Albedo (`hum_f_cauc` …, leer = keine).
 * Mit Textur wird die Materialfarbe WEISS, solange keine eigene Hautfarbe
 * gesetzt ist — sonst zöge die Farbe der Körperart die Albedo ins Dunkle
 * (Three.js multipliziert `color` und `map`). Eine eigene Farbe tönt die
 * Textur, wie es `Detailfarben` setzt.
 *
 * Läuft über `Koerperdetails.anwenden` und damit auf jeder Seite, die den
 * Körper baut (Szene, Studio, Ergebnis). Three.js kommt erst beim Laden
 * herein (`import('three')`), damit das Modul — wie `Koerperdetails` — in
 * Node prüfbar bleibt (`test_js_hauttextur.py`). Geladene Texturen werden
 * je Adresse gemerkt; eine zweite Figur derselben Ethnie lädt nichts neu.
 */
export class Hauttextur {

    static FELD = 'haut_textur';
    static ADRESSE = '/api/character/textur/';
    /** Materialgruppen der Haut (mit Censor). */
    static HAUT = [0, 1];
    /** Die wählbaren Albedos: Wert des Details → Datei und Anzeige. */
    static WAHL = [
        ['', 'Keine (Farbe der Körperart)'],
        ['hum_f_cauc', 'Frau – Europäisch'], ['hum_f_asian', 'Frau – Asiatisch'],
        ['hum_f_afro', 'Frau – Afrikanisch'], ['hum_f_latino', 'Frau – Lateinamerikanisch'],
        ['hum_m_cauc', 'Mann – Europäisch'], ['hum_m_asian', 'Mann – Asiatisch'],
        ['hum_m_afro', 'Mann – Afrikanisch'], ['hum_m_latino', 'Mann – Lateinamerikanisch'],
    ];
    /** Stärke der Bump-Karte (Three.js `bumpScale`, in Netzeinheiten ≈ m). */
    static BUMP = 0.0015;

    static _geladen = new Map();
    static _lader = null;

    /** Die Karten zu einem Wert: Albedo je Ethnie, Bump und Rauheit je Geschlecht. */
    static karten(wert) {
        if (!Hauttextur.WAHL.some(([w]) => w === wert) || !wert) return null;
        const geschlecht = wert.startsWith('hum_m_') ? 'male' : 'female';
        return { map: `${wert}_albedo.png`, bumpMap: `human_${geschlecht}_bump.png`,
                 roughnessMap: `human_${geschlecht}_roughness.png` };
    }

    /**
     * Textur nach `details` auf die Hautmaterialien setzen oder entfernen.
     * @returns Promise<boolean> — true, wenn eine Textur gesetzt wurde
     */
    static async anwenden(netz, details) {
        const materialien = Array.isArray(netz?.material) ? netz.material : null;
        if (!materialien) return false;
        const karten = Hauttextur.karten(details?.[Hauttextur.FELD]);
        if (!karten) { Hauttextur.entfernen(materialien); return false; }
        const geladen = {};
        for (const [rolle, datei] of Object.entries(karten)) {
            geladen[rolle] = await Hauttextur.laden(datei, rolle === 'map');
        }
        for (const g of Hauttextur.HAUT) {
            const m = materialien[g];
            if (!m) continue;
            for (const [rolle, textur] of Object.entries(geladen)) m[rolle] = textur;
            m.bumpScale = Hauttextur.BUMP;
            if (!details.haut) m.color.setRGB(1, 1, 1);
            m.needsUpdate = true;
        }
        return true;
    }

    /** Karten wieder weg — die Farbe setzt danach `Hautfarbe`/`Detailfarben`. */
    static entfernen(materialien) {
        let weg = 0;
        for (const g of Hauttextur.HAUT) {
            const m = materialien[g];
            if (!m?.map) continue;
            m.map = null; m.bumpMap = null; m.roughnessMap = null;
            m.needsUpdate = true;
            weg += 1;
        }
        return weg;
    }

    /** Eine Textur laden — einmal je Datei; Albedo in sRGB, Karten linear. */
    static async laden(datei, farbig) {
        // Albedos ohne die gemalten Brauen — die Figur zeichnet ihre eigenen
        // (`Brauenhaut`, 16.09.2026); die Abfrage ist Teil der Adresse.
        const adresse = Hauttextur.ADRESSE + datei + '/' + (farbig ? '?brauen=ohne' : '');
        if (Hauttextur._geladen.has(adresse)) return Hauttextur._geladen.get(adresse);
        const THREE = await import('three');
        Hauttextur._lader ??= new THREE.TextureLoader();
        const textur = await Hauttextur._lader.loadAsync(adresse);
        textur.colorSpace = farbig ? THREE.SRGBColorSpace : THREE.NoColorSpace;
        textur.anisotropy = 8;
        Hauttextur._geladen.set(adresse, textur);
        return textur;
    }
}
