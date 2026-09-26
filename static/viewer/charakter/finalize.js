/**
 * finalize.js — Finalize tab: Export, Cleanup, Format conversion.
 */
import { fn } from '../gemeinsam/registrierung.js';

/**
 * Ausgabeformate, die es noch nicht gibt — und was ihnen jeweils fehlt.
 *
 * Vorher standen dafür drei `else if`-Zweige mit je einer eigenen Meldung,
 * die sich nur in diesem einen Halbsatz unterschieden. Wer ein viertes
 * Format ergänzt, schreibt jetzt eine Zeile statt vier.
 */
const NOCH_NICHT = {
    glb: 'Three.js GLTFExporter',
    obj: 'ein serverseitiger Mesh-Export',
    fbx: 'Blender als Backend',
};

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
                alert('Szenendaten nicht verfügbar.');
            }
        } else if (NOCH_NICHT[format]) {
            // Drei fast gleiche Meldungen, die sich nur im fehlenden
            // Baustein unterschieden und alle denselben Schlusssatz
            // sagten (Befund `doppelcode`, 30.08.2026).
            alert(`${format.toUpperCase()}-Export ist noch in Entwicklung.`
                + `\n\nDafür fehlt: ${NOCH_NICHT[format]}.`
                + `\nDie Funktion kommt in einem späteren Update.`);
        }
    });

    // Cleanup button
    document.getElementById('fin-cleanup')?.addEventListener('click', () => {
        const collapseMorphs = document.getElementById('fin-collapse-morphs')?.checked;
        const removeUnused = document.getElementById('fin-remove-unused')?.checked;

        if (!collapseMorphs && !removeUnused) {
            alert('Bitte mindestens eine Cleanup-Option auswählen.');
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

        alert(`Konvertierung ${inFmt.toUpperCase()} → ${outFmt.toUpperCase()}\n\n`
            + 'Diese Funktion ist noch in Entwicklung.\n'
            + 'Sie wird serverseitig implementiert.');
        if (fn.serverLog) fn.serverLog('convert', `${inFmt} -> ${outFmt}`);
    });

}
