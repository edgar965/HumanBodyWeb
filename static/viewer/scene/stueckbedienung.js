import { state, REGION_IDS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _selectedInst, _bindSlider } from './utils.js';
import { Kleiderkatalog } from './kleiderkatalog.js';
import { Materialregler } from './materialregler.js';

/**
 * Stueckbedienung — der gemeinsame Teil der beiden Kleider-Bedienfelder der
 * Szene-Seite: Regler binden, Material sofort ändern, Neuanpassung entprellen,
 * Regionsregler, Entfernen-Knöpfe, Katalog laden.
 *
 * Umbau 16.08.2026: `loadKleiderUI()` (Reiter "Kleider", 184 Zeilen) und
 * `loadGarmentUI()` (Reiter "Assets", 101 Zeilen) verdrahteten dieselben
 * Bedienelemente unter zwei Vorsilben — dieselben acht Regler, dieselben drei
 * Materialregler, dieselbe Entprellung mit 400 ms, dieselben fünf
 * Regionsregler, dieselben Entfernen-Knöpfe, derselbe Katalog. Was die beiden
 * Reiter unterscheidet, steht jetzt in ihren eigenen Klassen.
 */
export class Stueckbedienung {

    /** Ruhezeit, bevor der Server neu anpasst. */
    static RUHE_MS = 400;

    /** Regler: Kennung ohne Vorsilbe und Anzeigeform. */
    static REGLER = [
        ['offset', wert => (wert / 1000).toFixed(3)],
        ['stiffness', wert => (wert / 100).toFixed(2)],
        ['min-dist', wert => wert + ' mm'],
        ['crotch-floor', wert => wert + ' mm'],
        ['lift', wert => wert + ' mm'],
        ['crotch-depth', wert => wert + ' mm'],
        ['roughness', wert => (wert / 100).toFixed(2)],
        ['metalness', wert => (wert / 100).toFixed(2)],
    ];

    /** Diese Regler lösen eine Neuanpassung am Server aus. */
    static REFIT_REGLER = ['offset', 'stiffness', 'min-dist', 'crotch-floor',
                           'lift', 'crotch-depth'];

    /**
     * @param wahl.vorsilbe    'kleider' oder 'garment'
     * @param wahl.schluessel  'kld_' oder 'gar_'
     * @param wahl.gewaehlt    () => { inst, key, mesh } | null
     * @param wahl.anpassen    () => Neuanpassung am Server
     * @param wahl.kennungMerken (kennung) => void — welche id angepasst wird
     * @param wahl.nachMaterial () => void — nach einer Materialänderung
     * @param wahl.regionen    (inst, key) => Verschiebungen anwenden
     * @param wahl.listeZeichnen () => void
     */
    constructor(wahl) {
        Object.assign(this, wahl);
        this.katalog = new Kleiderkatalog(`${wahl.vorsilbe}-category`);
        this._refitZeitgeber = null;
    }

    grundverdrahtung() {
        this._reglerBinden();
        this._material();
        this._refit();
        this._regionen();
        this._grundknoepfe();
        return this;
    }

    _reglerBinden() {
        for (const [kennung, form] of Stueckbedienung.REGLER) {
            const id = `${this.vorsilbe}-${kennung}`;
            _bindSlider(id, id + '-val', form);
        }
    }

    /**
     * Rauheit, Metallgrad und Farbe wirken sofort auf das gewählte Netz. Der
     * Assets-Reiter merkt den Stand danach im Zustand des Stücks — deshalb
     * `nachMaterial`.
     */
    _material() {
        const regler = new Materialregler(this.vorsilbe, this.gewaehlt);
        const merken = () => this.nachMaterial?.();
        regler.wirken(`${this.vorsilbe}-roughness`, (material, wert) => {
            material.roughness = wert / 100;
            merken();
        });
        regler.wirken(`${this.vorsilbe}-metalness`, (material, wert) => {
            material.metalness = wert / 100;
            merken();
        });
        const farbfeld = document.getElementById(`${this.vorsilbe}-color`);
        farbfeld?.addEventListener('input', () => {
            if (state._syncingSliders) return;
            const auswahl = this.gewaehlt();
            if (!auswahl) return;
            auswahl.mesh.material.color.set(farbfeld.value);
            merken();
        });
    }

    _refit() {
        for (const kennung of Stueckbedienung.REFIT_REGLER) {
            document.getElementById(`${this.vorsilbe}-${kennung}`)
                ?.addEventListener('input', () => this.refitBald());
        }
    }

    /** Neuanpassung anmelden — erst nach der Ruhezeit, sonst bei jedem Pixel. */
    refitBald() {
        if (state._syncingSliders) return;
        const auswahl = this.gewaehlt();
        if (!auswahl?.key?.startsWith(this.schluessel)) return;
        this.kennungMerken?.(auswahl.key.slice(this.schluessel.length));
        clearTimeout(this._refitZeitgeber);
        this._refitZeitgeber = setTimeout(() => this.anpassen(),
                                         Stueckbedienung.RUHE_MS);
    }

    /** Regionsregler verschieben Teile des Stücks — ohne Serverfrage. */
    _regionen() {
        for (const region of REGION_IDS) {
            const id = `${this.vorsilbe}-region-${region}`;
            _bindSlider(id, id + '-val', wert => (wert / 100).toFixed(2) + ' m');
            document.getElementById(id)?.addEventListener('input', () => {
                if (state._syncingSliders) return;
                const auswahl = this.gewaehlt();
                if (!auswahl) return;
                this.nachMaterial?.();
                this.regionen?.(auswahl.inst, auswahl.key);
            });
        }
    }

    _grundknoepfe() {
        document.getElementById(`${this.vorsilbe}-category`)
            ?.addEventListener('change', () => this.listeZeichnen());
        document.getElementById(`${this.vorsilbe}-remove`)
            ?.addEventListener('click', () => {
                if (state._selectedSubMesh) fn._removeSubMesh(state._selectedSubMesh);
            });
        document.getElementById(`${this.vorsilbe}-remove-all`)
            ?.addEventListener('click', () => this.alleEntfernen());
    }

    /**
     * Alle Stuecke DIESES Reiters von der Figur nehmen.
     *
     * BEFUND `doppelcode` (30.08.2026): Stand in `mhproxy_bedienung.js` noch
     * einmal, dort mit fest verdrahtetem `'mh_'`. Die Vorsilbe entscheidet,
     * WELCHE Stuecke gemeint sind — sie steckt im Schluessel der Netze
     * (`mh_…`, `gar_…`, `tpl_…`). Ein falscher Vorsilbenvergleich raeumt
     * entweder nichts weg oder die Stuecke des anderen Reiters mit.
     */
    static alleMitVorsilbe(vorsilbe) {
        const figur = _selectedInst();
        if (!figur) return;
        for (const schluessel of Object.keys(figur.clothMeshes)
                .filter(name => name.startsWith(vorsilbe))) {
            fn._removeSubMesh({ type: 'cloth', key: schluessel,
                                meshObj: figur.clothMeshes[schluessel],
                                charId: figur.id });
        }
    }

    alleEntfernen() {
        Stueckbedienung.alleMitVorsilbe(this.schluessel);
    }

    /** Katalog laden und die Liste zeichnen. true, wenn etwas da ist. */
    async katalogLaden() {
        const fertig = await this.katalog.laden();
        if (fertig) this.listeZeichnen();
        return fertig;
    }
}
