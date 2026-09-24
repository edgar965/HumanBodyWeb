/**
 * Speedeigenschaften — Maske und Bedienung eines Speed-Ereignisses
 * (`speed_kf`) auf einer Effekte-Spur.
 *
 * Aus `klip.js` herausgeloest, analog zu `klip_schluesselbilder.js`.
 */
import { fn } from '../../gemeinsam/registrierung.js';
import { Maskenbausteine as M } from './bausteine.js';
import { Effektespur } from '../effektespur.js';

/** Obergrenze des Schiebereglers — mehr als 4x wirkt in der Praxis wie ein Sprung. */
const MAX_SPEED = 4;

export class Speedeigenschaften {
    static maske(clip) {
        const speed = clip.data?.speed ?? 1;
        return M.gruppe(`Speed: ${clip.name}`, `
            ${M.zeile('Frame', M.zahl('prop-speed-frame', clip.startFrame, 'min="0"'))}
            ${M.zeile('Tempo', M.schieber('prop-speed-wert', speed, 0, MAX_SPEED, 0.01))}
            <div class="fussnote">0 = Standbild, 1 = normal, 2 = doppelt so schnell.
                Zwischen zwei Ereignissen wird linear interpoliert.</div>`);
    }

    static binden(clip) {
        M.an('prop-speed-frame', 'change', (e) => {
            clip.startFrame = Math.max(0, parseInt(e.target.value) || 0);
            fn.updateDuration();
            fn.renderTimeline();
        });
        const schieber = document.getElementById('prop-speed-wert');
        const anzeige = document.getElementById('prop-speed-wert-wert');
        // `M.schieber` zeigt beim Aufbau `toFixed(2)` (generischer Baustein,
        // fuer andere Regler gewollt) — hier gleich auf die kurze Fassung
        // umstellen (22.09.2026, Edgar: „1 oder 0, ohne Nachkommastellen").
        if (anzeige) anzeige.textContent = Effektespur.formatSpeed(clip.data?.speed);
        schieber?.addEventListener('input', (e) => {
            const wert = parseFloat(e.target.value) || 0;
            clip.data.speed = wert;
            if (anzeige) anzeige.textContent = Effektespur.formatSpeed(wert);
            fn.updateDuration();
            fn.renderTimeline();
        });
    }
}
