/**
 * Kleidungszustand — die Einstellungen EINES Kleidungsstücks an einer Figur:
 * Anpasswerte, Farbe, Material und die fünf Regionsverschiebungen.
 *
 * Umbau 16.08.2026, Punkt 10/11 des Auftrags: Dieser Datensatz hat DREIZEHN
 * Felder und verlässt seine Entstehungsstelle — er wird beim Anpassen gebaut
 * (`_doKleiderFit`, `_doGarmentFit`), beim Speichern der Szene abgelegt
 * (`character.js toJSON`), beim Laden wieder eingelesen
 * (`charakter_zubehoer.js`), in die Regler zurückgeschrieben
 * (`kleidung_anpassen.js`, `prop_garments.js`) und beim Entfernen gelöscht. An
 * jeder dieser Stellen stand die Feldliste erneut. Ein Feld dazu hieß: sechs
 * Stellen ändern — oder eine übersehen.
 *
 * Als reine Datenklasse mit `zuJson()`/`ausJson()`: Was in der Szenendatei
 * steht, bleibt unverändert (dieselben Namen, dieselben Werte).
 */
import { Protokoll } from '../gemeinsam/protokoll.js';
export class Kleidungszustand {

    /** Die fünf Regionen von oben nach unten. */
    static REGIONEN = ['Top', 'Upper', 'Mid', 'Lower', 'Bottom'];

    /**
     * Werte, wenn ein Feld fehlt. Sie stammen aus `charakter_zubehoer.js`, das
     * beim Laden einer Szene bisher als einzige Stelle Vorgaben kannte — die
     * Anpassfunktionen setzten alle Felder selbst. Ohne diese Tabelle bekäme
     * ein altes Kleidungsstück ohne `stiffness` den Wert 0 statt 0,5 und läge
     * anders am Körper.
     */
    static VORGABEN = {
        offset: 0, stiffness: 0.5, minDist: 3, crotchFloor: 0, lift: 0,
        crotchDepth: 0, roughness: 0.8, metalness: 0.0,
    };
    static VORGABE_FARBE = [0.3, 0.35, 0.5];

    /** Anpasswerte: Feldname → Reglerkennung ohne Vorsilbe und Teiler. */
    static ANPASSWERTE = [
        ['offset', 'offset', 1000],
        ['stiffness', 'stiffness', 100],
        ['minDist', 'min-dist', 1],
        ['crotchFloor', 'crotch-floor', 1],
        ['lift', 'lift', 1],
        ['crotchDepth', 'crotch-depth', 1],
    ];

    /** Materialwerte: Feldname → Reglerkennung, immer durch 100. */
    static MATERIALWERTE = [['roughness', 'roughness'], ['metalness', 'metalness']];

    constructor(werte = {}) {
        for (const [feld] of [...Kleidungszustand.ANPASSWERTE,
                              ...Kleidungszustand.MATERIALWERTE]) {
            this[feld] = werte[feld] ?? Kleidungszustand.VORGABEN[feld];
        }
        this.color = werte.color || [...Kleidungszustand.VORGABE_FARBE];
        for (const region of Kleidungszustand.REGIONEN) {
            this['region' + region] = werte['region' + region] || 0;
        }
    }

    /**
     * Zustand aus den Reglern der Seite lesen.
     *
     * @param vorsilbe  'kleider' oder 'garment' — dieselben Regler, zwei Reiter
     * @param farbe     THREE.Color
     * @param vorher    bisheriger Zustand; seine Regionsverschiebungen bleiben,
     *                  weil die Regler sie nicht führen
     * @param wert      (id) => Zahl, üblicherweise `_sliderVal`
     */
    static ausReglern(vorsilbe, farbe, vorher, wert) {
        const zustand = new Kleidungszustand(vorher || {});
        for (const [feld, kennung, teiler] of Kleidungszustand.ANPASSWERTE) {
            zustand[feld] = wert(`${vorsilbe}-${kennung}`) / teiler;
        }
        for (const [feld, kennung] of Kleidungszustand.MATERIALWERTE) {
            zustand[feld] = wert(`${vorsilbe}-${kennung}`) / 100;
        }
        zustand.color = [farbe.r, farbe.g, farbe.b];
        return zustand;
    }

