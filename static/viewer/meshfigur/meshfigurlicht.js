import * as THREE from 'three';

/**
 * Meshfigurlicht — das Licht der 3D-Ansichten von „Mesh to 3D“ und „Mesh-3D“ (12.10.2026).
 *
 * Edgar: „mach eine zweite 3D View im Job wo ich NUR das Mesh sehen kann, mit der gleichen Beleuchtung wie das 3D Modell“. Damit die zweite Ansicht nicht irgendwann anders
 * leuchtet als die erste, steht das Licht an EINER Stelle: ein Himmelslicht von oben (weiß, Boden warm-grau) und ein Hauptlicht, das an der Kamera hängt (schräg von rechts oben
 * vorn) — es wandert beim Drehen der Ansicht mit, sein Ziel ist der Ursprung der Szene. Genutzt von `Meshfigurbuehne` (Figur + Netz) und `Mesh3dnetzbuehne` (nur das Netz).
 */
export class Meshfigurlicht {
    static HIMMEL = 0xffffff;
    static BODEN = 0xc8c2ba;
    static STAERKE_HIMMEL = 1.3;
    static STAERKE_HAUPT = 1.0;
    /** Lage des Hauptlichts in Kamerakoordinaten. */
    static HAUPT_POSITION = [1, 1.5, 2];

    /** Das Licht in die Szene stellen; die Kamera kommt mit hinein (das Hauptlicht ist ihr Kind). */
    static einrichten(szene, kamera) {
        szene.add(new THREE.HemisphereLight(Meshfigurlicht.HIMMEL, Meshfigurlicht.BODEN, Meshfigurlicht.STAERKE_HIMMEL));
        const haupt = new THREE.DirectionalLight(0xffffff, Meshfigurlicht.STAERKE_HAUPT);
        haupt.position.set(...Meshfigurlicht.HAUPT_POSITION);
        kamera.add(haupt);
        szene.add(kamera);
    }
}
