import { THREE } from './state.js';
import { Lippengruppe } from '../gemeinsam/lippengruppe.js';
import { Detailfarben } from '../gemeinsam/detailfarben.js';

/**
 * Lippenbau — die Lippengruppe am Körpernetz der Szene anlegen.
 *
 * Die Sortierung rechnet `gemeinsam/lippengruppe.js` (ohne Three.js); hier
 * kommt die Netzseite dazu: neuer Index, neue Gruppen, und das zwölfte
 * Material (Index `Lippengruppe.LIPPEN`) hinter den elf aus
 * `koerpermaterialien.js`. Farbe und Glanz setzt danach
 * `Koerperdetails.anwenden` aus `inst.details` — hier steht nur die Vorgabe.
 *
 * EINMAL JE GEOMETRIE, direkt nach `Koerpernetz.netz` und VOR allem, was den
 * Index liest: `Hautverdeckung`/`Figurhaut` merken sich den vollen Index beim
 * ersten Maskieren (`userData.indexVoll`), `Koerperdetails` ihren Plan — beide
 * müssen die Lippen schon als Gruppe 11 sehen. Ein Morph-Nachladen
 * (`nur_punkte=1`) ersetzt nur die Punkte, die Gruppe bleibt.
 */
export class Lippenbau {

    static RAUHEIT = 1 - Detailfarben.VORGABE.lippen_glanz;

    /**
     * @param netz    Körpernetz mit Materialliste
     * @param lippen  Punktindizes der Lippen (`lippen` der Netzantwort)
     * @returns Zahl der abgespaltenen Dreiecke (0 = nichts getan)
     */
    static abspalten(netz, lippen) {
        const geo = netz?.geometry;
        if (!geo?.index || !lippen?.length || !Array.isArray(netz.material)) return 0;
        const aus = Lippengruppe.abspalten(geo.index.array, geo.groups, lippen);
        if (!aus.dreiecke) return 0;
        geo.setIndex(new THREE.BufferAttribute(aus.index, 1));
        geo.clearGroups();
        for (const g of aus.gruppen) geo.addGroup(g.start, g.count, g.materialIndex);
        netz.material[Lippengruppe.LIPPEN] = new THREE.MeshStandardMaterial({
            color: new THREE.Color(Detailfarben.VORGABE.lippen), roughness: Lippenbau.RAUHEIT,
            metalness: 0, side: THREE.DoubleSide });
        geo.userData.lippen = aus.dreiecke;
        return aus.dreiecke;
    }
}
