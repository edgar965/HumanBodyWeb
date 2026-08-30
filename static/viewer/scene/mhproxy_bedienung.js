import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _selectedInst, _selectedMHMesh, _bindSlider } from './utils.js';
import { _doMHProxyFit } from './mhproxy_anpassen.js';
import { _renderMHList } from './mhproxy_liste.js';
import { Mhverformung } from './mhproxy_verformung.js';
import { Kleiderkatalog } from './kleiderkatalog.js';
import { Materialregler } from './materialregler.js';
import { Stueckbedienung } from './stueckbedienung.js';

/**
 * MhProxyBedienung — das Bedienfeld für MakeHuman-Kleidung verdrahten.
 *
 * Aus `mh_proxy.js` herausgeloest (Umbau 16.08.2026): `loadMHProxyUI()` hatte
 * 243 Zeilen. Drei Dinge fielen dabei auf:
 *
 *  * VIER gleich gebaute Blöcke für Rauheit, Metallgrad, Farbe und Deckkraft —
 *    jeder mit `if (state._syncingSliders) return; const sel =
 *    _selectedMHMesh(); if (sel) …`. Der Kleider-Reiter hatte dieselben drei
 *    davon: jetzt beide über `Materialregler`.
 *  * Der Kleiderkatalog wurde endlos gepollt — hier und im Kleider-Reiter →
 *    beide über `Kleiderkatalog`.
 *  * Der Schwerpunkt der Vertexverformung wurde bei jeder Reglerbewegung neu
 *    gerechnet → `Mhverformung`.
 */
export class MhProxyBedienung {

    /** Regler: Kennung und Anzeigeform. Anzeigefeld ist immer Kennung + '-val'. */
    static REGLER = [
        ['mh-stiffness', wert => (wert / 100).toFixed(2)],
        ['mh-offset', wert => (wert / 1000).toFixed(3)],
        ['mh-scale', wert => wert + '%'],
        ['mh-y-offset', wert => wert + ' mm'],
        ['mh-roughness', wert => (wert / 100).toFixed(2)],
        ['mh-metalness', wert => (wert / 100).toFixed(2)],
        ['mh-opacity', wert => (wert / 100).toFixed(2)],
        ['mh-push-dist', wert => wert + ' mm'],
    ];

    /** Diese Regler lösen eine Neuanpassung am Server aus. */
    static REFIT_REGLER = ['mh-stiffness', 'mh-offset', 'mh-scale',
                           'mh-y-offset', 'mh-push-dist'];
    /** Diese wirken sofort auf die Vertices. */
    static VERFORM_REGLER = ['mh-offset', 'mh-scale', 'mh-y-offset'];

    /** Ruhezeit, bevor der Server neu anpasst. */
    static RUHE_MS = 400;

    constructor() {
        this.verformung = new Mhverformung();
        this.katalog = new Kleiderkatalog('mh-category');
        this._refitZeitgeber = null;
    }

    async verdrahten() {
        this._reglerBinden();
        this._material();
        this._refit();
        this._verformung();
        this._knoepfe();
        if (await this.katalog.laden()) _renderMHList();
        return this;
    }

    _reglerBinden() {
        for (const [id, form] of MhProxyBedienung.REGLER) {
            _bindSlider(id, id + '-val', form);
        }
    }

    /**
     * Material: Rauheit, Metallgrad, Farbe und Deckkraft. Dieselben vier
     * Regler wie im Kleider-Reiter, deshalb aus `Materialregler`.
     */
    _material() {
        new Materialregler('mh', _selectedMHMesh).grundwerte().deckkraft();
    }

    // ------------------------------------------------------------------- Refit

    _refit() {
        for (const id of MhProxyBedienung.REFIT_REGLER) {
            document.getElementById(id)
                ?.addEventListener('change', () => this._refitBald());
        }
    }

    /**
     * Neuanpassung anmelden. Ist noch keine Kleidung gewählt, wird die erste
     * MakeHuman-Kleidung der gewählten (oder irgendeiner) Figur genommen —
     * sonst wäre der Regler wirkungslos, ohne dass man erkennt, warum.
     */
    _refitBald() {
        if (state._syncingSliders) return;
        if (!state._selectedMHId) this._kleidungSuchen();
        if (!state._selectedMHId) return;
        clearTimeout(this._refitZeitgeber);
        this._refitZeitgeber = setTimeout(() => _doMHProxyFit(),
                                          MhProxyBedienung.RUHE_MS);
    }

    _kleidungSuchen() {
        let figur = _selectedInst();
        if (!figur && state.characters?.size > 0) {
            figur = state.characters.values().next().value;
        }
        if (!figur) return;
        const schluessel = Object.keys(figur.clothMeshes || {})
            .find(name => name.startsWith('mh_'));
        if (schluessel) state._selectedMHId = schluessel.slice(3);
    }

    // -------------------------------------------------------------- Verformung

    _verformung() {
        for (const id of MhProxyBedienung.VERFORM_REGLER) {
            document.getElementById(id)?.addEventListener('input', () => {
                if (!state._syncingSliders) this.verformung.anwenden();
            });
        }
    }

    // ------------------------------------------------------------------ Knöpfe

    _knoepfe() {
        document.getElementById('mh-category')
            ?.addEventListener('change', () => _renderMHList());
        document.getElementById('mh-create')
            ?.addEventListener('click', () => _doMHProxyFit());
        document.getElementById('mh-remove')?.addEventListener('click', () => {
            if (state._selectedMHId && state._selectedSubMesh) {
                fn._removeSubMesh(state._selectedSubMesh);
            }
        });
        document.getElementById('mh-push')
            ?.addEventListener('click', () => this.verformung.herausdruecken());
        document.getElementById('mh-push-undo')
            ?.addEventListener('click', () => this.verformung.zuruecknehmen());
        document.getElementById('mh-remove-all')
            ?.addEventListener('click', () => this.alleEntfernen());
    }

    /** Alle MakeHuman-Stuecke abnehmen — siehe `Stueckbedienung`. */
    alleEntfernen() {
        Stueckbedienung.alleMitVorsilbe('mh_');
    }
}
