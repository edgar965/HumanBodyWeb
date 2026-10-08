/**
 * Modellimportdialog — „Datei → Modell importieren…": ein Modell-JSON wie bisher ODER ein Blender-Modell (.blend).
 *
 * Edgar (08.10.2026): „Mach dafür den Import im UI, beim nächsten Mal soll das mit diesen Einstellungen im UI gehen".
 * Die Einstellungen (Ordner oder .blend, Name, Augen, Kachelgrößen, Grundfigur, Stücke) kommen vom Server
 * (`/api/character/blendimport/einstellungen/`, `core/dienste/blendimporteinstellungen.py`) samt den zuletzt benutzten
 * Werten; „Importieren" merkt sie dort. Ein Pfad statt Hochladen, weil die Texturen einer .blend oft NEBEN der Datei
 * liegen (bei „cute girl" nicht gepackt). Den Lauf zeigt `Blendimportfortschritt`.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Blendimportfortschritt } from './blendimportfortschritt.js';
import { escapeHtml } from './utils.js';

export class Modellimportdialog {

    static ID = 'modellimport-dialog';
    static STIL = `
#modellimport-dialog .scene-modal { width: min(760px, 96vw); }
#modellimport-dialog .mi-zeile { display: grid; grid-template-columns: 210px 1fr; gap: 6px 12px; align-items: center;
    margin: 6px 0; }
#modellimport-dialog input, #modellimport-dialog select { width: 100%; padding: 5px 7px; color: var(--text, #e8e8e8);
    background: var(--bg-input, #1d2233); border: 1px solid var(--border, #3a4058); border-radius: 4px;
    color-scheme: dark; }
#modellimport-dialog .scene-modal-body button { padding: 5px 12px; color: var(--text, #e8e8e8);
    background: var(--bg-input, #1d2233); border: 1px solid var(--border, #3a4058); border-radius: 4px; cursor: pointer; }
#modellimport-dialog .mi-hinweis { grid-column: 2; font-size: 0.75rem; color: var(--text-muted, #9aa3b5); }
#modellimport-dialog .mi-abschnitt { margin: 14px 0 6px; font-weight: 600; }
#modellimport-dialog .mi-quelle { min-height: 1.4em; font-size: 0.8rem; }
#modellimport-dialog .mi-balken { height: 10px; background: var(--bg-input, #1d2233); border-radius: 5px;
    overflow: hidden; margin: 8px 0; }
#modellimport-dialog .mi-balken > div { height: 100%; width: 0; background: var(--accent, #e94560);
    transition: width .4s; }
#modellimport-dialog .mi-schritte { display: flex; flex-wrap: wrap; gap: 4px 10px; font-size: 0.78rem; }
#modellimport-dialog .mi-schritte .fertig { color: var(--success, #5cb85c); }
#modellimport-dialog .mi-schritte .aktiv { color: var(--accent, #e94560); font-weight: 600; }`;

    /** Den Dialog öffnen (einmal bauen, danach wiederverwenden). */
    static async oeffnen() {
        const dialog = Modellimportdialog.dialog();
        dialog.classList.add('visible');
        await Modellimportdialog.laden(dialog);
    }

    static dialog() {
        let dialog = document.getElementById(Modellimportdialog.ID);
        if (dialog) return dialog;
        const stil = document.createElement('style');
        stil.textContent = Modellimportdialog.STIL;
        document.head.appendChild(stil);
        dialog = document.createElement('div');
        dialog.className = 'scene-modal-overlay';
        dialog.id = Modellimportdialog.ID;
        dialog.innerHTML = `<div class="scene-modal">
  <div class="scene-modal-header"><h4><i class="fas fa-file-import"></i> Modell importieren</h4>
    <button class="scene-modal-close" data-aktion="schliessen">&times;</button></div>
  <div class="scene-modal-body">
    <div class="mi-abschnitt">Modell-JSON</div>
    <button data-aktion="json">JSON-Datei wählen …</button>
    <div class="mi-abschnitt">Blender-Modell (.blend) → Genesis-Figur mit eigenen Stücken</div>
    <div class="mi-felder"></div>
    <div class="mi-quelle"></div>
    <div class="mi-lauf" hidden></div>
  </div>
  <div class="scene-modal-footer">
    <span class="dialoghinweis mi-meldung"></span>
    <button data-aktion="schliessen">Schließen</button>
    <button class="primary" data-aktion="starten">Importieren</button>
  </div></div>`;
        document.body.appendChild(dialog);
        dialog.addEventListener('click', ereignis => Modellimportdialog.klick(dialog, ereignis));
        dialog.addEventListener('change', () => Modellimportdialog.pruefen(dialog));
        return dialog;
    }

    static async klick(dialog, ereignis) {
        if (ereignis.target === dialog) { dialog.classList.remove('visible'); return; }
        const aktion = ereignis.target.closest('[data-aktion]')?.dataset.aktion;
        if (aktion === 'schliessen') dialog.classList.remove('visible');
        if (aktion === 'json') {
            dialog.classList.remove('visible');
            const { importJsonModell } = await import('./szene_dialoge.js');
            await importJsonModell();
        }
        if (aktion === 'starten') await Modellimportdialog.starten(dialog);
    }

    static meldung(dialog, text, fehler = false) {
        const feld = dialog.querySelector('.mi-meldung');
        feld.textContent = text || '';
        feld.classList.toggle('fehlertext', !!fehler);
    }

    static async laden(dialog) {
        const felder = dialog.querySelector('.mi-felder');
        try {
            const daten = await Serverabruf.json('/api/character/blendimport/einstellungen/');
            felder.innerHTML = daten.optionen.map(o => Modellimportdialog.feld(o, daten.werte[o.schluessel])).join('');
            dialog._schritte = daten.schritte;
            Modellimportdialog.meldung(dialog, '');
            await Modellimportdialog.pruefen(dialog);
        } catch (fehler) {
            Modellimportdialog.meldung(dialog, `Einstellungen nicht geladen: ${fehler.message}`, true);
        }
    }

    static feld(option, wert) {
        const id = `mi-${option.schluessel}`;
        const eingabe = option.art === 'wahl'
            ? `<select id="${id}" data-schluessel="${option.schluessel}">${option.werte.map(w =>
                `<option value="${escapeHtml(w.wert)}"${w.wert === wert ? ' selected' : ''}>${escapeHtml(w.text)}</option>`
            ).join('')}</select>`
            : `<input id="${id}" data-schluessel="${option.schluessel}" type="text" value="${escapeHtml(wert || '')}"
                 placeholder="A:\\…\\Ordner oder Datei.blend" autocomplete="off">`;
        const hinweis = option.hinweis ? `<div class="mi-hinweis">${escapeHtml(option.hinweis)}</div>` : '';
        return `<div class="mi-zeile"><label for="${id}">${escapeHtml(option.titel)}</label>${eingabe}${hinweis}</div>`;
    }

    static werte(dialog) {
        const aus = {};
        dialog.querySelectorAll('[data-schluessel]').forEach(e => { aus[e.dataset.schluessel] = e.value; });
        return aus;
    }

    /** Welche .blend gelesen wird und wie die Figur heißt — sichtbar, bevor etwas rechnet. */
    static async pruefen(dialog) {
        const feld = dialog.querySelector('.mi-quelle');
        const werte = Modellimportdialog.werte(dialog);
        if (!werte.pfad) { feld.textContent = 'Ordner oder .blend angeben.'; return null; }
        try {
            const q = await Serverabruf.senden('/api/character/blendimport/pruefen/', werte);
            const andere = q.kandidaten.slice(1).map(k => escapeHtml(k.datei)).join(', ');
            feld.innerHTML = `Liest <b>${escapeHtml(q.kandidaten[0].datei)}</b> (${q.kandidaten[0].mb} MB) — Figur `
                + `„<b>${escapeHtml(q.name)}</b>"${andere ? ` · nicht gelesen: ${andere}` : ''}`;
            feld.classList.remove('fehlertext');
            return q;
        } catch (fehler) {
            feld.textContent = fehler.message;
            feld.classList.add('fehlertext');
            return null;
        }
    }

    static async starten(dialog) {
        if (!(await Modellimportdialog.pruefen(dialog))) {
            Modellimportdialog.meldung(dialog, 'Pfad prüfen', true);
            return;
        }
        try {
            const antwort = await Serverabruf.senden('/api/character/blendimport/starten/',
                                                     { werte: Modellimportdialog.werte(dialog) });
            Modellimportdialog.meldung(dialog, `Import ${antwort.kennung} läuft — Einstellungen gemerkt.`);
            new Blendimportfortschritt(dialog.querySelector('.mi-lauf'), antwort.kennung, dialog._schritte || []).starten();
        } catch (fehler) {
            Modellimportdialog.meldung(dialog, `Nicht gestartet: ${fehler.message}`, true);
        }
    }
}
