/**
 * Haarenginerundenzeilen — die Zeilen EINER Runde in der Tabelle „Iterationen": eine Hauptzeile (sortierbare Kennzahlen) und
 * Unterzeilen (Notiz und Änderungen · Prüf-KI · Bilder · Dateien und Teile).
 *
 * Ein Eintrag in `ergebnis.iterationen` (`Iterationsrunde.ablegen`): Art, Note, Vergleichstafel, Renders je Blickwinkel, Modell-GLB,
 * Änderungen, Bericht der Prüf-KI. Die Zeilen zeigen, was da ist.
 *
 * Alles wird mit `textContent` gesetzt: Notiz und Begründung der Prüf-KI kommen aus einem Sprachmodell. `data-sort` trägt Zahlen mit
 * KOMMA („0,3723"): djangoBase liest Punkte als Tausendertrenner („0.3723" → 3723).
 */
export class Haarenginerundenzeilen {

    static ARTEN = {
        ausgang: 'Ausgangslage', optimierer: 'Optimierer', ki: 'Prüf-KI übernommen', ki_verworfen: 'Prüf-KI verworfen',
        begutachtung: 'Begutachtung (Rezept)',
    };
    static SPALTEN = [
        { label: '<input type="checkbox" id="iterationen-select-all" title="alle angezeigten wählen / Auswahl aufheben">',
          key: 'wahl', sortAus: true },
        // Die Nummer der Runde ist die ZWEITE Spalte (Edgar, 30.09.2026), das Aufklapp-Zeichen steht dahinter.
        { label: 'Runde', key: 'runde', num: true, titel: '★ = das beste Modell aller Runden' },
        { label: '', key: 'auf', sortAus: true, titel: 'Details auf-/zuklappen' },
        { label: 'Zeit', key: 'zeit' },
        { label: 'Art', key: 'art' },
        { label: 'Abweichung', key: 'abweichung', num: true, titel: '(1 − Umriss-IoU) + Farbabstand, kleiner ist besser' },
        { label: 'IoU', key: 'iou', num: true, titel: 'Deckung des Umrisses mit der Vorlage, Mittel über die Blickwinkel' },
        { label: 'Farbe', key: 'farbe', num: true, titel: 'Farbabstand zur Vorlage' },
        { label: 'Änderungen', key: 'aenderungen', num: true, titel: 'Zahl der Werte, die gegenüber der Vorrunde geändert wurden' },
        { label: 'Prüf-KI', key: 'ki', num: true, titel: 'Ähnlichkeit laut Prüf-KI, 1 (völlig anders) bis 10 — eine Einschätzung, keine Messung' },
        { label: 'vorn', key: 'vorn', sortAus: true, titel: 'Render von vorn — Klick: groß' },
        { label: '', key: 'loeschen', sortAus: true, titel: 'Runde löschen' },
    ];
    static LINKS = [
        ['modell', 'Modell als GLB (Figur, Haar, Rig)'], ['vergleich', 'Vergleichstafel (PNG)'],
    ];

    /** @param datei Adresse einer Datei aus `iterationen/`, @param bilder `Haarenginerundenbilder` */
    constructor(datei, bilder) {
        this.datei = datei;
        this.bilder = bilder;
    }

    static zahl(wert, stellen = 3) {
        return wert == null ? '—' : Number(wert).toLocaleString('de-DE', { maximumFractionDigits: stellen });
    }

    static komma(wert) {
        return wert == null ? '' : String(wert).replace('.', ',');
    }

    /** „2026-09-29 23:25:41" → „29.09. 23:25:41" (alles andere bleibt, wie es ist). */
    static zeit(text) {
        const t = /^\d{4}-(\d{2})-(\d{2})[ T](\d{2}:\d{2}(?::\d{2})?)/.exec(text || '');
        return t ? `${t[2]}.${t[1]}. ${t[3]}` : (text || '');
    }

    /** Dauer einer Iteration: „23 s", ab einer Minute „1:05 min". */
    static dauer(sekunden) {
        if (sekunden == null) return '';
        const s = Math.round(Number(sekunden));
        return s < 60 ? `${s} s` : `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')} min`;
    }

