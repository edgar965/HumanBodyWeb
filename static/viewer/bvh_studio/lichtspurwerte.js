import * as THREE from 'three';
import { state } from './state.js';
import { Schluesselpaar } from './schluesselpaar.js';

/**
 * Lichtspurwerte — ein Licht auf den Stand des Abspielkopfs setzen.
 *
 * Herausgelöst aus `spur_anwenden.js` (288 Zeilen). Die Keyframe-Suche kommt
 * jetzt aus `Schluesselpaar` — sie stand hier und in der Kameraspur gleich.
 *
 * WARUM `angle`, `penumbra` UND `distance` NUR MIT BEIDEN WERTEN GEMISCHT WERDEN
 * =============================================================================
 * Ein Punkt- oder Umgebungslicht hat keinen Öffnungswinkel; dort steht `null`.
 * Wird zwischen `null` und einer Zahl gemischt, kommt `NaN` heraus — und ein
 * `NaN` im Winkel macht den Lichtkegel unsichtbar, ohne Fehlermeldung. Deshalb:
 * Beide Keyframes müssen einen Wert haben, sonst bleibt der bisherige stehen.
 */
export class Lichtspurwerte {

    /** Zahlenfelder, die zwischen zwei Keyframes gemischt werden. */
    static ZAHLEN = ['intensity', 'angle', 'penumbra', 'distance'];

    static anwenden(spur) {
        if (!spur.light) return;
        const paar = Schluesselpaar.finden(spur.clips, state.playheadFrame);
        if (!paar) return;
        if (paar.sprung) Lichtspurwerte._setzen(spur, paar.vorher.data);
        else Lichtspurwerte._mischen(spur, paar);
        if (spur.light.target) spur.light.target.updateMatrixWorld();
        spur.lightHelper?.update?.();
    }

    /** Genau auf einen Keyframe. */
    static _setzen(spur, daten) {
        const licht = spur.light;
        licht.position.set(daten.position.x, daten.position.y, daten.position.z);
        if (daten.target && licht.target) {
            licht.target.position.set(daten.target.x, daten.target.y,
                                      daten.target.z);
        }
        licht.color.set(daten.color);
        licht.intensity = daten.intensity;
        for (const feld of ['angle', 'penumbra', 'distance']) {
            if (daten[feld] != null) licht[feld] = daten[feld];
        }
    }

    static _mischen(spur, paar) {
        const licht = spur.light;
        const anteil = paar.anteil;
        const vorher = paar.vorher.data;
        const nachher = paar.nachher.data;
        licht.position.lerpVectors(Lichtspurwerte._ort(vorher.position),
                                   Lichtspurwerte._ort(nachher.position), anteil);
        if (vorher.target && nachher.target && licht.target) {
            licht.target.position.lerpVectors(
                Lichtspurwerte._ort(vorher.target),
                Lichtspurwerte._ort(nachher.target), anteil);
        }
        licht.color.lerpColors(new THREE.Color(vorher.color),
                               new THREE.Color(nachher.color), anteil);
        for (const feld of Lichtspurwerte.ZAHLEN) {
            if (vorher[feld] == null || nachher[feld] == null) continue;
            licht[feld] = paar.mischen(feld, anteil);
        }
    }

    static _ort(punkt) {
        return new THREE.Vector3(punkt.x, punkt.y, punkt.z);
    }
}
