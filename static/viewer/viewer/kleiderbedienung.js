import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { bindSlider } from './utils.js';
import { _saveGarmentState, _applyGarmentState, _downloadPack,
         _loadDownloadPacks, _renderGarmentList } from './garment_liste.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Kleiderbedienung (Viewer-Seite) — das Bedienfeld des Garment Fitters:
 * 20 Regler, sechs Knöpfe, Katalog und das Ladefenster.
 *
 * Aus viewer/garment.js herausgeloest (Umbau 16.08.2026): `loadGarmentUI()`
 * hatte 124 Zeilen, davon 30 nur Reglerbindungen — jede einzeln ausgeschrieben,
 * obwohl es drei Gruppen mit gleichem Verhalten sind: solche, die sofort
 * wirken, solche, die eine Neuanpassung am Server auslösen, und solche, die nur
 * ihre Anzeige nachziehen. Die Gruppen stehen jetzt als Tabellen oben.
 */
export class Kleiderbedienung {

    /** Regionen des Kleidungsstücks, von oben nach unten. */
    static REGIONEN = ['top', 'upper', 'mid', 'lower', 'bottom'];

    /** Regler mit Anzeigeform. `live`: wirkt sofort, `refit`: Server rechnet neu. */
    static REGLER = [
        ['garment-offset', wert => (wert / 1000).toFixed(3), 'refit'],
        ['garment-stiffness', wert => (wert / 100).toFixed(2), 'refit'],
        ['garment-min-dist', wert => wert + ' mm', 'refit'],
        ['garment-crotch-floor', wert => wert + ' mm', 'refit'],
        ['garment-lift', wert => wert + ' mm', 'refit'],
        ['garment-crotch-depth', wert => wert + ' mm', 'refit'],
        ['garment-roughness', wert => (wert / 100).toFixed(2), 'live'],
        ['garment-metalness', wert => (wert / 100).toFixed(2), 'live'],
        ['garment-pos-x', wert => (wert / 100).toFixed(2) + ' m', 'live'],
        ['garment-pos-y', wert => (wert / 100).toFixed(2) + ' m', 'live'],
        ['garment-pos-z', wert => (wert / 100).toFixed(2) + ' m', 'live'],
        ['garment-scale-x', wert => (wert / 100).toFixed(2), 'live'],
        ['garment-scale-y', wert => (wert / 100).toFixed(2), 'live'],
        ['garment-scale-z', wert => (wert / 100).toFixed(2), 'live'],
    ];

    /**
     * @param anziehen   (id) => Kleidungsstück (neu) anziehen
     * @param abziehen   (id) => Stück entfernen
     * @param alleAb     () => alle Stücke entfernen
     */
    constructor({ anziehen, abziehen, alleAb }) {
        this.anziehen = anziehen;
        this.abziehen = abziehen;
        this.alleAb = alleAb;
    }

    async verdrahten() {
        this._regler();
        this._farbe();
        this._knoepfe();
        this._ladefenster();
        await this.katalogLaden();
        return this;
    }

    /** Das gewählte Stück, oder null. */
    gewaehlt() {
        const kennung = state.selectedGarmentId;
        if (!kennung || !state.garmentMeshes[kennung]) return null;
        return kennung;
    }

    // ------------------------------------------------------------------ Regler

    _regler() {
        for (const [id, form, art] of Kleiderbedienung.REGLER) {
            bindSlider(id, id + '-val', form);
            if (art === 'live') this._sofort(id);
            else if (art === 'refit') this._neuAnpassen(id);
        }
        for (const region of Kleiderbedienung.REGIONEN) {
            const id = `garment-region-${region}`;
            bindSlider(id, id + '-val', wert => (wert / 100).toFixed(2) + ' m');
            this._sofort(id);
        }
    }

    /** Wirkt ohne Serverfrage: Stand merken und auf das Netz anwenden. */
    _sofort(id) {
        document.getElementById(id)?.addEventListener('input', () => {
            const kennung = this.gewaehlt();
            if (!kennung) return;
            _saveGarmentState(kennung);
            _applyGarmentState(kennung);
        });
    }

