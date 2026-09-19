/**
 * Testfallansicht — der Knopf „Testcase" über dem 3D-Modell und die Zahlen dazu.
 *
 * Edgar (19.09.2026): „oben, wo das 3D-Modell ist, mit dem erzeugten Modell
 * zuschaltbar (oben mit einem Button ‚Testcase') das Ursula9-Modell, zum
 * Vergleich mit dem, was du erzeugt hast."
 *
 * Ein Auftrag mit `optionen.testfall.figur` (Dashboard: „Testfall") zeigt
 * die Leiste: „Testcase" baut die Referenzfigur einmal (`Genesis9Modell` des
 * Katalogeintrags, mit ihrer Haut) und schaltet zwischen Ergebnis und Referenz
 * um (`Ansicht3d.referenz`); „Bilder aus der Referenz erzeugen" rendert die
 * Fotos (`Testfallbilder`). Unter der Ansicht die Zahlen aus
 * `ergebnis.testfall` (`Bildmodelltestfall`): RMS und Maximum in mm, Höhe
 * beider, die schlechtesten Körperteile, und die 19 Proportionen
 * Referenz / Modell / Differenz.
 */
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Testfallbilder } from './testfallbilder.js';

export class Testfallansicht {

    constructor(auftrag, katalog, ansicht) {
        this.auftrag = auftrag;
        this.katalog = katalog || {};
        this.ansicht = ansicht;
        this.leiste = document.getElementById('testfall');
        this.zahlen = document.getElementById('testfall-zahlen');
        this.referenz = null;
        this.an = false;
        this._stand = null;
        if (!this.leiste) return;
        document.getElementById('testfall-schalter')?.addEventListener('click', () => this.umschalten());
        document.getElementById('testfall-bilder')?.addEventListener('click', () => this.bilderErzeugen());
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    figur() { return ((this.auftrag.zustand.optionen || {}).testfall || {}).figur || ''; }

    anzeige() {
        const f = this.figur();
        return (this.katalog.testfiguren || []).find(t => t.name === f)?.anzeige || f;
    }

    _melden(text) {
        const t = document.getElementById('testfall-text');
        if (t) t.textContent = text;
    }

    // ------------------------------------------------------- Umschalten

    async umschalten() {
        const knopf = document.getElementById('testfall-schalter');
        if (!this.figur() || !this.ansicht?.szene) return;
        if (!this.referenz) {
            knopf.disabled = true;
            this._melden(`Referenz ${this.anzeige()} wird gebaut …`);
            try {
                const neu = new Genesis9Modell('testfall', { figur: this.figur() });
                await neu.bauen();
                this.referenz = neu;
                this.ansicht.szene.add(neu.group);
                this.ansicht.referenz(neu);
            } catch (fehler) {
                this._melden(`Referenz nicht gebaut: ${fehler.message}`);
                knopf.disabled = false;
                return;
            }
            knopf.disabled = false;
        }
        this.an = !this.an;
        knopf.setAttribute('aria-pressed', String(this.an));
        knopf.classList.toggle('btn-primary', this.an);
        knopf.classList.toggle('btn-secondary', !this.an);
        this.ansicht.umschalten(this.an);
        this._melden(this.an ? `Referenz: ${this.anzeige()} (Bibliothek)` : `Ergebnis: ${this.auftrag.zustand.name}`);
    }

    async bilderErzeugen() {
        const knopf = document.getElementById('testfall-bilder');
        if (!this.figur()) return;
        knopf.disabled = true;
        try {
            await new Testfallbilder(this.auftrag).erzeugen(this.figur(), t => this._melden(t));
        } catch (fehler) {
            this._melden(`Bilder nicht erzeugt: ${fehler.message}`);
        } finally {
            knopf.disabled = false;
        }
    }

    // ------------------------------------------------------------ Zahlen

    zeigen(z) {
        const figur = this.figur();
        this.leiste.classList.toggle('hb-versteckt', !figur);
        if (!figur) { if (this.zahlen) this.zahlen.innerHTML = ''; return; }
        const t = (z.ergebnis || {}).testfall;
        const stand = JSON.stringify([figur, t ? [t.rms_mm, t.flaeche_mm] : null, z.updated_at]);
        if (stand === this._stand) return;
        this._stand = stand;
        if (!this._gemeldet) { this._melden(`Testfall: Referenz ${this.anzeige()}`); this._gemeldet = true; }
        if (!this.zahlen) return;
        if (!t) {
            this.zahlen.innerHTML = '<span class="hb-hinweis">Noch kein Vergleich — er kommt mit dem Schritt „Vorschau".</span>';
            return;
        }
        // Fläche (Punkt → nächstes Dreieck der Referenz) misst die Form; Punkt gegen Punkt zählt
        // auch Punkte, die nur auf der Haut verrutscht sind.
        const teile = Object.entries(t.flaeche_je_teil || t.je_teil || {}).sort((a, b) => b[1] - a[1]).slice(0, 5)
            .map(([k, v]) => `${k} ${v.toFixed(1)}`).join(', ');
        const flaeche = t.flaeche_mm !== undefined
            ? `<b>Fläche RMS ${t.flaeche_mm.toFixed(2)} mm</b>, max ${t.flaeche_max_mm.toFixed(1)} mm; Punkt zu Punkt `
            : '';
        const zeilen = (this.katalog.proportionen || []).map(m => {
            const r = (t.proportionen?.referenz || {})[m.schluessel];
            const mo = (t.proportionen?.modell || {})[m.schluessel];
            const d = (r !== undefined && mo !== undefined) ? (mo - r) : null;
            const klasse = d === null ? '' : (Math.abs(d) <= 0.5 ? 'hb-gut' : (Math.abs(d) <= 1.5 ? '' : 'hb-schlecht'));
            return `<tr><th>${m.name}</th><td>${r?.toFixed(1) ?? '–'}</td><td>${mo?.toFixed(1) ?? '–'}</td>`
                + `<td class="${klasse}">${d === null ? '–' : (d > 0 ? '+' : '') + d.toFixed(1)}</td></tr>`;
        }).join('');
        this.zahlen.innerHTML = `<div class="bildmodell-testfallkopf">`
            + `<strong>Testfall ${t.anzeige}</strong>: Abstand Modell − Referenz über ${t.punkte.toLocaleString('de-DE')} Käfigpunkte `
            + flaeche + `RMS ${t.rms_mm.toFixed(2)} mm, max ${t.max_mm.toFixed(1)} mm · `
            + `Höhe Referenz ${t.hoehe_cm.referenz} cm, Modell ${t.hoehe_cm.modell} cm`
            + (teile ? ` · schlechteste Teile (${t.flaeche_je_teil ? 'Fläche' : 'RMS'} mm): ${teile}` : '') + `</div>`
            + `<details><summary>Proportionen Referenz / Modell / Differenz (cm)</summary>`
            + `<table class="bildmodell-masse doku"><thead><tr><th>Maß</th><th>Referenz</th><th>Modell</th><th>Δ</th></tr></thead>`
            + `<tbody>${zeilen}</tbody></table></details>`;
    }
}
