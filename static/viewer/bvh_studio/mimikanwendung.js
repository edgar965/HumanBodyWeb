import * as THREE from 'three';
import { state } from './state.js';
import { sharedState } from '../character_core.js';
import { Mimikbasis } from './mimikbasis.js';
import { Mimikkurve } from './mimikkurve.js';
import { Lebendigkeit } from './lebendigkeit.js';

/**
 * Mimikanwendung — je Bild die Gesichtsknochen der Figur aus der Mimikspur setzen.
 *
 * Läuft NACH den Bewegungsspuren (`applyPlayhead`, zweiter Durchlauf): Der
 * Mischer der Körperanimation schreibt seine Knochen zuerst, die Mimik
 * überschreibt danach die Gesichtsknochen — auch den Kiefer und die
 * Ausdrücke, die ein Video mitgebracht hat. Rechnung je Bild:
 * Schlüsselbilder → Gewichte (`Mimikkurve`) + Lebendigkeit → Bewegungen je
 * Knochen (`Mimikbasis`) → `quaternion = ruhe · rot`, `position = ruhe + pos`.
 * Die Ruhelage kommt aus den Rigify-Daten (`sharedState.rigifySkeletonData`,
 * Blender-Achsen [w,x,y,z] → Three.js (x,z,−y,w), wie der Skelettbauer).
 */
export class Mimikanwendung {

    /** Ruhelage je Knochenname: `{q: Quaternion, p: Vector3}` (einmal gebaut). */
    static _ruhe = null;

    static ruhe() {
        if (Mimikanwendung._ruhe) return Mimikanwendung._ruhe;
        const daten = sharedState.rigifySkeletonData;
        if (!daten?.bones) return null;
        const aus = {};
        for (const b of daten.bones) {
            const q = b.local_quaternion, p = b.local_position;
            aus[b.name] = {
                q: new THREE.Quaternion(q[1], q[3], -q[2], q[0]),
                p: new THREE.Vector3(p[0], p[2], -p[1]),
            };
        }
        Mimikanwendung._ruhe = aus;
        return aus;
    }

    /** Die Figur (Skelett) zur Mimikspur: die Animation der verknüpften Modellspur. */
    static skelett(spur) {
        const modell = state.project.tracks[spur._modellIdx];
        if (!modell || modell.type !== 'model') return null;
        const animation = state.project.getLinkedAnimation(modell);
        return animation?.skeleton || animation?.mesh?.skeleton || null;
    }

    /** Gewichte der Spur an der Zeit `t` (Sekunden) samt Lebendigkeit. */
    static gewichte(spur, t) {
        const schluessel = spur.clips.filter(c => c.type === 'mimik_kf')
            .map(c => ({ frame: c.startFrame, ...c.data }));
        const pose = Mimikkurve.gewichte(schluessel, t * state.project.fps, state.project.fps);
        const zuschlag = Lebendigkeit.zuschlag(spur.lebendigkeit, t, pose);
        for (const [einheit, g] of Object.entries(zuschlag)) {
            pose[einheit] = Math.max(-1, Math.min(1, (pose[einheit] || 0) + g));
        }
        return pose;
    }

    /** Alle Mimikspuren an der Zeit `t` anwenden. */
    static alle(t) {
        if (!Mimikbasis.bereit) return;
        for (const spur of state.project.tracks) {
            if (spur.type !== 'mimik' || spur.muted) continue;
            const skelett = Mimikanwendung.skelett(spur);
            if (!skelett) continue;
            Mimikanwendung.setzen(skelett, spur._vorschau || Mimikanwendung.gewichte(spur, t));
        }
    }

    /** Gewichte auf ein Skelett legen — Knochen ohne Anteil gehen in die Ruhelage. */
    static setzen(skelett, gewichte) {
        const ruhe = Mimikanwendung.ruhe();
        if (!ruhe) return;
        const bewegungen = Mimikbasis.bewegungen(gewichte);
        for (const name of Mimikbasis.knochen()) {
            const knochen = Mimikanwendung._knochen(skelett, name);
            const lage = ruhe[name];
            if (!knochen || !lage) continue;
            const b = bewegungen[name];
            knochen.quaternion.copy(lage.q);
            knochen.position.copy(lage.p);
            if (b) {
                knochen.quaternion.multiply(b.rot);
                knochen.position.add(b.pos);
            }
        }
    }

    static _knochen(skelett, name) {
        if (!skelett._mimikKnochen) {
            skelett._mimikKnochen = {};
            for (const b of skelett.bones) {
                skelett._mimikKnochen[b.name] = b;
                skelett._mimikKnochen[b.name.replace(/_/g, '.')] = b;
            }
        }
        return skelett._mimikKnochen[name] || null;
    }
}
