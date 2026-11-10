/**
 * Meshgenesiskapselzeichner — zeichnet eine Zeile der Seite „Mesh-Genesis“ als Gerüst aus Kapseln (14.10.2026): der ganze Körper, der nackte Körper, Hände/Füße und die Kleider haben alle diese Form (Punkte mit Eltern, Radius, Farbe).
 * Eingabe = die Außenfläche (Dummy: Kapseln, wie das Soll aussieht — der Datensatz erzeugt die Eingabe aus dem Modell selbst), gewünschte Ausgabe = Kapseln in den Farben des Soll, Ausgabe des Netzes = eingefärbte Kapseln
 * (orange) mit Fehlerpunkten je Punkt (grün 0 mm bis rot ab `fehler_rot_mm`) und auf Wunsch dem Soll als Drahtgitter-Geist. Die Ansichtsart (`d.modus`, `Meshgenesismaterial`) wählt, wie die Flächen aussehen; „Punkte / Gerüst“
 * ersetzt sie durch die Punktwolke (Eingabe) bzw. Kugeln und Linien (Soll, Ausgabe).
 * Hat die Zeile eine eigene Eingabe (`d.eingabe`, etwa „Nur Körper“: dieselbe Außenfläche mit Kleidern wie beim ganzen Körper), zeichnet das Eingabefeld diese statt der Daten der Zeile.
 */
import { Meshgenesisechtzeichner } from './meshgenesisechtzeichner.js';
import { Meshgenesiskapseln } from './meshgenesiskapseln.js';

export class Meshgenesiskapselzeichner {
    /** @param {{punktradius?: number, eingabegroesse?: number, rohrradius?: number}} opt Kugelradius der Punkte, Punktgröße der Eingabe und Dicke der Linien im Gerüst, in m */
    constructor({ punktradius = 0.024, eingabegroesse = 0.016, rohrradius = 0.004 } = {}) {
        this.punktradius = punktradius;
        this.eingabegroesse = eingabegroesse;
        this.rohrradius = rohrradius;
    }

    _eingabe(inhalt, d) {
        const { beschreibung, teil } = d.eingabe ?? d;
        if (d.modus === 'punkte') inhalt.add(Meshgenesiskapseln.punktwolke(beschreibung.punkte, teil.soll, teil.eingabe.punkte, d.id, this.eingabegroesse));
        else inhalt.add(Meshgenesiskapseln.geruest(beschreibung.punkte, teil.soll, { modus: d.modus }));
    }

    _gerippe(punkte, lagen, farbe, kugeln = true) {
        return Meshgenesiskapseln.gerippe(punkte, lagen, { farbe, kugelradius: kugeln ? this.punktradius * 0.7 : 0, rohrradius: this.rohrradius });
    }

    /** @param {THREE.Group} inhalt; @param {string} art 'eingabe' | 'soll' | 'ausgabe'; @param {{beschreibung, teil, id, geist, modus, eingabe?}} d */
    zeichnen(inhalt, art, d) {
        // Echte Daten (15.10.2026): keine Kapseln — Punktwolke und Rig (`Meshgenesisechtzeichner`).
        if (d.echt) {
            Meshgenesisechtzeichner.zeichnen(inhalt, art, d);
            return;
        }
        if (art === 'eingabe') {
            this._eingabe(inhalt, d);
            return;
        }
        const { beschreibung, teil } = d;
        const punkte = beschreibung.punkte;
        const gerippe = d.modus === 'punkte';
        if (art === 'soll') {
            inhalt.add(gerippe ? this._gerippe(punkte, teil.soll, null) : Meshgenesiskapseln.geruest(punkte, teil.soll, { modus: d.modus }));
            return;
        }
        if (d.geist) inhalt.add(gerippe ? this._gerippe(punkte, teil.soll, Meshgenesiskapseln.GEISTFARBE, false) : Meshgenesiskapseln.geruest(punkte, teil.soll, { wand: true }));
        if (gerippe) inhalt.add(this._gerippe(punkte, teil.ausgabe, Meshgenesiskapseln.AUSGABEFARBE));
        else inhalt.add(Meshgenesiskapseln.geruest(punkte, teil.ausgabe, { modus: d.modus, tint: Meshgenesiskapseln.AUSGABEFARBE, deckkraft: 0.8 }));
        inhalt.add(Meshgenesiskapseln.fehlerpunkte(teil.ausgabe, teil.kennzahlen.je_gelenk_mm, beschreibung.fehler_rot_mm, this.punktradius));
    }
}