    static el(tag, text = '', klasse = '', titel = '') {
        const e = document.createElement(tag);
        if (text) e.textContent = text;
        if (klasse) e.className = klasse;
        if (titel) e.title = titel;
        return e;
    }

    _zelle(text, { num = false, sort = null, klasse = '', titel = '' } = {}) {
        const td = Haarenginerundenzeilen.el('td', text, [num ? 'num' : '', klasse].filter(Boolean).join(' '), titel);
        if (sort !== null && sort !== undefined) td.dataset.sort = String(sort);
        return td;
    }

    // ------------------------------------------------------------- Hauptzeile

    /** @param z {beste, offen, geloescht} */
    haupt(r, z) {
        const E = Haarenginerundenzeilen;
        const tr = E.el('tr', '', 'iter-zeile' + (r.uebernommen === false ? ' iter-verworfen' : '')
            + (z.geloescht ? ' iter-wird-geloescht' : ''));
        tr.dataset.id = String(r.runde);
        const wahl = this._zelle('', { klasse: 'kaestchen' });
        const kasten = E.el('input');
        Object.assign(kasten, { type: 'checkbox', className: 'job-check', value: String(r.runde), disabled: !!z.geloescht });
        kasten.setAttribute('aria-label', `Runde ${r.runde} wählen`);
        wahl.appendChild(kasten);
        const auf = this._zelle('');
        const knopf = E.el('button', z.offen ? '▾' : '▸', 'iter-auf', 'Details auf-/zuklappen');
        knopf.type = 'button';
        knopf.setAttribute('aria-expanded', String(!!z.offen));
        auf.appendChild(knopf);
        const nummer = this._zelle(String(r.runde), { num: true, sort: r.runde });
        if (z.beste) nummer.appendChild(E.el('span', ' ★', 'iter-beste', 'Das beste Modell aller Runden'));
        const n = r.note || {};
        const art = E.ARTEN[r.art] || (r.art ? r.art : 'Handrunde');
        tr.append(wahl, nummer, auf,
            this._zeit(r),
            this._zelle(z.geloescht ? `${art} — wird gelöscht …` : art),
            this._zelle(E.zahl(n.abweichung, 4), { num: true, sort: E.komma(n.abweichung) }),
            this._zelle(E.zahl(n.iou), { num: true, sort: E.komma(n.iou) }),
            this._zelle(E.zahl(n.farbe), { num: true, sort: E.komma(n.farbe) }),
            this._aenderungen(r), this._ki(r), this._vorn(r), this._loeschen(r));
        return tr;
    }

    /** Uhrzeit der Runde, darunter die Dauer der Iteration (Edgar, 30.09.2026: „zeige die Zeit pro Iteration in der
     *  Spalte Zeit an, zusätzlich zur absoluten Zeit"). Sortiert wird nach der Uhrzeit. Ältere Runden ohne
     *  gemessene Dauer zeigen nur die Uhrzeit. */
    _zeit(r) {
        const E = Haarenginerundenzeilen;
        const td = this._zelle(E.zeit(r.zeit), { sort: r.zeit || '', klasse: 'iter-zeit',
            titel: r.sekunden != null ? `Rechenzeit dieser Iteration: ${E.dauer(r.sekunden)}` : '' });
        if (r.sekunden != null) td.appendChild(E.el('small', E.dauer(r.sekunden), 'iter-dauer'));
        return td;
    }

    _aenderungen(r) {
        const namen = Object.keys(r.aenderungen || {});
        return this._zelle(namen.length ? String(namen.length) : '—',
            { num: true, sort: namen.length, titel: namen.join(', ') });
    }

    _ki(r) {
        const k = r.kritik;
        if (!k) return this._zelle('—', { num: true, sort: '' });
        const titel = `${k.modell || 'Prüf-KI'}${k.sekunden ? ` · ${k.sekunden} s` : ''}${k.urteil ? ` · ${k.urteil}` : ''}`;
        if (k.fehler && !k.aehnlichkeit) return this._zelle('Fehler', { num: true, sort: '', klasse: 'hb-schlecht', titel: `${titel} · ${k.fehler}` });
        return this._zelle(k.aehnlichkeit ? `${k.aehnlichkeit}/10` : 'KI', { num: true, sort: k.aehnlichkeit || '', titel });
    }

