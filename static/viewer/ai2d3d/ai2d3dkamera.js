/**
 * Ai2d3dkamera — die Kamera der Fotos auf der Seite „2d-3d-AI“ (24.10.2026): dieselbe Regel, nach der die Charakter-Seite die vier Exportfotos aufnimmt (`charakter/modellansichten.js`,
 * `Modellansichten.aufnehmen`): Blick auf die Mitte der Hülle, Abstand so, dass Höhe und Breite mit dem Rand ins Bild passen, plus halbe Tiefe. Hier für JEDEN Winkel um die Hochachse
 * (echte Fotos stehen auch bei 45°) — bei 0/90/180/270° ergibt die Formel genau die der Charakter-Seite (Breite = x bzw. z, Tiefe = z bzw. x).
 *
 * `rahmen`: Drehung vom Rahmen der Fotos in die Welt des Felds. Exporte: der Rahmen der Figurgruppe (vorne = +Z der Gruppe); die Mesh3D-AI-Figuren stehen im Rahmen des Datensatzes
 * (`Mesh3daigenesisfigur` richtet sie auf das Rig der Probe aus) — `Ai2d3dgenesis.rahmen` misst die Drehung dazwischen an der wahren Figur. Ohne Wahrheit: keine Drehung.
 */
import * as THREE from 'three';

export class Ai2d3dkamera {
    /** Höchstens so viele Punkte je Netz für die Hülle (wie `Modellansichten.PROBEN`): jeder Punkt wird gehäutet. */
    static PROBEN = 80000;

    /** Richtung von der Figur zur Kamera im Rahmen der Fotos: 0° vorne (+Z), 90° links (+X, die linke Körperseite), 180° hinten, 270° rechts. */
    static richtung(winkel) {
        const w = THREE.MathUtils.degToRad(winkel);
        return new THREE.Vector3(Math.sin(w), 0, Math.cos(w));
    }

    /**
     * Die Hülle der sichtbaren Netze unter `wurzel` im Rahmen der Fotos — gehäutet und mit Morphs (`getVertexPosition`), wie `Modellansichten._huelle`.
     * @param {THREE.Object3D} wurzel @param {THREE.Quaternion} rahmen Fotos → Welt @returns {THREE.Box3}
     */
    static huelle(wurzel, rahmen) {
        wurzel.updateMatrixWorld(true);
        const box = new THREE.Box3(), umkehr = rahmen.clone().invert(), p = new THREE.Vector3();
        wurzel.traverseVisible(o => {
            const lage = o.geometry?.getAttribute?.('position');
            if (!o.isMesh || !lage) return;
            const schritt = Math.max(1, Math.floor(lage.count / Ai2d3dkamera.PROBEN));
            for (let i = 0; i < lage.count; i += schritt) {
                o.getVertexPosition(i, p);
                box.expandByPoint(p.applyMatrix4(o.matrixWorld).applyQuaternion(umkehr));
            }
        });
        return box;
    }

    /**
     * Die Kamera nach der Regel stellen. @param {THREE.PerspectiveCamera} kamera (FOV und Seitenverhältnis gesetzt) @param {THREE.Box3} box im Rahmen der Fotos
     * @param {number} winkel Grad @param {THREE.Quaternion} rahmen @param {number} rand Luft um die Figur (`Modellansichten.RAND`) @returns {THREE.Vector3} das Blickziel in der Welt
     */
    static stellen(kamera, box, winkel, rahmen, rand = 1.08) {
        const mitte = box.getCenter(new THREE.Vector3()), g = box.getSize(new THREE.Vector3()), r = Ai2d3dkamera.richtung(winkel);
        const breite = Math.abs(r.z) * g.x + Math.abs(r.x) * g.z, tiefe = Math.abs(r.x) * g.x + Math.abs(r.z) * g.z;
        const halbTan = Math.tan(THREE.MathUtils.degToRad(kamera.fov / 2));
        const abstand = Math.max(g.y / 2 / halbTan, breite / 2 / (halbTan * kamera.aspect)) * rand + tiefe / 2;
        const ziel = mitte.clone().applyQuaternion(rahmen);
        kamera.position.copy(mitte).addScaledVector(r, abstand).applyQuaternion(rahmen);
        kamera.up.set(0, 1, 0).applyQuaternion(rahmen);
        kamera.lookAt(ziel);
        const entfernung = kamera.position.distanceTo(ziel);
        kamera.near = entfernung / 50;
        kamera.far = entfernung * 4;
        kamera.updateProjectionMatrix();
        return ziel;
    }

    /** Ein Feld (`Mesh3daiansicht`) auf den Winkel stellen: Kamera und Drehpunkt der Steuerung. Liefert `false`, wenn nichts Sichtbares im Feld liegt. */
    static feldStellen(ansicht, winkel, rahmen, rand = 1.08) {
        const box = Ai2d3dkamera.huelle(ansicht.inhalt, rahmen);
        if (box.isEmpty()) return false;
        const ziel = Ai2d3dkamera.stellen(ansicht.kamera, box, winkel, rahmen, rand);
        ansicht.steuerung.target.copy(ziel);
        ansicht.steuerung.update();
        ansicht.zeichnen();
        return true;
    }
}
