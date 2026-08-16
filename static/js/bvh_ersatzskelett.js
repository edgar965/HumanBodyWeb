/**
 * Ersatzskelett — die T-Pose-Figur, die die Auftragsseite zeigt, solange keine
 * echte Animation läuft.
 *
 * Aus `bvh_viewer.js` herausgeloest (Umbau 16.08.2026): `drawSimpleSkeleton()`
 * stand mitten in `initBVHViewer()` und trug seine 16 Gelenke und 15 Knochen
 * als Zahlenlisten im Rumpf. Sie stehen jetzt als benannte Tabellen oben.
 *
 * Klassisches Skript, kein ES-Modul: Die Seite lädt three.js r128 als globales
 * `THREE` vom CDN.
 */
class Ersatzskelett {

    static GELENKFARBE = 0xe94560;
    static KNOCHENFARBE = 0xff6b81;
    static GELENKGROESSE = 3;
    static KNOCHENDICKE = 1.5;

    /** Gelenke in Zentimetern über dem Boden: [x, y, z]. */
    static GELENKE = [
        [0, 100, 0],     //  0 Becken
        [0, 140, 0],     //  1 Lende
        [0, 170, 0],     //  2 Brust
        [0, 185, 0],     //  3 Kopf
        [-20, 170, 0],   //  4 Schulter links
        [-50, 150, 0],   //  5 Ellbogen links
        [-70, 130, 0],   //  6 Hand links
        [20, 170, 0],    //  7 Schulter rechts
        [50, 150, 0],    //  8 Ellbogen rechts
        [70, 130, 0],    //  9 Hand rechts
        [-10, 100, 0],   // 10 Hüfte links
        [-10, 55, 0],    // 11 Knie links
        [-10, 10, 0],    // 12 Fuß links
        [10, 100, 0],    // 13 Hüfte rechts
        [10, 55, 0],     // 14 Knie rechts
        [10, 10, 0],     // 15 Fuß rechts
    ];

    /** Knochen als Gelenkpaare. */
    static KNOCHEN = [
        [0, 1], [1, 2], [2, 3],          // Rumpf
        [2, 4], [4, 5], [5, 6],          // Arm links
        [2, 7], [7, 8], [8, 9],          // Arm rechts
        [0, 10], [10, 11], [11, 12],     // Bein links
        [0, 13], [13, 14], [14, 15],     // Bein rechts
    ];

    /** Figur in die Gruppe zeichnen. */
    static zeichnen(gruppe) {
        const gelenkstoff = new THREE.MeshPhongMaterial(
            { color: Ersatzskelett.GELENKFARBE });
        for (const [x, y, z] of Ersatzskelett.GELENKE) {
            const kugel = new THREE.Mesh(
                new THREE.SphereGeometry(Ersatzskelett.GELENKGROESSE, 8, 8),
                gelenkstoff);
            kugel.position.set(x, y, z);
            gruppe.add(kugel);
        }
        const knochenstoff = new THREE.MeshPhongMaterial(
            { color: Ersatzskelett.KNOCHENFARBE });
        for (const [von, nach] of Ersatzskelett.KNOCHEN) {
            gruppe.add(Ersatzskelett._knochen(von, nach, knochenstoff));
        }
        return gruppe;
    }

    /** Zylinder von Gelenk zu Gelenk. */
    static _knochen(von, nach, stoff) {
        const anfang = new THREE.Vector3(...Ersatzskelett.GELENKE[von]);
        const ende = new THREE.Vector3(...Ersatzskelett.GELENKE[nach]);
        const richtung = new THREE.Vector3().subVectors(ende, anfang);
        const koerper = new THREE.Mesh(
            new THREE.CylinderGeometry(Ersatzskelett.KNOCHENDICKE,
                                       Ersatzskelett.KNOCHENDICKE,
                                       richtung.length(), 6),
            stoff);
        koerper.position.copy(anfang).add(richtung.multiplyScalar(0.5));
        koerper.lookAt(ende);
        // Zylinder zeigen in Y, lookAt richtet nach Z — daher die Vierteldrehung.
        koerper.rotateX(Math.PI / 2);
        return koerper;
    }
}
