/**
 * Klipeigenschaften — Maske und Bedienung des ausgewaehlten Clips.
 *
 * Aus properties.js herausgeloest (Umbau 16.08.2026). Kamera- und
 * Licht-Schluesselbilder liegen in klip_schluesselbilder.js; hier stehen die
 * Clips mit Laufzeit: Ton, 3D-Objekt, Modell und BVH.
 */
import { fn } from '../../gemeinsam/registrierung.js';
import { Maskenbausteine as M } from './bausteine.js';
import { Schluesselbildeigenschaften } from './klip_schluesselbilder.js';

/** Vorgabelaenge, wenn ein Dauerfeld leer gelassen wird. */
const VORGABE_BILDER = 300;

export class Klipeigenschaften {
    static maske(clip) {
        if (clip.type === 'camera_kf' || clip.type === 'light_kf') {
            return Schluesselbildeigenschaften.maske(clip);
        }
        if (clip.type === 'audio') return Klipeigenschaften._ton(clip);
        if (clip.type === 'object_clip') return Klipeigenschaften._objekt(clip);
        if (clip.type === 'model') return Klipeigenschaften._modell(clip);
        return Klipeigenschaften._bvh(clip);
    }

    static binden(track, clip) {
        const art = clip.type || 'bvh';
        if (art === 'camera_kf' || art === 'light_kf') {
            Schluesselbildeigenschaften.binden(track, clip);
        } else if (art === 'audio') {
            Klipeigenschaften._tonBinden(clip);
        } else if (art === 'object_clip') {
            Klipeigenschaften._objektBinden(clip);
        } else if (art === 'model') {
            Klipeigenschaften._modellBinden(clip);
        } else {
            Klipeigenschaften._bvhBinden(clip);
        }
    }

    static _ton(clip) {
        const d = clip.data;
        const prozent = Math.round((d.volume || 1) * 100);
        const f = ' <span class="winzig">f</span>';
        return M.gruppe(`Audio: ${d.fileName || '?'}`, `
            ${M.zeile('Datei', `<span class="text-klein">${d.fileName || '—'}</span>`)}
            ${M.zeile('Dauer', `<span class="tonwert">${(d.audioDuration || 0).toFixed(1)}s</span>`)}
            ${M.zeile('Start', M.zahl('prop-audio-start', clip.startFrame, 'min="0"') + f)}
            ${M.zeile('Lautstärke', `<input type="range" value="${prozent}" id="prop-audio-vol" min="0"
                max="100"> <span id="prop-audio-vol-label" class="reglerwert">${prozent}%</span>`)}
            ${M.zeile('Fade In', M.zahl('prop-audio-fadein', d.fadeIn || 0, 'min="0"') + f)}
            ${M.zeile('Fade Out', M.zahl('prop-audio-fadeout', d.fadeOut || 0, 'min="0"') + f)}
            ${M.zeile('Offset', M.zahl('prop-audio-offset', d.offset || 0, 'min="0" step="0.1"') + ' <span class="winzig">s</span>')}`);
    }

    static _objekt(clip) {
        const f = ' <span class="winzig">f</span>';
        return M.gruppe('3D-Objekt Clip', `
            ${M.zeile('Datei', `<span class="text-klein">${clip.data?.fileName || '—'}</span>`)}
            ${M.zeile('Start', M.zahl('prop-oc-start', clip.startFrame, 'min="0"') + f)}
            ${M.zeile('Dauer', M.zahl('prop-oc-frames', clip.totalFrames, 'min="1"') + f)}
            <div class="fussnote">Objekt ist in der Szene sichtbar wenn der Playhead im Clip-Bereich ist.
                Position/Rotation/Größe über die Track-Eigenschaften oben.</div>`);
    }

    static _modell(clip) {
        const f = ' <span class="winzig">f</span>';
        return M.gruppe('Modell Clip', `
            ${M.zeile('Preset', `<input type="text" value="${clip.data?.preset || ''}" id="prop-model-preset"
                placeholder="z.B. FemaleGarment">`)}
            ${M.zeile('Body Type', `<input type="text" value="${clip.data?.bodyType || 'Female_Caucasian'}"
                id="prop-model-bodytype">`)}
            ${M.zeile('Start', M.zahl('prop-model-start', clip.startFrame, 'min="0"') + f)}
            ${M.zeile('Dauer', M.zahl('prop-model-frames', clip.totalFrames, 'min="1"') + f)}`);
    }

