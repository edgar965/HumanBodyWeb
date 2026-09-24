import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Maskenbausteine as M } from './bausteine.js';
import { Schaltknopf } from '../schaltknopf.js';
import { Lebendigkeit } from '../lebendigkeit.js';

/**
 * Scripteigenschaften — Maske und Bedienung der Script-Spur und ihrer Clips
 * (Lebendigkeit: Blinzeln, Blick, Atmen, Variation, Zucken, Schlucken, Saat).
 *
 * Edgar, 13.09.2026: „Lebendigkeit an bei neuer Spur, aber konfigurierbar";
 * 15.09.2026: Script als eigene Animationsart unter dem Modell. Jeder
 * Baustein hat An/Aus, Stärke und Abstand oder Tempo; die Saat macht die
 * Zufälle wiederholbar. Bis 14.09. stand diese Maske an der Mimikspur.
 */
export class Scripteigenschaften {

    /** Baustein → Beschriftung, zweites Feld (`abstand` [von, bis] s | `periode` s | `tempo` Hz). */
    static BAUSTEINE = [
        ['blinzeln', 'Blinzeln', 'abstand'], ['blick', 'Blick', 'abstand'],
        ['atmen', 'Atmen', 'periode'], ['variation', 'Variation um die Pose', 'tempo'],
        ['zucken', 'Zucken', 'abstand'], ['schlucken', 'Schlucken', 'abstand'],
    ];

    // ------------------------------------------------------------------- Spur
    static maske(track) {
        const modell = state.project.tracks[track._modellIdx];
        return `<div class="prop-group">
            <div class="prop-row"><label>Typ:</label><span class="marke-akzent">Script</span></div>
            <div class="prop-row"><label>Modell:</label>
                <span class="marke-akzent">${modell?.name || '(keins)'}</span></div>
            <div class="fussnote">Rechtsklick auf die Spur: Script hinzufügen. Ein Script wirkt, solange der
                Abspielkopf in seinem Clip steht; Klick auf den Clip zeigt seine Einstellungen.</div>
        </div>`;
    }

    // ------------------------------------------------------------------- Clip
    static clipMaske(clip) {
        const l = clip.data || (clip.data = Lebendigkeit.vorgabe());
        const zeilen = Scripteigenschaften.BAUSTEINE.map(([id, titel, feld]) => {
            const b = l[id] || {};
            const zweites = feld === 'abstand'
                ? `${M.zahl(`prop-script-${id}-von`, b.abstand?.[0] ?? 2, 'min="0.1" step="0.5" class="klein"')} –
                   ${M.zahl(`prop-script-${id}-bis`, b.abstand?.[1] ?? 6, 'min="0.1" step="0.5" class="klein"')} s`
                : feld === 'periode'
                ? `${M.zahl(`prop-script-${id}-periode`, b.periode ?? 4, 'min="0.5" step="0.5" class="klein"')} s`
                : `${M.zahl(`prop-script-${id}-tempo`, b.tempo ?? 0.3, 'min="0.05" step="0.05" class="klein"')} Hz`;
            return `<div class="prop-row"><label>${titel}:</label>
                ${Schaltknopf.bauen(`prop-script-${id}-an`, !!b.an)}
                <input type="range" id="prop-script-${id}-staerke" min="0" max="100" step="5"
                    value="${Math.round((b.staerke ?? 1) * 100)}" title="Stärke"> ${zweites}</div>`;
        }).join('');
        const f = ' <span class="winzig">f</span>';
        return `<div class="prop-group">
            <h3 class="gruppentitel">Script: Lebendigkeit ${Schaltknopf.bauen('prop-script-an', !!l.an)}</h3>
            ${M.zeile('Start', M.zahl('prop-script-start', clip.startFrame, 'min="0"') + f)}
            ${M.zeile('Dauer', M.zahl('prop-script-frames', clip.totalFrames, 'min="1"') + f)}
            ${zeilen}
            ${M.zeile('Saat', M.zahl('prop-script-saat', l.saat ?? 7, 'min="0" step="1" class="klein"'))}
            <div class="fussnote">Die Zeit zählt ab dem Clipanfang — ein verschobener Clip nimmt seine
                Blinzelfolge mit.</div>
        </div>`;
    }

    static clipBinden(track, clip) {
        const l = clip.data;
        const neu = () => fn.applyPlayhead();
        const neuzeichnen = () => { fn.updateDuration(); fn.renderTimeline(); neu(); };
        M.an('prop-script-start', 'change', (e) => {
            clip.startFrame = Math.max(0, parseInt(e.target.value) || 0);
            track.clips.sort((a, b) => a.startFrame - b.startFrame);
            state.selectedClipIdx = track.clips.indexOf(clip);
            neuzeichnen();
        });
        M.an('prop-script-frames', 'change', (e) => {
            clip.totalFrames = Math.max(1, parseInt(e.target.value) || clip.totalFrames);
            neuzeichnen();
        });
        M.an('prop-script-an', 'click', () => { l.an = !l.an; neu(); fn.updateProperties(); });
        M.an('prop-script-saat', 'change', (e) => { l.saat = parseInt(e.target.value) || 0; neu(); });
        for (const [id, _titel, feld] of Scripteigenschaften.BAUSTEINE) {
            const b = l[id] || (l[id] = { an: false, staerke: 1 });
            M.an(`prop-script-${id}-an`, 'click', () => { b.an = !b.an; neu(); fn.updateProperties(); });
            M.an(`prop-script-${id}-staerke`, 'input', (e) => { b.staerke = Number(e.target.value) / 100; neu(); });
            if (feld === 'abstand') {
                const setzen = () => {
                    const von = parseFloat(document.getElementById(`prop-script-${id}-von`).value) || 1;
                    const bis = parseFloat(document.getElementById(`prop-script-${id}-bis`).value) || von;
                    b.abstand = [Math.min(von, bis), Math.max(von, bis)];
                    neu();
                };
                M.an(`prop-script-${id}-von`, 'change', setzen);
                M.an(`prop-script-${id}-bis`, 'change', setzen);
            } else {
                M.an(`prop-script-${id}-${feld}`, 'change', (e) => {
                    b[feld] = parseFloat(e.target.value) || b[feld]; neu();
                });
            }
        }
    }
}
