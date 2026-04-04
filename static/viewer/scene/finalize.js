/**
 * finalize.js — Finalize tab: Export, Cleanup, Format conversion.
 */
import { state } from './state.js';
import { fn } from './registry.js';

export function initFinalizeTab() {
    // Export button
    document.getElementById('fin-export')?.addEventListener('click', () => {
        const format = document.getElementById('fin-format')?.value || 'json';
        const opts = {
            applyMorphs: document.getElementById('fin-apply-morphs')?.checked,
            applyPose: document.getElementById('fin-apply-pose')?.checked,
            includeRig: document.getElementById('fin-include-rig')?.checked,
            includeClothes: document.getElementById('fin-include-clothes')?.checked,
            includeHair: document.getElementById('fin-include-hair')?.checked,
        };

        if (format === 'json') {
            // Export scene as JSON
            if (fn.gatherSceneState) {
                const data = fn.gatherSceneState();
                data._exportOptions = opts;
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `scene_export_${Date.now()}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                if (fn.serverLog) fn.serverLog('export', `format=json`);
            } else {
                alert('Scene-Daten nicht verfuegbar.');
            }
        } else if (format === 'glb') {
            alert('GLB Export ist noch in Entwicklung.\n\nFuer GLB Export wird Three.js GLTFExporter benoetigt.\nDiese Funktion wird in einem zukuenftigen Update implementiert.');
        } else if (format === 'obj') {
            alert('OBJ Export ist noch in Entwicklung.\n\nOBJ Export benoetigt serverseitigen Mesh-Export.\nDiese Funktion wird in einem zukuenftigen Update implementiert.');
        } else if (format === 'fbx') {
            alert('FBX Export ist noch in Entwicklung.\n\nFBX Export benoetigt Blender als Backend.\nDiese Funktion wird in einem zukuenftigen Update implementiert.');
        }
    });

    // Cleanup button
    document.getElementById('fin-cleanup')?.addEventListener('click', () => {
        const collapseMorphs = document.getElementById('fin-collapse-morphs')?.checked;
        const removeUnused = document.getElementById('fin-remove-unused')?.checked;

        if (!collapseMorphs && !removeUnused) {
            alert('Bitte mindestens eine Cleanup-Option auswaehlen.');
            return;
        }

        let msg = 'Cleanup:\n';
        if (collapseMorphs) msg += '- Shape Keys werden zusammengefasst\n';
        if (removeUnused) msg += '- Unbenutzte Morphs werden entfernt\n';
        msg += '\nDiese Funktion ist noch in Entwicklung.';
        alert(msg);
        if (fn.serverLog) fn.serverLog('cleanup', `collapse=${collapseMorphs} remove=${removeUnused}`);
    });

    // Convert button
    document.getElementById('fin-convert')?.addEventListener('click', () => {
        const inFmt = document.getElementById('fin-conv-in')?.value || 'yaml';
        const outFmt = document.getElementById('fin-conv-out')?.value || 'json';

        if (inFmt === outFmt) {
            alert('Eingabe- und Ausgabeformat sind identisch.');
            return;
        }

        alert(`Konvertierung ${inFmt.toUpperCase()} → ${outFmt.toUpperCase()}\n\nDiese Funktion ist noch in Entwicklung.\nSie wird serverseitig implementiert.`);
        if (fn.serverLog) fn.serverLog('convert', `${inFmt} -> ${outFmt}`);
    });

    fn.initFinalizeTab = initFinalizeTab;
}
