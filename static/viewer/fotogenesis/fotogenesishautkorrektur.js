/**
 * Fotogenesishautkorrektur — die Haut-Korrekturen aus „Charakter" (Eigenheiten, Gleichmäßigkeit, Symmetrie, Schatten aufhellen, Retusche, Muttermale behalten) unter dem Feld
 * Genesis-Ergebnis der Foto-Genesis-Jobseite (20.11.2026, Edgar: „Du solltest die Haut Regler aus "Charakter" auf die Jobseite einbauen … die sind nicht da").
 *
 * Derselbe Block wie im Popup „Material · Haut" (`Genesis9hautausgleichregler`) an der Figur des Felds (`Genesis9Modell`, `Fotogenesistestfigur`): jeder Zug rechnet auf dem Server
 * neue Hautbilder aus den Kacheln des Tests (`Genesis9hautausgleich`, Quelle `TESTKACHEL`) und zeigt sie sofort. Nach dem Loslassen werden die Werte am Test abgelegt
 * (`Meshgenesistesthautkorrektur`); die Figur des Tests trägt sie danach überall, wo sie gebaut wird (Abspielleiste, Export, Testseite), beim nächsten Laden.
 * „Haut angleichen" zeichnet, solange seine Regler stehen, eigene Bilder darüber (`Fotogenesishautangleich._tauschen`).
 */
import { Genesis9hautausgleich } from '../gemeinsam/genesis9hautausgleich.js';
import { Genesis9hautausgleichregler } from '../gemeinsam/genesis9hautausgleichregler.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Fotogenesishautkorrektur {
    static WARTEN_MS = 250;
    static VERSUCHE = 240;

    /**
     * @param {HTMLElement|null} element `#fotogenesis-hautkorrektur`
     * @param {() => ({bereit?: Promise, modell: () => object|null, korrekturadresse: () => string|null}|null|undefined)} ort das Feld der Figur, gefragt, wenn es gebraucht wird
     */
    static binden(element, ort) {
        return element ? new Fotogenesishautkorrektur(element, ort) : null;
    }

    constructor(element, ort) {
        this.element = element;
        this.ort = ort;
        this.meldung = element.querySelector('[data-meldung]');
        this.flaeche = element.querySelector('[data-regler]');
        this.bereit = this._aufbauen();
    }

    _sagen(text) {
        this.meldung.textContent = text;
    }

    /** Das Feld gibt es erst, wenn die Seite steht (`Fotogenesisseite.aufbauen`), die Figur erst nach ihrem Bau. */
    async _ort() {
        for (let i = 0; i < Fotogenesishautkorrektur.VERSUCHE; i++) {
            const o = this.ort();
            if (o) return o;
            await new Promise(fertig => setTimeout(fertig, Fotogenesishautkorrektur.WARTEN_MS));
        }
        return null;
    }

    async _aufbauen() {
        const o = await this._ort();
        await o?.bereit;
        const modell = o?.modell(), adresse = o?.korrekturadresse();
        if (!modell || !adresse) {
            this._sagen('Keine Genesis-Figur des Tests im Feld — keine Korrekturen.');
            return;
        }
        if (!Genesis9hautausgleich.materialien(modell).length) {
            this._sagen('Die Figur trägt keine Hautkacheln des Tests (Schritt „Haut“ nicht gerechnet) — keine Korrekturen.');
            return;
        }
        this.modell = modell;
        this.adresse = adresse;
        this.flaeche.appendChild(Genesis9hautausgleichregler.block(modell, { praefix: 'fotogenesis-hautkorrektur-', geaendert: () => this._speichern(), hinweis: null }));   // Hinweis im Template
        this._sagen(Genesis9hautausgleich.aktiv(modell) ? 'Gespeicherte Korrekturen dieses Jobs.' : '');
    }

    /** Die Werte am Test ablegen (ganze Prozent, nur die von der Vorgabe abweichenden — wie `inst.hautausgleich`). */
    async _speichern() {
        const lauf = (this._lauf || 0) + 1;
        this._lauf = lauf;
        try {
            const antwort = await Serverabruf.senden(this.adresse, { werte: { ...(this.modell.hautausgleich || {}) } });
            if (lauf === this._lauf) this._sagen(Object.keys(antwort.werte || {}).length ? 'Gespeichert.' : 'Gespeichert: alle Korrekturen auf Standard.');
        } catch (fehler) {
            if (lauf === this._lauf) this._sagen(`Nicht gespeichert: ${fehler.message}`);
        }
    }
}
