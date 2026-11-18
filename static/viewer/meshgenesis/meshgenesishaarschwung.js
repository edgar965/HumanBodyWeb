/**
 * Meshgenesishaarschwung — Bewegung je Locke für Haar aus Einzelsträhnen (`haar_Bart`) auf der bewegten Ergebnisfigur (16.11.2026, Edgar zur Goldprinzessin: „die Strähnen müssen eine eigene
 * Bewegung haben“ — Option 2). Die Rechnung steht ohne Three.js in `gemeinsam/lockenpendel.js`; hier nur Häuten der Leitpunkte, Textur und Shader.
 *
 * Das Anzeigenetz bringt je Punkt seinen Leitpunkt (`leit` = Leitsträhne · (K+1) + Schritt) und die Leitsträhnen in Ruhe (`leitpunkte`, Server `Meshgenesisflaechennetz`). Je Bild:
 *   1. jeden Leitpunkt häuten wie der Shader der Figur (Gewichte des ersten Punkts mit diesem Leitpunkt — die Strähnen nehmen die Gewichte ihrer Leitsträhne, `Haarstraehnen.gewichte`):
 *      bindMatrixInverse · Σ w · (Knochen.matrixWorld · boneInverse) · bindMatrix · p
 *   2. `Lockenpendel.schritt` → Verschiebung je Leitpunkt (Locke − gehäutete Leitsträhne)
 *   3. in eine Float-Textur (K+1 breit, G hoch); der Vertex-Shader addiert sie nach dem Häuten zu jedem Punkt (`Shaderpatch` „haarschwung“), VOR dem Schub aus fremden Gliedern
 *      (`Meshgenesiskollision` hängt sich ebenfalls hinter `skinning_vertex`; der später angehängte Eingriff steht im Shader davor).
 * Stopp und Sprünge in der Zeit setzen die Locken zurück (dt 0).
 */
import * as THREE from 'three';
import { Lockenpendel } from '../gemeinsam/lockenpendel.js';
import { Shaderpatch } from '../gemeinsam/shaderpatch.js';

export class Meshgenesishaarschwung {
    static KOPF = 'attribute float schwungLeit;\nuniform sampler2D schwungTex;\nuniform float schwungK1;\n';
    static RUMPF = '{ int schwungI = int(schwungLeit + 0.5); int schwungK = int(schwungK1 + 0.5);\n'
        + '  transformed += texelFetch(schwungTex, ivec2(schwungI % schwungK, schwungI / schwungK), 0).xyz; }';

    /** An ein gebundenes Stück hängen, wenn sein Netz Leitsträhnen trägt. @param abbildung Rahmen der Kinematik → Rahmen der Figur oder null @returns {boolean} */
    static anbringen(mesh, netz, abbildung) {
        const geo = mesh?.geometry;
        if (!mesh?.isSkinnedMesh || !netz?.leit || !netz.leitpunkte || !geo || geo.attributes.position.count !== netz.leit.length) return false;
        const [g, k1] = netz.kopf.leit;
        geo.setAttribute('schwungLeit', new THREE.BufferAttribute(Float32Array.from(netz.leit), 1));
        const ruhe = Float32Array.from(netz.leitpunkte);
        if (abbildung) {
            const v = new THREE.Vector3();
            for (let i = 0; i < ruhe.length; i += 3) {
                v.set(ruhe[i], ruhe[i + 1], ruhe[i + 2]).applyQuaternion(abbildung.quaternion).add(abbildung.verschiebung);
                ruhe[i] = v.x; ruhe[i + 1] = v.y; ruhe[i + 2] = v.z;
            }
        }
        // je Leitpunkt die Gewichte seines ersten Punkts; ohne Punkt (hinter der sichtbaren Länge) die des vorigen Schritts
        const n = g * k1;
        const erster = new Int32Array(n).fill(-1);
        for (let i = 0; i < netz.leit.length; i++) if (erster[netz.leit[i]] < 0) erster[netz.leit[i]] = i;
        for (let j = 0; j < n; j++) if (erster[j] < 0 && j % k1 > 0) erster[j] = erster[j - 1];
        const si = geo.attributes.skinIndex, sw = geo.attributes.skinWeight;
        const index = new Uint16Array(n * 4), gewicht = new Float32Array(n * 4);
        for (let j = 0; j < n; j++) {
            const i = erster[j];
            if (i < 0) continue;
            for (let c = 0; c < 4; c++) { index[j * 4 + c] = si.getComponent(i, c); gewicht[j * 4 + c] = sw.getComponent(i, c); }
        }
        const daten = new Float32Array(n * 4);
        const tex = new THREE.DataTexture(daten, k1, g, THREE.RGBAFormat, THREE.FloatType);
        tex.minFilter = tex.magFilter = THREE.NearestFilter;
        tex.needsUpdate = true;
        const u = { schwungTex: { value: tex }, schwungK1: { value: k1 } };
        const eingriff = shader => {
            Object.assign(shader.uniforms, u);
            shader.vertexShader = shader.vertexShader.replace('#include <common>', `#include <common>\n${Meshgenesishaarschwung.KOPF}`);
            Shaderpatch.hinterInclude(shader, 'skinning_vertex', Meshgenesishaarschwung.RUMPF);
        };
        // immer ein Klon (samt dem Eingriff der Kollision, `Shaderpatch.klonen`) — ohne Kapseln trüge das Stück sonst das geteilte Material des Standbilds (`Meshgenesisgemeinsam`)
        const klonen = m => Shaderpatch.anhaengen(Shaderpatch.klonen(m), 'haarschwung', eingriff);
        mesh.material = Array.isArray(mesh.material) ? mesh.material.map(klonen) : klonen(mesh.material);
        mesh.userData.haarschwung = { zustand: Lockenpendel.anlegen(ruhe, g, k1), ruhe, index, gewicht, ziel: new Float32Array(n * 3), daten, tex, g, k1 };
        return true;
    }

