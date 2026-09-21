/**
 * Texturauflage — die gebackenen Fotokacheln (Stufe 2) auf das Modell der Auftragsseite legen.
 *
 * `ergebnis.fototextur.kacheln` (`Bildmodellfototextur`): je UDIM-Kachel eine JPG im
 * Auftrag, Fotofarbe über der getönten Daz-Albedo. Jede Materialgruppe des Körpers kennt
 * ihre Kachel (`material.userData.kachel`, `Genesis9netz.materialien`); für diese Gruppen
 * wird die Kachel als `map` eingehängt und die Farbe auf Weiß gestellt — der Hautton der
 * Stufe 1 (`ansicht3d.hauttonAnwenden`) steckt schon in der Kachel. Die Albedo aus dem
 * Texturvorrat kann später kommen als das Netz: darum bis 20× nachfassen, wie beim Hautton.
 * `fototextur.stand` (Zeit des Backens) gehört zum Stand: „Textur anpassen" schreibt dieselben
 * Dateinamen neu, die Kacheln müssen trotzdem neu geladen werden.
 *
 * Dazu seit 21.09.2026 `fototextur.verschiebung` (`Bildmodellhautverschiebung`: Alter, Tonus,
 * Masse aus MB-Labs Displacement, je Kachel ein Graustufen-PNG) als `displacementMap` —
 * Stärke und Bias wie `hauttextur.js` (0,01 m, −0,005: Texel 0,5 verschiebt nicht).
 */
import * as THREE from 'three';

export class Texturauflage {

    static VERSCHIEBUNG = 0.01;

    constructor(auftrag) {
        this.auftrag = auftrag;
        this.aktiv = false;
        this._lader = new THREE.TextureLoader();
    }

    anwenden(modell, fototextur, versuch = 0) {
        const kacheln = (fototextur || {}).kacheln || {};
        const verschiebung = (fototextur || {}).verschiebung || {};
        this.aktiv = Object.keys(kacheln).length > 0;
        if (!this.aktiv || !modell || !modell.bodyMesh) return;
        // Ein Lauf je Stand: derselbe Kachelsatz wird nicht noch einmal angestoßen.
        const marke = String((fototextur || {}).stand || '');
        const stand = JSON.stringify([kacheln, verschiebung]) + '@' + marke + '|' + (modell.bodyMesh.uuid || '');
        if (versuch === 0) { if (stand === this._stand) return; this._stand = stand; }
        const materialien = Array.isArray(modell.bodyMesh.material) ? modell.bodyMesh.material : [modell.bodyMesh.material];
        for (const m of materialien) {
            const kachel = m && m.userData ? String(m.userData.kachel) : '';
            if (!kacheln[kachel]) continue;
            this._laden(m, 'fotokachel', kacheln[kachel], marke, bild => {
                bild.colorSpace = THREE.SRGBColorSpace;
                m.map = bild;
                m.color.setRGB(1, 1, 1);
            });
            if (verschiebung[kachel]) {
                this._laden(m, 'verschiebung', verschiebung[kachel], marke, bild => {
                    bild.colorSpace = THREE.NoColorSpace;
                    m.displacementMap = bild;
                    m.displacementScale = Texturauflage.VERSCHIEBUNG;
                    m.displacementBias = -Texturauflage.VERSCHIEBUNG / 2;
                });
            } else if (m.displacementMap) {
                m.displacementMap = null; m.displacementScale = 1; m.displacementBias = 0;
                m.userData.verschiebung = ''; m.needsUpdate = true;
            }
        }
        // Das Netz der feinen Stufe kommt nach dem Käfig — dann noch einmal.
        if (versuch < 20) setTimeout(() => this.anwenden(modell, fototextur, versuch + 1), 1500);
    }

    /** Eine Kachel laden und über `setzen` ans Material hängen — einmal je Datei und Stand. */
    _laden(m, feld, datei, marke, setzen) {
        const kennung = datei + '@' + marke;
        if (m.userData[feld] === kennung) return;
        m.userData[feld] = kennung;
        const adresse = this.auftrag.dateiAdresse('ergebnis', datei) + `?t=${marke || Date.now()}`;
        this._lader.load(adresse, bild => {
            if (m.userData[feld] !== kennung) return;   // inzwischen ein neuerer Stand
            setzen(bild);
            m.needsUpdate = true;
        });
    }
}
