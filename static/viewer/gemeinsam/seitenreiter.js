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
 */
export class Seitenreiter {

    /**
     * @param {HTMLElement|null} leiste die Leiste mit den Knöpfen
     * @param {string} merkschluessel localStorage-Schlüssel für den zuletzt gewählten Reiter
     */
    static binden(leiste, merkschluessel) {
        if (!leiste) return null;
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
        try { gemerkt = localStorage.getItem(this.merkschluessel); } catch { gemerkt = null; }
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
        try { localStorage.setItem(this.merkschluessel, name); } catch { /* ohne Speicher: nur diese Sitzung */ }
        history.replaceState(null, '', `${location.pathname}${location.search}#${name}`);
    }
}
