import * as THREE from 'three';

/**
 * Clipabtastung — einen Animationsclip auf eine feste Bildrate neu abtasten.
 *
 * WOZU (27.09.2026, Edgar: „mach die FPS einstellung beim Export einstellbar,
 * default 30 fps"): Die Retarget-Clips tragen die Rate ihrer BVH (DanceKurz:
 * `Frame Time: 0.016667`, also 60 je Sekunde, 1004 Bilder). Blender rechnet
 * beim Import jede Keyframe-Zeit über die Szenen-FPS in eine Framenummer um;
 * passen Clip- und Szenenrate nicht zusammen, fallen Keyframes auf krumme
 * oder doppelte Frames. Mit einem Clip genau in der Exportrate liegt jedes
 * Keyframe auf einem eigenen, ganzen Frame.
 *
 * Numerische Spuren werden über ihren eigenen Interpolanten ausgewertet
 * (Quaternionen per Slerp, wie die Szene sie abspielt); alles andere
 * (Zeichenketten, Wahrheitswerte) bleibt unverändert.
 */
export class Clipabtastung {

    static VORGABE_FPS = 30;

    static abtasten(clip, fps = Clipabtastung.VORGABE_FPS) {
        const dauer = Math.max(clip.duration, 1 / fps);
        const n = Math.max(2, Math.ceil(dauer * fps - 1e-6) + 1);
        const spuren = clip.tracks.map((spur) => Clipabtastung._spur(spur, fps, dauer, n));
        return new THREE.AnimationClip(clip.name, dauer, spuren);
    }

    static _spur(spur, fps, dauer, n) {
        if (spur.ValueBufferType !== Float32Array) return spur;
        const groesse = spur.getValueSize();
        const interpolant = spur.createInterpolant(new Float32Array(groesse));
        const zeiten = new Float32Array(n);
        const werte = new Float32Array(n * groesse);
        for (let k = 0; k < n; k++) {
            const t = Math.min(k / fps, dauer);
            zeiten[k] = t;
            werte.set(interpolant.evaluate(t), k * groesse);
        }
        return new spur.constructor(spur.name, zeiten, werte, spur.getInterpolation());
    }
}
