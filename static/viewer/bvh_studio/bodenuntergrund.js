import * as THREE from 'three';

/**
 * Bodenuntergrund — der durchsichtige Boden und die opake Platte darunter.
 *
 * WARUM (Edgar, 13.09.2026: „beim Boden eine Transparenzeinstellung — die Füße
 * des Modells versinken immer noch im Boden, die sollen dann nicht verschwinden,
 * sondern noch sichtbar sein. Zwei Balken: Transparenz in % und Transparenz bis
 * zu wieviel cm"): Der Boden bekommt `opacity = 1 − Transparenz`, und in
 * `Tiefe` cm darunter liegt eine zweite, undurchsichtige Platte (Kind des
 * Bodennetzes, gleiche Geometrie, abgedunkelte Bodenfarbe). Was zwischen Boden
 * und Platte liegt — die versunkenen Füße —, scheint durch; was tiefer liegt,
 * verdeckt die Platte. Kein Clipping, keine offenen Schnittkanten an der Figur.
 *
 * Felder an der Bodenspur: `floorTransparenz` (0–100 %), `floorTiefe` (cm).
 */
export class Bodenuntergrund {
    /** Vorgaben: undurchsichtig, und wenn durchsichtig, 10 cm Blick nach unten. */
    static TRANSPARENZ = 0;
    static TIEFE_CM = 10;
    /** Wie viel dunkler die Platte als der Boden ist. */
    static ABDUNKELN = 0.6;
    /** Kleiner Abstand gegen Z-Fighting, wenn die Tiefe 0 ist. */
    static ABSTAND = 0.001;

    /** Durchlässigkeit 0…1 aus den Prozent der Spur. */
    static durchlaessigkeit(track) {
        const t = Number(track.floorTransparenz) || 0;
        return Math.min(1, Math.max(0, t / 100));
    }

    /** Boden-Material und Platte auf den Stand der Spur bringen. */
    static nachziehen(track) {
        const boden = track?.mesh;
        if (!boden?.material) return;
        const durch = Bodenuntergrund.durchlaessigkeit(track);
        const m = boden.material;
        m.transparent = durch > 0;
        m.opacity = 1 - durch;
        m.needsUpdate = true;

        const platte = Bodenuntergrund._platte(track);
        const tiefe = Math.max(0, Number(track.floorTiefe ?? Bodenuntergrund.TIEFE_CM)) / 100;
        platte.visible = durch > 0;
        platte.position.y = -(tiefe + Bodenuntergrund.ABSTAND);
        platte.geometry = boden.geometry;          // folgt jeder Größenänderung
        platte.material.color.copy(m.color).multiplyScalar(Bodenuntergrund.ABDUNKELN);
        platte.material.roughness = m.roughness;
        platte.material.metalness = m.metalness;
    }

    /** Die Platte unter dem Boden — beim ersten Aufruf angelegt, als Kind des Bodens. */
    static _platte(track) {
        if (track._untergrund) return track._untergrund;
        const material = new THREE.MeshStandardMaterial({ side: THREE.DoubleSide });
        const platte = new THREE.Mesh(track.mesh.geometry, material);
        platte.receiveShadow = true;
        platte.userData.isFloorUnderground = true;
        track.mesh.add(platte);
        track._untergrund = platte;
        return platte;
    }
}
