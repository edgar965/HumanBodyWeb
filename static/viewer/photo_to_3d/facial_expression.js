/**
 * Photo To 3D — Gesichtsausdruck auf die Knochen des HumanBody-Rigs legen.
 *
 * UMBAU 27.08.2026 (Befund `jsfunktionen`): `applyFacialExpression()` hatte 102
 * Zeilen. Die Deutung des Rohvektors steht jetzt in `Gesichtswerte`, die
 * Umrechnung in Knochendrehungen in `Gesichtsdrehungen` — hier bleibt das
 * Auftragen.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Gesichtsdrehungen } from './gesichtsdrehungen.js';
import { Gesichtswerte } from './gesichtswerte.js';

/**
 * @param {number[]} expr [jawOpen, smile, browUp, browDown, lipUp, lipCorner,
 *     cheekPuff, squint, noseWrinkle, eyeWide]
 */
export function applyFacialExpression(expr) {
    if (!state.rigifySkeleton || !state.rigifySkeleton.restQuats) return;
    const { boneByName, restQuats } = state.rigifySkeleton;

    const winkel = new THREE.Euler();
    const drehung = new THREE.Quaternion();
    const drehungen = Gesichtsdrehungen.aus(expr);
    for (const [name, [rx, ry, rz]] of Object.entries(drehungen.je_knochen)) {
        const knochen = boneByName[name];
        const ruhe = restQuats[name];
        if (!knochen || !ruhe) continue;
        // Blender lokal -> Three.js: Y und Z tauschen, neues Z negieren.
        winkel.set(rx, rz, -ry, 'XYZ');
        drehung.setFromEuler(winkel);
        knochen.quaternion.copy(ruhe).multiply(drehung);
    }

    if (state.rigifySkeleton.rootBone) {
        state.rigifySkeleton.rootBone.updateWorldMatrix(true, true);
    }
    if (state.bodyMesh && state.bodyMesh.skeleton) {
        state.bodyMesh.skeleton.update();
    }

    Protokoll.debug('FaceExpr', 'Applied:',
                    new Gesichtswerte(expr).alsObjekt());
}

fn.applyFacialExpression = applyFacialExpression;
