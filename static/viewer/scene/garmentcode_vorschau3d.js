import * as THREE from 'three';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { GarmentcodeFigur } from './garmentcode_figur.js';
import { GarmentcodePanels } from './garmentcode_panels.js';
import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';

/**
 * GarmentcodeVorschau3d — der Schnitt am Körper, ohne Simulation.
 *
 * WARUM (Edgar, 08.09.2026: „Button Vorschau für 2D und 3D soll schnell
 * gehen … Erst mit «Finalisieren» soll die lange Berechnung gemacht
 * werden"): Der Server zieht die flachen Panels an die Haut heran und hebt
 * sie um 6 mm Stoffdicke ab — gerechnet vom portierten UMA-Konformer
 * (`core/dienste/garmentvorschau3d.py`). Gemessen 0,4 s beim T-Shirt und
 * 1,0 s beim Jumpsuit, gegen 23 s für die echte Drapierung.
 *
 * WAS SIE NICHT KANN, UND WARUM DAS DASTEHEN MUSS
 * ===============================================
 * Keinen Faltenwurf. Ein Rocksaum liegt hier am Bein an, statt zu fallen,
 * und ein weiter Ärmel liegt am Arm. Die Meldung sagt das — sonst hält man
 * die Vorschau für das Ergebnis und wundert sich über den Unterschied nach
 * „Bauen 3D".
 */
export class GarmentcodeVorschau3d {

    static ADRESSE = '/api/garmentcode/vorschau3d/';
    static SCHLUESSEL = 'gc_vorschau';
    static FARBE = 0x6fa8dc;

    static async zeigen(reiter, figur, meldung, vorlage) {
        garmentcodeFortschritt.laeuft('vorschau3d');
        const daten = GarmentcodeFigur.formulardaten(figur);
        daten.append('ordner', reiter.ordner || '');
        const antwort = await Serverabruf.formular(
            GarmentcodeVorschau3d.ADRESSE, daten);
        if (antwort.fehler) throw new Error(antwort.fehler);

        // Die flachen Panels weichen: Beide zusammen sähen aus wie ein
        // Fehler — dieselbe Entscheidung wie beim Drapieren.
        GarmentcodePanels.entfernen(figur);
        const anzahl = GarmentcodeVorschau3d._anlegen(figur, antwort, vorlage);
        garmentcodeFortschritt.fertig('vorschau3d', `${anzahl} Punkte`);

        meldung.textContent = `Vorschau: ${anzahl} Punkte am Körper, `
            + `${antwort.hautabstand_mm} mm zur Haut`
            + (antwort.ungebunden
                ? `, ${antwort.ungebunden} Punkte ohne Fläche` : '')
            + ' — ohne Faltenwurf. „Bauen 3D" simuliert den Stoff.';
        return anzahl;
    }

    /**
     * Das Vorschaunetz an die Figur hängen.
     *
     * Als EIGENES Teilnetz (`clothMeshes`), nicht nur über `group.add`:
     * Sonst wählt ein Klick die ganze Figur, und Entf löscht sie mitsamt
     * Körper und Haaren — der Befund vom 08.09.2026.
     */
    static _anlegen(figur, antwort, vorlage) {
        // `GarmentcodeFigur.gewaehlt()` liefert `{id, inst}` — die
        // Szeneninstanz steckt in `.inst`. Wer hier `figur.group` nimmt,
        // bekommt `undefined` und meldet „liessen sich nicht anlegen",
        // waehrend der Server laengst geliefert hat (Befund 07.09.2026).
        const inst = figur.inst || figur;
        const gruppe = inst.group;
        if (!gruppe) return 0;
        GarmentcodeVorschau3d.entfernen(figur);

        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position',
            new THREE.Float32BufferAttribute(antwort.punkte, 3));
        geometrie.setIndex(antwort.dreiecke);
        geometrie.computeVertexNormals();

        const netz = new THREE.Mesh(geometrie, new THREE.MeshStandardMaterial({
            color: GarmentcodeVorschau3d.FARBE, roughness: 0.9,
            metalness: 0.0, side: THREE.DoubleSide,
            transparent: true, opacity: 0.92,
        }));
        netz.name = `${GarmentcodeVorschau3d.SCHLUESSEL}_${figur.id || inst.id}`;
        netz.userData.beschriftung = `${vorlage || 'Schnitt'} (Vorschau)`;
        gruppe.add(netz);
        if (inst.clothMeshes) {
            inst.clothMeshes[GarmentcodeVorschau3d.SCHLUESSEL] = netz;
        }
        return geometrie.attributes.position.count;
    }

    /** Beim Drapieren und vor einer neuen Vorschau: das alte Netz weg. */
    static entfernen(figur) {
        const inst = figur?.inst || figur;
        const schluessel = GarmentcodeVorschau3d.SCHLUESSEL;
        const netz = inst?.clothMeshes?.[schluessel];
        if (!netz) return false;
        delete inst.clothMeshes[schluessel];
        inst.group?.remove(netz);
        Netzentsorgung.entfernen(netz);
        return true;
    }
}
