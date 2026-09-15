import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Maskenbausteine as M } from './bausteine.js';
import { Schaltknopf } from '../schaltknopf.js';
import { Lebendigkeit } from '../lebendigkeit.js';
import { Mimikdialog } from '../mimikdialog.js';

/**
 * Mimikeigenschaften — Maske und Bedienung der Mimikspur (Lebendigkeit)
 * und ihrer Schlüsselbilder (Pose, Stärke, Übergang, Halten).
 *
 * Edgar, 13.09.2026: „Lebendigkeit an bei neuer Spur, aber konfigurierbar."
 * Jeder Baustein hat An/Aus, Stärke und Abstand oder Tempo; die Saat macht
 * die Zufälle wiederholbar.
 */
export class Mimikeigenschaften {

    /** Baustein → Beschriftung, zweites Feld (`abstand` [von, bis] s | `periode` s | `tempo` Hz). */
    static BAUSTEINE = [
        ['blinzeln', 'Blinzeln', 'abstand'], ['blick', 'Blick', 'abstand'],
        ['atmen', 'Atmen', 'periode'], ['variation', 'Variation um die Pose', 'tempo'],
        ['zucken', 'Zucken', 'abstand'], ['schlucken', 'Schlucken', 'abstand'],
    ];

    // ------------------------------------------------------------------- Spur
    static maske(track) {
        const l = track.lebendigkeit || (track.lebendigkeit = Lebendigkeit.vorgabe());
        const modell = state.project.tracks[track._modellIdx];
        const zeilen = Mimikeigenschaften.BAUSTEINE.map(([id, titel, feld]) => {
            const b = l[id] || {};
            const zweites = feld === 'abstand'
                ? `${M.zahl(`prop-mimik-${id}-von`, b.abstand?.[0] ?? 2, 'min="0.1" step="0.5" class="klein"')} –
                   ${M.zahl(`prop-mimik-${id}-bis`, b.abstand?.[1] ?? 6, 'min="0.1" step="0.5" class="klein"')} s`
                : feld === 'periode'
                ? `${M.zahl(`prop-mimik-${id}-periode`, b.periode ?? 4, 'min="0.5" step="0.5" class="klein"')} s`
                : `${M.zahl(`prop-mimik-${id}-tempo`, b.tempo ?? 0.3, 'min="0.05" step="0.05" class="klein"')} Hz`;
            return `<div class="prop-row"><label>${titel}:</label>
                ${Schaltknopf.bauen(`prop-mimik-${id}-an`, !!b.an)}
                <input type="range" id="prop-mimik-${id}-staerke" min="0" max="100" step="5"
                    value="${Math.round((b.staerke ?? 1) * 100)}" title="Stärke"> ${zweites}</div>`;
        }).join('');
        return `<div class="prop-group">
            <div class="prop-row"><label>Typ:</label><span class="marke-akzent">Mimik</span></div>
            <div class="prop-row"><label>Modell:</label><span class="marke-akzent">${modell?.name || '(keins)'}</span></div>
            <h3 class="gruppentitel">Lebendigkeit ${Schaltknopf.bauen('prop-mimik-an', !!l.an)}</h3>
            ${zeilen}
            ${M.zeile('Saat', M.zahl('prop-mimik-saat', l.saat ?? 7, 'min="0" step="1" class="klein"'))}
            <div class="fussnote">Rechtsklick auf die Spur: Pose setzen, Neutral, Mimik einrechnen.
                Die letzte Pose bleibt bis zum Ende stehen.</div>
        </div>`;
    }

    static binden(track) {
        const l = track.lebendigkeit;
        const neu = () => fn.applyPlayhead();
        M.an('prop-mimik-an', 'click', () => { l.an = !l.an; neu(); fn.updateProperties(); });
        M.an('prop-mimik-saat', 'change', (e) => { l.saat = parseInt(e.target.value) || 0; neu(); });
        for (const [id, _titel, feld] of Mimikeigenschaften.BAUSTEINE) {
            const b = l[id] || (l[id] = { an: false, staerke: 1 });
            M.an(`prop-mimik-${id}-an`, 'click', () => { b.an = !b.an; neu(); fn.updateProperties(); });
            M.an(`prop-mimik-${id}-staerke`, 'input', (e) => { b.staerke = Number(e.target.value) / 100; neu(); });
            if (feld === 'abstand') {
                const setzen = () => {
                    const von = parseFloat(document.getElementById(`prop-mimik-${id}-von`).value) || 1;
                    const bis = parseFloat(document.getElementById(`prop-mimik-${id}-bis`).value) || von;
                    b.abstand = [Math.min(von, bis), Math.max(von, bis)];
                    neu();
                };
                M.an(`prop-mimik-${id}-von`, 'change', setzen);
                M.an(`prop-mimik-${id}-bis`, 'change', setzen);
            } else {
                M.an(`prop-mimik-${id}-${feld}`, 'change', (e) => {
                    b[feld] = parseFloat(e.target.value) || b[feld]; neu();
                });
            }
        }
    }

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
