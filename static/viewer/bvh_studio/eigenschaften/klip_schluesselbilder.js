/**
 * Schluesselbildeigenschaften — Maske und Bedienung fuer Kamera- und
 * Licht-Schluesselbilder (camera_kf, light_kf).
 *
 * Aus properties.js herausgeloest (Umbau 16.08.2026).
 */
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Maskenbausteine as M } from './bausteine.js';
import { Schaltknopf } from '../schaltknopf.js';

const STUFEN = ['linear', 'smooth', 'step'];

export class Schluesselbildeigenschaften {
    static maske(clip) {
        return clip.type === 'camera_kf' ? Schluesselbildeigenschaften._kamera(clip)
                                         : Schluesselbildeigenschaften._licht(clip);
    }

    static binden(track, clip) {
        if (clip.type === 'camera_kf') Schluesselbildeigenschaften._kameraBinden(track, clip);
        else Schluesselbildeigenschaften._lichtBinden(track, clip);
    }

    static _kamera(clip) {
        const d = clip.data;
        const lage = ['x', 'y', 'z'].map(a => M.zeile(`Pos ${a.toUpperCase()}`,
            M.zahl(`prop-kf-p${a}`, d.position?.[a]?.toFixed(3) || 0, 'step="0.1"'))).join('');
        const dreh = ['x', 'y', 'z'].map(a => M.zeile(`Rot ${a.toUpperCase()}`,
            M.zahl(`prop-kf-r${a}`, ((d.rotation?.[a] || 0) * 180 / Math.PI).toFixed(1),
                   'step="1"') + ' °')).join('');
        const stufen = STUFEN.map(v =>
            `<option value="${v}" ${d.interpolation === v ? 'selected' : ''}>`
            + `${v[0].toUpperCase() + v.slice(1)}</option>`).join('');
        return M.gruppe('Kamera Keyframe', `
            ${M.zeile('Frame', M.zahl('prop-kf-frame', clip.startFrame, 'min="0"'))}
            ${lage}${dreh}
            ${M.zeile('FOV', M.zahl('prop-kf-fov', d.fov || 50, 'min="10" max="120"'))}
            ${M.zeile('Fade-Effekt', `<input type="checkbox" ${d.fade !== false ? 'checked' : ''}
                id="prop-kf-fade"> <span class="kaestchen-hinweis">aus = Sprung</span>`)}
            ${M.zeile('Interp.', `<select id="prop-kf-interp" ${d.fade === false ? 'disabled'
                : ''}>${stufen}</select>`)}
            <div class="abstand-6">
                <button id="prop-kf-set-view" class="knopf-schmal-grau">Aktuelle Ansicht übernehmen</button>
            </div>`);
    }

    static _licht(clip) {
        const d = clip.data;
        const lage = ['x', 'y', 'z'].map(a => M.zeile(`Pos ${a.toUpperCase()}`,
            M.zahl(`prop-lkf-p${a}`, d.position?.[a]?.toFixed(2) || 0, 'step="0.1"'))).join('');
        const an = d.visible !== false;
        return M.gruppe('Licht Keyframe', `
            ${M.zeile('Frame', M.zahl('prop-lkf-frame', clip.startFrame, 'min="0"'))}
            ${lage}
            ${M.zeile('Farbe', `<input type="color" value="${d.color || '#ffffff'}" id="prop-lkf-color">`)}
            ${M.zeile('Intensität', M.zahl('prop-lkf-intensity', d.intensity || 2, 'min="0" max="20" step="0.1"'))}
            ${d.angle == null ? '' : M.zeile('Winkel', M.zahl('prop-lkf-angle', (d.angle * 180 / Math.PI).toFixed(1), 'min="1" max="170" step="1"') + ' °')}
            ${d.penumbra == null ? '' : M.zeile('Penumbra', M.zahl('prop-lkf-penumbra', d.penumbra.toFixed(2), 'min="0" max="1" step="0.05"'))}
            ${d.distance == null ? '' : M.zeile('Reichweite', M.zahl('prop-lkf-distance', d.distance.toFixed(1), 'min="0" max="200" step="1"'))}
            ${M.zeile('Licht', Schaltknopf.bauen('prop-lkf-visible', an, true))}
            ${M.zeile('Fade-Effekt', `<input type="checkbox" ${d.fade !== false ? 'checked' : ''}
                id="prop-lkf-fade"> <span class="kaestchen-hinweis">aus = Sprung</span>`)}`);
    }

