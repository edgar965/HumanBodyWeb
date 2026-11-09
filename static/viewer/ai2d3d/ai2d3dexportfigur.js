import { Mesh3daianatomiehuelle } from '../mesh3dai/mesh3daianatomiehuelle.js';
import { Mesh3daiexportquelle } from '../mesh3dai/mesh3daiexportquelle.js';
import { Mesh3daifigurbewegung } from '../mesh3dai/mesh3daifigurbewegung.js';
import { Mesh3daiflaechennetz } from '../mesh3dai/mesh3daiflaechennetz.js';

/**
 * Ai2d3dexportfigur — die Figur eines 2d-3d-AI-Tests für die Exportleiste (31.10.2026, Server `Ai2d3dexportquelle`).
 *
 * Edgar: „baue diese Exportleiste sowohl auf die Mesh3d-ai jobs … als auch für /2d-3d-AI/test/edgartrip/". Feld 3 der Seite zeigt die Figur aus den Fotos als gehäutetes Anzeigenetz in der
 * Haltung der Fotos (`Ai2d3dtestfigur`) — ohne Skelett, nicht animierbar. Für den Export entsteht dieselbe Figur als Genesis9Modell in der Ruhelage mit DEMSELBEN Code wie auf der
 * Mesh3D-AI-Testseite (`Mesh3daifigurbewegung` ohne Feld): Regler der Form, Haut aus den Kacheln der Fotos (`figur_genesis.fototextur`, `Ai2d3dfigur._kacheln`), die Stücke aus den Fotos
 * am Skelett. Daten aus `/api/2d3dai/<job>/figur/` (wie `/api/mesh3dai/test/<kennung>/`) und `…/kleider/<g>/` (wirksame Wahl). Gebaut wird erst beim ersten Export.
 */
export class Ai2d3dexportfigur {

    /** @param adresse `/api/2d3dai/<job>/figur/` (`daten.test.adresse` der Seite) @param feld das Feld „Genesis-Modell“ (`Ai2d3dseite.genesisfeld`) — dann spielt die Abspielleiste
     *  darin dieselbe Figur, die exportiert wird (`Ai2d3dbewegung`, 31.10.2026); ohne Feld nur für den Export
     *  @param nackt ohne Stücke und ohne die Haut der KI (04.11.2026, Feld 1 der dritten Zeile: die Einpassung des Mesh3D-AI-Tests, `Ai2d3dgenesiszeile`) */
    constructor(adresse, feld = null, { nackt = false } = {}) {
        this.adresse = adresse;
        this.nackt = nackt;
        const ohneFeld = { neuZeigen() {}, zeichnen() {} };
        this.bewegung = new Mesh3daifigurbewegung(feld ?? ohneFeld, () => this._quelle());
        this.export = new Mesh3daiexportquelle(() => this.bewegung);
    }

    bvh() {
        return null;
    }

    /** Die Figur für den Export ist die bewegte (`Mesh3daiexportquelle`); ob das Anatomie-Stück darin fehlt, entscheidet dort `Mesh3daianatomiehuelle` nach der Regel des Servers. */
    async modell(angaben) {
        return this.export.modell(angaben);
    }

    /** Dieselbe Figur mit Kleidern und Haar für die Abspielleiste der Zeile 1 (`Ai2d3dbewegung`); `zeile1` = Form der Zeile 1 (`Ai2d3dzeile1bewegung`). */
    async koerperQuelle() {
        const q = await this._quelle();
        return q && { ...q, schluessel: `${q.schluessel}|zeile1` };
    }

    async _quelle() {
        const antwort = await fetch(this.adresse);
        const d = await antwort.json();
        if (!antwort.ok) throw new Error(d.error || `HTTP ${antwort.status}`);
        if (!d.figur_genesis) return null;
        const g = d.info.geschlecht;
        if (this.nackt) {
            const { fototextur: _haut, ...figur } = d.figur_genesis;
            return { schluessel: `${this.adresse}|${g}|nackt`, figur, stuecke: [], knochen: d.rig.knochen.map(k => k.name), ruhezentren: d.ruhezentren, ohneKnochen: [] };
        }
        const liste = await fetch(`${this.adresse}kleider/${g}/`).then(a => (a.ok ? a.json() : null)).catch(() => null);
        this._liste = liste;
        const stuecke = [];
        for (const st of liste?.stuecke ?? []) {
            const adresse = st.art !== 'haut' && st.wahl !== 'aus' ? st[st.wahl]?.netz : null;
            if (!adresse) continue;
            const netz = await Mesh3daiflaechennetz.holen(null, adresse).catch(fehler => { console.warn(`Ai2d3dexportfigur: ${st.id} nicht geladen (${fehler.message})`); return null; });
            if (netz) stuecke.push({ id: st.id, art: st.art, netz });
        }
        return { schluessel: `${this.adresse}|${g}`, figur: d.figur_genesis, stuecke, knochen: d.rig.knochen.map(k => k.name), ruhezentren: d.ruhezentren, ohneKnochen: [],
                 anatomieGetragen: Mesh3daianatomiehuelle.getragen(liste), zeile1: d.zeile1_form || null };
    }
}
