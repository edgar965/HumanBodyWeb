/**
 * BVH Studio — Debug panel (bone distance, foot position display).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';

const _dbgV = new THREE.Vector3();
let _dbgThrottle = 0;

export function updateDebugPanel() {
    // Throttle to ~10 fps
    if (++_dbgThrottle % 6 !== 0) return;

    const elDist = document.getElementById('debug-ground-dist');
    const elBone = document.getElementById('debug-lowest-bone');
    const elFootL = document.getElementById('debug-foot-l');
    const elFootR = document.getElementById('debug-foot-r');
    const elRoot = document.getElementById('debug-root-pos');
    const elFrame = document.getElementById('debug-frame');
    if (!elDist) return;

    elFrame.textContent = `Frame: ${state.playheadFrame}`;

    // Find active track with skeleton
    let found = false;
    for (const track of state.project.tracks) {
        if (track.muted || !track.skeleton) continue;
        const bones = track.skeleton.skeleton.bones;
        if (!bones || bones.length === 0) continue;

        let minY = Infinity;
        let lowestName = '';
        let minYL = Infinity, lowestL = '';
        let minYR = Infinity, lowestR = '';

        for (const b of bones) {
            b.getWorldPosition(_dbgV);
            const y = _dbgV.y;
            const n = b.name.toLowerCase();

            if (y < minY) { minY = y; lowestName = b.name; }

            // Left foot bones (foot, toe, heel)
            const isLeft = n.includes('_l') || n.includes('.l') || n.includes('left');
            const isRight = n.includes('_r') || n.includes('.r') || n.includes('right');
            const isFoot = n.includes('foot') || n.includes('toe') || n.includes('heel');

            if (isFoot && isLeft && y < minYL) { minYL = y; lowestL = b.name; }
            if (isFoot && isRight && y < minYR) { minYR = y; lowestR = b.name; }
        }

        // Root position
        const root = track.skeleton.rootBone;
        if (root) {
            root.getWorldPosition(_dbgV);
            elRoot.textContent = `Root: ${_dbgV.x.toFixed(3)}, ${_dbgV.y.toFixed(3)}, ${_dbgV.z.toFixed(3)} m`;
        }

        elDist.textContent = `Boden-Abstand: ${minY.toFixed(4)} m`;
        elBone.textContent = `Tiefster: ${lowestName}`;
        elFootL.textContent = minYL < Infinity ? `Fuß L: ${minYL.toFixed(4)} m (${lowestL})` : 'Fuß L: —';
        elFootR.textContent = minYR < Infinity ? `Fuß R: ${minYR.toFixed(4)} m (${lowestR})` : 'Fuß R: —';
        found = true;
        break;  // first active track
    }

    if (!found) {
        elDist.textContent = 'Boden-Abstand: —';
        elBone.textContent = 'Tiefster Knochen: —';
        elFootL.textContent = 'Fuß L: —';
        elFootR.textContent = 'Fuß R: —';
        elRoot.textContent = 'Root Position: —';
    }
}

// Register functions in registry
fn.updateDebugPanel = updateDebugPanel;
