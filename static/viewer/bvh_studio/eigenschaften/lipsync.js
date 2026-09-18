import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Maskenbausteine as M } from './bausteine.js';
import { Lipsynckurve } from '../../gemeinsam/lipsynckurve.js';

/**
 * Lipsynceigenschaften — Maske eines `lipsync`-Clips auf der Mimikspur.
 *
 * Zeigt, woraus der Clip entstand (Tondatei, Erkenner, Zahl der Mundformen),
 * die Mundform am Abspielkopf und den Versatz zum Ton (`offset`, wie beim
 * Audio-Clip). Ändern lässt sich der Start (das Bild, an dem der Ton beginnt)
 * — sonst nichts: die Mundformen kommen von Rhubarb, nicht von Hand
 * (`Lipsyncspur`, 18.09.2026).
 */
export class Lipsynceigenschaften {

    static FORMEN = {
        A: 'A · geschlossen (M, B, P)', B: 'B · leicht offen (K, S, T, EE)',
        C: 'C · offen (EH)', D: 'D · weit offen (AA)', E: 'E · gerundet (ER, AO)',
        F: 'F · gespitzt (UW, OW, W)', G: 'G · Zähne auf der Lippe (F, V)',
        H: 'H · Zunge oben (L)', X: 'X · Ruhe',
    };

    static maske(clip) {
        const d = clip.data || {};
        const fps = state.project.fps;
        const tonzeit = (state.playheadFrame - clip.startFrame) / fps + (d.offset || 0);
        const form = Lipsynckurve.form(d.cues || [], tonzeit);
        const f = ' <span class="winzig">f</span>';
        return M.gruppe(`Lippensynchronisation: ${d.fileName || 'Ton'}`, `
            ${M.zeile('Tondatei', `<span class="text-klein">${d.fileName || '—'}</span>`)}
            ${M.zeile('Mundformen', `<span class="tonwert">${(d.cues || []).length}</span>
                <span class="winzig">über ${(d.dauer || 0).toFixed(1)} s (${d.erkenner || 'Rhubarb'})</span>`)}
            ${M.zeile('Am Abspielkopf', `<span class="marke-akzent">${Lipsynceigenschaften.FORMEN[form] || form}</span>`)}
            ${M.zeile('Start', M.zahl('prop-lipsync-start', clip.startFrame, 'min="0"') + f)}
            ${M.zeile('Versatz', `<span class="tonwert">${(d.offset || 0).toFixed(2)} s</span>`)}
            <div class="fussnote">Genesis 9 spricht mit Daz' Visemes (Vis AA … Vis W), die anderen Figuren
                mit den MB-Lab-Mundeinheiten der Mimik. Ton verschoben? Clip neu anlegen
                (Rechtsklick auf die Mimikspur).</div>`);
    }

    static binden(track, clip) {
        M.an('prop-lipsync-start', 'change', (e) => {
            clip.startFrame = Math.max(0, parseInt(e.target.value, 10) || 0);
            track.clips.sort((a, b) => a.startFrame - b.startFrame);
            fn.applyPlayhead();
            fn.renderTimeline();
        });
    }
}
