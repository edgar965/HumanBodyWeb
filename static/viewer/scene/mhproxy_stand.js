import { state } from './state.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Der gemerkte Anzeigestand der Proxy-Liste: welche Kategorie offen ist und
 * welches Kleidungsstück gewählt war.
 *
 * Aus mhproxy_liste.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`:
 * `_renderMHList()` hatte 90 Zeilen). Vorher lag die offene Kategorie als
 * freies `let` im Modul — von dort kam kein anderer Baustein daran.
 */
export class Mhproxystand {
    /** Schlüssel im Ablagespeicher des Browsers. */
    static SCHLUESSEL = 'mh_proxy_state';

    /** Zuletzt aufgeklappte Kategorie. */
    static offeneKategorie = '';

    static sichern() {
        // `setItem` wirft bei vollem Speicher (QuotaExceededError) und im
        // privaten Fenster (SecurityError). Ungefangen brach damit der
        // AUFRUFER ab — in `_renderMHList` etwa die Zeile, die die Kategorie
        // aufklappt: Die Liste reagierte scheinbar grundlos nicht mehr. Ein
        // verlorener Merkzustand ist dagegen harmlos.
        try {
            localStorage.setItem(Mhproxystand.SCHLUESSEL, JSON.stringify({
                openCat: Mhproxystand.offeneKategorie,
                selectedId: state._selectedMHId,
            }));
        } catch (e) {
            Protokoll.warnung('MH-Proxy', 'Zustand nicht speicherbar:',
                              e?.name || e);
        }
    }

    static laden() {
        try {
            const stand = JSON.parse(
                localStorage.getItem(Mhproxystand.SCHLUESSEL));
            if (!stand) return;
            Mhproxystand.offeneKategorie = stand.openCat || '';
            state._selectedMHId = stand.selectedId || '';
        } catch (e) {
            Protokoll.debug('mhproxy', 'gemerkte Auswahl nicht lesbar', e);
        }
    }

    /** Kategorie aufklappen und den Stand sichern. */
    static aufklappen(kategorie) {
        Mhproxystand.offeneKategorie = kategorie;
        Mhproxystand.sichern();
    }
}
