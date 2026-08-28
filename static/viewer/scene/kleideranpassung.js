import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _charQueryParams, _selectedInst, _sliderVal } from './utils.js';
import { _skinifyMesh, convertInstToSkinned } from './skeleton.js';
import { _applyGarmentRegionOffsets,
         _computeGarmentRegionWeights } from './kleidung_anpassen.js';
import { Kleidungszustand } from './kleidungszustand.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Werkstofffreigabe } from '../gemeinsam/werkstofffreigabe.js';
import { Netzgeometrie } from '../gemeinsam/netzgeometrie.js';

/**
 * Kleideranpassung — ein Kleidungsstück am Server an die Figur anpassen lassen
 * und das Ergebnis in die Szene setzen.
 *
 * Umbau 16.08.2026: Dieser Ablauf stand ZWEIMAL fast gleich da —
 * `_doKleiderFit()` (103 Zeilen, Reiter "Kleider") und `_doGarmentFit()`
 * (101 Zeilen, Reiter "Assets"). Beide: Figur skinnen, Anpasswerte aus den
 * Reglern in eine Frage packen, POST/GET an `/api/character/garment/fit/`,
 * altes Netz entsorgen, Geometrie aus base64 bauen, Koordinaten drehen,
 * Material setzen, binden, Regionsgewichte rechnen, Zustand merken.
 *
 * Die Unterschiede sind Parameter geworden:
 *  * die Vorsilbe der Regler ('kleider' / 'garment'),
 *  * die Vorsilbe des Schlüssels ('kld_' / 'gar_'),
 *  * der Anpassmodus mit Hülle (nur Kleider-Reiter),
 *  * was danach noch zu tun ist (der Assets-Reiter pflegt `inst.garments`
 *    und stellt die Auswahl wieder her).
 */
export class Kleideranpassung {

    static ADRESSE = '/api/character/garment/fit/';
    static VORGABE_FARBE = '#4d5980';

    /**
     * @param wahl.vorsilbe    Reglervorsilbe, etwa 'kleider'
     * @param wahl.schluessel  Schlüsselvorsilbe, etwa 'kld_'
     * @param wahl.kennung     id des Stücks
     * @param wahl.huelle      true: die Hülle aus Stufe 1 mitsenden
     * @param wahl.modus       Anpassmodus für den Server
     * @param wahl.danach      (figur, schluessel, zustand, netz) => void
     */
    constructor(wahl) {
        Object.assign(this, wahl);
    }

    async ausfuehren() {
        const figur = _selectedInst();
        if (!figur || !this.kennung) return null;
        if (!figur.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
            convertInstToSkinned(figur);
        }
        const schluessel = this.schluessel + this.kennung;
        const farbe = this.farbe();
        const zustand = Kleidungszustand.ausReglern(
            this.vorsilbe, farbe, figur.garmentState[schluessel], _sliderVal);

        // `_refitting` hält die Regler davon ab, sich beim Nachziehen selbst
        // erneut auszulösen.
        state._refitting = true;
        try {
            const daten = await this.serverfrage(figur, zustand);
            if (!daten) return null;
            const netz = this.netzEinsetzen(figur, schluessel, daten, farbe,
                                           zustand);
            figur.garmentState[schluessel] = zustand;
            _computeGarmentRegionWeights(figur, schluessel);
            _applyGarmentRegionOffsets(figur, schluessel);
            this.danach?.(figur, schluessel, zustand, netz);
            fn.updateEquippedList(figur);
            fn.updateVertexCount();
            return netz;
        } catch (fehler) {
            console.error('Anpassen fehlgeschlagen:', fehler);
            return null;
        } finally {
            state._refitting = false;
        }
    }

    farbe() {
        const feld = document.getElementById(`${this.vorsilbe}-color`);
        return new THREE.Color(feld?.value || Kleideranpassung.VORGABE_FARBE);
    }

    // ------------------------------------------------------------------- Server

    async serverfrage(figur, zustand) {
        const frage = zustand.inFrage(_charQueryParams(figur));
        frage.set('garment_id', this.kennung);
        if (this.modus) frage.set('fit_mode', this.modus);

        const antwort = await (this.huelle && state._kleiderHullVertices
            ? this._mitHuelle(frage)
            : fetch(`${Kleideranpassung.ADRESSE}?${frage}`));
        const daten = await antwort.json();
        if (!daten.error) return daten;
        Protokoll.warnung('kleideranpassung', 'Anpassen fehlgeschlagen:', daten.error);
        return null;
    }

    /**
     * Stufe 2: Die in Stufe 1 gebaute Hülle geht als Rumpf mit — sie ist zu
     * groß für die Adresszeile.
     */
    _mitHuelle(frage) {
        const punkte = new Uint8Array(state._kleiderHullVertices.buffer);
        const b64 = btoa(String.fromCharCode(...punkte));
        return fetch(`${Kleideranpassung.ADRESSE}?${frage}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hull_vertices: b64 }),
        });
    }

    // --------------------------------------------------------------------- Netz

    netzEinsetzen(figur, schluessel, daten, farbe, zustand) {
        this._altesEntsorgen(figur, schluessel);
        const geo = Netzgeometrie.bauen(daten, THREE);

        const material = new THREE.MeshStandardMaterial({
            color: farbe, roughness: zustand.roughness,
            metalness: zustand.metalness, side: THREE.DoubleSide,
        });
        const netz = _skinifyMesh(geo, material, figur, daten);
        figur.clothMeshes[schluessel] = netz;
        figur.group.add(netz);
        // Die Regionsregler verschieben später von diesen Punkten aus.
        figur.garmentOrigPositions[schluessel] = new Float32Array(punkte);
        return netz;
    }

    _altesEntsorgen(figur, schluessel) {
        const alt = figur.clothMeshes[schluessel];
        if (!alt) return;
        figur.group.remove(alt);
        Werkstofffreigabe.netz(alt);   // samt Texturen
        delete figur.clothMeshes[schluessel];
    }
}
