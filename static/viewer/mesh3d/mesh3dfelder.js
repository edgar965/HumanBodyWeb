/**
 * Mesh3dfelder — Eingabefelder aus dem Katalog des Modell-Imports (11.10.2026).
 *
 * Der Katalog kommt vom Server (`/api/character/blendimport/einstellungen/?format=…`, `Blendimporteinstellungen.KATALOG`): je Option
 * `schluessel`, `titel`, `art` (`text`, `wahl`, `haken`), `werte`, `hinweis`, `nur_wenn`. Die Liste „Neuer Auftrag“ und die Einstellungen der
 * Jobseite bauen ihre Felder mit derselben Klasse — wie der Dialog der Charakter-Seite (`Modellimportformular`), nur ohne dessen Dialog.
 * Felder tragen `data-schluessel`; ein Haken trägt `an`/`aus`.
 */
import { escapeHtml } from '../charakter/utils.js';

export class Mesh3dfelder {

    /** Baut die Felder in `ziel`; `beiAenderung(werte)` läuft nach jeder Eingabe (Text erst beim Verlassen des Felds). */
    static bauen(ziel, optionen, werte, beiAenderung = null) {
        ziel.innerHTML = optionen.map(o => Mesh3dfelder._feld(o, werte[o.schluessel])).join('');
        const aendern = () => { Mesh3dfelder.abhaengigkeiten(ziel, optionen); if (beiAenderung) beiAenderung(Mesh3dfelder.lesen(ziel)); };
        ziel.querySelectorAll('select, input[type="checkbox"]').forEach(e => e.addEventListener('change', aendern));
        ziel.querySelectorAll('input[type="text"]').forEach(e => e.addEventListener('change', aendern));
        Mesh3dfelder.abhaengigkeiten(ziel, optionen);
    }

    static _feld(option, wert) {
        const id = `mesh3d-opt-${option.schluessel}`;
        const hinweis = option.hinweis ? `<div class="hb-hinweis">${escapeHtml(option.hinweis)}</div>` : '';
        if (option.art === 'haken') {
            return `<div class="mesh3d-feld mesh3d-feld-haken" data-feld="${option.schluessel}"><label for="${id}"><input id="${id}" type="checkbox"
                data-schluessel="${option.schluessel}" data-haken="an"${wert === 'an' ? ' checked' : ''}> ${escapeHtml(option.titel)}</label>${hinweis}</div>`;
        }
        const eingabe = option.art === 'wahl'
            ? `<select id="${id}" data-schluessel="${option.schluessel}">${option.werte.map(w =>
                `<option value="${escapeHtml(w.wert)}"${w.wert === wert ? ' selected' : ''}>${escapeHtml(w.text)}</option>`).join('')}</select>`
            : `<input id="${id}" data-schluessel="${option.schluessel}" type="text" value="${escapeHtml(wert || '')}"
                placeholder="${escapeHtml(option.platzhalter || '')}" autocomplete="off" spellcheck="false">`;
        return `<div class="mesh3d-feld" data-feld="${option.schluessel}"><label for="${id}">${escapeHtml(option.titel)}</label>${eingabe}${hinweis}</div>`;
    }

    static lesen(ziel) {
        const aus = {};
        ziel.querySelectorAll('[data-schluessel]').forEach(e => {
            aus[e.dataset.schluessel] = e.dataset.haken !== undefined ? (e.checked ? 'an' : 'aus') : e.value;
        });
        return aus;
    }

    /** Felder, die nur zu einer Wahl gehören („Eigener Name“), ausgrauen. */
    static abhaengigkeiten(ziel, optionen) {
        const werte = Mesh3dfelder.lesen(ziel);
        for (const option of optionen.filter(o => o.nur_wenn)) {
            const aktiv = Object.entries(option.nur_wenn).every(([k, soll]) => werte[k] === soll);
            const feld = ziel.querySelector(`[data-feld="${option.schluessel}"]`);
            const eingabe = ziel.querySelector(`[data-schluessel="${option.schluessel}"]`);
            if (!feld || !eingabe) continue;
            eingabe.disabled = !aktiv;
            feld.classList.toggle('inaktiv', !aktiv);
        }
    }

    /** Alle Felder sperren oder freigeben (während eines Laufs); ausgegraute Abhängige bleiben gesperrt. */
    static sperren(ziel, optionen, gesperrt) {
        ziel.querySelectorAll('[data-schluessel]').forEach(e => { e.disabled = gesperrt; });
        if (!gesperrt) Mesh3dfelder.abhaengigkeiten(ziel, optionen);
    }
}