    _vorn(r) {
        const td = this._zelle('', { klasse: 'iter-vorn' });
        const a = (r.je_ansicht || []).find(x => Math.round(x.winkel) === 0 && x.render);
        if (!a) return this._zelle('–', { klasse: 'iter-vorn' });
        const bild = Haarenginerundenzeilen.el('img', '', 'iter-mini', 'Render von vorn — Klick: groß');
        bild.src = this.datei(a.render);
        bild.alt = `Runde ${r.runde}: Render von vorn`;
        bild.loading = 'lazy';
        bild.dataset.winkel = '0';
        td.appendChild(bild);
        return td;
    }

    _loeschen(r) {
        const td = this._zelle('');
        const knopf = Haarenginerundenzeilen.el('button', '', 'btn btn-secondary btn-sm iter-loeschen', `Runde ${r.runde} löschen`);
        knopf.type = 'button';
        knopf.innerHTML = '<i class="fas fa-trash"></i>';
        td.appendChild(knopf);
        return td;
    }

    // ------------------------------------------------------------ Unterzeilen

    _unter(r, kopf, offen, inhalt) {
        const E = Haarenginerundenzeilen;
        const tr = E.el('tr', '', 'iter-unterzeile');
        tr.dataset.eltern = String(r.runde);
        tr.hidden = !offen;
        const td = E.el('td');
        td.colSpan = E.SPALTEN.length;
        const zeile = E.el('div', '', 'iter-unter');
        zeile.append(E.el('span', kopf, 'iter-unterkopf'), inhalt);
        td.appendChild(zeile);
        tr.appendChild(td);
        return tr;
    }

    /** Die Unterzeilen einer Runde, in der Reihenfolge, in der sie unter der Hauptzeile stehen. */
    unter(r, offen) {
        const E = Haarenginerundenzeilen;
        const aus = [];
        const notiz = this._notiz(r);
        if (notiz) aus.push(this._unter(r, 'Notiz und Änderungen', offen, notiz));
        const begutachtung = this._begutachtung(r);
        if (begutachtung) aus.push(this._unter(r, 'Begutachtung', offen, begutachtung));
        if (r.kritik) aus.push(this._unter(r, 'Prüf-KI', offen, this._kritik(r)));
        if (this.bilder.gruppen(r).length) {
            const bilder = this._unter(r, 'Bilder', offen, E.el('div', '', 'iter-unterinhalt iter-bilder'));
            bilder.dataset.bilder = 'leer';
            aus.push(bilder);
        }
        const dateien = this._dateien(r);
        if (dateien) aus.push(this._unter(r, 'Dateien und Teile', offen, dateien));
        return aus;
    }

    /** Die Kacheln der Unterzeile „Bilder" erst beim ersten Aufklappen bauen — tausend Runden mit je 18 Bildern
     *  wären sonst 18.000 Elemente, die keiner sieht. */
    bilderFuellen(tr, r) {
        if (tr.dataset.bilder !== 'leer') return;
        tr.dataset.bilder = 'voll';
        const raster = this.bilder.raster(r);
        if (raster) tr.querySelector('.iter-bilder').replaceChildren(raster);
    }

    _aenderungsliste(aenderungen) {
        const E = Haarenginerundenzeilen;
        const liste = E.el('span', '', 'iter-aenderungen');
        for (const [schluessel, [alt, neu]] of Object.entries(aenderungen || {})) {
            liste.appendChild(E.el('span', `${schluessel}: ${E.zahl(alt)} → ${E.zahl(neu)}`, 'iter-aenderung'));
        }
        return liste;
    }

    _notiz(r) {
        const E = Haarenginerundenzeilen;
        const hat = Object.keys(r.aenderungen || {}).length;
        if (!r.notiz && !hat) return null;
        const inhalt = E.el('div', '', 'iter-unterinhalt');
        if (r.notiz) inhalt.appendChild(E.el('p', r.notiz));
        if (hat) inhalt.append(E.el('span', 'Geändert: ', 'hb-hinweis'), this._aenderungsliste(r.aenderungen));
        return inhalt;
    }

