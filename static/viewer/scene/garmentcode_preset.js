/**
 * Voreinstellungen im Reglerbereich — fertige Kombinationen zum Anhaken.
 *
 * Edgar, 08.09.2026: „bei Online Tool sind das diese Einstellungen, kannst
 * du mir ein preset machen bei den ärmeln (checkbox) dafür?"
 *
 * EIN HÄKCHEN SETZT MEHRERE REGLER — und nimmt sie auch zurück
 * ===========================================================
 * Beim Anhaken werden die Werte des Presets gesetzt und die betroffenen
 * Schieber sichtbar nachgezogen; beim Abhaken kommen die VORHER geltenden
 * Werte zurück, nicht die Vorgabe des Stücks. Sonst verlöre man mit dem
 * Häkchen auch das, was man vorher selbst eingestellt hatte.
 *
 * DAS HÄKCHEN GEHT VON SELBST WEG, wenn danach einer seiner Regler von Hand
 * bewegt wird (`pruefen`). Ein Kästchen, das „eng anliegend" behauptet,
 * während die Ärmelweite längst wieder auf 2,0 steht, ist schlimmer als
 * keines — es sagt etwas Falsches über den Zustand.
 *
 * ZWEI PRESETS SCHLIESSEN SICH AUS, solange sie dieselben Regler anfassen:
 * „Eng anliegend, lang" und „Weit fallend" beide zu haken hätte keinen
 * definierten Zustand. Beim Anhaken wird deshalb jedes andere Preset mit
 * gemeinsamen Reglern abgehakt.
 */
import { garmentcodeReglerhilfe } from './garmentcode_reglerhilfe.js';

class GarmentcodePreset {
    constructor() {
        /** Zuletzt vom Server geliefert. */
        this.liste = [];
        /** Was vor dem Anhaken galt: {schluessel: {pfad: wert}}. */
        this.davor = {};
        /** Welche gerade gehakt sind. */
        this.aktiv = new Set();
    }

    /** Die Presets eines Kleidungsstücks übernehmen. */
    setzen(liste) {
        this.liste = Array.isArray(liste) ? liste : [];
        this.davor = {};
        this.aktiv.clear();
    }

    /** Die Presets einer Gruppe, für den Reglerbereich. */
    fuerGruppe(gruppe) {
        return this.liste.filter((p) => p.gruppe === gruppe);
    }

    /**
     * Der Kasten mit den Kästchen einer Gruppe.
     *
     * `setzt` bekommt die Werte des Presets und trägt sie in den
     * Reglerbereich; `liest` liefert den aktuell geltenden Wert eines
     * Pfades, damit das Abhaken ihn zurückgeben kann.
     */
    kasten(gruppe, setzt, liest) {
        const presets = this.fuerGruppe(gruppe);
        if (!presets.length) return null;
        const kasten = document.createElement('div');
        kasten.className = 'gc-presets';
        for (const preset of presets) {
            kasten.appendChild(this._zeile(preset, setzt, liest));
        }
        return kasten;
    }

    _zeile(preset, setzt, liest) {
        const zeile = document.createElement('label');
        zeile.className = 'gc-preset';
        const kaestchen = document.createElement('input');
        kaestchen.type = 'checkbox';
        kaestchen.dataset.preset = preset.schluessel;
        const text = document.createElement('span');
        text.textContent = preset.titel;
        zeile.appendChild(kaestchen);
        zeile.appendChild(text);
        kaestchen.addEventListener('change', () => {
            if (kaestchen.checked) this._anhaken(preset, setzt, liest);
            else this._abhaken(preset, setzt);
        });
        // Der Hinweis nennt die gemessene Wirkung — er ist der Grund, ein
        // Preset zu nehmen, und gehört deshalb in dieselbe Karte wie die
        // Hilfe der Regler.
        garmentcodeReglerhilfe.anhaengen(zeile, preset.titel, {
            text: preset.hinweis || '',
            bedingung: '',
            original: Object.entries(preset.werte)
                .map(([pfad, wert]) => `${pfad} = ${wert}`).join(' · '),
        });
        return zeile;
    }

    _anhaken(preset, setzt, liest) {
        const vorher = {};
        for (const pfad of Object.keys(preset.werte)) vorher[pfad] = liest(pfad);
        this.davor[preset.schluessel] = vorher;
        this.aktiv.add(preset.schluessel);
        setzt(preset.werte);
        this._andereAbhaken(preset);
    }

    _abhaken(preset, setzt) {
        const vorher = this.davor[preset.schluessel];
        this.aktiv.delete(preset.schluessel);
        delete this.davor[preset.schluessel];
        if (vorher) setzt(vorher);
    }

    /** Presets, die dieselben Regler anfassen, können nicht beide gelten. */
    _andereAbhaken(preset) {
        const meine = new Set(Object.keys(preset.werte));
        for (const andere of this.liste) {
            if (andere.schluessel === preset.schluessel) continue;
            const gemeinsam = Object.keys(andere.werte).some((p) => meine.has(p));
            if (!gemeinsam) continue;
            this.aktiv.delete(andere.schluessel);
            delete this.davor[andere.schluessel];
            const kaestchen = document.querySelector(
                `input[data-preset="${andere.schluessel}"]`);
            if (kaestchen) kaestchen.checked = false;
        }
    }

    /**
     * Nach einer Änderung von Hand: Häkchen entfernen, wo das Preset nicht
     * mehr gilt. `liest` liefert den geltenden Wert eines Pfades.
     */
    pruefen(geaenderterPfad, liest) {
        for (const schluessel of Array.from(this.aktiv)) {
            const preset = this.liste.find((p) => p.schluessel === schluessel);
            if (!preset || !(geaenderterPfad in preset.werte)) continue;
            if (this._gleich(liest(geaenderterPfad), preset.werte[geaenderterPfad])) {
                continue;
            }
            this.aktiv.delete(schluessel);
            delete this.davor[schluessel];
            const kaestchen = document.querySelector(
                `input[data-preset="${schluessel}"]`);
            if (kaestchen) kaestchen.checked = false;
        }
    }

    /** Zahlen kommen als Schieberwert zurück — auf zwei Stellen vergleichen. */
    _gleich(a, b) {
        if (typeof a === 'number' && typeof b === 'number') {
            return Math.abs(a - b) < 0.005;
        }
        return a === b;
    }
}

export const garmentcodePreset = new GarmentcodePreset();
