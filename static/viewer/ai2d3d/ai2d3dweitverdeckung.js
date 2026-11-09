/**
 * Ai2d3dweitverdeckung — Knopf „Haut unter weiten Stücken“ unter dem Feld Genesis-Ergebnis (08.11.2026, Edgar: „diese extra regel möchte ich per UI auf der Jobseite laufen lassen können?
 * Unter dem Genesis View?“).
 *
 * Ein Schritt nach der Kette: Der Server rechnet im eigenen Prozess unter der GPU-Sperre (`Ai2d3dweitverdeckung`, `mesh3dai/mesh3dai_kostuem_weitschritt.py`, Regel `Kostuemweitverdeckung`) und
 * schreibt die Hautmasken der Stücke neu. Die Figur liest sie beim Bau (`Ai2d3dtestfigur.verdeckt`): Ist der Lauf fertig, lädt die Seite neu. „Zurücksetzen“ gibt die Masken des Kostümlaufs zurück.
 */
import { Aktionsprotokoll } from '../gemeinsam/aktionsprotokoll.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Ai2d3dweitverdeckung {
    static TAKT_MS = 3000;

    /** @param {HTMLElement|null} element `#ai2d3d-weitverdeckung` */
    static binden(element) {
        return element ? new Ai2d3dweitverdeckung(element) : null;
    }

    constructor(element) {
        this.element = element;
        this.adresse = element.dataset.adresse;
        this.meldung = element.querySelector('[data-meldung]');
        this.rechnenKnopf = element.querySelector('[data-rechnen]');
        this.zuruecksetzenKnopf = element.querySelector('[data-zuruecksetzen]');
        this.lief = false;                  // lief beim letzten Stand ein Lauf? Endet er, lädt die Seite neu
        this.rechnenKnopf.addEventListener('click', () => this._starten('rechnen/'));
        this.zuruecksetzenKnopf.addEventListener('click', () => this._starten('zuruecksetzen/'));
        this._laden();
    }

    _sagen(text) {
        this.meldung.textContent = text;
    }

    async _laden() {
        try {
            this._zeigen(await Serverabruf.json(`${this.adresse}?t=${Date.now()}`));
        } catch (fehler) {
            if (fehler.name === 'AbortError') return;
            this._sagen(`Stand nicht lesbar: ${fehler.message}`);
            if (this.lief) this._planen();
        }
    }

    _planen() {
        clearTimeout(this._uhr);
        this._uhr = setTimeout(() => this._laden(), Ai2d3dweitverdeckung.TAKT_MS);
    }

    async _starten(pfad) {
        this.rechnenKnopf.disabled = this.zuruecksetzenKnopf.disabled = true;
        Aktionsprotokoll.melden('weitverdeckung', pfad);
        try {
            this._zeigen(await Serverabruf.senden(`${this.adresse}${pfad}`, {}));
        } catch (fehler) {
            this._sagen(`Nicht gestartet: ${fehler.message}`);
            this.rechnenKnopf.disabled = this.zuruecksetzenKnopf.disabled = false;
        }
    }

    /** Stand des Servers: {laeuft, zeile, angewandt, befund, sekunden, veraltet, zustand: {art, text}, rechenlauf}. */
    _zeigen(s) {
        if (this.lief && !s.laeuft) {
            if (['gerechnet', 'zurueckgesetzt'].includes(s.zustand?.art)) {
                this._sagen(`${s.zustand.text}. Die Seite lädt neu …`);
                Aktionsprotokoll.melden('weitverdeckung', `fertig: ${s.zustand.text}`);
                location.reload();
                return;
            }
        }
        this.lief = Boolean(s.laeuft);
        this.rechnenKnopf.disabled = this.lief;
        this.zuruecksetzenKnopf.disabled = this.lief;
        this.zuruecksetzenKnopf.hidden = !s.angewandt;
        this.rechnenKnopf.textContent = s.angewandt ? 'Neu rechnen' : 'Rechnen';
        if (this.lief) {
            this._sagen(s.zeile || 'Der Lauf startet …');
            this._planen();
            return;
        }
        const teile = [];
        if (s.angewandt) {
            const stuecke = Object.values(s.befund || {});
            const dazu = stuecke.reduce((summe, b) => summe + (b.dreiecke_dazu || 0), 0);
            teile.push(`Angewandt: ${dazu.toLocaleString('de-DE')} Dreiecke Haut mehr ausgeblendet`
                + (stuecke.length ? ` (${stuecke.map(b => `${b.name || b.art}: ${(b.dreiecke_dazu || 0).toLocaleString('de-DE')}`).join(', ')})` : '')
                + (s.sekunden ? `, gerechnet in ${Math.round(s.sekunden)} s.` : '.'));
        } else if (s.veraltet) {
            teile.push('Das Kostüm wurde seit dem letzten Lauf neu gerechnet, die Regel ist nicht angewandt.');
        } else if (s.zustand?.art === 'fehler') {
            teile.push(`Fehlgeschlagen: ${s.zustand.text}`);
        } else if (s.zustand?.art === 'nichts') {
            teile.push(s.zustand.text);
        } else {
            teile.push('Nicht angewandt: Die Haut folgt den Masken des Kostümlaufs.');
        }
        if (s.rechenlauf) teile.push('Mesh3D-AI rechnet diesen Test gerade, Start erst danach.');
        this._sagen(teile.join(' '));
    }
}
