import * as THREE from 'three';
import { _mergeSimpleGeos, _buildPlane, _buildRhombus, _makeDoubleSided } from './formenbauer.js';
import { _buildSpiralTutu, _buildSkirt } from './formen_band.js';
import { Wendelband } from './wendelband.js';

/**
 * Formstück — die Geometrie EINES Knochenteils und ihre Lage im Raum.
 *
 * WARUM (Befund `doppelcode`, 29.08.2026): `knochenformen.js` (DEF-Skelett)
 * und `rigformen.js` (Rigify-Rig) trugen diese beiden Abschnitte zeichengleich
 * doppelt — die Formen-Weiche mit ihren 15 Fällen und das Einpassen zwischen
 * Kopf und Spitze. Zusammen 82 von 205 bzw. 178 Zeilen, gemeldet als drei
 * Blöcke à 39, 18 und 18 Zeilen.
 *
 * Zwei Dinge unterscheiden die beiden Aufrufer, und nur zwei:
 *
 *   * Woher Kopf, Spitze und Länge kommen — beim DEF-Skelett aus der
 *     Knochenrichtung und dem längsten Kind, beim Rig aus `tailPos`.
 *   * Welcher Knochenindex am Ende drankommt.
 *
 * Beides bleibt beim jeweiligen Aufrufer. Was hier steht, ist der Teil, der
 * für beide gleich ist — und der bei einer neuen Form (`shape`) sonst an
 * ZWEI Stellen nachgezogen werden müsste. Genau das ist die Fehlerklasse:
 * Eine neue Form im DEF-Skelett, die im Rig stumm zum Zylinder wird.
 */
export class Formstueck {
    /**
     * Die Geometrie einer Form, zentriert im Ursprung, ausgerichtet auf Y.
     *
     * @param {Object} part Teil-Einstellungen (`shape` und ihre Beiwerte)
     * @param {number} radius Radius in Metern
     * @param {number} boneLen Länge des Knochens in Metern
     * @param {number} segments Rundungsauflösung
     * @returns {Object} BufferGeometry
     */
    static geometrie(part, radius, boneLen, segments) {
        switch (part.shape) {
            case 'box':
                return new THREE.BoxGeometry(radius * 2, boneLen, radius * 2, 1, 1, 1);
            case 'sphere_low':
                return new THREE.SphereGeometry(radius, segments, Math.max(4, segments >> 1));
            case 'sphere':
                return new THREE.SphereGeometry(radius, 24, 16);
            case 'cone':
                return new THREE.ConeGeometry(radius, boneLen, segments);
            case 'capsule':
                return new THREE.CapsuleGeometry(radius, Math.max(0.001, boneLen - radius * 2),
                                                 segments, Math.max(4, segments >> 1));
            case 'oval': {
                const geo = new THREE.SphereGeometry(radius, segments, Math.max(4, segments >> 1));
                geo.scale(1, boneLen / (radius * 2), 1);
                return geo;
            }
            case 'double_oval':
                return Formstueck._doppeloval(part, radius, boneLen, segments);
            case 'diamond': {
                const geo = new THREE.OctahedronGeometry(radius);
                geo.scale(1, boneLen / (radius * 2), 1);
                return geo;
            }
            case 'tutu':
                return Formstueck._tutu(part, radius, segments);
            case 'spiral_tutu':
                return _buildSpiralTutu(part, radius);
            case 'helix_ribbon':
                return Wendelband.bauen(part, radius);
            case 'skirt':
                return _buildSkirt(part, radius);
            case 'plane':
                return _buildPlane(part);
            case 'rhombus':
                return _buildRhombus(part);
            default: // cylinder
                return new THREE.CylinderGeometry(radius, radius, boneLen, segments, 1);
        }
    }

    /** Zwei überlappende Ovale übereinander — `overlap` regelt, wie weit. */
    static _doppeloval(part, radius, boneLen, segments) {
        const ov = part.overlap ?? 0.5;
        const halfLen = boneLen * 0.5;
        const ovalLen = halfLen + halfLen * ov;
        const scY = ovalLen / (radius * 2);
        const sep = halfLen * (1 - ov);
        const hSegs = Math.max(4, segments >> 1);
        const g1 = new THREE.SphereGeometry(radius, segments, hSegs);
        g1.scale(1, scY, 1); g1.translate(0, -sep, 0);
        const g2 = new THREE.SphereGeometry(radius, segments, hSegs);
        g2.scale(1, scY, 1); g2.translate(0, sep, 0);
        return _mergeSimpleGeos(g1, g2);
    }

