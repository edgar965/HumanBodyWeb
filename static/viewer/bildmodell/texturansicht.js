/**
 * Texturansicht — der Bereich „Textur" ganz unten auf der Auftragsseite.
 *
 * Edgar (19.09.2026): „Mach mir ganz unten einen Bereich nur für Textur. Darin
 * erstmal die ganze Textur in 2D, und einen Button zum Anpassen, wenn ich ein
 * Bild mit einer Textur entfernt habe … damit ich sehen kann, wie du die Textur
 * machst und anpasst, wenn ich die Bilder auswähle / abwähle, hinzufüge."
 *
 * Oben die fünf UDIM-Kacheln (`ergebnis.fototextur.kacheln`, 2048²; Klick öffnet
 * darunter das `Texturkachelpanel`: Körperteile der Kachel und die Beitragsbilder
 * der Fotos — Edgar, 20.09.: „mach klare Bilder was in das Bein, Nagel hineinkommt")
 * — wahlweise als Herkunftskarte (welches Bild welche Stelle liefert, Palette wie
 * `G9texturbacken.PALETTE`). Darunter die Tabelle der Bilder (`zustand.texturbilder`,
 * `Bildmodelltextur.liste`): Häkchen „für die Textur", Vorschau, Typ, wie das Bild
 * projiziert wird (Kamera bekannt — gerenderte Testfallbilder — oder Rig-
 * Registrierung gegen das Modell, mit Punktzahl und Fehler), Anteil, Texel, Löschen.
 * „Bild für die Textur hinzufügen" lädt mit Nutzung „nur Textur" hoch; „Textur
 * anpassen" startet nur den Schritt `textur` — mit neuen Dateien vorher die
 * Sichtung (Umfang „neue"). Die 3D-Ansicht oben zieht die Kacheln nach
 * (`texturauflage.js`, Marke `stand`).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Texturkachelpanel } from './texturkachel.js';

export class Texturansicht {

    static KACHELN = { 1001: 'Kopf', 1002: 'Rumpf', 1003: 'Beine', 1004: 'Arme', 1005: 'Nägel' };
    static PALETTE = [[230, 60, 60], [60, 140, 230], [60, 190, 90], [240, 170, 40],
                      [170, 80, 220], [40, 200, 200], [240, 100, 180], [150, 110, 60],
                      [120, 200, 40], [60, 60, 200], [230, 120, 60], [110, 110, 110]];
    constructor(auftrag, katalog, formular, steller) {
        this.auftrag = auftrag;
        this.formular = formular;
        this.steller = steller;
        this.panel = new Texturkachelpanel(auftrag);
        this.herkunft = false;
        this.geaendert = false;
        this._stand = '';
        document.getElementById('textur-herkunft')?.addEventListener('change', e => {
            this.herkunft = e.target.checked;
            this._stand = '';
            if (this._zustand) this.zeigen(this._zustand);
        });
        const dazu = document.getElementById('textur-dazu');
        dazu?.addEventListener('change', async () => {
            if (!dazu.files.length) return;
            const typen = {};
            for (const d of dazu.files) typen[d.name] = { nutzung: 'textur' };
            try { await this.auftrag.bilderHochladen([...dazu.files], typen); this.geaendert = true; }
            catch (fehler) { window.alert(fehler.message); }
            dazu.value = '';
        });
        document.getElementById('textur-anpassen')?.addEventListener('click', () => this.anpassen());
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    // ------------------------------------------------------------ Zeigen

    zeigen(z) {
        this._zustand = z;
        const ft = (z.ergebnis || {}).fototextur || null;
        if (z.status === 'fertig' && ft && this._letzterStand !== ft.stand) { this.geaendert = false; this._letzterStand = ft.stand; }
        const stand = JSON.stringify([ft ? ft.stand : null, z.texturbilder, z.texturreferenz, z.status, z.schritt, z.progress,
                                      (z.neue || []).length, this.herkunft, this.geaendert]);
        if (stand === this._stand) return;
        this._stand = stand;
        this._zahlen(z, ft);
        this._kacheln(ft);
        this.panel.referenz(z, ft);
        this.panel.zeigen(ft);
        this._tabelle(z, ft);
        this._knoepfe(z);
    }

    _zahlen(z, ft) {
        const feld = document.getElementById('textur-zahlen');
        if (!feld) return;
        if (!ft) { feld.textContent = 'noch keine Fototextur — „Textur anpassen" backt sie aus den gewählten Bildern'; return; }
        const teile = [`${Object.keys(ft.kacheln || {}).length} Kacheln ${ft.seite || ''}²`,
                       `HD-Deckung ${Math.round((ft.deckung_hd || 0) * 100)} %`,
                       `Punktfarbe ${Math.round((ft.deckung || 0) * 100)} %`,
                       `${ft.bilder} Bilder`];
        feld.textContent = teile.join(' · ');
    }

    _kacheln(ft) {
        const feld = document.getElementById('textur-kacheln');
        if (!feld) return;
        feld.innerHTML = '';
        if (!ft) return;
        const marke = ft.stand || Date.now();
        for (const [kachel, name] of Object.entries((ft.kacheln || {}))) {
            const fig = document.createElement('figure');
            fig.className = 'bildmodell-texturkachel';
            fig.classList.toggle('gewaehlt', this.panel.kachel === kachel);
            const a = document.createElement('a');
            a.href = this.auftrag.dateiAdresse('ergebnis', name) + `?t=${marke}`;
            a.title = `${kachel}: zeigen, was hineinkommt`;
            a.addEventListener('click', e => { e.preventDefault(); this.panel.waehlen(kachel, ft); this._stand = ''; this.zeigen(this._zustand); });
            const bild = document.createElement('img');
            bild.src = a.href;
            bild.alt = kachel;
            a.appendChild(bild);
            const h = (ft.herkunft || {})[kachel];
            if (this.herkunft && h) {
                const karte = document.createElement('img');
                karte.className = 'bildmodell-texturherkunft';
                karte.src = this.auftrag.dateiAdresse('ergebnis', h) + `?t=${marke}`;
                karte.alt = `Herkunft ${kachel}`;
                a.appendChild(karte);
            }
            const text = document.createElement('figcaption');
            text.textContent = `${kachel} · ${Texturansicht.KACHELN[kachel] || ''} `;
            const voll = document.createElement('a');
            voll.href = a.href;
            voll.target = '_blank';
            voll.textContent = '⤢';
            voll.title = `${kachel} in voller Größe öffnen`;
            text.appendChild(voll);
            fig.append(a, text);
            feld.appendChild(fig);
        }
    }

    // ----------------------------------------------------------- Tabelle

    _tabelle(z, ft) {
        const koerper = document.querySelector('#textur-bilder tbody');
        if (!koerper) return;
        koerper.innerHTML = '';
        const je = new Map(((ft || {}).je_bild || []).map((e, i) => [e.datei, { ...e, nummer: i }]));
        const bilder = z.texturbilder || [];
        bilder.forEach((b, i) => koerper.appendChild(this._zeile(b, je.get(b.datei), i + 1, bilder.length)));
        const leer = document.getElementById('textur-leer');
        if (leer) leer.classList.toggle('hb-versteckt', (z.texturbilder || []).length > 0);
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
            const antwort = await Serverabruf.senden(this.auftrag.adresse('texturreihenfolge/'), { reihenfolge: zeilen.map(z => z.dataset.datei) });
            if (antwort.error) throw new Error(antwort.error);
            this.auftrag.zustand.texturbilder = antwort.texturbilder;
        } catch (fehler) { window.alert(`Reihenfolge nicht gespeichert: ${fehler.message}`); }
    }

    _zeile(b, je, nr = 0, n = 0) {
        const tr = document.createElement('tr');
        tr.dataset.datei = b.datei;
        tr.classList.toggle('textur-aus', !b.gewaehlt);
        // Nr. (Edgar, 20.09.2026: „ändere ich die, wird das Bild sofort verschoben") — wie in der
        // Proportionentabelle: die Zeile rückt an die Stelle, die Nummern rücken nach, `texturreihenfolge/`.
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
        // Häkchen
        const wahl = document.createElement('td');
        const kasten = document.createElement('input');
        kasten.type = 'checkbox';
        kasten.checked = !!b.gewaehlt;
        kasten.disabled = !b.moeglich;
        kasten.title = b.moeglich ? 'für die Textur verwenden' : b.grund;
        kasten.addEventListener('change', async () => {
            try { await this.auftrag.bildStellen(b.datei, { textur_an: kasten.checked }); this.geaendert = true; }
            catch (fehler) { window.alert(fehler.message); }
        });
        wahl.appendChild(kasten);
        // Bild
        const bild = document.createElement('td');
        const img = document.createElement('img');
        img.className = 'bildmodell-texturvorschau';
        img.src = this.auftrag.dateiAdresse('zuschnitt', b.datei);
        img.alt = b.datei;
        img.title = `${b.datei} · ${b.breite || '?'} × ${b.hoehe || '?'} px`;
        if (je && je.nummer >= 0 && (je.anteil || 0) > 0) {
            const f = Texturansicht.PALETTE[je.nummer % Texturansicht.PALETTE.length];
            img.style.outline = `3px solid rgb(${f.join(',')})`;
        }
        bild.appendChild(img);
        // Datei und Typ
        const typ = document.createElement('td');
        typ.innerHTML = `<div class="bildmodell-texturdatei">${b.datei}</div><div class="hb-hinweis">${Texturansicht.typ(b)}</div>`
            + (b.grund ? `<div class="hb-hinweis bildmodell-texturgrund">${b.grund}</div>` : '');
        // Kamera
        const kamera = document.createElement('td');
        kamera.textContent = Texturansicht.kamera(b, je);
        // Anteil und Punkte
        const anteil = document.createElement('td');
        anteil.className = 'zahl';
        anteil.textContent = je ? `${(100 * (je.anteil || 0)).toFixed(1).replace('.', ',')} %` : '—';
        const punkte = document.createElement('td');
        punkte.className = 'zahl';
        punkte.textContent = je && je.texel ? je.texel.toLocaleString('de-DE') : '—';
        // Löschen
        const knoepfe = document.createElement('td');
        knoepfe.appendChild(this.steller.loeschenKnopf(`Bild ${b.datei} aus dem Auftrag löschen?`,
            async () => { await this.auftrag.bildLoeschen(b.datei); this.geaendert = true; }));
        tr.append(wahl, bild, typ, kamera, anteil, punkte, knoepfe);
        return tr;
    }

    static typ(b) {
        if (b.kategorie === 'koerper') return `Hauptbild Körper ${b.ansicht || ''}`;
        if (b.kategorie === 'kopf') return `Hauptbild Kopf ${b.ansicht || ''}`;
        if (b.kategorie === 'neben') return b.teil ? `Nebenbild · ${b.teil}` : 'Nebenbild';
        return b.kategorie || '';
    }

    static kamera(b, je) {
        const art = je ? je.kamera : b.kamera;
        const rig = je && je.punkte ? `Rig · ${je.punkte} Punkte · ${String(je.fehler_px).replace('.', ',')} px` : 'Rig';
        if (art === 'bekannt') return je && je.punkte ? `bekannt (gerendert) · ${rig}` : 'bekannt (gerendert)';
        if (art === 'rig') return rig;
        return '—';
    }

    // ------------------------------------------------------------ Knöpfe

    _knoepfe(z) {
        const knopf = document.getElementById('textur-anpassen');
        const text = document.getElementById('textur-lauf');
        const neue = (z.neue || []).length;
        if (knopf) {
            knopf.disabled = z.status === 'laeuft';
            knopf.querySelector('span').textContent = neue
                ? `${neue} neue ${neue === 1 ? 'Datei' : 'Dateien'} sichten und Textur anpassen`
                : 'Textur anpassen';
            knopf.classList.toggle('btn-primary', this.geaendert || neue > 0);
            knopf.classList.toggle('btn-secondary', !(this.geaendert || neue > 0));
        }
        if (text) {
            if (z.status === 'laeuft' && ['sichtung', 'textur'].includes(z.schritt)) {
                text.textContent = `${z.schritt === 'textur' ? 'Textur' : 'Sichtung'} läuft · ${z.progress_detail || ''}`;
            } else if (this.geaendert) {
                text.textContent = 'Auswahl geändert — „Textur anpassen" backt die Textur neu';
            } else {
                text.textContent = '';
            }
        }
    }

    /** Nur die Textur — mit neuen Dateien vorher die Sichtung (Umfang „neue"). */
    async anpassen() {
        const z = this.auftrag.zustand;
        const schritte = (z.neue || []).length ? ['sichtung', 'textur'] : ['textur'];
        try {
            const person = window.__bildmodell?.person?.werte?.() || {};
            const proportionen = window.__bildmodell?.proportionen?.werte?.() || {};
            const optionen = { ...(this.formular ? this.formular.werte() : {}), person, proportionen,
                               umfang: 'neue', textur: 'foto' };
            await this.auftrag.starten(optionen, schritte[0], {}, null, schritte);
        } catch (fehler) {
            window.alert(`Textur nicht gestartet: ${fehler.message}`);
        }
    }
}
