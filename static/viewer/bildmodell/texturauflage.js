/**
 * Texturauflage — die gebackenen Fotokacheln (Stufe 2) auf das Modell der Auftragsseite legen.
 *
 * `ergebnis.fototextur.kacheln` (`Bildmodellfototextur`): je UDIM-Kachel eine JPG im
 * Auftrag, Fotofarbe über der getönten Daz-Albedo. Jede Materialgruppe des Körpers kennt
 * ihre Kachel (`material.userData.kachel`, `Genesis9netz.materialien`); für diese Gruppen
 * wird die Kachel als `map` eingehängt und die Farbe auf Weiß gestellt — der Hautton der
 * Stufe 1 (`ansicht3d.hauttonAnwenden`) steckt schon in der Kachel. Die Albedo aus dem
 * Texturvorrat kann später kommen als das Netz: darum bis 20× nachfassen, wie beim Hautton.
 */
import * as THREE from 'three';

export class Texturauflage {

    constructor(auftrag) {
        this.auftrag = auftrag;
        this.aktiv = false;
        this._lader = new THREE.TextureLoader();
    }

    anwenden(modell, fototextur, versuch = 0) {
        const kacheln = (fototextur || {}).kacheln || {};
        this.aktiv = Object.keys(kacheln).length > 0;
        if (!this.aktiv || !modell || !modell.bodyMesh) return;
        // Ein Lauf je Stand: derselbe Kachelsatz wird nicht noch einmal angestoßen.
        const stand = JSON.stringify(kacheln) + '|' + (modell.bodyMesh.uuid || '');
        if (versuch === 0) { if (stand === this._stand) return; this._stand = stand; }
        const materialien = Array.isArray(modell.bodyMesh.material) ? modell.bodyMesh.material : [modell.bodyMesh.material];
        let belegt = 0;
        for (const m of materialien) {
            const kachel = m && m.userData ? String(m.userData.kachel) : '';
            if (!kacheln[kachel]) continue;
            if (m.userData.fotokachel === kacheln[kachel]) { belegt += 1; continue; }
            const adresse = this.auftrag.dateiAdresse('ergebnis', kacheln[kachel]) + `?t=${Date.now()}`;
            this._lader.load(adresse, bild => {
                bild.colorSpace = THREE.SRGBColorSpace;
                m.map = bild;
                m.color.setRGB(1, 1, 1);
                m.userData.fotokachel = kacheln[kachel];
                m.needsUpdate = true;
            });
            belegt += 1;
        }
        // Das Netz der feinen Stufe kommt nach dem Käfig — dann noch einmal.
        if (versuch < 20) setTimeout(() => this.anwenden(modell, fototextur, versuch + 1), 1500);
    }
}
