import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Gesichtsformbuehne } from './gesichtsformbuehne.js';
import { Gesichtsformguete } from './gesichtsformguete.js';
import { Schnittfelder } from './schnittfelder.js';
import { Vorderansicht } from './vorderansicht.js';

/**
 * Gesichtsformseite — die Seite „Gesichtsform" (Kopf-Eigen, 27.09.2026): laden, malen, rechnen, speichern.
 *
 * `POST /api/gesichtsform/profile/` liefert Figur (ohne/mit Kopf-Eigen), Ziel und Güte;
 * `rechnen/` legt den Morph ab und antwortet wie `profile/`; `speichern/` schreibt Stärke und Regler ins
 * Modell (beim Auftrag: dessen Modell). Ohne Ziel aus einem Netz beginnt das Ziel als die Figur selbst.
 * Jede Meldung steht sichtbar unter der Leiste — auch die Fehler des Servers.
 */
export class Gesichtsformseite {

    static ADRESSE = '/api/gesichtsform/';

    static starten(quelle) {
        const seite = new Gesichtsformseite(quelle);
        seite.laden();
        return seite;
    }

    constructor(quelle) {
        this.quelle = quelle.auftrag ? { auftrag: quelle.auftrag } : { modell: quelle.modell };
        this.el = id => document.getElementById(id);
        this.daten = null;
        this.buehne = new Gesichtsformbuehne(this.el('gf-buehne'), this.el('gf-buehnenhinweis'));
        const pinsel = () => parseFloat(this.el('gf-pinsel').value);
        this.schnitte = new Schnittfelder({ waagerecht: this.el('gf-schnitte-waagerecht'),
            senkrecht: this.el('gf-schnitte-senkrecht') }, pinsel, () => this._geaendert());
        this.vorn = new Vorderansicht(this.el('gf-vorn'), () => this._geaendert());
        this.guete = new Gesichtsformguete(this.el('gf-guete'));
        this._leiste();
    }

    _leiste() {
        for (const id of ['gf-waagerecht', 'gf-senkrecht']) {
            this.el(id).innerHTML = [5, 6, 7, 8, 9, 10]
                .map(n => `<option value="${n}"${n === 7 ? ' selected' : ''}>${n}</option>`).join('');
        }
        this.el('gf-pinsel').addEventListener('input', () => {
            this.el('gf-pinsel-wert').textContent = `${this.el('gf-pinsel').value} mm`;
        });
        this.el('gf-neu-messen').addEventListener('click', () => this.laden({ ziel_neu: true }));
        this.el('gf-ziel-figur').addEventListener('click', () => {
            this.schnitte.zuruecksetzen();
            this.vorn.zuruecksetzen();
            this._geaendert();
        });
        this.el('gf-rechnen').addEventListener('click', () => this.rechnen());
        this.el('gf-speichern').addEventListener('click', () => this.speichern());
        this.el('gf-wert').addEventListener('input', () => this._wertText());
        this.el('gf-wert').addEventListener('change', () => this._wertSetzen());
        this.el('gf-linien').addEventListener('change', () => this._linien());
        for (const r of document.querySelectorAll('input[name="gf-ansicht"]')) {
            r.addEventListener('change', () => { if (r.checked) this.buehne.ansicht(r.value); });
        }
    }

    _melden(text, fehler = false) {
        const m = this.el('gf-meldung');
        m.textContent = text;
        m.classList.toggle('fehler', fehler);
    }

    _knoepfe(an) {
        for (const id of ['gf-neu-messen', 'gf-rechnen', 'gf-ziel-figur']) this.el(id).disabled = !an;
        this.el('gf-speichern').disabled = !an || !(this.daten && this.daten.vorhanden);
    }

    async _anfrage(pfad, nutzlast, text) {
        this._knoepfe(false);
        this._melden(text);
        const beginn = performance.now();
        try {
            const d = await Serverabruf.senden(Gesichtsformseite.ADRESSE + pfad, {
                ...this.quelle, waagerecht: this.el('gf-waagerecht').value, senkrecht: this.el('gf-senkrecht').value,
                ...nutzlast,
            });
            const sekunden = ((performance.now() - beginn) / 1000).toFixed(1).replace('.', ',');
            this._melden(`${text.replace(' …', '')}: fertig in ${sekunden} s`);
            return d;
        } catch (fehler) {
            this._melden(`Fehler: ${fehler.message}`, true);
            return null;
        } finally {
            this._knoepfe(true);
        }
    }

    async laden(extra = {}) {
        const d = await this._anfrage('profile/', extra, 'Figur und Ziel werden gemessen …');
        if (d) await this._zeigen(d);
    }

    async rechnen() {
        const ziel = { schnitte: this.schnitte.ziel(), punkte: this.vorn.ziel() };
        const d = await this._anfrage('rechnen/', { ziel, zielquelle: this.daten?.zielquelle || 'seite' },
            'Kopf-Eigen wird gerechnet …');
        if (d) await this._zeigen(d);
    }

    async speichern() {
        const d = await this._anfrage('speichern/', { wert: parseFloat(this.el('gf-wert').value) }, 'Speichern …');
        if (d) this._melden(`${d.regler} = ${d.wert.toFixed(2)} in Modell „${d.modell}" gespeichert.`);
    }

    async _zeigen(d) {
        this.daten = d;
        this.el('gf-titel').textContent = `· ${d.titel}`;
        this.el('gf-waagerecht').value = String(d.lagen.waagerecht.length);
        this.el('gf-senkrecht').value = String(d.lagen.senkrecht.length);
        this.el('gf-wert').value = String(d.vorhanden ? d.wert : 1);
        this._wertText();
        this.schnitte.setzen(d, d.ziel);
        this.vorn.setzen(d, d.ziel);
        this.guete.zeigen(d.guete, d.max_mm);
        this._knoepfe(true);
        const quelle = { netz: 'aus dem Netz des Auftrags', gespeichert: 'zuletzt gerechnet' }[d.zielquelle]
            || 'noch keins — die Figur selbst, zum Malen';
        this._melden(`${this.el('gf-meldung').textContent} · Ziel: ${quelle}`);
        this._linien();
        try {
            await this.buehne.figur(d);
        } catch (fehler) {
            this._melden(`Figur nicht gebaut: ${fehler.message}`, true);
        }
    }

    _linien() {
        if (!this.daten) return;
        const figur = this.daten.ergebnis || this.daten.ist;
        this.buehne.schnittlinien(figur, this.schnitte.ziel(), this.el('gf-linien').checked);
    }

    _geaendert() { this._linien(); }

    _wertText() {
        this.el('gf-wert-text').textContent = parseFloat(this.el('gf-wert').value).toFixed(2).replace('.', ',');
    }

    async _wertSetzen() {
        if (!this.daten || !this.daten.vorhanden) return;
        await this.buehne.wert(this.daten.regler, parseFloat(this.el('gf-wert').value));
    }
}
