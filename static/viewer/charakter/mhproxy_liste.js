/**
 * Liste der MakeHuman-Proxys: anzeigen.
 *
 * Aus mh_proxy.js herausgeloest (Umbau 16.08.2026).
 *
 * UMBAU 27.08.2026 (Befund `jsfunktionen`): `_renderMHList()` hatte 90 Zeilen.
 * Der gemerkte Anzeigestand steht jetzt in `Mhproxystand`, ein Kategorieordner
 * mit seinen Zeilen in `Mhproxyordner`, das Rechtsklickmenue in `Mhproxymenue`.
 */

import { state } from './state.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Mhproxyordner } from './mhproxy_ordner.js';
import { Mhproxymenue } from './mhproxy_menue.js';
import { Mhproxystand } from './mhproxy_stand.js';


function _renderMHList() {
    const liste = document.getElementById('mh-list');
    if (!liste) return;
    liste.innerHTML = '';
    Mhproxystand.laden();

    const kategorie = document.getElementById('mh-category')?.value || '';
    const stuecke = kategorie
        ? state._garmentCatalog.filter(g => g._category === kategorie)
        : state._garmentCatalog;
    if (stuecke.length === 0) {
        liste.innerHTML = '<div class="leer-hinweis">Keine Garments</div>';
        return;
    }

    const aufKontextmenue = (x, y, stueck) =>
        Mhproxymenue.zeigen(x, y, stueck, _renderMHList);
    const gruppen = Mhproxyordner.gruppieren(stuecke);
    for (const [kat, inhalt] of Object.entries(gruppen)) {
        liste.appendChild(
            Mhproxyordner.element(kat, inhalt, liste, aufKontextmenue));
    }
    _zumGewaehlten(liste);
}

/** Das gemerkte Stueck in den sichtbaren Bereich holen. */
function _zumGewaehlten(liste) {
    if (!state._selectedMHId) return;
    const zeile = liste.querySelector(
        `[data-garment-id="${state._selectedMHId}"]`);
    // Erst nach dem Aufklappen — vorher steht die Zeile noch auf `display:none`
    // und `scrollIntoView` bewegt nichts.
    if (zeile) {
        setTimeout(() => zeile.scrollIntoView({ block: 'nearest' }),
                   Zeiten.ROLLEN_MS);
    }
}

export { _renderMHList };
