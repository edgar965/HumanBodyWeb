import { Stoffarten } from './stoffarten.js';

/**
 * Eigenkleidstoff — der Stoff eines eigenen Stücks (Oberteil, Hose, Socken): dieselben Werte wie am Daz-Stück (`Stueckstoff`, `Stoffarten`, `Stoffshader`), abgelegt
 * als Zahlen in den Reglern der Figur (25.10.2026 nachts, Auftrag Edgar: Stoffart, Webart, Fäden je cm, Glanz, Glanzsaum, Relief „auch an den eigenen Stücken“).
 *
 * WARUM ZAHLEN: Die Werte eines eigenen Stücks stehen in `inst.regler` unter `kleid:<art>:<feld>` (`Eigenkleidwerte`) und reisen mit „Modell speichern“; der Server
 * übergeht unbekannte Namen, erwartet aber Zahlen. Darum stehen Stoffart und Bindung als Index in `STOFFARTEN` bzw. `GEWEBE`, die Glanzsaumfarbe als 0xRRGGBB
 * (−1 = wie der Stoff) und alle Anteile in Prozent — `stoff(werte)` macht daraus das Objekt in der Form von `Stoffarten.werte`, das `Stoffshader.werte` liest.
 * Die Felder hier sind der Block „Stoff“ in `Eigenkleidfelder`; die Zeilen dazu baut `Genesis9eigenkleidstoff` mit `Stueckstoffzeilen` (wie am Daz-Stück).
 * Ohne Three.js und DOM, in Node prüfbar.
 */
export class Eigenkleidstoff {

    /** Index 0 = „eigene Werte“ (keine Vorwahl), dann die Arten in der Reihenfolge von `Stoffarten.ARTEN`. */
    static STOFFARTEN = ['', ...Object.keys(Stoffarten.ARTEN)];
    /** Index 0 = keine Bindung (`Stoffshader` Art 0); die Namen sind die Schlüssel von `Stoffshader.ARTEN`. */
    static GEWEBE = ['', 'leinwand', 'koeper', 'jersey', 'satin', 'narbung'];

    /** Die Stofffelder (`zeile: 'stoff'` — gebaut von `Genesis9eigenkleidstoff`, nicht von den Schiebern des Kastens); `rauheit` steht beim Stück selbst. */
    static FELDER = [
        { feld: 'stoffart', block: 'stoff', zeile: 'stoff', titel: 'Stoffart', wahl: Eigenkleidstoff.STOFFARTEN, vorgabe: 0 },
        { feld: 'metall', block: 'stoff', zeile: 'stoff', titel: 'Metall', min: 0, max: 100, schritt: 1, einheit: '%', vorgabe: 0 },
        { feld: 'glanz', block: 'stoff', zeile: 'stoff', titel: 'Glanz', min: 0, max: 200, schritt: 5, einheit: '%', vorgabe: 100 },
        { feld: 'glanzsaum', block: 'stoff', zeile: 'stoff', titel: 'Glanzsaum', min: 0, max: 100, schritt: 5, einheit: '%', vorgabe: 0 },
        { feld: 'glanzsaum_weich', block: 'stoff', zeile: 'stoff', titel: 'Saum weich', min: 0, max: 100, schritt: 5, einheit: '%', vorgabe: 80 },
        { feld: 'glanzsaum_farbe', block: 'stoff', zeile: 'stoff', titel: 'Saumfarbe', farbe: true, leer: true, vorgabe: -1 },
        { feld: 'relief', block: 'stoff', zeile: 'stoff', titel: 'Relief', min: 0, max: 200, schritt: 5, einheit: '%', vorgabe: 100 },
        { feld: 'gewebe', block: 'stoff', zeile: 'stoff', titel: 'Gewebe', wahl: Eigenkleidstoff.GEWEBE, vorgabe: 0 },
        { feld: 'faeden', block: 'stoff', zeile: 'stoff', titel: 'Fäden je cm', min: 0.5, max: 40, schritt: 0.5, einheit: 'je cm', vorgabe: 5 },
        { feld: 'struktur', block: 'stoff', zeile: 'stoff', titel: 'Struktur', min: 0, max: 100, schritt: 5, einheit: '%', vorgabe: 40 },
    ];

    /** '#rrggbb' oder '' aus der abgelegten Zahl (−1 = keine eigene Farbe). */
    static hex(zahl) {
        const n = Number(zahl);
        return Number.isFinite(n) && n >= 0 ? `#${(Math.round(n) & 0xffffff).toString(16).padStart(6, '0')}` : '';
    }

    /** Werte des Stücks (Feldeinheiten, `Eigenkleidwerte.alle`) → `stoff` in der Form von `Stoffarten.werte` (für `Stoffshader.werte`). */
    static stoff(werte) {
        const w = (feld, vorgabe) => (Number.isFinite(Number(werte?.[feld])) ? Number(werte[feld]) : vorgabe);
        const art = Eigenkleidstoff.GEWEBE[Math.round(w('gewebe', 0))] || '';
        return {
            stoffart: Eigenkleidstoff.STOFFARTEN[Math.round(w('stoffart', 0))] || '',
            rauheit: Math.min(1, Math.max(0, w('rauheit', 85) / 100)), metall: Math.min(1, Math.max(0, w('metall', 0) / 100)),
            glanz: w('glanz', 100) / 100, saum: w('glanzsaum', 0) / 100, saumstreuung: w('glanzsaum_weich', 80) / 100,
            saumfarbe: Eigenkleidstoff.hex(w('glanzsaum_farbe', -1)), relief: w('relief', 100) / 100,
            gewebe: art ? { art, faeden: w('faeden', 5), staerke: w('struktur', 40) / 100 } : { art: 'glatt', faeden: 0, staerke: 0 },
        };
    }

    /** Eine Stoffart → die Werte, die sie setzt (Feldeinheiten): alle Stofffelder außer Relief (das gehört dem Stück, wie am Daz-Stück) — oder null. */
    static ausStoffart(name) {
        const s = Stoffarten.werte(name);
        if (!s) return null;
        const prozent = v => Math.round(v * 100);
        return {
            stoffart: Eigenkleidstoff.STOFFARTEN.indexOf(name), rauheit: prozent(s.rauheit), metall: 0, glanz: prozent(s.glanz), glanzsaum: prozent(s.saum),
            glanzsaum_weich: prozent(s.saumstreuung), glanzsaum_farbe: -1, gewebe: Math.max(0, Eigenkleidstoff.GEWEBE.indexOf(s.gewebe.art)),
            faeden: s.gewebe.faeden, struktur: prozent(s.gewebe.staerke),
        };
    }

    /** Fäden und Struktur, die eine Bindung beim Umschalten bekommt (Feldeinheiten). */
    static gewebevorgabe(index) {
        const g = Stoffarten.gewebevorgabe(Eigenkleidstoff.GEWEBE[index] || 'leinwand');
        return { faeden: g.faeden, struktur: Math.round(g.staerke * 100) };
    }
}
