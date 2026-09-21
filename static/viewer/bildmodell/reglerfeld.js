import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Reglerfeld — Genesis-Regler direkt, „wie die Morph-Slider bei Genesis" (Ebene 3).
 *
 * Konzept `Docu/konzepte/2026-09-20_modell-aus-bildern-regler-und-textur.md`, 3.3
 * (Edgar, 21.09.2026: „ich brauche mehr Regler in diesem Prozess, anhand der paar
 * Pfeile kann man eine Figur nicht nachbauen"): Der Fit stellt 448 Regler, die
 * Seite zeigte nur die aktiven als Zahl. Jetzt: ALLE Formregler des Reglerplans
 * (`/api/character/genesis9-figur/regler/`, Bereiche Figur · Körper · Kopf · Mimik
 * · Hals … Füße), je Regler Schieber + Zahl, der Fit-Wert als graue Marke, ein
 * Schloss (= beim nächsten Start ab „Anpassung" festhalten — `festgehalten()`
 * wie bisher), „am Anschlag" rot, Suchfeld, „Zurück auf Fit" je Regler und je
 * Gruppe. Jeder Zug baut die Figur oben LIVE neu (`ansicht.reglerSetzen`).
 * Eigene Werte überleben einen Neuladen der Seite (`localStorage` je Auftrag)
 * — der Lauf selbst schreibt sie erst, wenn sie festgehalten mitgehen.
 */
export class Reglerfeld {

    static ADRESSE = '/api/character/genesis9-figur/regler/';
    static _plan = null;
    static MERKER = 'bildmodell.reglerfeld.';
    static NUR_FORM = ['figur', 'koerper', 'kopf', 'mimik', 'hals', 'brust', 'ruecken',
                       'taille', 'huefte', 'arme', 'haende', 'beine', 'fuesse'];

    constructor(auftrag, ansicht) {
        this.auftrag = auftrag;
        this.ansicht = ansicht;
        this.feld = document.getElementById('reglerliste');
        this.eigen = this._laden();            // {name: wert} — vom Nutzer gestellt
        this.fest = new Set(Object.keys(this.eigen));
        this.fit = {};
        this.zeilen = {};
        this.suche = '';
        this._stand = '';
        if (!this.feld) return;
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    // ------------------------------------------------------------ Werte

    /** Fit-Werte (Anpassung + Restmorph) mit den eigenen darüber — die Stellung der Figur. */
    stellung() {
        return { ...this.fit, ...this.eigen };
    }

    /** Für den Start: festgehaltene Regler `{name: wert}` — der Lauf hält sie ab „Anpassung". */
    festgehalten() {
        const aus = {};
        for (const name of this.fest) aus[name] = this.eigen[name] ?? this.fit[name] ?? 0;
        return aus;
    }

    _schluessel() { return Reglerfeld.MERKER + (this.auftrag.zustand.kennung || this.auftrag.zustand.id || ''); }

    _laden() {
        try { return JSON.parse(localStorage.getItem(this._schluessel()) || '{}') || {}; } catch (_) { return {}; }
    }

    _merken() {
        try { localStorage.setItem(this._schluessel(), JSON.stringify(this.eigen)); } catch (_) { /* privat */ }
    }

    // ------------------------------------------------------------ Zeigen

    async zeigen(z) {
        const a = (z.ergebnis || {}).anpassung;
        this.fit = this.auftrag.stellung();
        const fest = (a || {}).festgehalten || {};
        for (const [k, v] of Object.entries(fest)) if (!(k in this.eigen)) { this.eigen[k] = v; this.fest.add(k); }
        const stand = JSON.stringify([this.fit, Object.keys(this.eigen).length]);
        if (stand === this._stand) return;
        this._stand = stand;
        if (!a || !a.regler) { this.feld.innerHTML = ''; return; }
        const plan = await Reglerfeld.plan();
        this._bauen(plan, a);
        this._nachziehen();
    }

    static async plan() {
        if (!Reglerfeld._plan) {
            try { Reglerfeld._plan = await Serverabruf.json(Reglerfeld.ADRESSE); }
            catch (fehler) { Reglerfeld._plan = { bereiche: [] }; }
        }
        return Reglerfeld._plan;
    }

    _bauen(plan, a) {
        this.feld.innerHTML = '';
        this.zeilen = {};
        const kopf = document.createElement('div');
        kopf.className = 'bildmodell-reglerkopf';
        kopf.innerHTML = '<b>Genesis-Regler</b>';
        const suche = document.createElement('input');
        suche.type = 'search'; suche.placeholder = 'Regler suchen …'; suche.value = this.suche;
        suche.className = 'bildmodell-reglersuche';
        suche.addEventListener('input', () => { this.suche = suche.value.trim().toLowerCase(); this._filtern(); });
        const hinweis = document.createElement('span');
        hinweis.className = 'hb-hinweis';
        hinweis.textContent = 'Schieber = Figur oben sofort · Schloss = beim nächsten Start festhalten · graue Marke = Fit';
        kopf.append(suche, hinweis);
        this.feld.appendChild(kopf);
        const bekannt = new Set();
        for (const bereich of (plan.bereiche || [])) {
            if (!Reglerfeld.NUR_FORM.includes(bereich.schluessel) && !String(bereich.schluessel).startsWith('hb')) continue;
            const regler = (bereich.regler || []).filter(r => r.name);
            if (!regler.length) continue;
            this.feld.appendChild(this._gruppe(bereich.name, regler, a));
            regler.forEach(r => bekannt.add(r.name));
        }
        // Regler des Fits, die im Plan fehlen (Restmorph, ältere Sätze): eigene Gruppe.
        const rest = Object.keys(this.fit).filter(n => !bekannt.has(n)).map(n => ({ name: n, anzeige: n, min: -1, max: 2 }));
        if (rest.length) this.feld.appendChild(this._gruppe('Weitere (Fit)', rest, a));
        this._filtern();
    }

    _gruppe(name, regler, a) {
        const kasten = document.createElement('details');
        kasten.className = 'bildmodell-reglergruppe';
        const aktiv = regler.filter(r => (this.fit[r.name] || 0) !== 0 || r.name in this.eigen).length;
        kasten.open = aktiv > 0;
        const kopf = document.createElement('summary');
        kopf.innerHTML = `${name} <span class="hb-hinweis">(${aktiv} von ${regler.length} gestellt)</span>`;
        const zurueck = document.createElement('button');
        zurueck.type = 'button'; zurueck.className = 'btn btn-sm btn-secondary'; zurueck.textContent = 'Zurück auf Fit';
        zurueck.title = 'Alle eigenen Werte dieser Gruppe verwerfen';
        zurueck.addEventListener('click', e => { e.preventDefault(); for (const r of regler) this._zuruecksetzen(r.name, false); this._anwenden(); });
        kopf.appendChild(zurueck);
        kasten.appendChild(kopf);
        for (const r of regler) kasten.appendChild(this._zeile(r));
        return kasten;
    }

    _zeile(r) {
        const zeile = document.createElement('div');
        zeile.className = 'bildmodell-reglerzeile bildmodell-reglerzeile3';
        zeile.dataset.name = r.name;
        zeile.dataset.suche = `${r.anzeige || ''} ${r.name}`.toLowerCase();
        const schloss = document.createElement('input');
        schloss.type = 'checkbox'; schloss.title = 'Beim nächsten Start festhalten'; schloss.checked = this.fest.has(r.name);
        schloss.addEventListener('change', () => {
            if (schloss.checked) { this.fest.add(r.name); if (!(r.name in this.eigen)) this.eigen[r.name] = this.fit[r.name] ?? 0; }
            else this.fest.delete(r.name);
            this._merken();
        });
        const text = document.createElement('span');
        text.className = 'bildmodell-reglername';
        text.textContent = r.anzeige || r.name; text.title = r.name;
        const spur = document.createElement('span');
        spur.className = 'bildmodell-reglerspur';
        const marke = document.createElement('i');
        marke.className = 'bildmodell-reglermarke'; marke.title = 'Fit';
        const schieber = document.createElement('input');
        schieber.type = 'range'; schieber.min = r.min ?? -1; schieber.max = r.max ?? 1; schieber.step = 0.01;
        spur.append(schieber, marke);
        const zahl = document.createElement('input');
        zahl.type = 'number'; zahl.step = '0.01'; zahl.min = schieber.min; zahl.max = schieber.max;
        const setzen = wert => { this.eigen[r.name] = wert; this._merken(); this._nachziehen(); this._anwenden(); };
        schieber.addEventListener('input', () => { zahl.value = schieber.value; setzen(Number(schieber.value)); });
        zahl.addEventListener('change', () => setzen(Number(zahl.value) || 0));
        const zurueck = document.createElement('button');
        zurueck.type = 'button'; zurueck.className = 'bildmodell-reglerzurueck'; zurueck.textContent = '↺'; zurueck.title = 'Zurück auf den Fit-Wert';
        zurueck.addEventListener('click', () => { this._zuruecksetzen(r.name, true); this._anwenden(); });
        zeile.append(schloss, text, spur, zahl, zurueck);
        this.zeilen[r.name] = { zeile, schloss, schieber, zahl, marke, r };
        return zeile;
    }

    _zuruecksetzen(name, nachziehen) {
        delete this.eigen[name];
        this.fest.delete(name);
        this._merken();
        if (nachziehen) this._nachziehen();
    }

    _nachziehen() {
        for (const [name, e] of Object.entries(this.zeilen)) {
            const fit = this.fit[name] ?? 0;
            const wert = this.eigen[name] ?? fit;
            e.schieber.value = String(wert); e.zahl.value = String(Math.round(wert * 100) / 100);
            const min = Number(e.schieber.min), max = Number(e.schieber.max);
            e.marke.style.left = `${Math.max(0, Math.min(1, (fit - min) / (max - min || 1))) * 100}%`;
            e.zeile.classList.toggle('eigen', name in this.eigen);
            e.zeile.classList.toggle('anschlag', wert !== 0 && (wert <= min + 1e-6 || wert >= max - 1e-6));
            e.zeile.classList.toggle('aktiv', wert !== 0);
            e.schloss.checked = this.fest.has(name);
        }
    }

    _filtern() {
        for (const e of Object.values(this.zeilen)) {
            e.zeile.classList.toggle('hb-versteckt', !!this.suche && !e.zeile.dataset.suche.includes(this.suche));
        }
    }

    /** Die Figur oben mit der Stellung neu bauen (entprellt in `Ansicht3d.reglerSetzen`). */
    _anwenden() {
        this._nachziehen();
        this.ansicht?.reglerSetzen?.(this.stellung());
    }
}
