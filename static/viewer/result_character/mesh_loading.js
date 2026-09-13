/**
 * Result Character — Körper, Häutung, Hautfarbe.
 *
 * SEIT 13.09.2026 BAUT DIE SEITE DEN KÖRPER NICHT MEHR SELBST (Edgar: „Alle
 * HTML-Seiten … sollen die Figur NICHT selber bauen, sondern eine globale
 * Klasse nutzen"): `HumanbodyModell` (`gemeinsam/humanbodymodell.js`) holt
 * das Netz, spaltet die Lippen ab, färbt die Haut, häutet nachträglich
 * (`haeuten`, sobald Skelett und Gewichte da sind — sie laden parallel zum
 * Netz) und trägt die Details samt Brauen. Der Morph-Strom (WebSocket) und
 * das Zubehör (Kleidung, Frisur, GarmentCode mit ihren Bedienfeldern)
 * bleiben Sache dieser Seite; `state.modell` ist die Figur.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';
import { sharedState, loadSkinWeights } from '../character_core.js';
import { HumanbodyModell } from '../gemeinsam/humanbodymodell.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { Skelettnachfuehrung } from '../gemeinsam/skelettnachfuehrung.js';

const ss = sharedState;

export async function loadMesh(bodyType) {
    try {
        const modell = new HumanbodyModell('ergebnis', { body_type: bodyType });
        if (state.details) modell.details = state.details;
        // Ungehäutet: Skelett und Gewichte laden gerade nebenher; `haeuten` folgt.
        await modell.koerper(null, null, ss.skinColors);
        state.modell = modell;
        state.bodyMesh = modell.bodyMesh;
        state.bodyGeometry = modell.bodyMesh.geometry;
        state.scene.add(modell.group);
        fn.applySceneSkinSettings(state.bodyMesh);
        return true;
    } catch (e) {
        console.error('[result_character] Failed to load mesh:', e);
        return false;
    }
}

export function convertToRigifySkinnedMesh() {
    if (state.isSkinned || !state.modell?.bodyMesh) return;
    state.modell.haeuten(ss.rigifySkeletonData, ss.skinWeightData);
    state.bodyMesh = state.modell.bodyMesh;
    state.bodyGeometry = state.bodyMesh.geometry;
    state.rigifySkeleton = state.modell.skelett;
    // Rig-Vorgabe AN (12.09.2026): Der Helfer entstand nur beim Kippen des
    // Knopfs — steht der Schalter schon auf an, gehoert er hier dazu.
    if (state.rigVisible && !state.skeletonHelper) {
        state.skeletonHelper = Skelettanzeige.bauen(state.scene, state.rigifySkeleton.rootBone);
    }
    state.isSkinned = true;
    // Der Server schickt die Knochenlagen zum ersten Netz, gebunden wird
    // erst danach. Ohne diese Zeile bliebe der zuletzt gemeldete Stand
    // liegen, bis jemand einen Regler anfasst.
    if (state.skelettBewegte) skelettNachfuehren(state.skelettBewegte);
}

/**
 * Die neuen Knochenlagen vom Server anwenden — siehe `Skelettnachfuehrung`.
 *
 * @param {Object} bewegte {Knochenname: [x,y,z]} in Blender-Koordinaten
 */
export function skelettNachfuehren(bewegte) {
    state.skelettBewegte = bewegte;
    if (!state.skelettFuehrung && ss.rigifySkeletonData) {
        state.skelettFuehrung = new Skelettnachfuehrung(ss.rigifySkeletonData);
    }
    if (!state.skelettFuehrung || !state.isSkinned) return false;
    return state.skelettFuehrung.anwenden(
        state.bodyMesh, state.rigifySkeleton, bewegte);
}

export function applySkinColor(bodyType) {
    if (!state.modell) return;
    state.modell.bodyType = bodyType;
    state.modell.hautfarbe(ss.skinColors);
}

export async function reloadBodyMesh(newType) {
    if (newType === state.currentBodyType) return;
    state.currentBodyType = newType;

    if (state.mixer) { state.mixer.stopAllAction(); state.mixer = null; state.currentAction = null; }

    if (state.modell) {
        Netzentsorgung.entfernen(state.scene, state.modell.group);
        state.modell = null;
        state.bodyMesh = null;
    }
    state.bodyGeometry = null;
    state.rigifySkeleton = null;
    state.isSkinned = false;
    if (state.skeletonHelper) { state.scene.remove(state.skeletonHelper); state.skeletonHelper = null; }

    fn.removeAllCloth();
    fn.removeAllGarments();
    fn.removeHair();
    // GarmentCode-Stücke hängen am alten Skelett (`GarmentcodeStuecke`).
    fn.removeAllGarmentcode?.();

    try {
        await Promise.all([
            loadMesh(newType),
            loadSkinWeights(newType),
        ]);

        if (state.bodyMesh && ss.rigifySkeletonData && ss.skinWeightData) {
            convertToRigifySkinnedMesh();
        }

        applySkinColor(newType);
        fn.wsSend({ type: 'body_type', value: newType });

        if (state.isSkinned) {
            await fn.loadBVH();
        }
    } catch (e) {
        console.error('[result_character] Body type switch failed:', e);
    }
}

fn.loadMesh = loadMesh;
fn.reloadBodyMesh = reloadBodyMesh;

// Ueber die Registrierung erreichbar, damit `websocket.js` ihn nicht
// importieren muss — siehe `viewer/skinning.js`, Regression vom 05.09.2026.
fn.skelettNachfuehren = skelettNachfuehren;
