import { GEWEBEARTEN, gewebeart } from './gewebearten.js';

/**
 * Stoffarten — die Vorwahl „Stoffart“ im Block „Stoff“ eines Stücks (Assets → Eigen, Eigenschaften des Daz-Stücks).
 *
 * AUFTRAG (Edgar, 25.10.2026): „beim Regler: Stoff gibt es noch mehr Optionen, siehe die Optionen bei einigen Garments, z.B. die Anzahl der
 * Fäden, Glanz, stoffart usw. Durchforste alles und baue ein“. Bis dahin hatte der Block Rauheit, Metall und Gewebe (`Stueckstoff`); Glanz
 * (Daz' `Glossy Layered Weight` → `specularIntensity`) kam nur an Stücken mit Preset an (Eirgrid Shine), der Glanzsaum (`sheen`) nur an den
 * live gebauten GarmentCode-Stücken (`Garmentstoff`, fest 0,6).
 *
 * Eine Wahl setzt ALLE Stoffwerte des Stücks auf die Zeile hier — danach bleibt jeder Regler einzeln verstellbar, `stoffart` merkt nur,
 * wovon man ausging. Die Zahlen sind ANFANGSWERTE ZUM WEITERDREHEN, keine Messwerte (wie `gewebearten.js`):
 *
 *   rauheit       Material `roughness` (0 = spiegelnd, 1 = matt)
 *   glanz         Faktor auf die Spiegelung des Stücks (1 = wie geliefert, 0 = keine) — `Stoffshader`, Uniform `stoffSpiegel`
 *   saum          Glanzsaum (Sheen, Charlie-Verteilung): der helle Rand der Fasern unter streifendem Licht, 0..1
 *   saumstreuung  `sheenRoughness`: klein = harter Schimmer (Satin), groß = weicher Flaum (Wolle)
 *   saumfarbe     '' = wie der Stoff (ein weißer Saum stand auf schwarzer Leggings wie Haut, `Garmentstoff` 11.09.2026), sonst '#rrggbb'
 *   gewebe        Bindung im Shader (`Stoffshader`): Art, Fäden je cm (an der UV des Stücks), Struktur (Neigung der Normale)
 *
 * Die Feinheit ist die, bei der die Bindung im Bild zu sehen ist (bei 4 je cm am T-Shirt gemessen am stärksten, `Gewebe.KACHEL_M`) — echte
 * Fadenzahlen (Denim 25–30 je cm, Hemdenstoff 40–60) lägen unter einem Bildpunkt; der Shader blendet solche Feinheiten aus, statt zu flimmern.
 * Ohne Three.js und DOM: in Node prüfbar (`core/tests/unit/test_js_stoffarten.py`).
 */
export class Stoffarten {

    static ARTEN = {
        baumwolle: { titel: 'Baumwolle', rauheit: 0.85, glanz: 0.6, saum: 0.5, saumstreuung: 0.8,
                     gewebe: { art: 'leinwand', faeden: 5, staerke: 0.4 } },
        jersey: { titel: 'Jersey / T-Shirt', rauheit: 0.8, glanz: 0.6, saum: 0.6, saumstreuung: 0.9,
                  gewebe: { art: 'jersey', faeden: 4, staerke: 0.45 } },
        denim: { titel: 'Denim', rauheit: 0.9, glanz: 0.5, saum: 0.35, saumstreuung: 0.8,
                 gewebe: { art: 'koeper', faeden: 4, staerke: 0.6 } },
        seide: { titel: 'Seide', rauheit: 0.35, glanz: 1.0, saum: 0.8, saumstreuung: 0.35,
                 gewebe: { art: 'leinwand', faeden: 12, staerke: 0.15 } },
        satin: { titel: 'Satin', rauheit: 0.25, glanz: 1.0, saum: 0.9, saumstreuung: 0.25,
                 gewebe: { art: 'satin', faeden: 8, staerke: 0.15 } },
        leinen: { titel: 'Leinen', rauheit: 0.9, glanz: 0.4, saum: 0.4, saumstreuung: 0.9,
                  gewebe: { art: 'leinwand', faeden: 3, staerke: 0.6 } },
        wolle: { titel: 'Wolle / Strick', rauheit: 0.95, glanz: 0.3, saum: 0.8, saumstreuung: 1.0,
                 gewebe: { art: 'jersey', faeden: 1.5, staerke: 0.8 } },
        leder: { titel: 'Leder', rauheit: 0.45, glanz: 1.0, saum: 0.0, saumstreuung: 0.5,
                 gewebe: { art: 'narbung', faeden: 4, staerke: 0.3 } },
        sport: { titel: 'Kunstfaser / Sport', rauheit: 0.55, glanz: 0.9, saum: 0.3, saumstreuung: 0.5,
                 gewebe: { art: 'jersey', faeden: 7, staerke: 0.35 } },
    };

    /**
     * Bindungen, die es nur im Shader gibt — nicht in `GEWEBEARTEN`: Deren Liste muss die des GarmentCode-Reiters bleiben
     * (`test_gewebeauswahl`: Vorlage und Modul führen dieselben Arten), und die Kachel dort braucht ein kachelndes Höhenfeld.
     */
    static ZUSATZGEWEBE = {
        narbung: { titel: 'Narbung (Leder)', faedenJeCm: 4, staerke: 0.3 },
    };

    /** Die Werte zum Feld „Glanz“ und „Glanzsaum“ ohne Angabe: so sah ein Stück bis zum 25.10.2026 aus. */
    static VORGABE = { glanz: 1, saum: 0, saumstreuung: 0.8, saumfarbe: '', relief: 1 };

    /** Die Auswahl der Bindungen: `[[schluessel, titel]]`, ohne „glatt“ (das ist „Wie geliefert“). */
    static gewebewahl() {
        const aus = Object.entries(GEWEBEARTEN).filter(([s]) => s !== 'glatt').map(([s, a]) => [s, a.titel]);
        for (const [s, a] of Object.entries(Stoffarten.ZUSATZGEWEBE)) aus.push([s, a.titel]);
        return aus;
    }

    /** Fäden je cm und Struktur, die eine Bindung beim Umschalten bekommt. */
    static gewebevorgabe(art) {
        const zusatz = Stoffarten.ZUSATZGEWEBE[art];
        if (zusatz) return { faeden: zusatz.faedenJeCm, staerke: zusatz.staerke };
        const g = gewebeart(art);
        return { faeden: g.faedenJeCm, staerke: g.staerke };
    }

    /** Die Stoffwerte einer Art als neues Objekt für `werte.stoff` — oder null bei unbekanntem Namen. Metall ist bei Stoff immer 0. */
    static werte(name) {
        const a = Stoffarten.ARTEN[name];
        if (!a) return null;
        return {
            stoffart: name, rauheit: a.rauheit, metall: 0, glanz: a.glanz, saum: a.saum, saumstreuung: a.saumstreuung, saumfarbe: '',
            gewebe: { ...a.gewebe },
        };
    }
}
