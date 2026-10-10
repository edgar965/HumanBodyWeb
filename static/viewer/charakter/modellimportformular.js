/**
 * Modellimportformular — die Felder EINES Quellformats im Dialog „Modell importieren" (.blend, .obj, .fbx).
 *
 * Alle drei Reiter benutzen diese Klasse (Edgar, 10.10.2026: „möglichst gemeinsamen Code mit dem Blender-Import"): derselbe
 * Aufbau der Felder aus dem Katalog des Servers (`/api/character/blendimport/einstellungen/?format=…`), dieselben
 * Abhängigkeiten („Eigener Name" nur bei „Eigener Name"), dieselbe Prüfung der Quelle. Was je Format anders ist, schickt der
 * Server im Katalog (Titel und Hinweis des Pfads, fehlende Fragen) — hier gibt es keine Verzweigung nach dem Format.
 * Die Feld-Kennungen tragen das Format (`mi-obj-augen`): drei Formulare liegen zugleich im Dialog.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { escapeHtml } from './utils.js';

export class Modellimportformular {

    constructor(format, tafel) {
        this.format = format;
        this.tafel = tafel;
        this.felder = tafel.querySelector('.mi-felder');
        this.quelle = tafel.querySelector('.mi-quelle');
        this.optionen = [];
        this.schritte = [];
        this.geladen = false;
        tafel.addEventListener('change', () => { this.abhaengigkeiten(); this.pruefen(); });
    }

    /** Katalog und gemerkte Werte vom Server holen und die Felder bauen. Wirft bei einem Fehler (der Dialog meldet ihn). */
    async laden() {
        const daten = await Serverabruf.json(`/api/character/blendimport/einstellungen/?format=${encodeURIComponent(this.format)}`);
        this.optionen = daten.optionen;
        this.schritte = daten.schritte;
        this.felder.innerHTML = daten.optionen.map(o => this.feld(o, daten.werte[o.schluessel])).join('');
        // Die Zusammenfassung der Haut-Größen steht direkt unter den beiden Haut-Feldern (mit den Feldern neu gebaut).
        const haut = document.createElement('div');
        haut.className = 'mi-haut';
        this.eingabe('browser_px').closest('.mi-zeile').after(haut);
        this.geladen = true;
        this.abhaengigkeiten();
        await this.pruefen();
    }

    eingabe(schluessel) {
        return this.tafel.querySelector(`[data-schluessel="${schluessel}"]`);
    }

    feld(option, wert) {
        const id = `mi-${this.format}-${option.schluessel}`;
        const hinweis = option.hinweis ? `<div class="mi-hinweis">${escapeHtml(option.hinweis)}</div>` : '';
        if (option.art === 'haken') {
            // Ein Kästchen trägt `an`/`aus` — wie eine Auswahl, nur mit zwei Werten (`werte()` liest den Stand).
            return `<div class="mi-zeile"><label for="${id}"><input id="${id}" type="checkbox" data-schluessel="${option.schluessel}"
                 data-haken="an"${wert === 'an' ? ' checked' : ''}> ${escapeHtml(option.titel)}</label>${hinweis}</div>`;
        }
        const eingabe = option.art === 'wahl'
            ? `<select id="${id}" data-schluessel="${option.schluessel}">${option.werte.map(w =>
                `<option value="${escapeHtml(w.wert)}"${w.wert === wert ? ' selected' : ''}>${escapeHtml(w.text)}</option>`
            ).join('')}</select>`
            : `<input id="${id}" data-schluessel="${option.schluessel}" type="text" value="${escapeHtml(wert || '')}"
                 placeholder="${escapeHtml(option.platzhalter || 'A:\\…\\Ordner oder Datei')}" autocomplete="off">`;
        return `<div class="mi-zeile"><label for="${id}">${escapeHtml(option.titel)}</label>${eingabe}${hinweis}</div>`;
    }

    werte() {
        const aus = {};
        this.tafel.querySelectorAll('[data-schluessel]').forEach(e => {
            aus[e.dataset.schluessel] = e.dataset.haken !== undefined ? (e.checked ? 'an' : 'aus') : e.value;
        });
        return aus;
    }

    /** Felder, die nur zu einer Wahl gehören („Eigener Name"), ausgrauen — und die Haut-Größen in einem Satz sagen. */
    abhaengigkeiten() {
        const werte = this.werte();
        for (const option of this.optionen.filter(o => o.nur_wenn)) {
            const aktiv = Object.entries(option.nur_wenn).every(([schluessel, soll]) => werte[schluessel] === soll);
            const eingabe = this.eingabe(option.schluessel);
            eingabe.disabled = !aktiv;
            eingabe.closest('.mi-zeile').classList.toggle('inaktiv', !aktiv);
        }
        const gespeichert = Number(werte.kachel_px);
        const browser = Number(werte.browser_px);
        this.tafel.querySelector('.mi-haut').textContent = browser >= gespeichert
            ? `Haut: Jede Kachel wird mit ${gespeichert} × ${gespeichert} px gespeichert und im Browser immer in dieser Größe geladen.`
            : `Haut: Jede Kachel wird mit ${gespeichert} × ${gespeichert} px gespeichert. Normal lädt der Browser eine Kopie `
              + `mit ${browser} × ${browser} px; Strg+Alt+H zeigt die volle Größe.`;
    }

    /** Welche Datei gelesen wird und wie die Figur heißt — sichtbar, bevor etwas rechnet. Gibt den Steckbrief oder null. */
    async pruefen() {
        const werte = this.werte();
        if (!werte.pfad) { this.quelle.textContent = 'Ordner oder Datei angeben.'; return null; }
        try {
            const q = await Serverabruf.senden('/api/character/blendimport/pruefen/', { ...werte, format: this.format });
            const andere = q.kandidaten.slice(1).map(k => escapeHtml(k.datei)).join(', ');
            this.quelle.innerHTML = `Liest <b>${escapeHtml(q.kandidaten[0].datei)}</b> (${q.kandidaten[0].mb} MB) — Figur `
                + `„<b>${escapeHtml(q.name)}</b>"${andere ? ` · nicht gelesen: ${andere}` : ''}`;
            this.quelle.classList.remove('fehlertext');
            return q;
        } catch (fehler) {
            this.quelle.textContent = fehler.message;
            this.quelle.classList.add('fehlertext');
            return null;
        }
    }
}
