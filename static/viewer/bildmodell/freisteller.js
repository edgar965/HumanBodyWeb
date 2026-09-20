import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Dialoggroesse } from './dialoggroesse.js';

/**
 * Freisteller — „Hintergrund weg" an jeder Bildzeile und Bildkachel (20.09.2026).
 *
 * Edgar: „mach einen Button zum Entfernen des Hintergrunds für die Bilder, mit
 * Regler und Preview-Fenster, Speichern des neuen Bildes. Das neue Bild soll an
 * ALLEN Stellen, wo es vorkommt, ersetzt werden (Textur, Hauptbild usw.)."
 *
 * Ein `<dialog>` (`bildmodell_freisteller_dialog.html`, EINES je Seite): links
 * das Bild, rechts die Vorschau vom Server (`freisteller/<datei>/vorschau/`,
 * Maske aus rembg beim ersten Aufruf, ~6 s; danach je Reglerzug ~0,2 s), darunter
 * die Regler Schwelle / Weichzeichnen / Rand / Hintergrund. „Speichern" schreibt
 * das Bild über den Ausschnitt (derselbe Name — Textur, GVHMR, FLAME, Fotolinien
 * lesen ihn), „Zurücksetzen" holt das Bild von vorher. Nach beidem tauscht die
 * Seite alle Bilder dieses Ausschnitts (`dateiAdresse` hängt `freisteller.stand` an).
 */
export class Freisteller {

    static MERKER = 'bildmodell.freisteller.groesse';
    static WARTEN_MS = 250;
    static VORGABE = { schwelle: 50, weich: 2, rand: 0, hintergrund: 'weiss' };

    constructor(auftrag) {
        this.auftrag = auftrag;
        this.dialog = document.getElementById('freisteller-dialog');
        this.datei = null;
        this._timer = null;
        this._lauf = 0;
        if (!this.dialog) return;
        this.felder = {};
        for (const e of this.dialog.querySelectorAll('[data-feld]')) this.felder[e.dataset.feld] = e;
        for (const k of this.dialog.querySelectorAll('[data-tat="schliessen"]')) k.addEventListener('click', () => this.schliessen());
        this.dialog.querySelector('[data-tat="speichern"]')?.addEventListener('click', () => this.speichern());
        this.dialog.querySelector('[data-tat="zurueck"]')?.addEventListener('click', () => this.zuruecksetzen());
        for (const r of this.dialog.querySelectorAll('[data-regler]')) {
            r.addEventListener('input', () => { this._werteZeigen(); this._vorschauSpaeter(); });
        }
        Dialoggroesse.merken(this.dialog, Freisteller.MERKER);
    }

    /** Der Knopf für den Eintrag `b` — keiner für ein Drehvideo. */
    element(b) {
        if (b.video) return null;
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-sm ' + (b.freisteller ? 'btn-secondary' : 'btn-primary');
        knopf.innerHTML = '<i class="fas fa-eraser"></i> Hintergrund';
        knopf.title = b.freisteller
            ? 'Hintergrund entfernt — Fenster öffnen: Regler, neu speichern oder zurücksetzen'
            : 'Hintergrund entfernen: Vorschau mit Reglern, dann speichern — das Bild wird überall ersetzt';
        knopf.disabled = (this.auftrag.zustand || {}).status === 'laeuft';
        knopf.addEventListener('click', () => this.oeffnen(b.datei));
        return knopf;
    }

    _eintrag() { return ((this.auftrag.zustand || {}).bilder || []).find(b => b.datei === this.datei) || null; }

    regler() {
        const aus = { ...Freisteller.VORGABE };
        for (const r of this.dialog.querySelectorAll('[data-regler]')) {
            aus[r.dataset.regler] = r.type === 'range' ? Number(r.value) : r.value;
        }
        return aus;
    }

    _reglerSetzen(werte) {
        for (const r of this.dialog.querySelectorAll('[data-regler]')) {
            if (werte[r.dataset.regler] !== undefined) r.value = String(werte[r.dataset.regler]);
        }
        this._werteZeigen();
    }

