/**
 * Proportionenansicht — die Tabelle der Bilder: Bild, Löschen, Ersetzen, Vorher, Nachher.
 *
 * Edgar (19.09.2026, abends): „Mach endlich eine Tabelle mit Bildern, Spalten:
 * Bild, Button Löschen, Button Ersetzen, Bild vorher, Bild nachher. Ein Bild
 * pro Zeile, Popup auf dem Bild gibt die Maße an."
 *
 * Eine Zeile je Hauptbild des Auftrags (`zustand.fotolinien`, Reihenfolge vom
 * Server: Körper vorn, Seite, hinten, dreiviertel, Kopf): das Foto mit seinen
 * Maßlinien (Klick → Popup mit diesem Bild) und darunter die Typ-Boxen, die
 * Knöpfe Löschen und Ersetzen (`Bildsteller`), dann das Vorher-Bild (das
 * gerenderte Ziel der Ansicht, Linien wie eingestellt, Klick → Popup) und das
 * Nachher-Bild (das Modell mit den gemessenen Werten). Bilder ohne Ansicht der
 * Proportionen (dreiviertel, Kopf von der Seite) haben kein Vorher/Nachher.
 * Lagen und Werte der Linien hält der `Proportionendialog`; Bildhöhe über den
 * Schieber (`localStorage`); „Bild hinzufügen" lädt eine Datei in den Auftrag
 * und lässt sie sichten (die Sichtung ordnet sie ein, die Typ-Box korrigiert).
 */
import { Bildsteller } from './bildsteller.js';
import { Proportionendialog } from './proportionendialog.js';
import { Proportionenlinien } from './proportionenlinien.js';

export class Proportionenansicht {

    static MERKER = 'bildmodell.prop.hoehe';
    static HOEHE = { min: 160, max: 900, vorgabe: 320 };
    static SPALTEN = ['Bild', 'Löschen', 'Ersetzen', 'Bild vorher (Ziel)', 'Bild nachher (Modell)'];
    static ANSICHT = { vorne: 'von vorn', seite: 'von der Seite', hinten: 'von hinten', dreiviertel: 'dreiviertel' };

