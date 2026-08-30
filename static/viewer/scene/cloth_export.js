/**
 * Cloth-Export Bridge.
 * Serializes the current generated-model scene + its active animation
 * into a binary payload, POSTs it to the cloth-export API, polls for the
 * rendered MP4, and triggers a download.
 *
 * Aufruf von der Konsole:
 *   window.__exportClothMP4({ engine: 'warp_only', quality: 'medium', duration: 3.0 })
 *
 * NICHT `fn.exportClothMP4` (Befund `jsregistrierung`, 29.08.2026): Hier stand
 * genau das — nur liegt `fn` nicht auf `window`, sondern ist der Modulzustand
 * von `gemeinsam/registrierung.js`. Von der Konsole aus war die Anleitung
 * also unbrauchbar, und die Anmeldung daneben las niemand. Der Weg, der
 * funktioniert, ist `window.__exportClothMP4` — die Zeile stand schon da.
 */
import { THREE } from './state.js';
import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { float32ToBase64, uint32ToBase64 }
    from '../gemeinsam/kodierung.js';
import { Netznutzlast } from '../gemeinsam/netznutzlast.js';
import { Ausgabeoptionen } from '../gemeinsam/ausgabeoptionen.js';

function _selectedInstWithGenerated() {
    const inst = state.characters.get(state.selectedCharacterId);
    if (!inst) throw new Error('Kein Charakter ausgewählt.');
    if (!inst.generatedConfig) throw new Error('Charakter ist kein generiertes Rig-Modell.');
    if (!inst.bodyMesh || !inst.bodyMesh.skeleton) throw new Error('bodyMesh ohne Skeleton.');
    const ud = inst.bodyMesh.userData || {};
    if (!ud.boneVertexRanges) throw new Error('boneVertexRanges fehlen (Modell muss regeneriert werden).');
    return inst;
}

/**
 * Sample per-frame bone world matrices while the mixer plays.
 * Returns Float32Array(N * numBones * 16), row-major.
 */
async function _sampleBoneMatrices(inst, duration, fps) {
    const mesh = inst.bodyMesh;
    const skel = mesh.skeleton;
    const bones = skel.bones;
    const N = Math.max(1, Math.ceil(duration * fps));
    const out = new Float32Array(N * bones.length * 16);

    if (!state.mixer || !state.currentAction) {
        // No active animation — emit identity matrix per frame
        const id = new THREE.Matrix4().identity();
        for (let f = 0; f < N; f++) for (let b = 0; b < bones.length; b++) {
            id.toArray(out, (f * bones.length + b) * 16);
        }
        return { matrices: out, frameCount: N };
    }

    const wasPlaying = !!state.playing;
    const origTime = state.currentAction.time;
    const clip = state.currentAction.getClip();
    const dt = 1 / fps;

    state.currentAction.play();
    state.currentAction.paused = true;

    for (let f = 0; f < N; f++) {
        const t = Math.min(f * dt, clip.duration);
        state.currentAction.time = t;
        state.mixer.update(0);
        mesh.updateMatrixWorld(true);
        for (let b = 0; b < bones.length; b++) {
            bones[b].updateMatrixWorld(true);
            bones[b].matrixWorld.toArray(out, (f * bones.length + b) * 16);
        }
    }
    // restore
    state.currentAction.time = origTime;
    state.currentAction.paused = !wasPlaying;
    state.mixer.update(0);
    return { matrices: out, frameCount: N };
}

/**
 * Build the payload the server expects for POST /api/cloth/export/.
 */
export async function buildClothPayload({ duration = 3.0, fps = 30 } = {}) {
    const inst = _selectedInstWithGenerated();
    const mesh = inst.bodyMesh;
    const geo = mesh.geometry;
    const skel = mesh.skeleton;
    const positions = new Float32Array(geo.attributes.position.array);
    const faces = new Uint32Array(geo.index.array);
    const skinI = new Uint32Array(geo.attributes.skinIndex.array); // Three.js stores uint16 but we promote
    const skinW = new Float32Array(geo.attributes.skinWeight.array);
    const boneNames = skel.bones.map(b => b.name);
    // Inverse bind: skel.boneInverses (Matrix4[]), concat into Float32Array(num_bones * 16)
    const invBind = new Float32Array(skel.boneInverses.length * 16);
    skel.boneInverses.forEach((m, i) => m.toArray(invBind, i * 16));

    const { matrices, frameCount } = await _sampleBoneMatrices(inst, duration, fps);

    const ranges = mesh.userData.boneVertexRanges;  // bone_name -> {start, count}
    const bone_parts = inst.generatedConfig.bone_parts || {};

    return Netznutzlast.bauen({
        name: inst.presetName || 'scene',
        punkte: positions, dreiecke: faces,
        hautindizes: skinI, hautgewichte: skinW,
        knochennamen: boneNames, bindeinverse: invBind,
        matrizen: matrices, fps, bilder: frameCount,
        bereiche: ranges, knochenteile: bone_parts,
    });
}

/**
 * Export the selected character with the active animation as MP4 via the
 * chosen cloth engine. Returns the download URL.
 */
export async function exportClothMP4({ engine = 'warp_only', quality = 'medium', duration = 3.0, fps = 30,
    outputDir = '', filename = '', width = 1920, height = 1080 } = {}) {
    const payload = await buildClothPayload({ duration, fps });
    Ausgabeoptionen.anhaengen(payload, {engine, quality, width, height,
                                        outputDir, filename});
    Protokoll.debug('Cloth Export',
        `engine=${engine} quality=${quality} res=${width}x${height} frames=${payload.anim_frames} dir=${outputDir||'(default)'} file=${filename||'(auto)'}`);
    // Der Abruf WIRFT bei jedem Status außer 2xx, und diese Funktion hat keinen
    // Aufrufer im Projekt — sie hängt an `fn.`/`window.__` und wird aus der
    // Konsole oder einem Knopf gerufen. Ohne diesen Fänger wäre ein Serverfehler
    // eine stille „Unhandled promise rejection" (Befund `jsfaenger`, 17.08.2026).
    // Erst melden, dann weiterwerfen: Wer aus der Konsole ruft, will den Fehler
    // auch als Rückgabe sehen.
    let data;
    try {
        data = await Serverabruf.senden('/api/cloth/export/', payload);
    } catch (fehler) {
        Protokoll.fehler('Cloth Export', 'Abruf fehlgeschlagen:', fehler.message);
        throw fehler;
    }
    if (!data.ok) {
        Protokoll.fehler('Cloth Export', 'Server meldet einen Fehler:', data);
        throw new Error(data.error || data.log || 'Export fehlgeschlagen');
    }
    Protokoll.info('Cloth Export', 'MP4:', data.url);
    if (data.url) window.open(data.url, '_blank');
    return data;
}

window.__exportClothMP4 = exportClothMP4;
