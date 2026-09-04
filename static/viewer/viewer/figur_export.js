/**
 * FigurExport — die Figur des Viewers als GLB, für Roomguest.
 *
 * WARUM (05.09.2026): Roomguest (Unity-Client, A:\Roomguest) spielt die hier
 * gestaltete Figur. Der Viewer hält sie fertig: `state.bodyMesh` ist ein
 * SkinnedMesh mit dem DEF-Skelett als Kind (`Hautbindung`), Haare und
 * Garderobe hängen als weitere SkinnedMeshes an demselben Skelett. Three.js'
 * GLTFExporter schreibt genau das als GLB — Netz, Skin, Werkstoffe samt
 * Texturen. Morphs sind im Netz schon eingerechnet (der Server liefert die
 * verformten Punkte), deshalb kommen keine Morph-Targets mit.
 *
 * Zwei Wege, ein Rumpf: `ablegen` schickt die GLB an den Server
 * (`core/api/figur_export.py`), wo Roomguest sie abholt; `herunterladen`
 * gibt sie dem Browser. Ausgelöst über Datei -> Exportieren (`Seitenbefehle`).
 */
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class FigurExport {

    static ADRESSE = '/api/character/figur-glb';
    static VORGABE = 'figur';
    static TYP = 'model/gltf-binary';

    /** @param {Object} state der Viewer-Zustand (`viewer/state.js`) */
    constructor(state) {
        this.state = state;
    }

    /** Was in die GLB kommt: Körper, Haare, Garderobe, Garnituren — sichtbare. */
    objekte() {
        const s = this.state;
        const alle = [s.bodyMesh, s.hairMesh,
                      ...Object.values(s.loadedAssets || {}),
                      ...Object.values(s.garmentMeshes || {})];
        return alle.filter(o => o && o.visible !== false);
    }

    /** Dateiname ohne Endung: der Modellname oder `figur`. */
    name() {
        const roh = this.state.currentPresetName || FigurExport.VORGABE;
        return roh.replace(/[^\w\s\-]/g, '').trim() || FigurExport.VORGABE;
    }

    /** Die GLB als ArrayBuffer. Wirft, wenn keine Figur da ist. */
    async alsGlb() {
        const objekte = this.objekte();
        if (!objekte.length) throw new Error('Keine Figur geladen');
        const ergebnis = await new GLTFExporter().parseAsync(
            objekte, { binary: true, onlyVisible: true });
        if (!(ergebnis instanceof ArrayBuffer)) {
            throw new Error('Der Exporter lieferte kein GLB');
        }
        return ergebnis;
    }

    /** Auf den Server: {name, bytes, pfad}. */
    async ablegen() {
        const name = this.name();
        const glb = await this.alsGlb();
        const daten = new FormData();
        daten.append('glb', new Blob([glb], { type: FigurExport.TYP }), name + '.glb');
        const antwort = await Serverabruf.formular(
            `${FigurExport.ADRESSE}/${encodeURIComponent(name)}/ablegen/`, daten);
        Protokoll.info('Viewer', `Figur abgelegt: ${antwort.pfad} (${antwort.bytes} Bytes)`);
        return antwort;
    }

    /** In den Browser: Anzahl Bytes. */
    async herunterladen() {
        const name = this.name();
        const glb = await this.alsGlb();
        const adresse = URL.createObjectURL(new Blob([glb], { type: FigurExport.TYP }));
        const link = document.createElement('a');
        link.href = adresse;
        link.download = name + '.glb';
        link.click();
        URL.revokeObjectURL(adresse);
        Protokoll.info('Viewer', `Figur heruntergeladen: ${name}.glb (${glb.byteLength} Bytes)`);
        return glb.byteLength;
    }
}
