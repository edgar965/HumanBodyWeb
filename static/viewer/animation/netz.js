/**
 * Netz und Skelett der Animationsseite laden.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026). Seit 13.09.2026 baut
 * `HumanbodyModell` (`gemeinsam/humanbodymodell.js`) den Körper — wie auf
 * jeder Seite; hier bleiben Seitenzustand, Punktzahl und die Häutung
 * (`haeuten`, sobald Skelett und Gewichte da sind).
 */

import { HumanbodyModell } from '../gemeinsam/humanbodymodell.js';
import { Seitenzustand } from './seitenzustand.js';
import { applySceneSkinSettings, applySkinColor } from './material.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';


export async function loadMesh() {
    try {
        const modell = new HumanbodyModell('animation', {});
        await modell.koerper();
        Seitenzustand.modell = modell;
        Seitenzustand.bodyMesh = modell.bodyMesh;
        const geo = Seitenzustand.bodyMesh.geometry;
        Seitenzustand.bodyGeometry = geo;
        Seitenzustand.scene.add(modell.group);

        document.getElementById('vertex-count').textContent =
            geo.attributes.position.count.toLocaleString();

        applySceneSkinSettings();
        applySkinColor();
        Seitenzustand.groesseAnpassen();
    } catch (e) {
        Protokoll.fehler('Netz', 'nicht ladbar:', e);
    }
}

export async function loadRigifySkeleton() {
    // `jsonOderNull`: Ohne Skelett laeuft die Seite weiter (kein Skinning),
    // deshalb warnen statt werfen — wie die frueheren `if (resp.ok)`-Zweige.
    const daten = await Serverabruf.jsonOderNull('/api/character/rigify-skeleton/');
    if (!daten) return;
    Seitenzustand.rigifySkeletonData = daten;
    Protokoll.debug('Skelett', `DEF-Skelett geladen: ${daten.bone_count} Knochen`);
}

export async function loadSkinWeights() {
    const daten = await Serverabruf.jsonOderNull('/api/character/skin-weights/');
    if (daten) Seitenzustand.skinWeightData = daten;
}

export function convertToRigifySkinnedMesh(rigifySkel, swData) {
    const modell = Seitenzustand.modell;
    if (Seitenzustand.isSkinned || !modell?.bodyMesh) return;
    modell.haeuten(Seitenzustand.rigifySkeletonData, swData);
    Seitenzustand.bodyMesh = modell.bodyMesh;
    Seitenzustand.bodyGeometry = modell.bodyMesh.geometry;
    Seitenzustand.rigifySkeleton = modell.skelett;
    Seitenzustand.isSkinned = true;
    Protokoll.debug('Netz', 'SkinnedMesh gebaut,',
                    Seitenzustand.rigifySkeleton.skeleton.bones.length, 'Knochen');
}

// Die Skalierungsgruppe des BVH-Skeletts liegt jetzt im Seitenzustand
// (`Seitenzustand.skelWrapper`) — hier war sie ein `export let`, auf das
// wiedergabe.js schrieb: ein TypeError zur Laufzeit (Umbau 16.08.2026).