    _werteZeigen() {
        for (const r of this.dialog.querySelectorAll('[data-regler]')) {
            const w = this.dialog.querySelector(`[data-wert="${r.dataset.regler}"]`);
            if (w) w.textContent = r.type === 'range' ? `${r.value}${r.dataset.einheit || ''}` : '';
        }
    }

    oeffnen(datei) {
        if (!this.dialog) { window.alert('Kein Freisteller-Fenster auf dieser Seite.'); return; }
        this.datei = datei;
        const e = this._eintrag() || {};
        this.felder.datei.textContent = datei;
        this.felder.foto.src = this.auftrag.dateiAdresse('zuschnitt', datei);
        this.felder.vorschau.removeAttribute('src');
        this._reglerSetzen((e.freisteller || {}).regler || Freisteller.VORGABE);
        const zurueck = this.dialog.querySelector('[data-tat="zurueck"]');
        if (zurueck) zurueck.disabled = !(e.freisteller && e.freisteller.vorher);
        if (!this.dialog.open) this.dialog.showModal();
        this._melden('Maske wird gerechnet (rembg, beim ersten Mal einige Sekunden) …');
        this._vorschau();
    }

    schliessen() { if (this.dialog?.open) this.dialog.close(); }

    _melden(t) { if (this.felder.text) this.felder.text.textContent = t; }

    _vorschauSpaeter() {
        if (this._timer) clearTimeout(this._timer);
        this._timer = setTimeout(() => this._vorschau(), Freisteller.WARTEN_MS);
    }

    async _vorschau() {
        const lauf = ++this._lauf;
        try {
            const antwort = await fetch(this.auftrag.adresse(`freisteller/${encodeURIComponent(this.datei)}/vorschau/`), {
                method: 'POST', headers: { 'Content-Type': 'application/json', ...Serverabruf._csrfKopf() },
                body: JSON.stringify(this.regler()), credentials: 'same-origin',
            });
            if (lauf !== this._lauf) return;
            if (!antwort.ok) {
                let text = `${antwort.status}`;
                try { text = (await antwort.json()).error || text; } catch (_) { /* kein JSON */ }
                throw new Error(text);
            }
            const blob = await antwort.blob();
            if (lauf !== this._lauf) return;
            if (this.felder.vorschau.src && this.felder.vorschau.src.startsWith('blob:')) URL.revokeObjectURL(this.felder.vorschau.src);
            this.felder.vorschau.src = URL.createObjectURL(blob);
            this._melden('Vorschau — Regler ziehen, dann „Speichern"');
        } catch (fehler) {
            if (lauf === this._lauf) this._melden(`Vorschau nicht möglich: ${fehler.message}`);
        }
    }

    async speichern() {
        this._melden('Speichern — Bild in voller Größe, Hautton neu messen …');
        try {
            await this._senden('speichern/', this.regler());
            this._melden('Gespeichert — das Bild ist überall ersetzt (Schätzungen dazu fallen weg, der nächste Lauf rechnet sie neu).');
            const zurueck = this.dialog.querySelector('[data-tat="zurueck"]');
            if (zurueck) zurueck.disabled = false;
            this.felder.foto.src = this.auftrag.dateiAdresse('zuschnitt', this.datei);
        } catch (fehler) {
            this._melden(`Nicht gespeichert: ${fehler.message}`);
        }
    }

    async zuruecksetzen() {
        if (!window.confirm('Das Bild von vor dem Freistellen zurückholen?')) return;
        try {
            await this._senden('zuruecksetzen/', {});
            this._melden('Zurückgesetzt — das Bild von vorher ist wieder überall.');
            this.felder.foto.src = this.auftrag.dateiAdresse('zuschnitt', this.datei);
            this._vorschau();
        } catch (fehler) {
            this._melden(`Nicht zurückgesetzt: ${fehler.message}`);
        }
    }

    async _senden(pfad, rumpf) {
        const antwort = await Serverabruf.senden(this.auftrag.adresse(`freisteller/${encodeURIComponent(this.datei)}/${pfad}`), rumpf);
        if (antwort.error) throw new Error(antwort.error);
        this.auftrag.eintragUebernehmen(antwort);
        return antwort;
    }
}
