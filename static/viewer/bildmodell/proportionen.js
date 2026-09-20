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
 * Spalte „Nr." (Edgar, 20.09.2026: „Wenn ich die Zahl ändere, dann ändert sich
 * die Reihenfolge der Bilder gleich"): die Zeile springt sofort an die Stelle,
 * die Nummern rücken nach, der Server merkt sich die Reihe (`bilder[].reihe`).
 */
import { dbTabelle } from '/static/djangobase/js/tabelle_bauen.js';
import { tabellenBinden } from '/static/djangobase/js/tabellen_auto.js';
import { Bildsteller } from './bildsteller.js';
import { Gvhmrknopf } from './gvhmrknopf.js';
import { Proportionendialog } from './proportionendialog.js';
import { Proportionenlinien } from './proportionenlinien.js';

export class Proportionenansicht {

    static MERKER = 'bildmodell.prop.hoehe';
    static HOEHE = { min: 160, max: 900, vorgabe: 320 };
    /** Die Spalten nach djangoBase-Muster (`tabelle_bauen.js`): sortierbar Nr., Bild, SMPL; die Knöpfe
     *  und die gerenderten Bilder nicht (`sortAus`). Edgar (20.09.2026): „Mach die Tabelle nach djangoBase
     *  muster, sortierbar" — „ich brauch kein ‚Bild neu' sondern eines um eine GVHMR erkennung zu machen". */
    static SPALTEN = [
        { label: 'Nr.', key: 'nr', num: true, titel: 'Platz in der Tabelle — Nummer ändern = Zeile an diese Stelle' },
        { label: 'Bild', key: 'bild', titel: 'Ansicht und Datei — Klick ins Bild: Maße ziehen' },
        { label: 'Löschen', key: 'loeschen', sortAus: true },
        { label: 'Ersetzen', key: 'ersetzen', sortAus: true },
        { label: 'SMPL (GVHMR)', key: 'gvhmr', titel: 'SMPL-X mit GVHMR für dieses Bild — Ausgabefenster mit Netz, Rig und Zahlen' },
        { label: 'SMPL-X mit Rig', key: 'smplx', sortAus: true },
        { label: 'Verwenden', key: 'verwenden', titel: 'Welche GVHMR-Ergebnisse in die Form eingehen (Edgar: „dann entscheide ich, welche davon genommen werden")' },
        { label: 'Bild vorher (Ziel)', key: 'ziel', sortAus: true },
        { label: 'Bild nachher (Modell)', key: 'modell', sortAus: true },
    ];
    static KEY = 'bildmodell-proportionen';
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
        // Kein `updated_at`: das ändert sich im Lauf bei jedem Fortschritt und baute die Tabelle samt
        // Bildern alle paar Sekunden neu (Blinken). `p.stand` wechselt nur, wenn die Bilder neu sind.
        const stand = JSON.stringify([p.stand || '', Object.keys(p.ansichten || {}), fotos.map(f => [f.datei, f.ansicht, f.px_je_m]),
            (z.bilder || []).map(b => [b.datei, b.kategorie, b.ansicht, b.nutzung, b.gewicht, b.gvhmr_an,
                b.gvhmr ? (b.gvhmr.stand || b.gvhmr.fehler) : '']),
            z.status, z.schritt, (z.optionen || {}).gvhmr_bild || '']);
        if (stand === this._stand) return;
        this._stand = stand;
        this.feld.innerHTML = '';
        const knopf = document.getElementById('proportionen-anpassen');
        if (knopf) knopf.disabled = !Object.keys(this.dialog.quellen).length;
        if (!fotos.length) {
            this.feld.innerHTML = '<p class="hb-hinweis">Noch kein Hauptbild — „Bild hinzufügen" oder Bilder unten als Hauptbild einordnen.</p>';
            return;
        }
        // Kopf und Rahmen aus djangoBase, die Zeilen als DOM (Bilder mit SVG, Knöpfe mit Handlern).
        this.feld.innerHTML = dbTabelle({ key: Proportionenansicht.KEY, spalten: Proportionenansicht.SPALTEN,
                                          zeilen: [], klasse: 'bildmodell-proptabelle' });
        const rumpf = this.feld.querySelector('tbody');
        fotos.forEach((f, i) => rumpf.appendChild(this._zeile(f, (p.ansichten || {})[f.ansicht], z, i + 1, fotos.length)));
        tabellenBinden(this.feld);
        this.linienZeichnen();
    }

    _zeile(f, r, z, nr, n) {
        const b = (z.bilder || []).find(e => e.datei === f.datei) || { datei: f.datei };
        const tr = document.createElement('tr');
        tr.dataset.datei = f.datei;
        tr.dataset.ansicht = f.ansicht || '';
        // 0. die Nummer — editierbar, ändert die Reihenfolge sofort
        const nummer = document.createElement('td');
        nummer.className = 'bildmodell-propnr num';
        nummer.dataset.sort = String(nr);
        const eingabe = document.createElement('input');
        eingabe.type = 'number';
        eingabe.min = 1; eingabe.max = n; eingabe.step = 1;
        eingabe.value = nr;
        eingabe.title = 'Nummer ändern = Zeile an diese Stelle';
        eingabe.addEventListener('change', () => this._umordnen(tr, Number(eingabe.value)));
        eingabe.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); eingabe.blur(); } });
        nummer.appendChild(eingabe);
        tr.appendChild(nummer);
        // 1. das Foto mit Linien und Typ-Boxen
        const foto = document.createElement('td');
        foto.className = 'bildmodell-propfoto';
        foto.dataset.sort = `${b.kategorie || ''} ${b.ansicht || ''} ${f.datei}`;
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
        const frei = this.steller.freisteller.element(b);   // „Hintergrund" (20.09.2026)
        if (frei) ersetzen.appendChild(frei);
        tr.append(loeschen, ersetzen);
        // 3. SMPL-X mit GVHMR für dieses Bild — Knopf und Stand (Höhe, Dauer), `Gvhmrknopf` über den Steller.
        const gvhmr = document.createElement('td');
        gvhmr.className = 'bildmodell-propgvhmr';
        // Kopfbild: „Kopf (FLAME)" statt GVHMR (20.09.2026) — Knopf, Stand und Bild aus `b.flame`.
        const kopf = Gvhmrknopf.kopfbild(b);
        const knopfdienst = kopf ? this.steller.flame : this.steller.gvhmr;
        const gvhmrKnopf = knopfdienst.element(b);
        if (gvhmrKnopf) gvhmr.appendChild(gvhmrKnopf);
        const stand = knopfdienst.constructor.stand(b);
        gvhmr.dataset.sort = '';   // ohne Ergebnis: leer = ans Ende, nicht der Knopftext
        if (stand) {
            gvhmr.dataset.sort = String(stand.sort);
            const text = document.createElement('div');
            text.className = 'hb-hinweis klein';
            text.textContent = stand.text;
            gvhmr.appendChild(text);
        }
        tr.appendChild(gvhmr);
        // 3b. Das SMPL-X-Netz mit Rig als Bild (Edgar: „das SMPL ausgabefenster nun auch dauernd sichtbar,
        //     als neue Spalte") — gerendert nach dem Lauf (`Bildmodellgvhmrbild`); Klick öffnet das Fenster.
        const smplx = document.createElement('td');
        const netz = kopf ? b.flame : b.gvhmr;
        if (netz && netz.bild) {
            const src = this.auftrag.dateiAdresse('ergebnis', netz.bild) + `?t=${encodeURIComponent(netz.stand || '')}`;
            // Seit 20.09. spät im Ausschnitt und in der Kamera des Fotos (`bild_breite`/`bild_hoehe`);
            // ältere Läufe: aufgestellt von vorn, 480 × 640. Kopfbild: der FLAME-Kopf von vorn.
            const text = kopf
                ? `FLAME-Kopf (PyMAF-X) · ${(netz.punkte || 0).toLocaleString('de-DE')} Punkte`
                : `SMPL-X (GVHMR)${netz.gelenke ? ' mit Rig' : ''}${netz.kamera ? ' · Sicht des Fotos' : ' · von vorn (alt)'}`
                  + ` · ${netz.hoehe_m ? netz.hoehe_m.toFixed(2) + ' m' : ''}`;
            const g = this._figur(`smplx:${f.datei}`, netz.bild_breite || 480, netz.bild_hoehe || 640, src, text,
                kopf ? 'Klick: Ausgabefenster mit dem FLAME-Kopf in 3D' : 'Klick: Ausgabefenster mit Netz, Rig und Zahlen');
            g.dataset.wer = 'smplx';
            g.addEventListener('click', () => knopfdienst.fenster.oeffnen(f.datei, false));
            smplx.appendChild(g);
        } else {
            smplx.className = 'hb-hinweis';
            smplx.textContent = netz && netz.bild_fehler ? `Bild: ${netz.bild_fehler}` : '—';
        }
        tr.appendChild(smplx);
        // 3c. Verwenden: Häkchen je Ergebnis, sortierbar (ja vor nein vor ohne Ergebnis).
        const verwenden = document.createElement('td');
        const kasten = this.steller.gvhmr.verwendenFeld(b);
        verwenden.dataset.sort = kasten ? (Gvhmrknopf.verwendet(b) ? '2' : '1') : '';
        if (kasten) verwenden.appendChild(kasten);
        tr.appendChild(verwenden);
        // 4./5. Vorher (Ziel) und Nachher (Modell) der Ansicht
        for (const wer of ['ziel', 'modell']) {
            const td = document.createElement('td');
            if (r) {
                const stand = ((z.ergebnis || {}).proportionen || {}).stand || '';
                const src = this.auftrag.dateiAdresse('ergebnis', r.bild[wer]) + `?t=${encodeURIComponent(stand)}`;
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

    /** Die Zeile an Stelle `ziel` (1..n) setzen, alle Nummern nachrücken, die Reihe ablegen. */
    async _umordnen(tr, ziel) {
        const rumpf = tr.parentElement;
        if (!rumpf) return;
        const zeilen = [...rumpf.children].filter(z => z !== tr);
        const stelle = Math.min(Math.max(1, Math.round(ziel) || 1), zeilen.length + 1) - 1;
        zeilen.splice(stelle, 0, tr);
        zeilen.forEach((z, i) => { rumpf.appendChild(z); const e = z.querySelector('.bildmodell-propnr input'); if (e) e.value = i + 1; });
        try {
            await this.auftrag.reihenfolgeSetzen(zeilen.map(z => z.dataset.datei));
        } catch (fehler) { window.alert(`Reihenfolge nicht gespeichert: ${fehler.message}`); }
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

    /** Klick im Bild: auf einer Linie → dieses Maß im Popup, sonst das Popup mit diesem Bild —
     *  und die Modellsicht oben zeigt danach dasselbe Bild (20.09.2026). */
    amBild(e, id) {
        const gruppe = e.target.closest ? e.target.closest('g[data-mass]') : null;
        window.__bildmodell?.modellsicht?.quelleWaehlen?.(id, true);
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
