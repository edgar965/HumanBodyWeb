/**
 * Fotogenesismeshfigur — Feld 3 der Mesh-Zeile der Jobseite: die Genesis-Figur, die `Genesis9.meshgenesis` in die geometrische Figur eingepasst hat (28.10.2026, Edgar: „eine extra Zeile
 * ganz oben … das dritte Bild mit dem Mesh Modell anstelle von Genesis“).
 *
 * Daten: `genesis` in `<Job>/abnahme/training_figur.json` (`mesh_auf_genesis.py`, `figur_eintragen`): je Foto die Punkte der Figur in dessen Haltung, Dreiecke des Käfigs, Zahlen
 * der Einpassung (`masse`), seit 28.10.2026 abends Farben je Punkt aus den Fotos (`farben`, wie die geometrische Figur — Edgar: „warum ist das Genesis Modell rechts grau? fixe“)
 * und die Abnahme. Die Daten teilt sich der Zeichner mit `Fotogenesistrainingfigur` (ein Abruf). Ansichtsarten wie die anderen Felder (Ersatzmaterial auf Ebene 1); „Textur“ zeigt die
 * Farben, ohne sie (ältere Läufe) die Oberfläche.
 */
import { Fotogenesisnetz } from './fotogenesisnetz.js';
import { Fotogenesistrainingfigur } from './fotogenesistrainingfigur.js';

export class Fotogenesismeshfigur {
    /** @param {Fotogenesistrainingfigur} quelle der Zeichner der geometrischen Figur (dieselbe Datei) */
    constructor(quelle) {
        this.quelle = quelle;
        this.bereit = quelle.bereit;
        this._netze = new Map();
    }

    get daten() {
        return this.quelle.daten;
    }

    /** Zahlen der Einpassung (`masse` des Laufs) oder null. */
    get masse() {
        return this.daten?.genesis?.masse ?? null;
    }

    /** Figur und ihre Stücke: die Augäpfel (`augen`, seit 28.10.2026 abends, Edgar: „nur die augen fehlen“; der Käfig hat keine) und die Hüllen aus der geometrischen Figur über
     *  Haar und Kleidung (`haar`, `kleid`; Edgar: „Die Umrisse des Genesis sind aber kleiner als die Vorgabe“ — der Körper liegt dort innen, `mesh_auf_genesis.huellen`). */
    _netz(nr) {
        const g = this.daten?.genesis, punkte = g?.fotos?.[String(nr + 1)];
        if (!punkte) return null;
        if (this._netze.has(nr)) return this._netze.get(nr);
        const netze = [Fotogenesistrainingfigur.stueck(punkte, g.dreiecke, g.farben)];
        for (const stueck of Fotogenesismeshfigur.STUECKE) {
            const p = g[stueck]?.fotos?.[String(nr + 1)];
            if (p) netze.push(Fotogenesistrainingfigur.stueck(p, g[stueck].dreiecke, g[stueck].farben));
        }
        this._netze.set(nr, netze);
        return netze;
    }

    /** Kleidung seit 30.10.2026 je Art ein Stück (Edgar: „Unterhose nicht erkannt (stattdessen T-Shirt an der Stelle gebaut)“, `Genesishuellen`); `kleid` = sonstige
     *  Kleidung bzw. die eine Hülle älterer Läufe. */
    static STUECKE = ['augen', 'haar', 'kleid', 'oberteil', 'unterteil', 'socken'];

    /** Zeichner von `Meshgenesisansicht`: `d = {nr, modus}`. */
    zeichnen(inhalt, _art, d) {
        if (!this.daten) {
            inhalt.userData.hinweis = this.quelle.fehler ? `Figur nicht geladen: ${this.quelle.fehler}` : 'Figur wird geladen …';
            return;
        }
        const netze = this._netz(d.nr);
        if (!netze) {
            inhalt.userData.hinweis = 'Noch keine Genesis-Figur aus der Mesh-Methode für dieses Foto (mesh_auf_genesis.py).';
            return;
        }
        for (const netz of netze) inhalt.add(netz);
        // „Textur“: die eigenen Farben, wenn der Lauf sie hat (sonst Oberfläche); alle anderen Arten mit dem Ersatzmaterial — wie `Fotogenesistrainingfigur`
        const farbig = !!this.daten.genesis.farben;
        inhalt.userData.genesisErsatz = d.modus === 'textur' ? (farbig ? undefined : Fotogenesisnetz.ersatz('oberflaeche')) : Fotogenesisnetz.ersatz(d.modus);
    }
}
