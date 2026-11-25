import { escapeHtml } from '../utils.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';

/**
 * Smplmassanzeige — Kopfzeile und Maße eines SMPL-Körpers im Eigenschaften-Reiter (25.11.2026 aus `Smpleigenschaften` herausgelöst).
 *
 * Eine geformte Figur hat nach einem Reglerzug noch keine Maße: Gemessen wird (0,25 s auf dem Server), sobald die Figur `RUHE_MS` ruht — auch zugeklappt, damit die Tabelle beim
 * Aufklappen schon dasteht (Edgar, 25.11.2026: „Maße … werden erst gemessen, wenn der Bereich offen ist; das dauert 5–8 s“ → „fixe“).
 */
export class Smplmassanzeige {

    static RUHE_MS = 150;
    static ADRESSE = '/api/character/smpl-figur/';
    static _figur = null;
    static _warten = null;

    static zeigen(inst) {
        Smplmassanzeige._figur = inst;
        clearTimeout(Smplmassanzeige._warten);
        const kopf = document.getElementById('prop-smpl-kopf');
        const punkte = inst.bodyMesh?.geometry?.attributes?.position?.count || 0;
        if (kopf) kopf.textContent = `${inst.koerper} · ${punkte} Punkte · ${inst.hoehe ? (inst.hoehe * 100).toFixed(0) : '?'} cm`;
        const behaelter = document.getElementById('prop-smpl-masse');
        if (!behaelter) return;
        if (Object.keys(inst.masse || {}).length) return Smplmassanzeige._tabelle(inst, behaelter);
        Smplmassanzeige._hinweis(behaelter, 'Maße werden gemessen …');
        Smplmassanzeige._warten = setTimeout(() => Smplmassanzeige._holen(inst, behaelter), Smplmassanzeige.RUHE_MS);
    }

    static async _holen(inst, behaelter) {
        const name = inst.koerper;
        const gilt = () => Smplmassanzeige._figur === inst && inst.koerper === name;       // inzwischen weitergezogen oder eine andere Figur gewählt: deren Messung gilt
        try {
            const daten = await Serverabruf.json(`${Smplmassanzeige.ADRESSE}${encodeURIComponent(name)}/masse/`);
            if (inst.koerper === name) inst.masse = daten.masse || {};
            if (gilt()) Smplmassanzeige._tabelle(inst, behaelter);
        } catch (fehler) {
            if (gilt()) Smplmassanzeige._hinweis(behaelter, `Maße nicht messbar: ${fehler.message}`);
        }
    }

    static _hinweis(behaelter, text) {
        behaelter.innerHTML = `<div class="hb-hinweis">${escapeHtml(text)}</div>`;
    }

    /** Die vorgegebenen Maße — Zentimeter und Grad, wie in der YAML. */
    static _tabelle(inst, behaelter) {
        const namen = Object.keys(inst.masse || {}).sort();
        if (!namen.length) return Smplmassanzeige._hinweis(behaelter, 'Keine Maße vorhanden.');
        behaelter.innerHTML = '';
        for (const name of namen) {
            const wert = inst.masse[name];
            const zeile = document.createElement('div');
            zeile.className = 'slider-row';
            const text = typeof wert === 'number' ? String(+wert.toFixed(2)) : String(wert);
            zeile.innerHTML = `<label>${escapeHtml(name)}</label><span class="slider-val">${escapeHtml(text)}</span>`;
            behaelter.appendChild(zeile);
        }
    }
}