    /** Anpasswerte als Suchparameter — was der Server zum Anpassen braucht. */
    inFrage(frage) {
        frage.set('offset', this.offset.toFixed(4));
        frage.set('stiffness', this.stiffness.toFixed(2));
        frage.set('min_dist', this.minDist);
        frage.set('crotch_floor', this.crotchFloor);
        frage.set('lift', this.lift);
        frage.set('crotch_depth', this.crotchDepth);
        frage.set('color_r', this.color[0].toFixed(3));
        frage.set('color_g', this.color[1].toFixed(3));
        frage.set('color_b', this.color[2].toFixed(3));
        return frage;
    }

    /**
     * Zustand in die Regler schreiben — die Umkehrung von
     * `ausReglernUebernehmen`. Vorher standen dafür elf fast gleiche Blöcke
     * (`if (el) { el.value = …; el.dispatchEvent(new Event('input')); }`).
     *
     * Das `input`-Ereignis muss mit, damit die Wertanzeige neben dem Regler
     * folgt; `state._syncingSliders` verhindert dabei, dass die Änderung als
     * Benutzereingabe gilt.
     */
    inRegler(vorsilbe) {
        for (const [feld, kennung, teiler] of Kleidungszustand.ANPASSWERTE) {
            Kleidungszustand._setzen(`${vorsilbe}-${kennung}`,
                                     Math.round(this[feld] * teiler));
        }
        for (const [feld, kennung] of Kleidungszustand.MATERIALWERTE) {
            Kleidungszustand._setzen(`${vorsilbe}-${kennung}`,
                                     Math.round(this[feld] * 100));
        }
        for (const region of Kleidungszustand.REGIONEN) {
            Kleidungszustand._setzen(
                `${vorsilbe}-region-${region.toLowerCase()}`,
                Math.round(this['region' + region] * 100));
        }
        return this;
    }

    static _setzen(id, wert) {
        const feld = document.getElementById(id);
        if (!feld) { Protokoll.debug('kleidungszustand', `kein Feld ${id}`); return; }
        feld.value = wert;
        feld.dispatchEvent(new Event('input'));
    }

    /** Farbe als #rrggbb, wie ein Farbwähler sie erwartet. */
    farbhex(hexAus) {
        return hexAus(this.color[0], this.color[1], this.color[2]);
    }

    /** Flaches Objekt, wie es bisher in der Szenendatei stand. */
    zuJson() {
        const daten = {};
        for (const [feld] of Kleidungszustand.ANPASSWERTE) daten[feld] = this[feld];
        for (const [feld] of Kleidungszustand.MATERIALWERTE) daten[feld] = this[feld];
        daten.color = [...this.color];
        for (const region of Kleidungszustand.REGIONEN) {
            daten['region' + region] = this['region' + region];
        }
        return daten;
    }

    static ausJson(daten) {
        return new Kleidungszustand(daten || {});
    }

    /**
     * Reglerstände in einen bestehenden Zustand schreiben — anders als
     * `ausReglern` werden hier AUCH die Regionsverschiebungen übernommen, denn
     * beim Bedienen der Regler sind sie gemeint.
     */
    ausReglernUebernehmen(vorsilbe, wert, farbe) {
        for (const [feld, kennung, teiler] of Kleidungszustand.ANPASSWERTE) {
            this[feld] = wert(`${vorsilbe}-${kennung}`) / teiler;
        }
        for (const [feld, kennung] of Kleidungszustand.MATERIALWERTE) {
            this[feld] = wert(`${vorsilbe}-${kennung}`) / 100;
        }
        for (const region of Kleidungszustand.REGIONEN) {
            const kennung = region.toLowerCase();
            this['region' + region] = wert(`${vorsilbe}-region-${kennung}`) / 100;
        }
        if (farbe) this.color = [farbe.r, farbe.g, farbe.b];
        return this;
    }
}
