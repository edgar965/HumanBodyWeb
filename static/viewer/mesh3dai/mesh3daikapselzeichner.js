/**
 * Mesh3daikapselzeichner — zeichnet eine Zeile der Seite „Mesh3D-AI“ als Gerüst aus Kapseln (14.10.2026): der ganze Körper, der nackte Körper, Hände/Füße und die Kleider haben alle diese Form (Punkte mit Eltern, Radius, Farbe).
 * Eingabe = die Außenfläche (Dummy: Kapseln, wie das Soll aussieht — der Datensatz erzeugt die Eingabe aus dem Modell selbst), gewünschte Ausgabe = Kapseln in den Farben des Soll, Ausgabe des Netzes = eingefärbte Kapseln
 * (orange) mit Fehlerpunkten je Punkt (grün 0 mm bis rot ab `fehler_rot_mm`) und auf Wunsch dem Soll als Drahtgitter-Geist. Die Ansichtsart (`d.modus`, `Mesh3daimaterial`) wählt, wie die Flächen aussehen; „Punkte / Gerüst“
 * ersetzt sie durch die Punktwolke (Eingabe) bzw. Kugeln und Linien (Soll, Ausgabe).
 * Hat die Zeile eine eigene Eingabe (`d.eingabe`, etwa „Nur Körper“: dieselbe Außenfläche mit Kleidern wie beim ganzen Körper), zeichnet das Eingabefeld diese statt der Daten der Zeile.
 */
import { Mesh3daiechtzeichner } from './mesh3daiechtzeichner.js';
import { Mesh3daikapseln } from './mesh3daikapseln.js';

export class Mesh3daikapselzeichner {
    /** @param {{punktradius?: number, eingabegroesse?: number, rohrradius?: number}} opt Kugelradius der Punkte, Punktgröße der Eingabe und Dicke der Linien im Gerüst, in m */
    constructor({ punktradius = 0.024, eingabegroesse = 0.016, rohrradius = 0.004 } = {}) {
        this.punktradius = punktradius;
        this.eingabegroesse = eingabegroesse;
        this.rohrradius = rohrradius;
    }

    _eingabe(inhalt, d) {
        const { beschreibung, teil } = d.eingabe ?? d;
        if (d.modus === 'punkte') inhalt.add(Mesh3daikapseln.punktwolke(beschreibung.punkte, teil.soll, teil.eingabe.punkte, d.id, this.eingabegroesse));
        else inhalt.add(Mesh3daikapseln.geruest(beschreibung.punkte, teil.soll, { modus: d.modus }));
    }

    _gerippe(punkte, lagen, farbe, kugeln = true) {
        return Mesh3daikapseln.gerippe(punkte, lagen, { farbe, kugelradius: kugeln ? this.punktradius * 0.7 : 0, rohrradius: this.rohrradius });
    }

    /** @param {THREE.Group} inhalt; @param {string} art 'eingabe' | 'soll' | 'ausgabe'; @param {{beschreibung, teil, id, geist, modus, eingabe?}} d */
    zeichnen(inhalt, art, d) {
        // Echte Daten (15.10.2026): keine Kapseln — Punktwolke und Rig (`Mesh3daiechtzeichner`).
        if (d.echt) {
            Mesh3daiechtzeichner.zeichnen(inhalt, art, d);
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
            inhalt.add(gerippe ? this._gerippe(punkte, teil.soll, null) : Mesh3daikapseln.geruest(punkte, teil.soll, { modus: d.modus }));
            return;
        }
        if (d.geist) inhalt.add(gerippe ? this._gerippe(punkte, teil.soll, Mesh3daikapseln.GEISTFARBE, false) : Mesh3daikapseln.geruest(punkte, teil.soll, { wand: true }));
        if (gerippe) inhalt.add(this._gerippe(punkte, teil.ausgabe, Mesh3daikapseln.AUSGABEFARBE));
        else inhalt.add(Mesh3daikapseln.geruest(punkte, teil.ausgabe, { modus: d.modus, tint: Mesh3daikapseln.AUSGABEFARBE, deckkraft: 0.8 }));
        inhalt.add(Mesh3daikapseln.fehlerpunkte(teil.ausgabe, teil.kennzahlen.je_gelenk_mm, beschreibung.fehler_rot_mm, this.punktradius));
    }
}
