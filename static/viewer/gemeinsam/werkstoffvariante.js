/**
 * Werkstoffvariante — ein Werkstoff ohne Bildkarten, für „Textur aus".
 *
 * NUR FÜR EXPORT-KOPIEN, NIE FÜR DIE LEBENDE SZENE (26.09.2026): Für
 * OBJ/PLY/STL/DAE arbeitet der Modellexport ohnehin mit gebackenen Kopien
 * (`Netzpose.gebacken`) — dort darf `material` bedenkenlos ausgetauscht
 * werden. Für GLB/.blend MIT Rig exportiert der Modellexport dagegen das
 * lebende `SkinnedMesh` (ein Klon würde das Skelett neu binden müssen, siehe
 * `three/addons/utils/SkeletonUtils.js` — hier bewusst nicht nachgebaut).
 * `Modellexport.ohneLiveTextur` tauscht dafür `mesh.material` NUR FÜR DIE
 * DAUER DES EXPORTS aus und stellt es in einem `finally` zurück — ein
 * Wimpernschlag lang zeigt die Bühne dann das texturlose Netz. Bekannter,
 * bewusst in Kauf genommener Kompromiss, kein Übersehen.
 */
export class Werkstoffvariante {

    //: Slots, die Three.js' Standard- und Physical-Material kennen. `feld in
    //: werkstoff` schützt vor `undefined`-Zuweisungen an Materialtypen, die
    //: den Slot gar nicht haben.
    static BILDSLOTS = [
        'map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap',
        'bumpMap', 'alphaMap', 'displacementMap', 'clearcoatMap', 'clearcoatNormalMap',
        'clearcoatRoughnessMap', 'sheenColorMap', 'sheenRoughnessMap', 'specularMap',
        'specularColorMap', 'specularIntensityMap', 'transmissionMap', 'thicknessMap',
        'iridescenceMap', 'iridescenceThicknessMap',
    ];

    /** Ein Klon des Werkstoffs — dieselbe Farbe, keine Bildkarten. */
    static klonOhneTextur(werkstoff) {
        const klon = werkstoff.clone();
        for (const feld of Werkstoffvariante.BILDSLOTS) if (feld in klon) klon[feld] = null;
        klon.needsUpdate = true;
        return klon;
    }

    /**
     * `obj.material` (Einzel- oder Array) je Objekt gegen texturlose Klone
     * tauschen. @returns eine Funktion, die den Originalzustand zurückholt.
     */
    static tauschen(objekte) {
        const original = objekte.map((obj) => obj.material);
        objekte.forEach((obj) => {
            obj.material = Array.isArray(obj.material)
                ? obj.material.map((m) => Werkstoffvariante.klonOhneTextur(m))
                : Werkstoffvariante.klonOhneTextur(obj.material);
        });
        return () => objekte.forEach((obj, i) => { obj.material = original[i]; });
    }
}
