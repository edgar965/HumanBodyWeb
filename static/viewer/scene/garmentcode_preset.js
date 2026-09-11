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
 * definierten Zustand — beim Anhaken wird jedes andere mit gemeinsamen
 * Reglern abgehakt, VOR dem Setzen (das Setzen merkt die aktive Liste).
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
    kasten(gruppe, setzt, liest, zuruecksetzt = null) {
        // Nicht mit `null` ueberschreiben: Der Passform-Kasten wird nach den
        // Gruppen gezeichnet und reicht den Ruecksetzer eigens durch.
        if (zuruecksetzt) this.zuruecksetzt = zuruecksetzt;
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
        // Auch `zurueck` merken: Ballerina nimmt den Absatz der Pumps auf
        // die Vorgabe — abgehakt soll er wiederkommen, nicht nur der Einstieg.
        const pfade = [...Object.keys(preset.werte), ...(preset.zurueck || [])];
        for (const pfad of pfade) vorher[pfad] = liest(pfad);
        this.davor[preset.schluessel] = vorher;
        this.aktiv.add(preset.schluessel);
        // `zurueck` (11.09.2026): Pfade, die das Preset auf die Vorgabe
        // nimmt — die Leggings das Bündchen, das eine frühere Fassung oder
        // „Eng anliegend" hinterlassen hat. Vor `setzt`, weil das den Bau
        // anstößt und die Werte merkt.
        if (this.zuruecksetzt && preset.zurueck?.length) this.zuruecksetzt(preset.zurueck);
        this._andereAbhaken(preset);         // vor `setzt` — siehe Modulkopf
        setzt(preset.werte);
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

    /**
     * Welche Voreinstellungen gerade angehakt sind — für das Gedaechtnis.
     *
     * Als Feld und nicht als `Set`: Es geht so, wie es ist, in den
     * `localStorage` und wieder heraus.
     */
    aktiveListe() {
        return Array.from(this.aktiv);
    }

    /**
     * Häkchen setzen, ohne Werte zu ändern.
     *
     * Beim Wiederherstellen stehen die Werte schon (`Garmentcodegedaechtnis`);
     * hier fehlt nur das Kaestchen. `davor` bleibt LEER: Es haelt die Werte,
     * die vor dem Anhaken galten, damit ein Abhaken sie zuruecknimmt. Nach
     * einem Seitenstart gibt es kein „davor" mehr — ein Abhaken laesst die
     * Regler dann stehen, statt sie auf einen erfundenen Stand zu ziehen.
     */
    anhaken(namen) {
        if (!Array.isArray(namen)) return 0;
        let gesetzt = 0;
        for (const schluessel of namen) {
            if (!this.liste.some((p) => p.schluessel === schluessel)) continue;
            this.aktiv.add(schluessel);
            const kaestchen = document.querySelector(
                `input[data-preset="${schluessel}"]`);
            if (kaestchen) kaestchen.checked = true;
            gesetzt += 1;
        }
        return gesetzt;
    }

    /** Das gezeichnete Preset zu einem Schlüssel — oder `null`. */
    preset(schluessel) {
        return this.liste.find((p) => p.schluessel === schluessel) || null;
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
