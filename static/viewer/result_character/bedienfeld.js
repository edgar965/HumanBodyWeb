import { fn } from '../gemeinsam/registrierung.js';
import { el, Abschnitt, modellwahlFuellen } from './bauteile.js';
import { Knopfleiste } from './knopfleiste.js';
import { Morphregler } from './morphregler.js';
import { Stoffabschnitt } from './stoffabschnitt.js';

/**
 * Bedienfeld — das Seitenfeld der Ergebnisseite: Knopfleiste, vier Reiter,
 * darin Modellwahl, Morphs und Stoff.
 *
 * Aus ui_panel.js herausgeloest (Umbau 16.08.2026): `buildControlPanel` hatte
 * 211 Zeilen. Die vier Reiter wurden viermal von Hand gebaut (vier Zeilen je
 * Reiter), die zwei leeren Reiterinhalte zweimal — beides jetzt Tabellen.
 */
export class Bedienfeld {

    /** Die Reiter: Kennung und Beschriftung. Der erste ist offen. */
    static REITER = [
        ['eigenschaften', 'Eigenschaften'],
        ['assets', 'Assets'],
        ['animation', 'Animation'],
        ['szene', 'Szene'],
    ];

    /** Reiter ohne eigene Bedienung — Symbol und Text. */
    static HINWEISE = {
        animation: ['fa-running', 'Animation wird vom Video gesteuert'],
        szene: ['fa-lightbulb', 'Szene-Einstellungen'],
    };

    constructor(behaelter, daten) {
        this.behaelter = behaelter;
        this.daten = daten;
        this.leiste = el('div', 'rc-tab-bar');
        this.inhalt = el('div', 'rc-tab-content');
        this.flaechen = new Map();
    }

    bauen() {
        this.behaelter.innerHTML = '';
        Knopfleiste.bauen(this.behaelter);
        for (const [kennung, text] of Bedienfeld.REITER) {
            this.leiste.appendChild(this._reiter(kennung, text));
            this.inhalt.appendChild(this._flaeche(kennung));
        }
        this._eigenschaften();
        this._assets();
        this.behaelter.append(this.leiste, this.inhalt);
        return this;
    }

    _reiter(kennung, text) {
        const reiter = el('div', 'rc-tab'
                          + (kennung === Bedienfeld.REITER[0][0] ? ' active' : ''));
        reiter.textContent = text;
        reiter.dataset.tab = kennung;
        reiter.addEventListener('click', () => this.zeigen(kennung));
        return reiter;
    }

    _flaeche(kennung) {
        const flaeche = el('div', 'rc-tab-pane'
                           + (kennung === Bedienfeld.REITER[0][0] ? ' active' : ''));
        flaeche.id = 'rc-tab-' + kennung;
        const hinweis = Bedienfeld.HINWEISE[kennung];
        if (hinweis) flaeche.appendChild(this._hinweis(...hinweis));
        this.flaechen.set(kennung, flaeche);
        return flaeche;
    }

    _hinweis(symbol, text) {
        const knoten = el('div', 'rc-tab-empty');
        knoten.innerHTML = `<i class="fas ${symbol} rc-tab-empty-icon"></i>${text}`;
        return knoten;
    }

    /** Reiter umschalten — vorher zwei Schleifen mit `remove('active')`. */
    zeigen(kennung) {
        for (const reiter of this.leiste.querySelectorAll('.rc-tab')) {
            reiter.classList.toggle('active', reiter.dataset.tab === kennung);
        }
        for (const [name, flaeche] of this.flaechen) {
            flaeche.classList.toggle('active', name === kennung);
        }
    }

    // ------------------------------------------------------------ Reiterinhalte

    _eigenschaften() {
        const flaeche = this.flaechen.get('eigenschaften');
        const modell = new Abschnitt('Modell', true);
        const wahl = el('select', 'rc-select');
        wahl.id = 'rc-model-preset';
        modell.anhaengen(wahl);
        modellwahlFuellen(wahl, name => fn.reloadForPreset(name));
        flaeche.append(modell.el, new Morphregler(this.daten).bauen());
    }

    _assets() {
        this.flaechen.get('assets').appendChild(new Stoffabschnitt().bauen());
    }
}
