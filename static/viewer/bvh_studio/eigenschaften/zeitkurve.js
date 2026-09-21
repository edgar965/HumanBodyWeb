/**
 * Zeitkurveneigenschaften — die Geschwindigkeitskurve eines BVH-Clips im
 * Eigenschaftsfeld: Punkte hinzufügen, bearbeiten, löschen.
 *
 * Rechnung in `../zeitkurve.js` (Node-testbar); hier nur Maske und Bedienung,
 * wie bei den übrigen `eigenschaften/*`-Klassen. Ohne Punkte läuft der Clip
 * mit konstantem `speed` wie bisher — dieser Abschnitt ist rein additiv.
 */
import { fn } from '../../gemeinsam/registrierung.js';
import { state } from '../state.js';
import { Maskenbausteine as M } from './bausteine.js';
import { Zeitkurve } from '../zeitkurve.js';

export class Zeitkurveneigenschaften {

    static maske(clip) {
        const punkte = clip.data?.remap || [];
        const zeilen = punkte.map((p, i) => `
            <div class="prop-row prop-kurvenpunkt">
                <input type="number" class="kurve-u" data-i="${i}" min="0" max="100" step="1"
                    value="${Math.round(p.u * 100)}"><span class="winzig">%→</span>
                <input type="number" class="kurve-v" data-i="${i}" min="0" max="100" step="1"
                    value="${Math.round(p.v * 100)}"><span class="winzig">%</span>
                <select class="kurve-art" data-i="${i}">
                    <option value="linear" ${p.interpolation === 'smooth' || p.interpolation === 'step' ? '' : 'selected'}>gerade</option>
                    <option value="smooth" ${p.interpolation === 'smooth' ? 'selected' : ''}>weich</option>
                    <option value="step" ${p.interpolation === 'step' ? 'selected' : ''}>hart</option>
                </select>
                <button class="kurve-loeschen knopf-klein" data-i="${i}" title="Punkt löschen">
                    <i class="fas fa-times"></i></button>
            </div>`).join('');
        return M.gruppe('Geschwindigkeitskurve', `
            <div class="fussnote">Zeitanteil % im Clip → welcher Anteil der Quelle dort läuft.
                Ohne Punkte: konstantes Tempo (Speed oben). Zwei Punkte mit gleichem zweiten Wert
                halten die Bewegung dazwischen an.</div>
            ${zeilen || '<div class="fussnote">Noch keine Punkte.</div>'}
            <div class="prop-row">
                <button id="prop-kurve-punkt" class="knopf-klein">+ Punkt am Abspielkopf</button>
                ${punkte.length ? '<button id="prop-kurve-reset" class="knopf-klein">Zurücksetzen</button>' : ''}
            </div>`);
    }

    static binden(clip) {
        M.an('prop-kurve-punkt', 'click', () => Zeitkurveneigenschaften._punktHinzufuegen(clip));
        M.an('prop-kurve-reset', 'click', () => {
            clip.data.remap = [];
            fn.updateProperties();
            fn.renderTimeline();
        });
        document.querySelectorAll('.kurve-u, .kurve-v').forEach(feld => {
            feld.addEventListener('change', (e) => Zeitkurveneigenschaften._wertGeaendert(clip, e));
        });
        document.querySelectorAll('.kurve-art').forEach(feld => {
            feld.addEventListener('change', (e) => {
                const punkt = clip.data.remap?.[Number(e.target.dataset.i)];
                if (punkt) punkt.interpolation = e.target.value;
            });
        });
        document.querySelectorAll('.kurve-loeschen').forEach(knopf => {
            knopf.addEventListener('click', (e) => {
                clip.data.remap.splice(Number(e.currentTarget.dataset.i), 1);
                fn.updateProperties();
                fn.renderTimeline();
            });
        });
    }

    static _wertGeaendert(clip, e) {
        const punkt = clip.data.remap?.[Number(e.target.dataset.i)];
        if (!punkt) return;
        const wert = Math.min(100, Math.max(0, parseFloat(e.target.value) || 0)) / 100;
        if (e.target.classList.contains('kurve-u')) punkt.u = wert;
        else punkt.v = wert;
        clip.data.remap.sort((a, b) => a.u - b.u);
        fn.updateProperties();
        fn.renderTimeline();
    }

    /** Neuer Punkt am Abspielkopf — `v` so gewählt, dass sich am Bild nichts ändert. */
    static _punktHinzufuegen(clip) {
        const beginn = clip.startFrame / state.project.fps;
        const zeit = state.playheadFrame / state.project.fps;
        if (zeit < beginn || zeit > beginn + clip.duration) {
            alert('Der Abspielkopf muss innerhalb dieses Clips stehen.');
            return;
        }
        const u = clip.duration > 0 ? (zeit - beginn) / clip.duration : 0;
        clip.data = clip.data || {};
        clip.data.remap = clip.data.remap || [];
        const v = Zeitkurve.quellanteil(clip.data.remap, u);
        clip.data.remap.push({ u, v, interpolation: 'linear' });
        clip.data.remap.sort((a, b) => a.u - b.u);
        fn.updateProperties();
        fn.renderTimeline();
    }
}
