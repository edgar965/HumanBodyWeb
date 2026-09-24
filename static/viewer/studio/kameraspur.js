import * as THREE from 'three';
import { state } from './state.js';
import { Schluesselpaar } from './schluesselpaar.js';

/**
 * Kameraspur — die Kamera auf den Stand des Abspielkopfs setzen.
 *
 * Herausgelöst aus `spur_anwenden.js` (288 Zeilen).
 *
 * ZWEI WEGE, UND DER ERSTE IST DER RICHTIGE
 * =========================================
 * 1. **Blickziel (`lookAt`).** Haben beide Keyframes eines, werden Standort UND
 *    Ziel gemischt und die Kamera schaut auf den gemischten Punkt. Das ist die
 *    „Maya-Cam"-Bedeutung und der Grund, warum die Kamera nicht mitten im Flug
 *    am Motiv vorbeischaut — der häufigste Klagepunkt („Kamera bewegt sich wirr
 *    durch die Szene").
 * 2. **Drehung (Quaternion-Slerp).** Für ältere Projekte ohne Blickziel. Mit
 *    Short-Arc-Korrektur: Zeigen die beiden Quaternionen in verschiedene
 *    Hemisphären (`dot < 0`), wird eines negiert. Ohne das dreht die Kamera
 *    einmal fast ganz herum, obwohl beide Keyframes dieselbe Blickrichtung
 *    meinen.
 *
 * WARUM DIE UMLAUFSTEUERUNG ANBLEIBT
 * ==================================
 * `OrbitControls` wird bewusst NICHT abgeschaltet: Der Nutzer will die Kamera
 * auch während der Wiedergabe von Hand bewegen können.
 */
export class Kameraspur {

    static anwenden(spur) {
        if (!spur.cameraActive) return;
        const paar = Schluesselpaar.finden(spur.clips, state.playheadFrame);
        if (!paar) return;
        if (paar.sprung) Kameraspur._setzen(paar.vorher.data);
        else Kameraspur._mischen(paar);
        state.camera.updateProjectionMatrix();
    }

    /** Genau auf einen Keyframe. */
    static _setzen(daten) {
        state.camera.position.set(daten.position.x, daten.position.y,
                                  daten.position.z);
        if (daten.lookAt) {
            state.camera.lookAt(daten.lookAt.x, daten.lookAt.y, daten.lookAt.z);
        } else {
            state.camera.quaternion.copy(Kameraspur.drehung(daten));
        }
        state.camera.fov = daten.fov;
    }

    static _mischen(paar) {
        const gewicht = paar.gewichtung;
        const vorher = paar.vorher.data;
        const nachher = paar.nachher.data;
        state.camera.position.lerpVectors(Kameraspur._ort(vorher.position),
                                          Kameraspur._ort(nachher.position),
                                          gewicht);
        if (vorher.lookAt && nachher.lookAt) {
            state.camera.lookAt(new THREE.Vector3().lerpVectors(
                Kameraspur._ort(vorher.lookAt), Kameraspur._ort(nachher.lookAt),
                gewicht));
        } else {
            state.camera.quaternion.copy(
                Kameraspur._slerp(vorher, nachher, gewicht));
        }
        state.camera.fov = vorher.fov + (nachher.fov - vorher.fov) * gewicht;
    }

    static _ort(punkt) {
        return new THREE.Vector3(punkt.x, punkt.y, punkt.z);
    }

    /**
     * Drehung eines Keyframes.
     *
     * Das gespeicherte Quaternion hat Vorrang — es ist eindeutig. Die
     * Euler-Winkel sind der Rückfall für ältere Projekte, die nur x/y/z
     * geschrieben haben.
     */
    static drehung(daten) {
        if (daten.quaternion) {
            const q = daten.quaternion;
            return new THREE.Quaternion(q.x, q.y, q.z, q.w);
        }
        return new THREE.Quaternion().setFromEuler(
            new THREE.Euler(daten.rotation.x, daten.rotation.y, daten.rotation.z));
    }

    /** Slerp mit Short-Arc-Korrektur (siehe Klassendoku). */
    static _slerp(vorher, nachher, gewicht) {
        const von = Kameraspur.drehung(vorher);
        const nach = Kameraspur.drehung(nachher);
        if (von.dot(nach) < 0) {
            nach.set(-nach.x, -nach.y, -nach.z, -nach.w);
        }
        return new THREE.Quaternion().slerpQuaternions(von, nach, gewicht);
    }
}