    static _bvh(clip) {
        const f = ' <span class="winzig">f</span>';
        return M.gruppe(`Clip: ${clip.name}`, `
            ${M.zeile('Start', M.zahl('prop-clip-start', clip.startFrame, 'min="0"') + ' <span class="text-winzig">frames</span>')}
            ${M.zeile('Trim In', M.zahl('prop-clip-trim-in', clip.trimIn, 'min="0"'))}
            ${M.zeile('Trim Out', M.zahl('prop-clip-trim-out', clip.trimOut, 'min="0"'))}
            ${M.zeile('Speed', M.zahl('prop-clip-speed', clip.speed, 'min="0.1" max="4" step="0.1"'))}
            ${M.zeile('Smooth', M.zahl('prop-clip-smooth', clip.smoothSigma, 'min="0" max="10" step="0.5"'))}
            ${M.zeile('Boden', `<input type="checkbox" ${clip.groundFix ? 'checked' : ''} id="prop-clip-ground">`)}
            ${M.zeile('Blend In', M.zahl('prop-clip-blend-in', clip.blendIn, 'min="0"') + f)}
            ${M.zeile('Blend Out', M.zahl('prop-clip-blend-out', clip.blendOut, 'min="0"') + f)}`);
    }

    static _tonBinden(clip) {
        M.an('prop-audio-start', 'change', (e) => {
            clip.startFrame = parseInt(e.target.value) || 0;
            fn.updateDuration();
            fn.renderTimeline();
        });
        M.an('prop-audio-vol', 'input', (e) => {
            clip.data.volume = parseInt(e.target.value) / 100;
            document.getElementById('prop-audio-vol-label').textContent = e.target.value + '%';
        });
        M.an('prop-audio-fadein', 'change',
             (e) => { clip.data.fadeIn = parseInt(e.target.value) || 0; });
        M.an('prop-audio-fadeout', 'change',
             (e) => { clip.data.fadeOut = parseInt(e.target.value) || 0; });
        M.an('prop-audio-offset', 'change',
             (e) => { clip.data.offset = parseFloat(e.target.value) || 0; });
    }

    static _objektBinden(clip) {
        // Ein Objektclip bestimmt, WANN das Objekt sichtbar ist — deshalb muss
        // nach jeder Aenderung auch der Abspielkopf neu ausgewertet werden.
        const neuzeichnen = () => {
            fn.updateDuration();
            fn.renderTimeline();
            fn.applyPlayhead();
        };
        M.an('prop-oc-start', 'change', (e) => {
            clip.startFrame = Math.max(0, parseInt(e.target.value) || 0);
            neuzeichnen();
        });
        M.an('prop-oc-frames', 'change', (e) => {
            clip.totalFrames = Math.max(1, parseInt(e.target.value) || VORGABE_BILDER);
            neuzeichnen();
        });
    }

    static _modellBinden(clip) {
        const neuzeichnen = () => { fn.updateDuration(); fn.renderTimeline(); };
        M.an('prop-model-preset', 'change', (e) => {
            clip.data.preset = e.target.value;
            clip.name = e.target.value;
            fn.renderTimeline();
        });
        M.an('prop-model-bodytype', 'change',
             (e) => { clip.data.bodyType = e.target.value; });
        M.an('prop-model-start', 'change', (e) => {
            clip.startFrame = parseInt(e.target.value) || 0;
            neuzeichnen();
        });
        M.an('prop-model-frames', 'change', (e) => {
            clip.totalFrames = Math.max(1, parseInt(e.target.value) || VORGABE_BILDER);
            neuzeichnen();
        });
    }

    static _bvhBinden(clip) {
        const neuzeichnen = () => { fn.updateDuration(); fn.renderTimeline(); };
        M.an('prop-clip-start', 'change', (e) => {
            clip.startFrame = parseInt(e.target.value) || 0;
            neuzeichnen();
        });
        M.an('prop-clip-trim-in', 'change', (e) => {
            clip.trimIn = Math.max(0, Math.min(clip.totalFrames - 1,
                                               parseInt(e.target.value) || 0));
            neuzeichnen();
        });
        M.an('prop-clip-trim-out', 'change', (e) => {
            clip.trimOut = Math.max(0, parseInt(e.target.value) || 0);
            neuzeichnen();
        });
        M.an('prop-clip-speed', 'change', (e) => {
            clip.speed = Math.max(0.1, parseFloat(e.target.value) || 1);
            neuzeichnen();
        });
        M.an('prop-clip-smooth', 'change',
             (e) => { clip.smoothSigma = Math.max(0, parseFloat(e.target.value) || 0); });
        M.an('prop-clip-ground', 'change', (e) => { clip.groundFix = e.target.checked; });
        M.an('prop-clip-blend-in', 'change',
             (e) => { clip.blendIn = Math.max(0, parseInt(e.target.value) || 0); });
        M.an('prop-clip-blend-out', 'change',
             (e) => { clip.blendOut = Math.max(0, parseInt(e.target.value) || 0); });
    }
}
