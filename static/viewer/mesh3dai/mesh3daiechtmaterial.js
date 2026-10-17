/**
 * Mesh3daiechtmaterial — die Ansichtsarten (`Mesh3daimaterial.MODI`) für die ECHTE Figur auf der Seite „Mesh3D-AI“ (15.10.2026, Edgar: „wo ist die Umschaltung der Ansicht verschwunden?“).
 * Farben gibt es nur in „Textur“ und „Punkte“; Oberfläche, Drahtnetz, Oberfläche + Drahtnetz, Matcap und Röntgen zeichnen ALLE Felder in einer Farbe (`EINHEIT`) — Edgar, 15.10.2026: „warum ist links das Modell
 * blau (also mit textur), bei Ansicht Oberfläche? das muss einheitlich sein in allen views“ (links stand die Außenfläche mit den blauen Kleidern, Mitte und rechts der Körper in Hautfarbe).
 * „Textur“: die Bilder der Figur, wenn der Job sie hat (`Mesh3daitexturen`), sonst die Farbe je Punkt; „Punkte“ zeichnet die Punkte der Fläche in der Farbe je Punkt.
 */
import * as THREE from 'three';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';
import { Mesh3daitextur } from './mesh3daitextur.js';

export class Mesh3daiechtmaterial {
    static PUNKTGROESSE = 0.006;
    /** Die eine Farbe aller Felder in Oberfläche, Drahtnetz, Matcap, Röntgen (heller Ton wie Blenders „Solid“, auf dem hellen und dem dunklen Grund zu sehen). */
    static EINHEIT = 0xc4bcb2;

    static _mat(schluessel, fabrik) {
        return Mesh3daigemeinsam.material(`echt:${schluessel}`, fabrik);
    }

    /**
     * Die Fläche des Soll als Geist unter der Ausgabe. Er wird ZUERST gezeichnet (`renderOrder` −1, im Durchgang der deckenden Objekte, additiv, ohne Tiefe) und von der Ausgabe ganz überdeckt — zu sehen ist
     * er nur, wo die Vorhersage danebenliegt. Die erste Fassung (durchscheinend, Tiefentest gegen die Ausgabe) lag fleckig über Hemd und Hose, wo beide Flächen fast gleich tief liegen
     * (Edgar, 15.10.2026: „warum ist im Ergebnisfenster das Modell doppelt, oder mit schatten?“).
     */
    static geist(geo) {
        const mesh = new THREE.Mesh(geo, Mesh3daiechtmaterial._mat('geist', () => new THREE.MeshBasicMaterial({ color: 0x2c3342, blending: THREE.AdditiveBlending, depthWrite: false })));
        mesh.renderOrder = -1;
        return mesh;
    }

    /** @param {THREE.BufferGeometry} geo mit `color` je Punkt @param {string} modus Schlüssel aus `Mesh3daimaterial.MODI` @returns {THREE.Object3D} */
    /**
     * @param {THREE.BufferGeometry} geo mit `color` je Punkt (bei Bildern dazu `uv` und Gruppen je Material) @param {string} modus Schlüssel aus `Mesh3daimaterial.MODI`
     * @param {THREE.Material[]|null} bilder die Materialien mit den Bildern der Figur in der Reihenfolge der Gruppen von `geo` (nur „Textur“) @returns {THREE.Object3D}
     */
    static netz(geo, modus, bilder = null) {
        const m = Mesh3daiechtmaterial._mat;
        const farbe = Mesh3daiechtmaterial.EINHEIT;
        switch (modus) {
            case 'drahtnetz':
                return new THREE.Mesh(geo, m('draht', () => new THREE.MeshBasicMaterial({ color: farbe, wireframe: true })));
            case 'oberflaeche_draht': {
                const gruppe = new THREE.Group();
                gruppe.add(new THREE.Mesh(geo, m('flaeche_versetzt', () => new THREE.MeshStandardMaterial({ color: farbe, roughness: 0.75, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 }))));
                gruppe.add(new THREE.Mesh(geo, m('draht_weiss', () => new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: true, transparent: true, opacity: 0.25 }))));
                return gruppe;
            }
            case 'textur':
                if (bilder?.length && geo.groups.length) return new THREE.Mesh(geo, bilder);
                return new THREE.Mesh(geo, m('textur', () => new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.8 })));
            case 'matcap':
                return new THREE.Mesh(geo, m('matcap', () => new THREE.MeshMatcapMaterial({ matcap: Mesh3daitextur.matcap(), color: farbe })));
            case 'normalen':
                return new THREE.Mesh(geo, m('normalen', () => new THREE.MeshNormalMaterial()));
            case 'roentgen':
                return new THREE.Mesh(geo, m('roentgen', () => new THREE.MeshBasicMaterial({ color: 0x8f877e, transparent: true, opacity: 0.28, depthWrite: false, blending: THREE.AdditiveBlending })));
            case 'punkte':
                return new THREE.Points(geo, m('punkte', () => new THREE.PointsMaterial({ size: Mesh3daiechtmaterial.PUNKTGROESSE, vertexColors: true, sizeAttenuation: true })));
            default:
                return new THREE.Mesh(geo, m('oberflaeche', () => new THREE.MeshStandardMaterial({ color: farbe, roughness: 0.75 })));
        }
    }
}