    /**
     * Löst eine Neuanpassung am Server aus — erst beim Loslassen (`change`),
     * nicht bei jedem Pixel.
     */
    _neuAnpassen(id) {
        document.getElementById(id)?.addEventListener('change', () => {
            const kennung = this.gewaehlt();
            if (!kennung) return;
            _saveGarmentState(kennung);
            this.anziehen(kennung);
        });
    }

    _farbe() {
        const feld = document.getElementById('garment-color');
        feld?.addEventListener('input', () => {
            const kennung = this.gewaehlt();
            if (!kennung) return;
            state.garmentMeshes[kennung].material.color.set(feld.value);
            _saveGarmentState(kennung);
        });
    }

    // ------------------------------------------------------------------ Knöpfe

    _knoepfe() {
        document.getElementById('garment-create')?.addEventListener('click', () => {
            if (!state.selectedGarmentId) {
                Protokoll.warnung('kleiderbedienung', 'Kein Kleidungsstück gewählt');
                return;
            }
            this.anziehen(state.selectedGarmentId);
        });
        document.getElementById('garment-update')?.addEventListener('click', () => {
            const kennung = this.gewaehlt();
            if (!kennung) return;
            _saveGarmentState(kennung);
            this.anziehen(kennung);
        });
        document.getElementById('garment-refit-all')
            ?.addEventListener('click', ereignis => this.alleNeu(ereignis.currentTarget));
        document.getElementById('garment-remove')?.addEventListener('click', () => {
            const kennung = this.gewaehlt();
            if (kennung) this.abziehen(kennung);
        });
        document.getElementById('garment-remove-all')
            ?.addEventListener('click', () => this.alleAb());
        document.getElementById('garment-category')
            ?.addEventListener('change', () => _renderGarmentList());
        document.getElementById('garment-edit-pattern')?.addEventListener('click', () => {
            if (state.selectedGarmentId && fn.peLoadFromGarment) {
                fn.peLoadFromGarment(state.selectedGarmentId);
            }
        });
    }

    /** Alle Stücke neu anpassen — dauert, deshalb sperrt der Knopf sich selbst. */
    async alleNeu(knopf) {
        const kennungen = Object.keys(state.garmentMeshes);
        if (!kennungen.length) return;
        knopf.disabled = true;
        knopf.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refit...';
        try {
            for (const kennung of kennungen) _saveGarmentState(kennung);
            for (const kennung of kennungen) await this.anziehen(kennung);
        } finally {
            knopf.disabled = false;
            knopf.innerHTML = '<i class="fas fa-sync"></i> Refit';
        }
    }

    /** Das Ladefenster holt seine Pakete erst beim Aufklappen. */
    _ladefenster() {
        const knopf = document.getElementById('garment-download-btn');
        const fenster = document.getElementById('garment-download-panel');
        if (knopf && fenster) {
            knopf.addEventListener('click', async () => {
                const offen = fenster.style.display !== 'none';
                fenster.style.display = offen ? 'none' : 'block';
                if (!offen) await _loadDownloadPacks();
            });
        }
        document.getElementById('garment-pack-download')
            ?.addEventListener('click', () => _downloadPack());
    }

    // ----------------------------------------------------------------- Katalog

    async katalogLaden() {
        try {
            const daten = await Serverabruf.json('/api/character/garment/library/');
            state._garmentCatalog = Object.values(daten.garments || {}).flat();
            this._kategorienFuellen(daten.categories);
            _renderGarmentList();
        } catch (fehler) {
            Protokoll.warnung('kleiderbedienung', 'Kleiderliste nicht ladbar:', fehler);
            const liste = document.getElementById('garment-list');
            if (liste) {
                liste.innerHTML =
                    '<div class="listen-hinweis">Keine Garment-Library</div>';
            }
        }
    }

    _kategorienFuellen(kategorien) {
        const feld = document.getElementById('garment-category');
        if (!feld || !kategorien) return;
        for (const kategorie of kategorien) {
            feld.appendChild(new Option(
                kategorie.charAt(0).toUpperCase() + kategorie.slice(1), kategorie));
        }
    }
}
