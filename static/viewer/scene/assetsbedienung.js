import { state } from './state.js';
import { _selectedGarmentMesh, _renderGarmentList } from './garments.js';
import { _applyGarmentRegionOffsets,
         _saveSelectedGarmentState, _doGarmentFit } from './kleidung_anpassen.js';
import { Stueckbedienung } from './stueckbedienung.js';

/**
 * Assetsbedienung — der Reiter "Assets" der Szene-Seite (Garment Fit).
 *
 * Aus scene/garments.js herausgeloest (Umbau 16.08.2026): `loadGarmentUI()`
 * hatte 101 Zeilen, die dieselben Bedienelemente verdrahteten wie der
 * Kleider-Reiter — nur unter der Vorsilbe `garment` statt `kleider`. Der
 * gemeinsame Teil steckt in `Stueckbedienung`; eigen ist hier nur, dass nach
 * jeder Änderung der Zustand des Stücks mitgeschrieben wird
 * (`_saveSelectedGarmentState`) und dass der Anlegen-Knopf sofort anpasst.
 */
export class Assetsbedienung {

    async verdrahten() {
        this.teile = new Stueckbedienung({
            vorsilbe: 'garment',
            schluessel: 'gar_',
            gewaehlt: _selectedGarmentMesh,
            anpassen: () => _doGarmentFit(),
            kennungMerken: kennung => { state._selectedGarmentId = kennung; },
            // Der Assets-Reiter führt den Zustand je Stück mit; ohne das gingen
            // Material- und Regionsänderungen beim nächsten Anpassen verloren.
            nachMaterial: () => _saveSelectedGarmentState(),
            regionen: (figur, schluessel) =>
                _applyGarmentRegionOffsets(figur, schluessel),
            listeZeichnen: () => _renderGarmentList(),
        }).grundverdrahtung();

        document.getElementById('garment-create')
            ?.addEventListener('click', () => _doGarmentFit());
        await this.teile.katalogLaden();
        return this;
    }
}