    constructor(auftrag, katalog) {
        this.auftrag = auftrag;
        this.katalog = katalog || {};
        this.feld = document.getElementById('proportionen');
        if (!this.feld) return;
        this.dialog = new Proportionendialog(auftrag, katalog, () => this.linienZeichnen());
        this.steller = new Bildsteller(auftrag, katalog);
        this._schieber();
        this._hinzufuegen();
        document.getElementById('proportionen-anpassen')?.addEventListener('click', () => this.dialog.oeffnen());
        this._stand = null;
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    /** Die eingestellten Werte (cm je Schlüssel) — gehen mit jedem Start als `optionen.proportionen`. */
    werte() { return this.dialog.werte(); }

    // ------------------------------------------------------------ Kopf

    _schieber() {
        const s = document.getElementById('proportionen-hoehe');
        if (!s) return;
        let gemerkt = null;
        try { gemerkt = Number(localStorage.getItem(Proportionenansicht.MERKER)); } catch (e) { gemerkt = null; }
        const h = Proportionenansicht.HOEHE;
        s.min = h.min; s.max = h.max;
        s.value = gemerkt && gemerkt >= h.min && gemerkt <= h.max ? gemerkt : h.vorgabe;
        this._hoeheSetzen(s.value);
        s.addEventListener('input', () => {
            this._hoeheSetzen(s.value);
            try { localStorage.setItem(Proportionenansicht.MERKER, String(s.value)); } catch (e) { /* ohne Merker */ }
        });
    }

    _hoeheSetzen(px) {
        this.feld.style.setProperty('--prop-hoehe', `${Number(px)}px`);
        const t = document.getElementById('proportionen-hoehe-wert');
        if (t) t.textContent = `${Number(px)} px`;
    }

    /** „Bild hinzufügen" im Kopf: Datei in den Auftrag, die Sichtung ordnet sie ein. */
    _hinzufuegen() {
        const eingabe = document.getElementById('proportionen-dazu');
        eingabe?.addEventListener('change', async () => {
            if (!eingabe.files.length) return;
            try {
                await this.auftrag.bilderHochladen([...eingabe.files]);
                await window.__bildmodell?.bilder?.neueSichten();
            } catch (fehler) { window.alert(fehler.message); }
            eingabe.value = '';
        });
    }

    // --------------------------------------------------------- Tabelle

    zeigen(z) {
        this.dialog.quellenAufbauen();
        const p = (z.ergebnis || {}).proportionen || {};
        const fotos = z.fotolinien || [];
        const stand = JSON.stringify([z.updated_at, Object.keys(p.ansichten || {}), fotos.map(f => [f.datei, f.ansicht, f.px_je_m]),
            (z.bilder || []).map(b => [b.datei, b.kategorie, b.ansicht, b.nutzung, b.gewicht])]);
        if (stand === this._stand) return;
        this._stand = stand;
        this.feld.innerHTML = '';
        const knopf = document.getElementById('proportionen-anpassen');
        if (knopf) knopf.disabled = !Object.keys(this.dialog.quellen).length;
        if (!fotos.length) {
            this.feld.innerHTML = '<p class="hb-hinweis">Noch kein Hauptbild — „Bild hinzufügen" oder Bilder unten als Hauptbild einordnen.</p>';
            return;
        }
        const tabelle = document.createElement('table');
        tabelle.className = 'db-tabelle bildmodell-proptabelle';
        tabelle.innerHTML = `<thead><tr>${Proportionenansicht.SPALTEN.map(s => `<th>${s}</th>`).join('')}</tr></thead>`;
        const rumpf = document.createElement('tbody');
        for (const f of fotos) rumpf.appendChild(this._zeile(f, (p.ansichten || {})[f.ansicht], z));
        tabelle.appendChild(rumpf);
        this.feld.appendChild(tabelle);
        this.linienZeichnen();
    }

    _zeile(f, r, z) {
        const b = (z.bilder || []).find(e => e.datei === f.datei) || { datei: f.datei };
        const tr = document.createElement('tr');
        tr.dataset.datei = f.datei;
        tr.dataset.ansicht = f.ansicht || '';
        // 1. das Foto mit Linien und Typ-Boxen
        const foto = document.createElement('td');
        foto.className = 'bildmodell-propfoto';
        const id = `foto:${f.datei}`;
        const fig = this._figur(id, f.breite, f.hoehe, this.auftrag.dateiAdresse('zuschnitt', f.datei),
            `${b.kategorie === 'kopf' ? 'Kopf' : 'Körper'} ${Proportionenansicht.ANSICHT[b.ansicht] || b.ansicht || ''} · ${f.datei}`,
            this.dialog.quellen[id] ? 'Klick: Maße in diesem Bild ziehen' : 'Keine Maßlinien für diese Ansicht');
        if (this.dialog.quellen[id]) fig.addEventListener('click', e => this.amBild(e, id));
        else fig.classList.add('bildmodell-propohne');
        foto.appendChild(fig);
        if (b.kategorie) foto.appendChild(this.steller.wahlzeile(b));
        tr.appendChild(foto);
        // 2./3. Löschen und Ersetzen
        const loeschen = document.createElement('td');
        loeschen.appendChild(this.steller.loeschenKnopf(`Bild ${b.datei} löschen?`, () => this.auftrag.bildLoeschen(b.datei)));
        const ersetzen = document.createElement('td');
        ersetzen.appendChild(this.steller.ersetzenKnopf(b.quelle || b.datei));
        tr.append(loeschen, ersetzen);
        // 4./5. Vorher (Ziel) und Nachher (Modell) der Ansicht
        for (const wer of ['ziel', 'modell']) {
            const td = document.createElement('td');
            if (r) {
                const src = this.auftrag.dateiAdresse('ergebnis', r.bild[wer]) + `?t=${Date.now()}`;
                const g = this._figur(wer === 'ziel' ? `ziel:${f.ansicht}` : `modell:${f.ansicht}`, r.breite, r.hoehe, src,
                    wer === 'ziel' ? 'Vorher — Ziel, wie eingestellt' : 'Nachher — aus dem Modell',
                    wer === 'ziel' ? 'Klick: Maße im Zielnetz ziehen' : 'Nachher — aus dem Modell');
                g.dataset.wer = wer;
                if (wer === 'ziel') g.addEventListener('click', e => this.amBild(e, `ziel:${f.ansicht}`));
                td.appendChild(g);
            } else {
                td.className = 'hb-hinweis';
                td.textContent = '—';
            }
            tr.appendChild(td);
        }
        return tr;
    }

    _figur(id, breite, hoehe, src, text, titel) {
        const fig = document.createElement('figure');
        fig.className = 'bildmodell-propbild';
        fig.dataset.quelle = id;
        fig.style.aspectRatio = `${breite} / ${hoehe}`;
        fig.title = titel;
        fig.innerHTML = `<img src="${src}" alt="${text}"><svg viewBox="0 0 ${breite} ${hoehe}" class="bildmodell-proplinien"></svg>`
            + `<figcaption>${text}</figcaption>`;
        return fig;
    }

    /** Klick im Bild: auf einer Linie → dieses Maß im Popup, sonst das Popup mit diesem Bild. */
    amBild(e, id) {
        const gruppe = e.target.closest ? e.target.closest('g[data-mass]') : null;
        this.dialog.oeffnen(id, gruppe ? gruppe.dataset.mass : null);
    }

    /** Linien neu zeichnen — beim Anzeigen und nach jeder Eingabe im Popup. */
    linienZeichnen() {
        const p = this.dialog.daten();
        for (const fig of this.feld.querySelectorAll('figure[data-quelle]')) {
            const id = fig.dataset.quelle;
            const svg = fig.querySelector('svg');
            const [, , vb, vh] = svg.getAttribute('viewBox').split(' ').map(Number);
            const bezug = Proportionenlinien.bezug(vb, vh);
            if (id.startsWith('modell:')) {
                const r = (p.ansichten || {})[id.slice(7)];
                const eintraege = Object.entries(((r || {}).linien || {}).modell || {}).map(([k, [von, bis]]) => ({
                    k, name: this._name(k), p: von, q: bis, wert: (p.modell || {})[k], eingestellt: false,
                }));
                svg.innerHTML = Proportionenlinien.markup(eintraege, bezug);
                continue;
            }
            if (!this.dialog.quellen[id]) continue;
            const eintraege = Object.entries(this.dialog.lagen[id] || {}).map(([k, linie]) => ({
                k, name: this._name(k), p: linie[0], q: linie[1], wert: this.dialog.wert(id, k),
                eingestellt: this.dialog.eingaben[k] !== undefined && this.dialog.eingaben[k] !== null && this.dialog.eingaben[k] !== '',
            }));
            svg.innerHTML = Proportionenlinien.markup(eintraege, bezug);
        }
    }

    _name(k) {
        return (this.katalog.proportionen || []).find(m => m.schluessel === k)?.name || k;
    }
}