    /** Flache Scheibe mit hängendem Aussenrand, als LatheGeometry gedreht. */
    static _tutu(part, radius, segments) {
        const thickness = part.tutuThickness ?? 0.01;
        const droop = part.tutuDroop ?? 0.03;
        const droopStart = part.tutuDroopStart ?? 0.7;
        const innerR = radius * 0.08; // kleines Loch mittig um den Knochen
        const outerR = radius;
        const halfT = thickness * 0.5;
        const droopR = outerR * droopStart;
        const radSegs = Math.max(16, segments * 4);
        // Profilpunkte in der XY-Ebene (X = Radius, Y = Höhe), um Y gedreht
        const pts = [
            new THREE.Vector2(innerR, halfT),                  // innen oben
            new THREE.Vector2(droopR, halfT),                  // flach bis zum Knick
            new THREE.Vector2(outerR, -droop),                 // Aussenkante haengt
            new THREE.Vector2(outerR - 0.002, -droop - halfT), // Aussenkante unten
            new THREE.Vector2(droopR, -halfT),                 // flach ab dem Knick
            new THREE.Vector2(innerR, -halfT),                 // innen unten
        ];
        const geo = _makeDoubleSided(new THREE.LatheGeometry(pts, radSegs));
        const tOff = part.tutuOffset ?? 0;
        if (Math.abs(tOff) > 0.0001) geo.translate(0, tOff, 0);
        return geo;
    }

    /**
     * Die Geometrie zwischen Kopf und Spitze legen — Ort UND Drehung.
     *
     * Wirkt auf `shapeGeo` selbst (`applyMatrix4`), wie die beiden Fassungen
     * vorher auch.
     *
     * @param {Object} shapeGeo BufferGeometry, zentriert im Ursprung
     * @param {Object} kopf Vector3, Ansatz des Knochens
     * @param {Object} spitze Vector3, Ende des Knochens
     * @param {Object} ersatzrichtung Vector3 — greift NUR, wenn Kopf und
     *     Spitze zusammenfallen. Beim DEF-Skelett ist das die Knochenrichtung,
     *     beim Rig die Y-Achse; das ist der einzige Unterschied der beiden
     *     Aufrufer an dieser Stelle.
     * @param {Object} part Teil-Einstellungen wegen `shapeRotation`
     */
    static einpassen(shapeGeo, kopf, spitze, ersatzrichtung, part) {
        const midpoint = new THREE.Vector3().lerpVectors(kopf, spitze, 0.5);
        const direction = new THREE.Vector3().subVectors(spitze, kopf);
        if (direction.length() > 0.0001) direction.normalize();
        else direction.copy(ersatzrichtung);

        const yAxis = new THREE.Vector3(0, 1, 0);
        const shapeQuat = new THREE.Quaternion();
        if (Math.abs(direction.dot(yAxis)) < 0.9999) {
            shapeQuat.setFromUnitVectors(yAxis, direction);
        } else if (direction.y < 0) {
            shapeQuat.setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI);
        }

        // Drehung um die Formmitte in Weltachsen: premultiply, damit sie NACH
        // der Ausrichtung am Knochen wirkt.
        if (part.shapeRotation) {
            const sr = part.shapeRotation;
            const rx = sr.x || 0, ry = sr.y || 0, rz = sr.z || 0;
            if (rx || ry || rz) {
                const deg = Math.PI / 180;
                const userRot = new THREE.Quaternion().setFromEuler(
                    new THREE.Euler(rx * deg, ry * deg, rz * deg));
                shapeQuat.premultiply(userRot);
            }
        }

        const mat4 = new THREE.Matrix4();
        mat4.compose(midpoint, shapeQuat, new THREE.Vector3(1, 1, 1));
        shapeGeo.applyMatrix4(mat4);
    }
}
