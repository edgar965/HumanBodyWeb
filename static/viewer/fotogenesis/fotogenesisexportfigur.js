import { Meshgenesisanatomiehuelle } from '../meshgenesis/meshgenesisanatomiehuelle.js';
import { Meshgenesisexportquelle } from '../meshgenesis/meshgenesisexportquelle.js';
import { Meshgenesisfigurbewegung } from '../meshgenesis/meshgenesisfigurbewegung.js';
import { Meshgenesisflaechennetz } from '../meshgenesis/meshgenesisflaechennetz.js';

/**
 * Fotogenesisexportfigur — die Figur eines Foto-Genesis-Tests für die Exportleiste (31.10.2026, Server `Fotogenesisexportquelle`).
 *
 * Edgar: „baue diese Exportleiste sowohl auf die Mesh3d-ai jobs … als auch für /foto-genesis/test/edgartrip/". Feld 3 der Seite zeigt die Figur aus den Fotos als gehäutetes Anzeigenetz in der
 * Haltung der Fotos (`Fotogenesistestfigur`) — ohne Skelett, nicht animierbar. Für den Export entsteht dieselbe Figur als Genesis9Modell in der Ruhelage mit DEMSELBEN Code wie auf der
 * Mesh-Genesis-Testseite (`Meshgenesisfigurbewegung` ohne Feld): Regler der Form, Haut aus den Kacheln der Fotos (`figur_genesis.fototextur`, `Fotogenesisfigur._kacheln`), die Stücke aus den Fotos
 * am Skelett. Daten aus `/api/fotogenesis/<job>/figur/` (wie `/api/meshgenesis/test/<kennung>/`) und `…/kleider/<g>/` (wirksame Wahl). Gebaut wird erst beim ersten Export.
 */
export class Fotogenesisexportfigur {

    /** @param adresse `/api/fotogenesis/<job>/figur/` (`daten.test.adresse` der Seite) @param feld das Feld „Genesis-Modell“ (`Fotogenesisseite.genesisfeld`) — dann spielt die Abspielleiste
     *  darin dieselbe Figur, die exportiert wird (`Fotogenesisbewegung`, 31.10.2026); ohne Feld nur für den Export
     *  @param nackt ohne Stücke und ohne die Haut der KI (04.11.2026, Feld 1 der dritten Zeile: die Einpassung des Mesh-Genesis-Tests, `Fotogenesisgenesiszeile`) */
    constructor(adresse, feld = null, { nackt = false } = {}) {
        this.adresse = adresse;
        this.nackt = nackt;
        const ohneFeld = { neuZeigen() {}, zeichnen() {} };
        this.bewegung = new Meshgenesisfigurbewegung(feld ?? ohneFeld, () => this._quelle());
        this.export = new Meshgenesisexportquelle(() => this.bewegung);
    }

    bvh() {
        return null;
    }

    /** Die Figur für den Export ist die bewegte (`Meshgenesisexportquelle`); ob das Anatomie-Stück darin fehlt, entscheidet dort `Meshgenesisanatomiehuelle` nach der Regel des Servers. */
    async modell(angaben) {
        return this.export.modell(angaben);
    }

    /** Dieselbe Figur mit Kleidern und Haar für die Abspielleiste der Zeile 1 (`Fotogenesisbewegung`); `zeile1` = Form der Zeile 1 (`Fotogenesiszeile1bewegung`). */
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
            const netz = await Meshgenesisflaechennetz.holen(null, adresse).catch(fehler => { console.warn(`Fotogenesisexportfigur: ${st.id} nicht geladen (${fehler.message})`); return null; });
            if (netz) stuecke.push({ id: st.id, art: st.art, netz });
        }
        return { schluessel: `${this.adresse}|${g}`, figur: d.figur_genesis, stuecke, knochen: d.rig.knochen.map(k => k.name), ruhezentren: d.ruhezentren, ohneKnochen: [],
                 anatomieGetragen: Meshgenesisanatomiehuelle.getragen(liste), zeile1: d.zeile1_form || null };
    }
}
