import { Seitenreiterwartet } from './seitenreiterwartet.js';

/**
 * Seitenreiter — Reiter einer ganzen Seite: Knöpfe `[role=tab][data-reiter]` in einer
 * Leiste, Felder `[data-reiterfeld]` im Dokument.
 *
 * Erster Nutzer: „Modell aus Dateien" mit den Reitern 3D und Mesh (Edgar, 26.09.2026:
 * „brauch ich einen zweiten Tab. Aktueller Tabname: 3D, neuer Tab: Mesh").
 * Welcher Reiter beim Öffnen gilt: `#<reiter>` in der Adresse (ein Link kann direkt auf
 * „Mesh" zeigen), sonst der zuletzt gewählte (localStorage, je Seite ein Schlüssel),
 * sonst der erste. Ein Wechsel schreibt die Adresse mit `replaceState` — der Zurück-Knopf
 * bleibt beim Seitenwechsel, nicht beim Reiterwechsel.
 *
 * Seit 03.10.2026 meldet ein gewählter Wechsel `reiterwechsel` an der Leiste, und mit `{ wartet: true }` steht bis `reiterfertig`
 * eine Sanduhr. Die Leiste wird von einem kleinen Modul GEBUNDEN, das nur diese Datei lädt — nicht von der Seitenklasse: Die hängt an
 * dreißig Modulen und three.js und ist erst nach deren Laden da; so lange blieben die Reiter tot (Edgar: „nicht anklickbar").
 */
export class Seitenreiter {

    /**
     * @param {HTMLElement|null} leiste die Leiste mit den Knöpfen
     * @param {string|null} merkschluessel localStorage-Schlüssel für den zuletzt gewählten Reiter; `null`: nichts merken (die Seite
     *   öffnet auf dem ersten Reiter, außer die Adresse nennt einen)
     * @param {{wartet?: boolean}} optionen `wartet`: bis die Seite `reiterfertig` meldet, steht eine Sanduhr (`Seitenreiterwartet`);
     *   die Seite hört auf `reiterwechsel` an der Leiste (Ereignis mit `detail.name`)
     */
    static binden(leiste, merkschluessel, { wartet = false } = {}) {
        if (!leiste) return null;
        if (wartet) new Seitenreiterwartet(leiste);
        const reiter = new Seitenreiter(leiste, merkschluessel);
        reiter.zeigen(reiter.anfang());
        leiste.addEventListener('click', e => {
            const knopf = e.target.closest('[role="tab"][data-reiter]');
            if (knopf) reiter.zeigen(knopf.dataset.reiter, true);
        });
        window.addEventListener('hashchange', () => {
            const name = location.hash.slice(1);
            if (reiter.namen().includes(name)) reiter.zeigen(name);
        });
        return reiter;
    }

    constructor(leiste, merkschluessel) {
        this.leiste = leiste;
        this.merkschluessel = merkschluessel;
    }

    namen() {
        return [...this.leiste.querySelectorAll('[role="tab"][data-reiter]')].map(k => k.dataset.reiter);
    }

    anfang() {
        const namen = this.namen();
        const ausAdresse = location.hash.slice(1);
        if (namen.includes(ausAdresse)) return ausAdresse;
        let gemerkt = null;
        if (this.merkschluessel) {
            try { gemerkt = localStorage.getItem(this.merkschluessel); } catch { gemerkt = null; }
        }
        return namen.includes(gemerkt) ? gemerkt : namen[0];
    }

    zeigen(name, gewaehlt = false) {
        for (const knopf of this.leiste.querySelectorAll('[role="tab"][data-reiter]')) {
            knopf.setAttribute('aria-selected', String(knopf.dataset.reiter === name));
        }
        for (const feld of document.querySelectorAll('[data-reiterfeld]')) {
            feld.hidden = feld.dataset.reiterfeld !== name;
        }
        if (!gewaehlt) return;
        if (this.merkschluessel) {
            try { localStorage.setItem(this.merkschluessel, name); } catch { /* ohne Speicher: nur diese Sitzung */ }
        }
        history.replaceState(null, '', `${location.pathname}${location.search}#${name}`);
        this.leiste.dispatchEvent(new CustomEvent('reiterwechsel', { detail: { name } }));
    }
}