    /** Runde im Modus „Begutachtung" (30.09.2026): Kommentar, das Rezept (Aufrufe an `ModellMitKleidern`), ein Fehler
     *  darin, und die 3D-Note gegen das Netz. Alles `textContent` — das Rezept ist Text, kein Code, der hier läuft. */
    _begutachtung(r) {
        const E = Haarenginerundenzeilen;
        if (!r.aufrufe && !r.kommentar && !r.fehler && !(r.note || {}).netz) return null;
        const inhalt = E.el('div', '', 'iter-unterinhalt');
        if (r.kommentar) inhalt.appendChild(E.el('p', r.kommentar));
        if (r.fehler) inhalt.appendChild(E.el('p', `Rezept fehlerhaft: ${r.fehler}`, 'hb-schlecht'));
        if (r.aufrufe) {
            const code = E.el('pre', r.aufrufe, 'iter-rezept');
            inhalt.appendChild(code);
        }
        const n = (r.note || {}).netz;
        if (n) {
            inhalt.appendChild(E.el('p', `Netz: Stoff ${E.zahl(n.modell_mm, 1)} mm, Körper ${E.zahl(n.koerper_mm, 1)} mm `
                + `zur Netzoberfläche · Deckung ${E.zahl(100 * (n.deckung || 0), 1)} % · Netz-Abweichung ${E.zahl(n.abweichung, 4)}`
                + (r.note.foto != null ? ` · Foto-Abweichung ${E.zahl(r.note.foto, 4)}` : ''), 'hb-hinweis'));
        }
        return inhalt;
    }

    _kritik(r) {
        const E = Haarenginerundenzeilen;
        const k = r.kritik;
        const inhalt = E.el('div', '', 'iter-unterinhalt');
        const kopf = [`Prüf-KI ${k.modell || ''}`.trim(), k.sekunden ? `${E.zahl(k.sekunden, 1)} s` : '',
            k.aehnlichkeit ? `Ähnlichkeit ${k.aehnlichkeit}/10` : ''].filter(Boolean).join(' · ');
        inhalt.appendChild(E.el('p', kopf, 'iter-kikopf'));
        if (k.fehler) inhalt.appendChild(E.el('p', `Fehler: ${k.fehler}`, 'hb-schlecht'));
        if (k.urteil) inhalt.appendChild(E.el('p', `Urteil: ${k.urteil}`));
        const v = k.vorschlag;
        if (v) {
            inhalt.appendChild(E.el('p', `Vorschlag der Prüf-KI: Abweichung ${E.zahl(v.vorher, 4)} → ${E.zahl(v.abweichung, 4)} — `
                + (v.uebernommen ? 'übernommen' : 'nicht übernommen (schlechter als die Toleranz erlaubt)')));
        }
        if (k.begruendung) inhalt.appendChild(E.el('p', `Begründung: ${k.begruendung}`));
        if (Object.keys(k.aenderungen || {}).length) {
            inhalt.append(E.el('span', 'Vorgeschlagen: ', 'hb-hinweis'), this._aenderungsliste(k.aenderungen));
        }
        return inhalt;
    }

    _dateien(r) {
        const E = Haarenginerundenzeilen;
        const d = r.dateien || {};
        const inhalt = E.el('div', '', 'iter-unterinhalt mesh-downloads iter-dateien');
        let etwas = false;
        for (const [schluessel, text] of E.LINKS) {
            if (!d[schluessel]) continue;
            const a = E.el('a', text);
            a.href = this.datei(d[schluessel]);
            a.download = d[schluessel];
            inhalt.appendChild(a);
            etwas = true;
        }
        const teile = Object.keys(r.teile || {});
        if (teile.length) {
            inhalt.appendChild(E.el('span', `Teile: ${teile.join(', ')}`, 'hb-hinweis'));
            etwas = true;
        }
        return etwas ? inhalt : null;
    }
}
