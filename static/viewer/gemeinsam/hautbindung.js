/**
 * Hautbindung — ein Netz durch ein SkinnedMesh mit demselben Aussehen ersetzen.
 *
 * WARUM DIESES MODUL (28.08.2026, Befund `doppelcode`): Diese neun Zeilen
 *
 *     const mat = netz.material;
 *     const pos = netz.position.clone();
 *     const vis = netz.visible;
 *     szene.remove(netz);
 *     netz = new THREE.SkinnedMesh(geometrie, mat);
 *     netz.position.copy(pos);
 *     netz.visible = vis;
 *     netz.add(skelett.rootBone);
 *     netz.bind(skelett.skeleton);
 *     szene.add(netz);
 *
 * standen DREIMAL: `scene/skeleton.js`, `viewer/skinning.js` und
 * `result_character/mesh_loading.js`.
 *
 * SIE WAREN SCHON AUSEINANDERGELAUFEN: Die Fassung in `mesh_loading.js` hat
 * `visible` NICHT mitgenommen. Wer den Körper ausgeblendet hatte und dann das
 * Skelett zuschaltete, bekam ihn zurück — ohne dass der Schalter umsprang.
 * Beim Zusammenziehen gilt die vollständige Fassung; das ist eine Änderung an
 * genau dieser einen Stelle, und sie ist hier benannt.
 *
 * WAS SONST PASSIERT, WENN MAN EINE ZEILE VERGISST: Ein SkinnedMesh ohne
 * `bind()` rendert in der Ruhelage und bewegt sich nie — es sieht aus wie ein
 * Modell, das die Animation nicht kennt. Ohne `rootBone` als Kind bleiben die
 * Knochenmatrizen auf Identität; das Ergebnis ist dasselbe, nur aus einem
 * anderen Grund. Beides wirft nichts.
 */
export class Hautbindung {

    /**
     * @param szene die Szene, in der das Netz hängt
     * @param netz das bisherige (nicht gebundene) Netz
     * @param geometrie die Geometrie MIT `skinIndex`/`skinWeight`
     * @param skelett {rootBone, skeleton} aus `buildRigifySkeleton`
     * @param THREE die Three.js-Instanz der Seite
     * @returns das neue SkinnedMesh
     */
    static ersetzen(szene, netz, geometrie, skelett, THREE) {
        const werkstoff = netz.material;
        const ort = netz.position.clone();
        const sichtbar = netz.visible;
        szene.remove(netz);

        const gebunden = new THREE.SkinnedMesh(geometrie, werkstoff);
        gebunden.position.copy(ort);
        gebunden.visible = sichtbar;
        gebunden.add(skelett.rootBone);
        gebunden.bind(skelett.skeleton);
        szene.add(gebunden);
        return gebunden;
    }
}
