import { THREE } from './state.js';
import { Augenbrauen } from '../gemeinsam/augenbrauen.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Augenbrauenbau — die Brauen einer Figur als eigenes Netz in ihrer Gruppe.
 *
 * Die Härchen rechnet `gemeinsam/augenbrauen.js` aus dem Körper (Augenmitte,
 * Hautfläche); hier kommt Three.js dazu: Material (Farbe aus
 * `inst.details.brauen`), das Netz in `inst.group`, und die BEWEGUNG — ist
 * der Körper gehäutet, bekommt jeder Streifen die Hautgewichte seines
 * Wurzelpunkts und hängt am selben Skelett. So folgen die Brauen dem Kopf
 * wie die Wimpern, die Teil des Körpernetzes sind.
 *
 * NEU GEBAUT wird bei jedem Anlass, der die Haut verändert: Körper geladen,
 * Morphpunkte vom Server (`Charakterkoerper.reload`), Häutung
 * (`convertInstToSkinned`), Regler im Abschnitt. Der Bau kostet wenig (60
 * Streifen, Suche in ein paar tausend Hautpunkten), darum kein Zwischenstand.
 *
 * DER ANKER (Hautpunkte unter dem Bogen, `Augenbrauen.anker`) liegt an der
 * Geometrie (`userData.brauenanker`) und wird neu bestimmt, solange kein
 * `Eyebrows_*`-Morph steht — dann ist die Brauenhaut in Ruhe und der Bogen
 * vom Auge aus gilt. Steht einer, bleibt der gemerkte Anker, und die Streifen
 * folgen der gehobenen, gewölbten oder gekippten Haut. Ohne das stand die
 * Braue bei jedem Regler wieder an derselben Stelle (Edgar, 12.09.2026).
 */
export class Augenbrauenbau {

    static NAME = 'augenbrauen';
    static RAUHEIT = 0.9;
    static MORPHVORSATZ = 'Eyebrows_';

    /**
     * Brauen der Figur (neu) bauen. `punkte` sind frisch gelieferte
     * Körperpunkte, sonst gilt das Positionsattribut des Körpers.
     * @returns Zahl der Streifen (0 = nichts gebaut)
     */
    static bauen(inst, punkte = null) {
        const koerper = inst?.bodyMesh;
        const geo = koerper?.geometry;
        if (!geo?.attributes?.position || !inst.details) return 0;
        const index = geo.userData?.indexVoll?.index || geo.index?.array;
        const gruppen = geo.userData?.indexVoll?.gruppen || geo.groups;
        if (!index || !gruppen?.length) return 0;
        const roh = Augenbrauen.bauen(punkte || geo.attributes.position.array, index, gruppen,
                                      inst.details.brauen_staerke ?? 1,
                                      Augenbrauenbau.anker(inst, geo));
        geo.userData.brauenanker = roh.anker;
        Augenbrauenbau.entfernen(inst);
        if (!roh.haare) return 0;
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(roh.positionen, 3));
        g.setIndex(new THREE.BufferAttribute(roh.index, 1));
        g.computeVertexNormals();
        const material = new THREE.MeshStandardMaterial({
            color: new THREE.Color(inst.details.brauen), roughness: Augenbrauenbau.RAUHEIT,
            metalness: 0, side: THREE.DoubleSide });
        const netz = Augenbrauenbau._netz(g, material, koerper, roh.wurzeln);
        netz.name = Augenbrauenbau.NAME;
        netz.userData.augenbrauen = true;
        netz.visible = koerper.visible;
        inst.augenbrauen = netz;
        inst.group.add(netz);
        return roh.haare;
    }

    /** Der gemerkte Anker — oder null, wenn er (neu) vom Auge aus bestimmt werden soll. */
    static anker(inst, geo) {
        const ruhe = !Object.keys(inst.morphs || {}).some(n => n.startsWith(Augenbrauenbau.MORPHVORSATZ));
        return ruhe ? null : (geo.userData.brauenanker || null);
    }

    /** Gehäuteter Körper → gehäutete Brauen mit den Gewichten der Wurzelpunkte. */
    static _netz(g, material, koerper, wurzeln) {
        const si = koerper.geometry.attributes.skinIndex;
        const sw = koerper.geometry.attributes.skinWeight;
        if (!koerper.isSkinnedMesh || !si || !sw || !koerper.skeleton) {
            return new THREE.Mesh(g, material);
        }
        const n = wurzeln.length;
        const indizes = new Float32Array(n * 4), gewichte = new Float32Array(n * 4);
        for (let i = 0; i < n; i++) {
            const w = wurzeln[i];
            for (let k = 0; k < 4; k++) {
                indizes[4 * i + k] = si.getComponent(w, k);
                gewichte[4 * i + k] = sw.getComponent(w, k);
            }
        }
        g.setAttribute('skinIndex', new THREE.Float32BufferAttribute(indizes, 4));
        g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(gewichte, 4));
        const netz = new THREE.SkinnedMesh(g, material);
        netz.bind(koerper.skeleton, koerper.bindMatrix);
        return netz;
    }

    /** Nur die Farbe — ohne Neubau. */
    static faerben(inst) {
        const m = inst?.augenbrauen?.material;
        if (!m?.color || !inst.details?.brauen) return false;
        m.color.set(inst.details.brauen);
        return true;
    }

    static entfernen(inst) {
        if (!inst?.augenbrauen) return;
        Netzentsorgung.entfernen(inst.group, inst.augenbrauen);
        inst.augenbrauen = null;
    }

    static sichtbar(inst, sichtbar) {
        if (inst?.augenbrauen) inst.augenbrauen.visible = !!sichtbar;
    }

    /** Bauen und Fehler melden statt werfen — der Aufrufer baut gerade den Körper. */
    static sicher(inst, punkte = null) {
        try {
            return Augenbrauenbau.bauen(inst, punkte);
        } catch (fehler) {
            Protokoll.warnung('Augenbrauen', fehler.message);
            return 0;
        }
    }
}
