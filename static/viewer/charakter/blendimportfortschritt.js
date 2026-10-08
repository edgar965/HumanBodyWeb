/**
 * Blendimportfortschritt — der Lauf eines Blender-Imports im Dialog „Modell importieren" (08.10.2026).
 *
 * Fragt `/api/character/blendimport/<kennung>/zustand/` alle zwei Sekunden: Balken (im Schritt „figur" der Fortschritt
 * des Auftrags „Mesh to 3D", den der Server auf das Band umrechnet), die Schritte mit Haken, die letzte Meldung, ein
 * Fehler im Klartext samt „Ab hier neu" und „Anhalten". Ist er fertig, wird das Modell in die Szene geladen
 * (`fn.addCharacterFromPreset`, derselbe Weg wie „Charakter hinzufügen → Gespeicherte Modelle").
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { fn } from '../gemeinsam/registrierung.js';
import { escapeHtml } from './utils.js';

export class Blendimportfortschritt {

    static TAKT_MS = 2000;
    static TITEL = { export: 'Lesen', umposen: 'Haltung', koerper: 'Körpernetz', figur: 'Genesis-Figur', stuecke: 'Kleider & Haar',
                     haut: 'Haut backen', augen: 'Augen', modell: 'Modell' };

    constructor(feld, kennung, schritte) {
        this.feld = feld;
        this.kennung = kennung;
        this.schritte = schritte;
        this.uhr = null;
        this.geladen = false;
        this.feld.hidden = false;
        this.feld.innerHTML = '<div class="mi-balken"><div></div></div><div class="mi-schritte"></div>'
            + '<div class="mi-detail dialoghinweis"></div><div class="mi-knoepfe"></div>';
        this.feld.addEventListener('click', ereignis => this.klick(ereignis));
    }

    adresse(teil) {
        return `/api/character/blendimport/${encodeURIComponent(this.kennung)}/${teil}/`;
    }

    starten() {
        clearInterval(this.uhr);
        this.uhr = setInterval(() => this.abfragen(), Blendimportfortschritt.TAKT_MS);
        return this.abfragen();
    }

    async abfragen() {
        let z;
        try {
            z = await Serverabruf.json(this.adresse('zustand'));
        } catch (fehler) {
            this.zeigen({ status: 'unbekannt', detail: `Zustand nicht lesbar: ${fehler.message}` });
            return;
        }
        this.zeigen(z);
        if (z.status !== 'laeuft' && z.status !== 'neu') clearInterval(this.uhr);
        if (z.status === 'fertig' && !this.geladen) await this.laden(z);
    }

    zeigen(z) {
        const lauf = z.figur_lauf;
        const prozent = Math.max(z.fortschritt || 0, lauf ? lauf.fortschritt : 0);
        this.feld.querySelector('.mi-balken > div').style.width = `${prozent}%`;
        const fertigBis = this.schritte.indexOf(z.schritt);
        this.feld.querySelector('.mi-schritte').innerHTML = this.schritte.map((s, i) => {
            const art = z.status === 'fertig' || i < fertigBis ? 'fertig' : (i === fertigBis ? 'aktiv' : '');
            const dauer = (z.dauer || {})[s];
            return `<span class="${art}">${art === 'fertig' ? '✓ ' : ''}${Blendimportfortschritt.TITEL[s] || s}`
                + `${dauer ? ` (${Math.round(dauer)} s)` : ''}</span>`;
        }).join('');
        const detail = this.feld.querySelector('.mi-detail');
        const text = lauf ? `Mesh to 3D ${lauf.kennung}: ${lauf.schritt || ''} — ${lauf.detail || ''}` : (z.detail || '');
        detail.textContent = z.status === 'gescheitert' ? `Gescheitert — ${z.fehler || 'ohne Grund'}` : text;
        detail.classList.toggle('fehlertext', z.status === 'gescheitert');
        const knoepfe = this.feld.querySelector('.mi-knoepfe');
        if (z.status === 'laeuft' || z.status === 'neu') {
            knoepfe.innerHTML = '<button data-lauf="anhalten">Anhalten</button>';
        } else if (z.status === 'gescheitert' || z.status === 'angehalten') {
            knoepfe.innerHTML = `<button data-lauf="neu" data-ab="${escapeHtml(z.schritt || '')}">`
                + `Ab „${escapeHtml(Blendimportfortschritt.TITEL[z.schritt] || z.schritt || 'Anfang')}" neu</button>`;
        } else {
            knoepfe.innerHTML = '';
        }
    }

    async klick(ereignis) {
        const knopf = ereignis.target.closest('[data-lauf]');
        if (!knopf) return;
        try {
            if (knopf.dataset.lauf === 'anhalten') await Serverabruf.senden(this.adresse('anhalten'), {});
            if (knopf.dataset.lauf === 'neu') {
                await Serverabruf.senden(this.adresse('neu'), { ab: knopf.dataset.ab || null });
                this.starten();
            }
        } catch (fehler) {
            this.feld.querySelector('.mi-detail').textContent = fehler.message;
        }
    }

    async laden(z) {
        this.geladen = true;
        const name = ((z.ergebnis || {}).modell || {}).name;
        const detail = this.feld.querySelector('.mi-detail');
        if (!name) { detail.textContent = 'Fertig, aber kein Modell im Ergebnis'; return; }
        try {
            await fn.addCharacterFromPreset(name);
            detail.textContent = `Fertig — Modell „${name}" geladen, Stücke in der Garderobe.`;
        } catch (fehler) {
            detail.textContent = `Fertig, Modell „${name}" nicht geladen: ${fehler.message}`;
            detail.classList.add('fehlertext');
        }
    }
}
