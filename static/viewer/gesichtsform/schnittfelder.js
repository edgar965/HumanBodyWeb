import { Schnittfeld } from './schnittfeld.js';

/**
 * Schnittfelder — alle Schnitte der Seite „Gesichtsform", waagerecht und senkrecht getrennt.
 *
 * Die Figur (ohne Kopf-Eigen, `ist`) gibt je Schnitt das Raster vor (1 mm, im Gesichtsoval der Figur).
 * Ergebnis und Ziel kommen auf eigenen Rastern (anderer Rahmen, anderes Oval) und werden darauf
 * umgelegt: linear zwischen gültigen Proben, `null`, wo die nächste gültige Probe weiter als `NAH` weg
 * ist — dort hat das Ziel keine Vorgabe (Haar, Augenmulde, Mundspalt am Netz).
 */
export class Schnittfelder {

    static NAH = 1.5;

    constructor(behaelter, pinsel, beiAenderung) {
        this.behaelter = behaelter;          // {waagerecht: Element, senkrecht: Element}
        this.pinsel = pinsel;
        this.beiAenderung = beiAenderung;
        this.felder = [];
    }

    setzen(daten, ziel) {
        for (const kasten of Object.values(this.behaelter)) kasten.innerHTML = '';
        this.felder = [];
        const guete = (daten.guete || {}).schnitte || [];
        for (const p of daten.ist.schnitte) {
            const kasten = this.behaelter[p.art];
            if (!kasten) continue;
            const erg = Schnittfelder.finde((daten.ergebnis || {}).schnitte, p);
            const zi = Schnittfelder.finde((ziel || {}).schnitte, p);
            const feld = new Schnittfeld(kasten, p, this.pinsel, this.beiAenderung);
            feld.setzen(p.z, erg ? Schnittfelder.umlegen(erg, p.u) : null,
                zi ? Schnittfelder.umlegen(zi, p.u) : p.z.slice(),
                guete.find(g => g.art === p.art && Math.abs(g.lage - p.lage) < 0.2));
            this.felder.push(feld);
        }
    }

    /** Das Ziel aller Schnitte — `[{art, lage, u, z}]` in mm. */
    ziel() { return this.felder.map(f => f.ziel()); }

    /** „Ziel = Figur": das Ziel jedes Schnitts auf die gezeigte Figur (mit Kopf-Eigen, sonst ohne). */
    zuruecksetzen() {
        for (const f of this.felder) {
            f.zielwerte = (f.ergebnis || f.ist).slice();
            f.zeichnen();
        }
    }

    static finde(liste, p) {
        return (liste || []).find(q => q.art === p.art && Math.abs(q.lage - p.lage) < 0.05) || null;
    }

    /** Profil `q` ({u, z}) auf das Raster `u` legen. */
    static umlegen(q, u) {
        const gueltig = q.u.map((x, i) => [x, q.z[i]]).filter(([, z]) => z !== null && z !== undefined);
        return u.map((x) => {
            let links = null, rechts = null;
            for (const probe of gueltig) {
                if (probe[0] <= x && (!links || probe[0] > links[0])) links = probe;
                if (probe[0] >= x && (!rechts || probe[0] < rechts[0])) rechts = probe;
            }
            const nah = [links, rechts].filter(p => p && Math.abs(p[0] - x) <= Schnittfelder.NAH);
            if (!nah.length) return null;
            if (nah.length === 1 || rechts[0] === links[0]) return nah[0][1];
            const w = (x - links[0]) / (rechts[0] - links[0]);
            return links[1] + w * (rechts[1] - links[1]);
        });
    }
}
