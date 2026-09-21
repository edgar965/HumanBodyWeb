import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Dialoggroesse } from './dialoggroesse.js';
import { Freistellerpinsel } from './freistellerpinsel.js';
import { Freistellerzoom } from './freistellerzoom.js';
import { Freistellervorschau } from './freistellervorschau.js';

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
 *
 * Seit 21.09.2026 dazu (Edgar: „mehr automatische, halbautomatische und manuelle
 * Möglichkeiten zur Korrektur"): Modellwahl (rembg-Sitzungen, SAM mit Klickpunkten,
 * Weiß-Key), Matting, GrabCut-Verfeinerung und Pinselstriche auf dem Foto links
 * (`Freistellerpinsel`) — alles Teil der Regler, gespeichert am Eintrag, beim Öffnen zurück.
 */
export class Freisteller {

    static MERKER = 'bildmodell.freisteller.groesse';
    static WARTEN_MS = 250;
    static VORGABE = { schwelle: 50, weich: 2, rand: 0, hintergrund: 'weiss',
                       modell: 'u2net_human_seg', matting: false, verfeinern: '', striche: [], punkte: [],
                       toleranz: 20, positiv: false };
    /** Modelle, die rembg beim ersten Mal lädt — die Vorschau dauert dann Minuten, nicht Sekunden. */
    static LANGSAM = { 'isnet-general-use': '170 MB', 'birefnet-portrait': '900 MB', 'birefnet-general': '900 MB',
                       'bria-rmbg': '170 MB', 'sam': '400 MB' };

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
        // Positivliste (Edgar, 21.09.2026: „halbautomatisches Tool anhand der Positiv-Liste" — „WO IST DIE
        // POSITIVSCHWELLE??" — „soll NUR außerhalb der Figur gelten"): eigener Block mit Haken
        // (Regler `positiv`); die Positivschwelle schaltet beim Ziehen ein. Der Kern (erodiertes Innere
        // der Maske + „Pinsel/Punkt Person") bleibt ganz; außerhalb bleibt nur anhängender Hautton.
        const positiv = this.dialog.querySelector('[data-regler="positiv"]');
        positiv?.addEventListener('change', () => this._positivZeigen(true));
        this.dialog.querySelector('[data-regler="toleranz"]')?.addEventListener('input', () => {
            if (positiv && !positiv.checked) { positiv.checked = true; this._positivZeigen(true); }
        });
        // Pinsel und Klickpunkte auf dem Foto links; jeder Strich holt die Vorschau neu.
        this.pinsel = new Freistellerpinsel(this.felder.leinwand, this.felder.foto, () => { this._knoepfeSchalten(); this._vorschauSpaeter(); });
        for (const r of this.dialog.querySelectorAll('input[name="freisteller-werkzeug"]')) {
            r.addEventListener('change', () => { if (r.checked) { this.pinsel.werkzeug = r.value; this.pinsel.zeichnen(); this._werkzeugHinweis(); } });
        }
        const breite = this.dialog.querySelector('[data-pinsel="breite"]');
        breite?.addEventListener('input', () => { this.pinsel.regler = Number(breite.value); this._breiteZeigen(); this.pinsel.zeichnen(); });
        this.dialog.querySelector('[data-tat="rueckgaengig"]')?.addEventListener('click', () => this.pinsel.rueckgaengig());
        this.dialog.querySelector('[data-tat="wiederholen"]')?.addEventListener('click', () => this.pinsel.wiederholen());
        this.dialog.querySelector('[data-tat="striche-weg"]')?.addEventListener('click', () => this.pinsel.leeren());
        // Strg+Z / Strg+Y im Fenster — nicht in Textfeldern. Regler, Haken und die Werkzeug-Radios
        // sind auch INPUTs und halten nach dem Klick den Fokus; dort MUSS es gehen (Edgar, 21.09.2026:
        // „undo funktioniert nicht im Fenster mit Pinsel usw").
        this.dialog.addEventListener('keydown', e => {
            if (!(e.ctrlKey || e.metaKey)) return;
            if (e.target.matches?.('textarea, select, input:not([type=radio]):not([type=checkbox]):not([type=range]):not([type=button])')) return;
            if (e.key === 'z' || e.key === 'Z') { e.preventDefault(); this.pinsel.rueckgaengig(); }
            if (e.key === 'y' || e.key === 'Y') { e.preventDefault(); this.pinsel.wiederholen(); }
        });
        this.felder.foto?.addEventListener('load', () => this._breiteZeigen());
        // Rad vergrößert, mittlere Taste schiebt — Foto und Vorschau gleich (Edgar, 21.09.2026:
        // „ein Vergrößerungsmöglichkeit … zum genauen Arbeiten").
        this.zoom = new Freistellerzoom([this.felder['buehne-foto'], this.felder['buehne-vorschau']], s => this._zoomZeigen(s));
        // Die Vorschau rechnet der Browser selbst (Edgar: „die slider sollen sofort wirken").
        this.vorschau = new Freistellervorschau(this.felder.vorschau);
        this.dialog.querySelector('[data-tat="einpassen"]')?.addEventListener('click', () => this.zoom.einpassen());
        Dialoggroesse.merken(this.dialog, Freisteller.MERKER);
    }

    /** Rückgängig / Wiederholen / Alle weg nur, wenn es etwas zu tun gibt. */
    _knoepfeSchalten() {
        const p = this.pinsel;
        const setzen = (tat, an) => { const k = this.dialog.querySelector(`[data-tat="${tat}"]`); if (k) k.disabled = !an; };
        setzen('rueckgaengig', p.rueckgaengigMoeglich);
        setzen('wiederholen', p.wiederholenMoeglich);
        setzen('striche-weg', !p.leer);
    }

    /** Block hervorheben, wenn die Positivliste an ist; `gemeldet`: Hinweis und Vorschau dazu. */
    _positivZeigen(gemeldet = false) {
        const an = !!this.dialog.querySelector('[data-regler="positiv"]')?.checked;
        this.dialog.querySelector('.bildmodell-freistellerpositiv')?.classList.toggle('an', an);
        if (!gemeldet) return;
        if (an) this._melden('Positivliste an: Figur mit „Pinsel Person" markieren (Kopf, Körper) — das bleibt ganz; außerhalb bleibt nur, was Hautton hat und an der Figur hängt. Positivschwelle regelt die Weite.');
        this._vorschauSpaeter();
    }

    _zoomZeigen(s) {
        const w = this.dialog.querySelector('[data-wert="zoom"]');
        if (w) w.textContent = s > 1 ? `${s.toFixed(1).replace('.', ',')}×` : '';
        const k = this.dialog.querySelector('[data-tat="einpassen"]');
        if (k) k.disabled = s <= 1;
    }

    _breiteZeigen() {
        const w = this.dialog.querySelector('[data-wert="breite"]');
        if (w) w.textContent = this.pinsel.breitePx() ? `${this.pinsel.breitePx()} px` : '';
    }

    /** SAM braucht Punkte: wer einen Punkt setzt, bekommt das Modell dazu gestellt. */
    _werkzeugHinweis() {
        const modell = this.dialog.querySelector('[data-regler="modell"]');
        if (this.pinsel.werkzeug.startsWith('punkt-') && modell && modell.value !== 'sam') {
            modell.value = 'sam';
            this._melden('Modell auf „SAM (Klickpunkte)" gestellt — Punkte setzen: grün Person, rot Hintergrund');
        }
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
            aus[r.dataset.regler] = r.type === 'range' ? Number(r.value) : r.type === 'checkbox' ? r.checked : r.value;
        }
        if (this.pinsel) { aus.striche = this.pinsel.striche(); aus.punkte = this.pinsel.punkte(); }
        return aus;
    }

    _reglerSetzen(werte) {
        for (const r of this.dialog.querySelectorAll('[data-regler]')) {
            if (werte[r.dataset.regler] === undefined) continue;
            if (r.type === 'checkbox') r.checked = !!werte[r.dataset.regler];
            else r.value = String(werte[r.dataset.regler]);
        }
        this.pinsel?.setzen(werte.striche || [], werte.punkte || []);
        const ansehen = this.dialog.querySelector('input[name="freisteller-werkzeug"][value=""]');
        if (ansehen) { ansehen.checked = true; this.pinsel.werkzeug = ''; }
        this._knoepfeSchalten();
        this._breiteZeigen();
        this._werteZeigen();
        this._positivZeigen();
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
        this._grundlageWeg();
        this._reglerSetzen((e.freisteller || {}).regler || Freisteller.VORGABE);
        const zurueck = this.dialog.querySelector('[data-tat="zurueck"]');
        if (zurueck) zurueck.disabled = !(e.freisteller && e.freisteller.vorher);
        if (!this.dialog.open) this.dialog.showModal();
        this._melden('Maske wird gerechnet (rembg, beim ersten Mal einige Sekunden) …');
        this.zoom?.einpassen();
        this.pinsel?.passen();
        this._vorschau();
    }

    schliessen() { if (this.dialog?.open) this.dialog.close(); }

    /** Grundlage verwerfen (anderes Bild, Bild neu geschrieben) und die Leinwand leeren. */
    _grundlageWeg() {
        this.vorschau.grundlage = null;
        this._grundlageStand = null;
        const c = this.felder.vorschau;
        if (c && c.getContext) c.getContext('2d').clearRect(0, 0, c.width, c.height);
    }

    _melden(t) { if (this.felder.text) this.felder.text.textContent = t; }

    /** Was den Server braucht (Netz, GrabCut, Positivliste): ändert sich das, kommt die Grundlage neu. */
    _grundlageSchluessel(regler) {
        const serverseitig = regler.verfeinern === 'grabcut' || regler.positiv;
        return JSON.stringify([this.datei, regler.modell, regler.matting, regler.punkte, regler.verfeinern, !!regler.positiv,
                               serverseitig ? regler.striche : null]);
    }

    /** Reglerzug: mit passender Grundlage sofort im Browser zeichnen, sonst (entprellt) die Grundlage holen. */
    _vorschauSpaeter() {
        const regler = this.regler();
        if (this.vorschau.grundlage && this._grundlageSchluessel(regler) === this._grundlageStand) {
            this._zeichnen();
            return;
        }
        if (this._timer) clearTimeout(this._timer);
        this._timer = setTimeout(() => this._vorschau(), Freisteller.WARTEN_MS);
    }

    /** Sofort zeichnen, höchstens einmal je Durchlauf der Ereignisschleife. */
    _zeichnen() {
        if (this._zeichnet) return;
        this._zeichnet = true;
        setTimeout(() => {
            this._zeichnet = false;
            if (this.vorschau.grundlage) this.vorschau.zeichnen(this.regler());
        }, 0);
    }

    /** Grundlage vom Server (Bild, Maske, Abstandskarte), dann zeichnen. true bei Erfolg. */
    async _vorschau() {
        const lauf = ++this._lauf;
        const regler = this.regler();
        const modell = regler.modell;
        if (Freisteller.LANGSAM[modell]) this._melden(`Vorschau — Modell ${modell} (beim ersten Mal lädt rembg ${Freisteller.LANGSAM[modell]}) …`);
        else if (regler.verfeinern) this._melden('Vorschau — GrabCut rechnet …');
        else if (regler.positiv) this._melden('Vorschau — Positivliste wird gerechnet …');
        try {
            const antwort = await fetch(this.auftrag.adresse(`freisteller/${encodeURIComponent(this.datei)}/grundlage/`), {
                method: 'POST', headers: { 'Content-Type': 'application/json', ...Serverabruf._csrfKopf() },
                body: JSON.stringify(regler), credentials: 'same-origin',
            });
            if (lauf !== this._lauf) return false;
            const daten = await antwort.json().catch(() => ({}));
            if (!antwort.ok) throw new Error(daten.error || `${antwort.status}`);
            if (lauf !== this._lauf) return false;
            await this.vorschau.setzen(daten);
            this._grundlageStand = this._grundlageSchluessel(regler);
            this.vorschau.zeichnen(this.regler());
            this._melden('Vorschau — Regler wirken sofort; „Speichern" rechnet in voller Größe');
            return true;
        } catch (fehler) {
            if (lauf === this._lauf) this._melden(`Vorschau nicht möglich: ${fehler.message}`);
            return false;
        }
    }

    async speichern() {
        this._melden('Speichern — Bild in voller Größe, Hautton neu messen …');
        try {
            const eintrag = await this._senden('speichern/', this.regler());
            const zurueck = this.dialog.querySelector('[data-tat="zurueck"]');
            if (zurueck) zurueck.disabled = false;
            // Das gespeicherte Bild ist der neue Ausgangspunkt: Striche und Punkte sind in der
            // Maske, die Regler kommen neutral vom Server zurück, die Vorschau rechnet neu.
            this.felder.foto.src = this.auftrag.dateiAdresse('zuschnitt', this.datei);
            this._grundlageWeg();
            this._reglerSetzen(((eintrag.bild || {}).freisteller || {}).regler || Freisteller.VORGABE);
            this._melden('Gespeichert — Vorschau wird neu gerechnet …');
            if (await this._vorschau()) this._melden('Gespeichert — das Bild ist überall ersetzt; Schätzungen (SMPL, FLAME) bleiben.');
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
            this._grundlageWeg();
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