    /** Bildnummer aendern: Clips neu sortieren, Zeitleiste neu zeichnen. */
    static _bildnummer(track, clip, id) {
        M.an(id, 'change', (e) => {
            clip.startFrame = parseInt(e.target.value) || 0;
            track.clips.sort((a, b) => a.startFrame - b.startFrame);
            fn.renderTimeline();
        });
    }

    static _kameraBinden(track, clip) {
        Schluesselbildeigenschaften._bildnummer(track, clip, 'prop-kf-frame');
        for (const a of ['x', 'y', 'z']) {
            M.an(`prop-kf-p${a}`, 'change',
                 (e) => { clip.data.position[a] = parseFloat(e.target.value) || 0; });
            M.an(`prop-kf-r${a}`, 'change', (e) => {
                clip.data.rotation[a] = (parseFloat(e.target.value) || 0) * Math.PI / 180;
            });
        }
        M.an('prop-kf-fov', 'change',
             (e) => { clip.data.fov = parseFloat(e.target.value) || 50; });
        M.an('prop-kf-interp', 'change',
             (e) => { clip.data.interpolation = e.target.value; });
        M.an('prop-kf-fade', 'change', (e) => {
            clip.data.fade = e.target.checked;
            fn.updateProperties();  // Auswahl Interpolation frei-/sperren
        });
        M.an('prop-kf-set-view', 'click',
             () => Schluesselbildeigenschaften._ansichtUebernehmen(clip));
    }

    /** Aktuelle Kameraansicht in das Schluesselbild schreiben. */
    static _ansichtUebernehmen(clip) {
        const k = state.camera;
        clip.data.position = { x: k.position.x, y: k.position.y, z: k.position.z };
        clip.data.rotation = { x: k.rotation.x, y: k.rotation.y, z: k.rotation.z };
        clip.data.quaternion = { x: k.quaternion.x, y: k.quaternion.y,
                                 z: k.quaternion.z, w: k.quaternion.w };
        if (state.controls?.target) {
            clip.data.lookAt = { x: state.controls.target.x,
                                 y: state.controls.target.y,
                                 z: state.controls.target.z };
        }
        clip.data.fov = k.fov;
        fn.updateProperties();
    }

    static _lichtBinden(track, clip) {
        Schluesselbildeigenschaften._bildnummer(track, clip, 'prop-lkf-frame');
        for (const a of ['x', 'y', 'z']) {
            M.an(`prop-lkf-p${a}`, 'change',
                 (e) => { clip.data.position[a] = parseFloat(e.target.value) || 0; });
        }
        M.an('prop-lkf-color', 'input', (e) => { clip.data.color = e.target.value; });
        M.an('prop-lkf-intensity', 'change',
             (e) => { clip.data.intensity = parseFloat(e.target.value) || 2; });
        M.an('prop-lkf-angle', 'change', (e) => {
            clip.data.angle = (parseFloat(e.target.value) || 30) * Math.PI / 180;
        });
        M.an('prop-lkf-penumbra', 'change', (e) => {
            clip.data.penumbra = Math.max(0, Math.min(1, parseFloat(e.target.value) || 0));
        });
        M.an('prop-lkf-distance', 'change',
             (e) => { clip.data.distance = parseFloat(e.target.value) || 50; });
        M.an('prop-lkf-fade', 'change', (e) => { clip.data.fade = e.target.checked; });
        M.an('prop-lkf-visible', 'click', () => {
            clip.data.visible = !(clip.data.visible !== false);  // undefined → true
            fn.updateProperties();
            fn.renderTimeline?.();
        });
    }
}
