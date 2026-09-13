import * as THREE from 'three';
import { Lippengruppe } from './lippengruppe.js';
import { Detailfarben } from './detailfarben.js';
import { Lippenhaut } from './lippenhaut.js';

/**
 * Lippenbau — die Lippengruppe am Körpernetz anlegen (Szene und BVH Studio).
 *
 * Die Sortierung rechnet `gemeinsam/lippengruppe.js` (ohne Three.js); hier
 * kommt die Netzseite dazu: neuer Index, neue Gruppen, und das zwölfte
 * Material (Index `Lippengruppe.LIPPEN`) hinter den elf aus
 * `koerpermaterialien.js`. Farbe und Glanz setzt danach
 * `Koerperdetails.anwenden` aus den `details` der Figur — hier steht nur die
 * Vorgabe. Lag bis 13.09.2026 in `scene/`; das Studio baut seine Figur selbst
 * (`Spurfigur`) und zeigte keine Lippen (Edgar: „werden die Lippen,
 * Augenbrauen, Fingernägel usw. nicht angezeigt").
 *
 * EINMAL JE GEOMETRIE, direkt nach `Koerpernetz.netz` und VOR allem, was den
 * Index liest: `Hautverdeckung`/`Figurhaut` merken sich den vollen Index beim
 * ersten Maskieren (`userData.indexVoll`), `Koerperdetails` ihren Plan — beide
 * müssen die Lippen schon als Gruppe 11 sehen. Ein Morph-Nachladen
 * (`nur_punkte=1`) ersetzt nur die Punkte, die Gruppe bleibt.
 *
 * `lippen` kommt seit 13.09.2026 als `{punkte, saum}`: Mit Saum (Abstand zum
 * Lippenrand je Punkt) färbt der HAUTSHADER die Lippen und lässt den Rand
 * glatt auslaufen (`Lippenhaut`) — dann wird NICHT abgespalten, das
 * Lippenmaterial an Index LIPPEN bleibt nur der Wertehalter für Farbe und
 * Glanz. Ohne Saum (reine Punktliste, ältere Antwort) wie bisher je Dreieck.
 */
export class Lippenbau {

    static RAUHEIT = 1 - Detailfarben.VORGABE.lippen_glanz;

    /**
     * @param netz    Körpernetz mit Materialliste
     * @param lippen  `lippen` der Netzantwort: `{punkte, saum}` oder Punktindizes
     * @returns Zahl der abgespaltenen Dreiecke (0 = nichts getan)
     */
    static abspalten(netz, lippen) {
        const geo = netz?.geometry;
        const punkte = Array.isArray(lippen) ? lippen : lippen?.punkte;
        if (!geo?.index || !punkte?.length || !Array.isArray(netz.material)) return 0;
        netz.material[Lippengruppe.LIPPEN] = new THREE.MeshStandardMaterial({
            color: new THREE.Color(Detailfarben.VORGABE.lippen), roughness: Lippenbau.RAUHEIT,
            metalness: 0, side: THREE.DoubleSide });
        geo.userData.lippensaum = Lippenhaut.anlegen(netz, lippen);
        if (geo.userData.lippensaum) { geo.userData.lippen = 0; return 0; }
        const aus = Lippengruppe.abspalten(geo.index.array, geo.groups, punkte);
        if (!aus.dreiecke) return 0;
        geo.setIndex(new THREE.BufferAttribute(aus.index, 1));
        geo.clearGroups();
        for (const g of aus.gruppen) geo.addGroup(g.start, g.count, g.materialIndex);
        geo.userData.lippen = aus.dreiecke;
        return aus.dreiecke;
    }
}