    /** Je Bild nach dem Mischer. @param dt Sekunden seit dem letzten Bild (0: Locken zurück auf die Figur) */
    static stellen(kleider, dt, gruppe) {
        gruppe?.updateMatrixWorld(true);
        const m = new THREE.Matrix4(), inv = new THREE.Matrix4(), unten = new THREE.Vector3();
        for (const { mesh } of kleider || []) {
            const s = mesh.userData.haarschwung;
            const sk = mesh.skeleton;
            if (!s || !sk) continue;
            const mat = sk.bones.map((b, i) => m.multiplyMatrices(b.matrixWorld, sk.boneInverses[i]).premultiply(mesh.bindMatrixInverse).multiply(mesh.bindMatrix).elements.slice());
            const { ruhe, index, gewicht, ziel } = s;
            for (let j = 0, n = s.g * s.k1; j < n; j++) {
                const x = ruhe[j * 3], y = ruhe[j * 3 + 1], z = ruhe[j * 3 + 2];
                let px = 0, py = 0, pz = 0;
                for (let c = 0; c < 4; c++) {
                    const w = gewicht[j * 4 + c];
                    if (!w) continue;
                    const e = mat[index[j * 4 + c]];
                    px += w * (e[0] * x + e[4] * y + e[8] * z + e[12]);
                    py += w * (e[1] * x + e[5] * y + e[9] * z + e[13]);
                    pz += w * (e[2] * x + e[6] * y + e[10] * z + e[14]);
                }
                ziel[j * 3] = px; ziel[j * 3 + 1] = py; ziel[j * 3 + 2] = pz;
            }
            inv.copy(mesh.matrixWorld).invert();
            unten.set(0, -1, 0).transformDirection(inv);
            const v = Lockenpendel.schritt(s.zustand, ziel, dt, [unten.x, unten.y, unten.z]);
            for (let j = 0, n = s.g * s.k1; j < n; j++) {
                s.daten[j * 4] = v[j * 3]; s.daten[j * 4 + 1] = v[j * 3 + 1]; s.daten[j * 4 + 2] = v[j * 3 + 2];
            }
            s.tex.needsUpdate = true;
        }
    }

    /** Für Sichtproben aus der Konsole: größte Auslenkung (m) über alle Haarstücke. */
    static auslenkung(kleider) {
        let a = 0;
        for (const { mesh } of kleider || []) if (mesh.userData.haarschwung) a = Math.max(a, Lockenpendel.auslenkung(mesh.userData.haarschwung.zustand));
        return a;
    }
}
