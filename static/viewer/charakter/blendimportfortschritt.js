/**
 * Blendimportfortschritt — der Lauf eines Blender-Imports im Dialog „Modell importieren" (08.10.2026).
 *
 * Zeigt den Stand, den `Blendimportzustand` alle zwei Sekunden holt (derselbe, den die Leiste oben neben „HumanBody"
 * zeigt): Balken (im Schritt „figur" der Fortschritt des Auftrags „Mesh to 3D", den der Server auf das Band umrechnet),
 * die Schritte mit Haken, die letzte Meldung, ein Fehler im Klartext samt „Ab hier neu" und „Anhalten". Jeder Stand geht
 * auch an `bei` (der Dialog sperrt damit „Importieren", solange der Import rechnet). Ist er fertig, wird das Modell in
 * die Szene geladen (`fn.addCharacterFromPreset`, derselbe Weg wie „Charakter hinzufügen → Gespeicherte Modelle").
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Blendimportzustand } from './blendimportzustand.js';
import { Importpflege } from './importpflege.js';
import { escapeHtml } from './utils.js';

export class Blendimportfortschritt {

    static TITEL = Blendimportzustand.TITEL;

    constructor(feld, kennung, schritte, bei = null) {
        this.feld = feld;
        this.kennung = kennung;
        this.schritte = schritte;
        this.bei = bei;
        this.geladen = false;
        this.hoerer = ereignis => {
            if (ereignis.detail.kennung === this.kennung) this.aufZustand(ereignis.detail);
        };
        this.klickhoerer = ereignis => this.klick(ereignis);
        this.feld.hidden = false;
        this.feld.innerHTML = '<div class="mi-balken"><div></div></div><div class="mi-schritte"></div>'
            + '<div class="mi-detail dialoghinweis"></div><div class="mi-knoepfe"></div>';
        this.feld.addEventListener('click', this.klickhoerer);
    }

    adresse(teil) {
        return `/api/character/blendimport/${encodeURIComponent(this.kennung)}/${teil}/`;
    }

    starten() {
        document.removeEventListener(Blendimportzustand.EREIGNIS, this.hoerer);
        document.addEventListener(Blendimportzustand.EREIGNIS, this.hoerer);
        return Blendimportzustand.beobachten(this.kennung);
    }

    /** Nicht mehr zuhören (der Dialog zeigt einen anderen Import): weder dem Stand noch den Klicks im Feld. */
    beenden() {
        document.removeEventListener(Blendimportzustand.EREIGNIS, this.hoerer);
        this.feld.removeEventListener('click', this.klickhoerer);
    }

    async aufZustand(z) {
        this.zeigen(z);
        if (this.bei) this.bei(z);
        if (z.status === 'fertig' && !this.geladen) await this.laden(z);
    }

    zeigen(z) {
        this.feld.querySelector('.mi-balken > div').style.width = `${Blendimportzustand.prozent(z)}%`;
        // Die Schritte nennt der Stand selbst (ein .blend-Import hat kein „umwandeln", OBJ/FBX schon); ältere Stände ohne `schritte`
        // zeigen die des Dialogs.
        const schritte = z.schritte || this.schritte;
        const fertigBis = schritte.indexOf(z.schritt);
        this.feld.querySelector('.mi-schritte').innerHTML = schritte.map((s, i) => {
            const art = z.status === 'fertig' || i < fertigBis ? 'fertig' : (i === fertigBis ? 'aktiv' : '');
            const dauer = (z.dauer || {})[s];
            return `<span class="${art}">${art === 'fertig' ? '✓ ' : ''}${Blendimportfortschritt.TITEL[s] || s}`
                + `${dauer ? ` (${Math.round(dauer)} s)` : ''}</span>`;
        }).join('');
        const lauf = z.figur_lauf;
        const detail = this.feld.querySelector('.mi-detail');
        const getrennt = z.verbindung === 'getrennt';
        const text = lauf ? `Mesh to 3D ${lauf.kennung}: ${lauf.schritt || ''} — ${lauf.detail || ''}` : (z.detail || '');
        detail.textContent = getrennt ? z.detail
            : (z.status === 'gescheitert' ? `Gescheitert — ${z.fehler || 'ohne Grund'}` : text);
        detail.classList.toggle('fehlertext', z.status === 'gescheitert' && !getrennt);
        detail.classList.toggle('verbindungstext', getrennt);
        // „Abbrechen" (rechnet noch) und „Löschen" (gescheitert/angehalten) entfernen den Import samt Daten (Edgar, 10.10.2026); „Kopieren"
        // legt den Fehlertext in die Zwischenablage. `this.laeuft` merkt sich, ob die Rückfrage „abbrechen" oder „löschen" sagt.
        const knoepfe = this.feld.querySelector('.mi-knoepfe');
        this.laeuft = Blendimportzustand.laeuft(z);
        this.fehlertext = z.status === 'gescheitert' && !getrennt ? `Import „${z.quelle?.name || this.kennung}" gescheitert: ${z.fehler || 'ohne Grund'}` : '';
        const loeschen = '<button data-lauf="loeschen">'
            + `${this.laeuft ? 'Abbrechen und löschen' : 'Import löschen'}</button>`;
        const kopieren = this.fehlertext ? '<button data-lauf="kopieren">Fehler kopieren</button>' : '';
        if (this.laeuft) {
            knoepfe.innerHTML = `<button data-lauf="anhalten">Anhalten</button>${loeschen}`;
        } else if (z.status === 'gescheitert' || z.status === 'angehalten') {
            knoepfe.innerHTML = `<button data-lauf="neu" data-ab="${escapeHtml(z.schritt || '')}">`
                + `Ab „${escapeHtml(Blendimportfortschritt.TITEL[z.schritt] || z.schritt || 'Anfang')}" neu</button>${loeschen}${kopieren}`;
        } else {
            knoepfe.innerHTML = '';
        }
    }

    async klick(ereignis) {
        const knopf = ereignis.target.closest('[data-lauf]');
        if (!knopf) return;
        try {
            if (knopf.dataset.lauf === 'kopieren') await Importpflege.kopieren(this.fehlertext, knopf);
            if (knopf.dataset.lauf === 'loeschen') {
                // Die Rückfrage mit dem Plan; danach hört niemand mehr auf den Stand (`vorSenden`), und `Importpflege` meldet das Löschen.
                await Importpflege.loeschen(this.kennung, { abbrechen: this.laeuft, vorSenden: () => Blendimportzustand.vergessen() });
            }
            if (knopf.dataset.lauf === 'anhalten') await Serverabruf.senden(this.adresse('anhalten'), {});
            if (knopf.dataset.lauf === 'neu') {
                await Serverabruf.senden(this.adresse('neu'), { ab: knopf.dataset.ab || null });
                this.starten();
            }
        } catch (fehler) {
            this.feld.querySelector('.mi-detail').textContent = fehler.message;
            if (knopf.dataset.lauf === 'loeschen') this.starten();      // nicht gelöscht: der Import besteht, der Stand wird weiter gezeigt
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
