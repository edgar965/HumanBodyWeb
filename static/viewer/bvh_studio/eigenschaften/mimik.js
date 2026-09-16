import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Maskenbausteine as M } from './bausteine.js';
import { Mimikdialog } from '../mimikdialog.js';

/**
 * Mimikeigenschaften — Maske und Bedienung der Mimikspur und ihrer
 * Schlüsselbilder (Pose, Stärke, Übergang, Halten).
 *
 * Die Lebendigkeit (Blinzeln, Blick, …) stand bis 14.09.2026 hier an der
 * Spur; seit 15.09.2026 ist sie ein Script-Clip auf der Script-Spur
 * (`eigenschaften/script.js`) — mit Anfang und Ende.
 */
export class Mimikeigenschaften {

    // ------------------------------------------------------------------- Spur
    static maske(track) {
        const modell = state.project.tracks[track._modellIdx];
        return `<div class="prop-group">
            <div class="prop-row"><label>Typ:</label><span class="marke-akzent">Mimik</span></div>
            <div class="prop-row"><label>Modell:</label><span class="marke-akzent">${modell?.name || '(keins)'}</span></div>
            <div class="fussnote">Rechtsklick auf die Spur: Pose setzen, Neutral, Mimik einrechnen.
                Die letzte Pose bleibt bis zum Ende stehen. Blinzeln und Blick: Script-Spur.</div>
        </div>`;
    }

    static binden(_track) {}

    // ---------------------------------------------------------- Schlüsselbild
    static schluesselMaske(clip) {
        const d = clip.data || {};
        return `<div class="prop-group">
            <div class="prop-row"><label>Pose:</label><span class="marke-akzent">${clip.name}</span>
                <button id="prop-mimik-pose" class="knopf-akzent"><i class="fas fa-smile"></i> Ändern…</button></div>
            ${M.zeile('Bild', M.zahl('prop-mimik-frame', clip.startFrame, 'min="0" step="1"'))}
            <div class="prop-row"><label>Stärke:</label><input type="range" id="prop-mimik-staerke"
                min="0" max="100" step="5" value="${Math.round((d.staerke ?? 1) * 100)}" class="dehnen">
                <span id="prop-mimik-staerke-wert" class="reglerwert">${Math.round((d.staerke ?? 1) * 100)}</span> %</div>
            <div class="prop-row"><label>Übergang:</label><select id="prop-mimik-uebergang" class="dehnen">
                <option value="weich" ${d.uebergang !== 'linear' ? 'selected' : ''}>weich</option>
                <option value="linear" ${d.uebergang === 'linear' ? 'selected' : ''}>linear</option></select></div>
            ${M.zeile('Halten', M.zahl('prop-mimik-halten', d.halten ?? 0, 'min="0" step="0.1"') + ' s')}
        </div>`;
    }

    static schluesselBinden(track, clip) {
        const d = clip.data || (clip.data = {});
        const neu = () => { fn.applyPlayhead(); fn.renderTimeline(); };
        M.an('prop-mimik-pose', 'click', () => Mimikdialog.oeffnen(track, clip.startFrame, clip));
        M.an('prop-mimik-frame', 'change', (e) => {
            clip.startFrame = Math.max(0, parseInt(e.target.value) || 0);
            track.clips.sort((a, b) => a.startFrame - b.startFrame);
            state.selectedClipIdx = track.clips.indexOf(clip);
            neu();
        });
        M.an('prop-mimik-staerke', 'input', (e) => {
            d.staerke = Number(e.target.value) / 100;
            document.getElementById('prop-mimik-staerke-wert').textContent = e.target.value;
            neu();
        });
        M.an('prop-mimik-uebergang', 'change', (e) => { d.uebergang = e.target.value; neu(); });
        M.an('prop-mimik-halten', 'change', (e) => { d.halten = Math.max(0, parseFloat(e.target.value) || 0); neu(); });
    }
}
