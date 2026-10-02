/**
 * Architektur2d3dreiter — die Reiter der Seite Hilfe → Architektur → 2D3D („Ablauf und Klassen", „Workflow").
 *
 * Beide Reiter stehen im HTML (`data-reiter="ablauf"`, `data-reiter="workflow"`); ohne dieses Skript sind sie
 * untereinander sichtbar, nichts fehlt. Das Skript blendet den jeweils anderen aus. Gemerkt wird der Reiter in der
 * Adresse (`#workflow`), damit ein Verweis auf ihn funktioniert — und ein Verweis auf eine Klassenkarte oder einen Baum
 * (`#k-Engine2d3dKleidernetz`, `#baum-netz`) öffnet den Reiter, in dem das Ziel steht.
 */
export class Architektur2d3dreiter {
    static aufbauen() {
        return new Architektur2d3dreiter(document.querySelector('[data-reiter-seite]')).aufbauen();
    }

    constructor(seite) {
        this.seite = seite;
        this.knoepfe = seite ? [...seite.querySelectorAll('[data-aktion="reiter"]')] : [];
        this.flaechen = seite ? [...seite.querySelectorAll('[data-reiter]')] : [];
    }

    aufbauen() {
        if (!this.seite || !this.flaechen.length) {
            console.error('Architektur2d3dreiter: keine Reiterseite gefunden — alle Abschnitte bleiben sichtbar');
            return this;
        }
        this.knoepfe.forEach(knopf => knopf.addEventListener('click', () => this.zeigen(knopf.dataset.ziel, true)));
        window.addEventListener('hashchange', () => this.ausAdresse());
        this.ausAdresse();
        return this;
    }

    /** Der Reiter, den die Adresse meint: sein Name selbst oder der Reiter, in dem das Ziel des Ankers steht. */
    reiterVon(hash) {
        const name = decodeURIComponent((hash || '').replace(/^#/, ''));
        if (this.flaechen.some(f => f.dataset.reiter === name)) return {reiter: name, ziel: null};
        const ziel = name ? document.getElementById(name) : null;
        const flaeche = ziel ? ziel.closest('[data-reiter]') : null;
        return {reiter: flaeche ? flaeche.dataset.reiter : this.flaechen[0].dataset.reiter, ziel};
    }

    ausAdresse() {
        const {reiter, ziel} = this.reiterVon(window.location.hash);
        this.zeigen(reiter, false);
        if (ziel) ziel.scrollIntoView();
    }

    zeigen(reiter, merken) {
        this.flaechen.forEach(f => { f.hidden = f.dataset.reiter !== reiter; });
        this.knoepfe.forEach(k => k.classList.toggle('active', k.dataset.ziel === reiter));
        if (merken) window.history.replaceState(null, '', '#' + reiter);
    }
}
