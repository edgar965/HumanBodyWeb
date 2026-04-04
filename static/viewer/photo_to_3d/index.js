/**
 * Photo To 3D — Main orchestrator (ES module entry point).
 *
 * Two models side-by-side:
 *   Left:  HumanBody (our morph system)
 *   Right: SMPL-X (academic body model with shape betas)
 *
 * Photo analysis sets SMPL-X betas -> both models update.
 */

import { state } from './state.js';
import { fn } from './registry.js';

// Import all modules so they register their functions in the registry.
import { initScene, animate } from './scene.js';
import { loadMesh, loadRigifySkeleton, requestMeshUpdate, applySkinColor, buildRigifySkeleton } from './humanbody_mesh.js';
import { applyFacialExpression } from './facial_expression.js';
import { loadSmplxModel, loadSmplxTexture, requestSmplxUpdate, showSmplxRig, buildSmplxPanel } from './smplx_model.js';
import { loadMorphs, buildMorphPanel } from './humanbody_morphs.js';
import { initModelToggle, initRigToggle, initSmplxToggle, initSmplxRigToggle } from './toggles.js';
import { initPhotoUpload, analyzePhoto } from './photo_upload.js';
import {
    loadBackendStatus, initSaveButton,
    initTextureButtons, enableTextureButtons, showTextureProgress,
    initPhotoTabs, loadJobResult, captureAndSaveScreenshot,
} from './job_management.js';
import { renderAlignmentPreview } from './alignment_preview.js';
import { startWizard } from './wizard.js';

console.log('[Photo To 3D] ES modules loaded');

// =========================================================================
// Init
// =========================================================================
function init() {
    initScene();

    // Load data: skeleton first, then mesh (so SkinnedMesh can be created)
    loadMorphs();
    loadRigifySkeleton().then(() => {
        loadMesh().then(() => {
            animate();
            loadSmplxModel();
        });
    });

    // UI bindings
    initModelToggle();
    initRigToggle();
    initSmplxToggle();
    initSmplxRigToggle();
    initPhotoUpload();
    initPhotoTabs();
    initTextureButtons();
    initSaveButton();
    loadBackendStatus();
    buildSmplxPanel();
}

// =========================================================================
// Boot
// =========================================================================
init();

// Auto-load job if ?job=<uuid> is in URL
{
    const params = new URLSearchParams(window.location.search);
    const jobId = params.get('job');
    if (jobId) {
        setTimeout(async () => {
            await loadJobResult(jobId);
            const tab = params.get('tab');
            if (tab) {
                const tabEl = document.querySelector(`.photo-tab[data-tab="${tab}"]`);
                if (tabEl) tabEl.click();
            }
            if (params.get('reanalyze') === '1') {
                setTimeout(() => analyzePhoto(), 500);
            }
        }, 1500);
    }
}
