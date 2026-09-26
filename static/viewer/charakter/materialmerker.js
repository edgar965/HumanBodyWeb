import { state } from './state.js';
import { _selectedGarmentMesh } from './garments.js';
import { Materialregler } from './materialregler.js';

/**
 * Materialmerker — Farbe, Rauheit und Metallgrad eines Kleidungsstücks wirken
 * sofort auf das Netz UND werden im Zustand des Stücks gemerkt.
 *
 * DER BEFUND (Edgar, 09.09.2026: „farbe der Schuhe wird nicht gespeichert")
 * ========================================================================
 * Im Reiter „Modell" steht der Block „Garment Eigenschaften" — er geht auf,
 * sobald man ein Stück aus Garment Fit anklickt (`Reiterzuordnung` schickt
 * `gar_…` dorthin). Seine drei Materialbedienungen schrieben ausschliesslich
 * in `mesh.material`:
 *
 *     colorPicker.addEventListener('input', () => {
 *         const sel = _selectedGarmentMesh();
 *         if (sel) sel.mesh.material.color.set(colorPicker.value);   // und sonst nichts
 *     });
 *
 * Gespeichert wird aber `inst.garmentState[key]` (`character.js toJSON`). Die
 * Farbe war also zu SEHEN und stand nirgends, wo das Speichern hinsieht.
 * Belegt an Edgars eigener Datei `FemaleGarmentCode.json`: Die Schuhe
 * (`shoes/toigo_mj_cloth_shoes`) tragen dort [0.0742, 0.0999, 0.2159] — das
 * ist auf die dritte Stelle genau `#4d5980` in linearem sRGB, also die
 * Vorgabefarbe `Kleideranpassung.VORGABE_FARBE`, nicht die eingestellte.
 *
 * Der Assets-Reiter hatte den Weg längst (`Stueckbedienung.nachMaterial` ->
 * `_saveSelectedGarmentState`), die Modell-Seite auch
 * (`Kleiderbedienung._farbe`) — nur dieser eine Block nicht.
 *
 * `state._syncingSliders` schützt wie überall davor, dass das Nachziehen der
 * Anzeige als Eingabe gilt; `merken` schreibt ausserdem nur, wenn wirklich ein
 * Stück gewählt ist. Ohne Auswahl passiert nichts — genau der Fall, den das
 * Reitergedächtnis beim Seitenstart herstellt und der am selben Tag die
 * GarmentCode-Farben aller Stücke überschrieben hat.
 */
export class Materialmerker {

    /** Zustandsfeld → Reglerkennung ohne Vorsilbe, Wert 0..100. */
    static ANTEILE = [['roughness', 'roughness'], ['metalness', 'metalness']];

    /**
     * @param vorsilbe  Kennungs-Vorsilbe der Regler, etwa 'prop-garment'
     * @param gewaehlt  () => { inst, key, mesh } | null
     */
    constructor(vorsilbe, gewaehlt = _selectedGarmentMesh) {
        this.vorsilbe = vorsilbe;
        this.gewaehlt = gewaehlt;
    }

    verdrahten() {
        const regler = new Materialregler(this.vorsilbe, this.gewaehlt);
        for (const [feld, kennung] of Materialmerker.ANTEILE) {
            regler.wirken(`${this.vorsilbe}-${kennung}`, (material, wert) => {
                material[feld] = wert / 100;
                this.merken({ [feld]: wert / 100 });
            });
        }
        this._farbe();
        return this;
    }

    _farbe() {
        const feld = document.getElementById(`${this.vorsilbe}-color`);
        feld?.addEventListener('input', () => {
            if (state._syncingSliders) return;
            const auswahl = this.gewaehlt();
            if (!auswahl) return;
            // Aus dem Material gelesen, nicht aus dem Feldtext: Gemerkt wird
            // damit genau das, was auf dem Netz liegt — und in derselben Form
            // (linear, drei Kanäle), die `Kleidungszustand` führt.
            const farbe = auswahl.mesh.material.color;
            farbe.set(feld.value);
            this.merken({ color: [farbe.r, farbe.g, farbe.b] });
        });
        return this;
    }

    /** Werte in den Zustand des gewählten Stücks schreiben. */
    merken(werte) {
        const auswahl = this.gewaehlt();
        const zustand = auswahl && auswahl.inst.garmentState[auswahl.key];
        if (!zustand) return false;
        // In das vorhandene Objekt schreiben, nicht ersetzen: Andere Stellen
        // halten eine Referenz darauf (`_saveSelectedGarmentState` sagt es
        // ebenso).
        Object.assign(zustand, werte);
        return true;
    }
}
