/**
 * Mesh3dvarianten — die Karte „Empfehlungen und Varianten“ der Jobseite „Mesh-3D“ (13.10.2026, Konzept „Mesh-3D ohne Nacharbeit“).
 *
 * Edgar: „mach im Job Optionen für die unterschiedlichen Einstellungen, mit Vorschlag, was ich machen soll — ggf. mit Option, die Jobs mit beiden Optionen (z. B. nah und ignorieren für kleidung_zug)
 * auszurechnen und zu vergleichen“, und „berechnen von mehreren Ausgaben in einem Job“. Je Feld (`kleidung_zug`, `basis`, `pose`): der Wert, den der Auftrag jetzt hat, die Empfehlung mit ihrem Grund,
 * der Knopf „Varianten rechnen“ (mit den Minuten) — und, sobald Varianten da sind, die Tabelle Hauptausgabe gegen Varianten mit den Vergleichsbildern. „Diese übernehmen“ macht eine Variante zur Ausgabe
 * des Auftrags. Dieselbe Auswahl steht als „Ausgabe“ über der 3D-Ansicht: jede fertige Variante lässt sich dort ansehen.
 *
 * Der Zustand kommt von der Seite (`z.varianten`, `Mesh3dvergleich`); geschrieben wird über `/api/mesh3d/<kennung>/varianten/…`. Texte gehen über `textContent` (Namen stammen aus Dateien).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3dvarianten {
    constructor(seite) {
        this.seite = seite;
        this.karte = document.getElementById('varianten-karte');
        this.meldung = document.getElementById('varianten-meldung');
        this.felder = document.getElementById('varianten-felder');
        this.vergleiche = document.getElementById('varianten-vergleiche');
        this.anhalten = document.getElementById('varianten-anhalten');
        this.loeschen = document.getElementById('varianten-loeschen');
        this.wahl = document.getElementById('buehne-ausgabe');
        this.wahlFeld = document.getElementById('buehne-ausgabe-feld');
        this._stand = '';
        this._z = null;
        this.anhalten.addEventListener('click', () => this._senden('anhalten/', {}, 'Angehalten.'));
        this.loeschen.addEventListener('click', () => {
            if (window.confirm('Alle Varianten dieses Auftrags löschen? Gespeicherte Modelle bleiben.')) this._senden('loeschen/', {}, 'Varianten gelöscht.');
        });
        this.wahl.addEventListener('change', () => this.seite.buehne.ausgabeWaehlen(this.wahl.value || null));
    }

    zeigen(z) {
        this._z = z;
        const v = z.varianten;
        this.karte.hidden = !v;
        this.wahlFeld.hidden = !v || !v.eintraege.some(e => e.status === 'fertig');
        if (!v) return;
        this._ausgabe(v);
        this.anhalten.hidden = !v.laeuft;
        this.loeschen.hidden = !v.eintraege.length;
        if (!Mesh3danzeige.geaendert(this, '_stand', [v, z.status])) return;
        this._felder(v, z);
        this._vergleiche(v);
    }

    /** Die Auswahl „Ausgabe“ über der 3D-Ansicht: Hauptausgabe und jede fertige Variante. */
    _ausgabe(v) {
        const fertig = v.eintraege.filter(e => e.status === 'fertig');
        const jetzt = this.seite.buehne.ausgabe || '';
        const optionen = [['', v.haupt ? 'Ausgabe: übernommene Variante' : 'Ausgabe: erster Lauf'], ...fertig.filter(e => e.id !== v.haupt).map(e => [e.id, `Variante${e.automatisch ? ' (automatisch)' : ''}: ${e.titel}`])];
        const marke = JSON.stringify(optionen);
        if (this.wahl.dataset.marke !== marke) {
            this.wahl.replaceChildren(...optionen.map(([wert, text]) => Object.assign(document.createElement('option'), { value: wert, textContent: text })));
            this.wahl.dataset.marke = marke;
        }
        if (jetzt && !optionen.some(([wert]) => wert === jetzt)) this.seite.buehne.ausgabeWaehlen(null);           // die Variante gibt es nicht mehr
        this.wahl.value = optionen.some(([wert]) => wert === jetzt) ? jetzt : '';
    }

    // ---------------------------------------------------------------- Felder

    _felder(v, z) {
        this.felder.replaceChildren();
        const gesperrt = z.status === 'laeuft' || v.laeuft || v.rechnet_import;
        for (const feld of v.felder) {
            const empfehlung = v.empfehlungen.find(e => e.schluessel === feld.schluessel);
            const block = document.createElement('div');
            block.className = 'mesh3d-variantenfeld';
            const kopf = document.createElement('div');
            kopf.className = 'mesh3d-variantenkopf';
            const titel = document.createElement('strong');
            titel.textContent = feld.titel;
            const jetzt = document.createElement('span');
            jetzt.className = 'hb-hinweis';
            jetzt.textContent = `Jetzt: ${this._text(feld, feld.aktuell)}`;
            kopf.append(titel, jetzt);
            block.appendChild(kopf);
            if (empfehlung) block.appendChild(this._empfehlung(empfehlung, feld, gesperrt));
            block.appendChild(this._rechnen(feld, gesperrt, z));
            this.felder.appendChild(block);
        }
    }

    _text(feld, wert) {
        return feld.werte.find(w => w.wert === wert)?.text.split(' — ')[0] || wert;
    }

    /** Die Empfehlung als Zeile: wer sie ausspricht (Vergleich der gerechneten Läufe oder eine Regel), was, warum — und der Knopf, sie zu übernehmen. */
    _empfehlung(e, feld, gesperrt) {
        const zeile = document.createElement('div');
        zeile.className = 'mesh3d-empfehlung';
        const quelle = { vergleich: 'Vergleich der Läufe', regel: 'Regel', keine: 'Hinweis' }[e.quelle] || '';
        const text = document.createElement('span');
        text.className = 'hb-hinweis';
        text.textContent = e.empfohlen ? `Empfohlen: ${this._text(feld, e.empfohlen)} (${quelle}) — ${e.text}` : `Hinweis: ${e.text}`;
        zeile.appendChild(text);
        if (e.empfohlen && e.empfohlen !== e.aktuell) {
            const knopf = this._knopf('Empfehlung übernehmen', 'fa-check', gesperrt, 'Den empfohlenen Wert im Auftrag setzen; er gilt ab „Neu berechnen“');
            knopf.addEventListener('click', () => (e.id
                ? this._senden('uebernehmen/', { id: e.id }, 'Variante übernommen.')
                : this._einstellung({ [feld.schluessel]: e.empfohlen })));
            zeile.appendChild(knopf);
        }
        return zeile;
    }

    /** „Varianten rechnen“: die Werte, die weder die Hauptausgabe noch eine Variante schon hat, mit den Minuten, die es kostet. */
    _rechnen(feld, gesperrt, z) {
        const zeile = document.createElement('div');
        zeile.className = 'mesh3d-schrittzeile';
        if (!feld.offen.length) {
            const hinweis = document.createElement('span');
            hinweis.className = 'hb-hinweis';
            hinweis.textContent = 'Alle Werte sind gerechnet.';
            zeile.appendChild(hinweis);
            return zeile;
        }
        const fertig = z.figur && !z.figur.fehlt && z.status === 'fertig';
        const offen = feld.offen.map(w => this._text(feld, w)).join(', ');
        const knopf = this._knopf(`Varianten rechnen: ${offen} (≈ ${feld.minuten} min)`, 'fa-clone', gesperrt || !fertig,
            fertig ? 'Dieselbe Figur mit den anderen Werten rechnen (eine GPU, nacheinander) und mit der Hauptausgabe vergleichen' : 'Erst die Hauptausgabe rechnen („Neu berechnen“)');
        knopf.addEventListener('click', () => this._senden('', { feld: feld.schluessel, werte: feld.offen }, null));
        zeile.appendChild(knopf);
        return zeile;
    }

    _knopf(text, symbol, gesperrt, titel) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-secondary btn-sm';
        knopf.disabled = Boolean(gesperrt);
        knopf.title = titel;
        const i = document.createElement('i');
        i.className = `fas ${symbol}`;
        const t = document.createElement('span');
        t.textContent = ` ${text}`;
        knopf.append(i, t);
        return knopf;
    }

    // ------------------------------------------------------------- Vergleich

    _vergleiche(v) {
        this.vergleiche.replaceChildren();
        for (const gruppe of v.gruppen) {
            // Ohne Variante gibt es nichts zu vergleichen: eine Tabelle mit nur dem ersten Lauf wäre Rauschen (und „noch nicht alle fertig“ gelogen).
            if (!gruppe.spalten.some(s => s.rolle === 'variante')) continue;
            const feld = v.felder.find(f => f.schluessel === gruppe.feld);
            const block = document.createElement('div');
            block.className = 'mesh3d-vergleich';
            const titel = document.createElement('h3');
            titel.className = 'engine2d3dkleider-gruppe';
            titel.textContent = `Vergleich: ${gruppe.titel}`;
            block.appendChild(titel);
            const tabelle = document.createElement('div');
            const spalten = [{ titel: '' }, ...gruppe.spalten.map(s => ({ titel: this._spaltentitel(s, feld), num: true }))];
            const zeilen = v.zeilen.map(z => [{ text: z.titel + (z.einheit ? ` (${z.einheit})` : '') + (z.gewertet ? '' : ' · nur Auskunft') },
                ...gruppe.spalten.map(s => ({ text: s.status === 'fertig' ? Mesh3danzeige.zahl(s.werte[z.schluessel], 2) : '' }))]);
            Mesh3danzeige.tabelle(tabelle, spalten, zeilen);
            block.appendChild(tabelle);
            block.appendChild(this._schluss(gruppe, feld));
            const bilder = document.createElement('div');
            bilder.className = 'mesh3d-bilder';
            Mesh3danzeige.bilder(bilder, gruppe.spalten.map(s => ({ adresse: s.bild, titel: this._spaltentitel(s, feld), gross: true })));
            block.appendChild(bilder);
            block.appendChild(this._knoepfe(gruppe, v));
            this.vergleiche.appendChild(block);
        }
    }

    _spaltentitel(s, feld) {
        const wert = feld && s.wert ? this._text(feld, s.wert) : '';
        const lauf = s.status === 'laeuft' ? ` — rechnet ${s.prozent} %` : s.status === 'angelegt' ? ' — wartet' : s.status === 'gescheitert' ? ' — gescheitert' : s.status === 'angehalten' ? ' — angehalten' : '';
        return `${s.rolle === 'haupt' ? 'Erster Lauf' : s.automatisch ? 'Variante (automatisch)' : 'Variante'}${wert ? `: ${wert}` : ''}${lauf}`;
    }

    /** Was der Vergleich sagt — ohne Gesamtnote: eine Spalte, die in allen gewerteten Zeilen nicht schlechter ist, sonst „das Bild entscheidet“. */
    _schluss(gruppe, feld) {
        const zeile = document.createElement('div');
        zeile.className = 'hb-hinweis mesh3d-schluss';
        const fertig = gruppe.spalten.filter(s => s.status === 'fertig').length;
        const e = gruppe.empfehlung;
        if (fertig < 2) zeile.textContent = 'Noch nicht alle Läufe fertig.';
        else if (e) zeile.textContent = `Vorschlag: ${this._text(feld, e.wert)} — ${e.grund}.`;
        else zeile.textContent = 'Keine Empfehlung — keine Spalte ist in allen gewerteten Zeilen mindestens so gut wie die anderen; das Bild entscheidet. Zeilen „nur Auskunft“ zählen nicht (ein kleinerer Umfang ist nicht besser).';
        return zeile;
    }

    _knoepfe(gruppe, v) {
        const zeile = document.createElement('div');
        zeile.className = 'mesh3d-schrittzeile';
        const gesperrt = v.laeuft || v.rechnet_import;
        for (const s of gruppe.spalten.filter(x => x.rolle === 'variante')) {
            if (s.status === 'fertig') {
                const nimm = this._knopf(`Übernehmen: ${s.wert}`, 'fa-check', gesperrt || v.haupt === s.id,
                    v.haupt === s.id ? 'Diese Variante ist die Ausgabe des Auftrags' : 'Den Wert im Auftrag setzen, diese Figur als Ausgabe zeigen und ihr Modell speichern');
                nimm.addEventListener('click', () => this._senden('uebernehmen/', { id: s.id }, `Variante „${s.wert}“ übernommen — das Modell wird gespeichert.`));
                zeile.appendChild(nimm);
            }
            const weg = this._knopf(`Löschen: ${s.wert}`, 'fa-trash', gesperrt, 'Diese Variante entfernen (gespeicherte Modelle bleiben)');
            weg.addEventListener('click', () => this._senden('loeschen/', { id: s.id }, 'Variante gelöscht.'));
            zeile.appendChild(weg);
        }
        return zeile;
    }

    // ------------------------------------------------------------- Schreiben

    async _senden(pfad, rumpf, erfolg) {
        this.meldung.classList.remove('fehlertext');
        this.meldung.textContent = 'wird gesendet …';
        try {
            const antwort = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/varianten/${pfad}`, rumpf);
            if (antwort.error) throw new Error(antwort.error);
            const minuten = antwort.minuten ? ` (≈ ${antwort.minuten} min)` : '';
            this.meldung.textContent = erfolg || `${antwort.angelegt?.length || 0} Variante(n) gestartet${minuten} — sie rechnen nacheinander.`;
            this._stand = '';
            await this.seite.aktualisieren();
        } catch (fehler) {
            this.meldung.classList.add('fehlertext');
            this.meldung.textContent = `Nicht möglich: ${fehler.daten?.error || fehler.message}`;
        }
    }

    async _einstellung(werte) {
        this.meldung.classList.remove('fehlertext');
        try {
            await this.seite.einstellungSetzen(werte);
            this.meldung.textContent = 'Eingestellt — gilt ab „Neu berechnen“.';
        } catch (fehler) {
            this.meldung.classList.add('fehlertext');
            this.meldung.textContent = `Nicht gespeichert: ${fehler.daten?.error || fehler.message}`;
        }
    }
}
