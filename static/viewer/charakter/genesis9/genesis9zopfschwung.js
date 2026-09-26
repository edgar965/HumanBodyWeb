/**
 * Genesis9zopfschwung — die eigenen Knochen eines Daz-Haars (Eirgrid: 14
 * Zöpfe unter `spine4`) schwingen in der Bewegung nach.
 *
 * DAZ' RIG FÜR ZOPFHAARE ist eine Knochenkette am Figurskelett; ohne dForce
 * hängt sie starr an der Figur, die Posen-Presets stellen sie. Hier hängen
 * dieselben Knochen im Browser-Skelett (`Genesis9/koerpernetz.py`, `skelett.
 * eigene`), und jeder bekommt ein Verlet-Pendel nach der SpringBone-Rechnung
 * des VRM-1.0-Standards (VRMC_springBone-1.0, Abschnitt „Update"):
 *
 *     next = tail + (tail − prev)·(1 − dragForce)
 *                 + (elternRot · ruheRot · achse)·stiffness·dt
 *                 + gravityDir·gravityPower·dt
 *     next = kopf + normalize(next − kopf)·länge
 *     knochen.quaternion = ruheRot · fromUnitVectors(achse,
 *                              (elternRot · ruheRot)⁻¹ · normalize(next − kopf))
 *
 * Die Zahlen sind die Vorgabewerte der Spezifikation: stiffness 1,0,
 * dragForce 0,5, gravityPower 0 (die Ruhelage der Zöpfe hängt schon —
 * die Bindung ist das Standbild). Die Rechnung steht ohne Three.js in
 * `gemeinsam/zopfpendel.js` (Node-Test `test_js_zopfpendel`); hier nur das
 * Holen der Knochen und das Schreiben der Quaternionen. Läuft nach dem
 * Mixer, vor dem Weichgewebe (das die Zopfknochen dann mit Tempo liest).
 * Gemessen (Ballett 0030, Eirgrid Pose Back): Spitzen bis 17 cm ausgelenkt,
 * im Stand nach 2 s unter 1 cm.
 *
 * Steht die Animation, kehren die Zöpfe in die Bindpose zurück; ein neues
 * Skelett (`neuFormen`) verwirft den Zustand.
 */
import { THREE, state } from '../state.js';
import { Zopfpendel } from '../../gemeinsam/zopfpendel.js';

export class Genesis9zopfschwung {

    static _figuren = new Map();       // inst -> {skelett, glieder: [...]}
    static _v = new THREE.Vector3();
    static _w = new THREE.Vector3();
    static _q = new THREE.Quaternion();
    static _q2 = new THREE.Quaternion();

    /** Aus der Szenenschleife: nach `mixer.update(dt)`. */
    static takt(dt) {
        for (const inst of state.characters.values()) {
            const namen = inst?.eigeneKnochen;
            if (!namen?.length || !inst.skelett?.boneByName) continue;
            let eintrag = Genesis9zopfschwung._figuren.get(inst);
            if (!eintrag || eintrag.skelett !== inst.skelett) {
                eintrag = Genesis9zopfschwung._anlegen(inst, namen);
                Genesis9zopfschwung._figuren.set(inst, eintrag);
            }
            if (!state.playing || dt <= 0) {
                Genesis9zopfschwung._ruhe(eintrag);
                continue;
            }
            Genesis9zopfschwung._bild(eintrag, dt);
        }
        // `state.characters` ist id -> Figur: Verwaiste über die WERTE erkennen.
        const lebend = new Set(state.characters.values());
        for (const inst of [...Genesis9zopfschwung._figuren.keys()]) {
            if (!lebend.has(inst)) Genesis9zopfschwung._figuren.delete(inst);
        }
    }

    /** Je Zopfknochen: Achse und Länge zum Kind (Bindpose), Ruhedrehung, Pendelspitze. */
    static _anlegen(inst, namen) {
        inst.group.updateMatrixWorld(true);
        const glieder = [];
        for (const name of namen) {
            const bone = inst.skelett.boneByName[name];
            const kind = bone?.children?.find(k => k.isBone);
            if (!bone || !kind) continue;
            const laenge = kind.getWorldPosition(new THREE.Vector3())
                .distanceTo(bone.getWorldPosition(new THREE.Vector3()));
            if (!(laenge > 1e-6)) continue;
            glieder.push({
                bone, laenge,
                achse: kind.position.clone().normalize(),
                ruheRot: bone.quaternion.clone(),
                pendel: null,          // `Zopfpendel.glied`, beim ersten Bild
            });
        }
        return { skelett: inst.skelett, glieder, gruppe: inst.group };
    }

    static _ruhe(eintrag) {
        for (const g of eintrag.glieder) {
            g.bone.quaternion.copy(g.ruheRot);
            g.pendel = null;
        }
    }

    static _bild(eintrag, dt) {
        const { _v: v, _w: w, _q: q, _q2: q2 } = Genesis9zopfschwung;
        eintrag.gruppe.updateMatrixWorld(true);
        for (const g of eintrag.glieder) {
            const kopf = g.bone.getWorldPosition(v).toArray();
            const elternRot = g.bone.parent.getWorldQuaternion(q);
            // Ruherichtung in der Welt: elternRot · ruheRot · achse.
            const ruhe = w.copy(g.achse).applyQuaternion(g.ruheRot).applyQuaternion(elternRot).toArray();
            if (!g.pendel) g.pendel = Zopfpendel.glied(g.laenge, kopf, ruhe);
            const richtung = new THREE.Vector3().fromArray(Zopfpendel.schritt(g.pendel, kopf, ruhe, dt));
            // Die Drehung: Richtung zurück in den Raum vor der Ruhedrehung.
            q2.copy(elternRot).multiply(g.ruheRot).invert();
            richtung.applyQuaternion(q2);
            g.bone.quaternion.copy(g.ruheRot).multiply(
                new THREE.Quaternion().setFromUnitVectors(g.achse, richtung));
            g.bone.updateMatrixWorld(true);
        }
    }

    /**
     * Für Sichtproben aus der Konsole (ein verstecktes Fenster bekommt kein
     * `requestAnimationFrame`): `schritte` Bilder zu `dt` Sekunden — Mixer
     * und Zopfschwung — und die größte Auslenkung der Spitzen.
     */
    static probe(schritte = 30, dt = 1 / 30) {
        if (!state.mixer) return null;
        const war = state.playing;
        state.playing = true;
        for (let i = 0; i < schritte; i++) {
            state.mixer.update(dt);
            Genesis9zopfschwung.takt(dt);
        }
        state.playing = war;
        let max = 0;
        for (const inst of state.characters.values()) {
            max = Math.max(max, Genesis9zopfschwung.auslenkung(inst) || 0);
        }
        return max;
    }

    /** Für Sichtproben: wie weit die Spitzen von der Ruhe abweichen (m). */
    static auslenkung(inst) {
        const eintrag = Genesis9zopfschwung._figuren.get(inst);
        if (!eintrag) return null;
        let max = 0;
        for (const g of eintrag.glieder) {
            if (!g.pendel) continue;
            const kopf = g.bone.getWorldPosition(new THREE.Vector3()).toArray();
            const ruhe = g.achse.clone().applyQuaternion(g.ruheRot)
                .applyQuaternion(g.bone.parent.getWorldQuaternion(new THREE.Quaternion())).toArray();
            max = Math.max(max, Zopfpendel.auslenkung(g.pendel, kopf, ruhe));
        }
        return max;
    }
}

window.__zopfschwung = Genesis9zopfschwung;
