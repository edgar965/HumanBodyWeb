import { Engine2d3dKleiderlaeufelayout } from './engine2d3dkleiderlaeufelayout.js';
import { Engine2d3dKleiderLaufanzeige } from './engine2d3dkleiderlaufanzeige.js';
import { Engine2d3dKleiderlaufzeit } from './engine2d3dkleiderlaufzeit.js';

/**
 * Engine2d3dKleiderrenderlaeufe — die Render-Läufe des Auftrags als eigene Tabelle unter dem Render-Schritt (04.10.2026).
 *
 * Edgar: „als nächstes, iterativ — evtl. mit getrenntem Abschnitt — die Render jobs. Rendere erstmal nur 10 Frames und verbessere die Qualität … wenn
 * die ersten 10 Frames gut sind, nimm 30, und dann das ganze BVH." Jeder fertige Lauf bleibt (`Engine2d3dKleiderrenderlaeufe` auf dem Server): ein
 * Bogen mit vier Bildern, das Video, die Anmerkung, was gegenüber dem Lauf davor geändert wurde. Neueste zuerst; die Zeilen ändern sich nur, wenn
 * ein Lauf dazukommt (der Zustand kommt im Takt, ein Neuaufbau je Takt flackerte).
 */
export class Engine2d3dKleiderrenderlaeufe {

    /** Schlüssel und Überschrift je Spalte, in der Reihenfolge der Tabelle. Die Schlüssel nie umbenennen: Unter ihnen liegen die gemerkten Breiten. */
    static SPALTEN = [
        ['lauf', 'Lauf'], ['aktion', 'Aktion'], ['bilder', 'Bilder'], ['groesse', 'Größe · Proben'], ['erstellungszeit', 'Erstellungszeit'],
        ['gelaufen', 'Gelaufen am'], ['verzeichnis', 'Verzeichnis'], ['dateiname', 'Dateiname'], ['bogen', 'Bogen'], ['anmerkung', 'Anmerkung'],
    ];
    /** Spalten ohne Sortierung (Knöpfe und Bilder). */
    static OHNE_SORT = ['aktion', 'bogen'];

    /** @param seite `Engine2d3dKleiderseite`, @param neuRendern `async (nummern | 'alle') => …` — vom Render-Schritt (`Engine2d3dKleiderrender.neu`) */
    constructor(seite, neuRendern) {
        this.seite = seite;
        this.neuRendern = neuRendern;
        this.feld = document.getElementById('render-laeufe');
        this._stand = '';
        this._gesperrt = false;
        this._grund = '';
        this._layoutDa = false;
        this._wartend = null;
        this._anzeige = null;                   // die Anzeige „läuft" (`Engine2d3dKleiderLaufanzeige`) in der Zeile des laufenden Renders
        this.layout = new Engine2d3dKleiderlaeufelayout();
        this.layout.bereit.then(() => {
            this._layoutDa = true;
            if (this._wartend) this.zeigen(...this._wartend);
        });
        // Ein Zuhörer für alle Knöpfe: Die Zeilen werden bei jedem neuen Lauf neu gebaut, der Rahmen `feld` bleibt.
        this.feld.addEventListener('click', ereignis => {
            const knopf = ereignis.target.closest('.engine2d3dkleider-neu');
            if (knopf && !knopf.disabled) this._neu(knopf.dataset.nr === 'alle' ? 'alle' : [Number(knopf.dataset.nr)]);
        });
    }

    /** Jeder Lauf wird mit seinen eigenen Einstellungen und dem Modell von heute noch einmal gerechnet und ERSETZT seine Zeile — vorher fragen. */
    _neu(wahl) {
        const alle = wahl === 'alle';
        const text = alle
            ? `Alle ${this._anzahl} Läufe nacheinander neu rendern?\n\nJeder Lauf wird mit seinen eigenen Einstellungen und dem heutigen Modell gerechnet; `
                + 'Video und Bogen der Zeilen werden ersetzt. Das dauert, je nach Länge der Läufe, lange.'
            : `Lauf #${wahl[0]} neu rendern?\n\nMit denselben Einstellungen und dem heutigen Modell; Video und Bogen dieser Zeile werden ersetzt.`;
        if (window.confirm(text)) this.neuRendern(wahl);
    }

    /** Die Knöpfe sperren, solange gerechnet wird oder der Auftrag nicht rendern kann (`grund` steht als Hinweis am Knopf). */
    sperren(gesperrt, grund = '') {
        this._gesperrt = !!gesperrt;
        this._grund = grund;
        for (const knopf of this.feld.querySelectorAll('.engine2d3dkleider-neu')) this._knopf(knopf);
    }

    _knopf(knopf) {
        knopf.disabled = this._gesperrt;
        knopf.title = this._gesperrt ? (this._grund || 'Es läuft schon ein Render')
            : knopf.dataset.nr === 'alle' ? 'Alle Läufe nacheinander mit ihren Einstellungen und dem heutigen Modell neu rendern (ersetzt die Zeilen)'
                : `Lauf #${knopf.dataset.nr} mit denselben Einstellungen und dem heutigen Modell neu rendern (ersetzt diese Zeile)`;
    }

    _neuKnopf(nr, beschriftung) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-outline-secondary btn-sm engine2d3dkleider-neu';
        knopf.dataset.nr = String(nr);
        const symbol = document.createElement('i');
        symbol.className = 'fas fa-rotate-right';
        knopf.append(symbol, ` ${beschriftung}`);
        this._knopf(knopf);
        return knopf;
    }

    /**
     * @param laeufe die Läufe des Zustands (`render.laeufe`)
     * @param aktiv  der Render-Stand (`render`), solange ein Render läuft, sonst null — dann steht in der Zeile dieses Laufs (bei „Neu" die ersetzte, sonst eine
     *               vorläufige oberste Zeile) eine sichtbare Anzeige mit Fortschritt (04.10.2026, Edgar: „mach eine sichtbare UI wenn ein Render lauf läuft, in der Zeile wo der läuft")
     */
    zeigen(laeufe, aktiv = null) {
        if (!this._layoutDa) {                  // erst bauen, wenn die gemerkten Breiten vom Server im Browser stehen (djangoBase bindet die Tabelle gleich nach dem Bauen)
            this._wartend = [laeufe, aktiv];
            return;
        }
        const liste = laeufe || [];
        const nr = aktiv ? Number(aktiv.neu_nr) || Math.max(0, ...liste.map(l => Number(l.nr) || 0)) + 1 : 0;      // Nummer des laufenden Laufs
        // auch ein ERSETZTER Lauf (gleiche Nummer, neue Zeit) baut neu; ebenso Beginn und Ende eines Renders (der Fortschritt dazwischen ändert nur die Anzeige)
        const stand = liste.map(l => `${l.nr}:${l.zeit}`).join(',') + (nr ? `|laeuft:${nr}` : '');
        if (stand === this._stand) {
            this._fortschritt(aktiv);
            return;
        }
        this._stand = stand;
        this._anzahl = liste.length;
        this._anzeige = null;
        this.feld.replaceChildren();
        if (!liste.length && !nr) return;
        const titel = document.createElement('div');
        titel.className = 'hb-hinweis engine2d3dkleider-lauftitel';
        const text = document.createElement('span');
        text.textContent = `Render-Läufe (${liste.length}) — neueste zuerst${nr ? ` · Lauf #${nr} läuft` : ''}`;
        titel.append(text, this._neuKnopf('alle', 'Alle neu rendern'));
        // djangoBase-Tabelle (04.10.2026, Edgar: „Tabelle als djangoBase (sortierbar)"): `sortable` + `data-sort-key`; den Rest bindet `tabellen_auto.js`
        // (Beobachter, sobald die Kopfzeile da ist). Die Sortierung nimmt `data-sort` an der Zelle, die Anzeige darf formatiert sein.
        const rahmen = document.createElement('div');
        rahmen.className = 'db-tabelle-rahmen engine2d3dkleider-laufrahmen';
        // Der Rahmen lässt sich mit dem Griff unten rechts aufziehen (`resize: both`); Größe und Spaltenbreiten bleiben auf dem Server und im Browser (`Engine2d3dKleiderlaeufelayout`).
        this.layout.anwenden(rahmen);
        const tabelle = document.createElement('table');
        tabelle.className = 'db-tabelle sortable';
        tabelle.dataset.sortKey = 'engine2d3dkleider-render-laeufe';
        const kopf = tabelle.createTHead().insertRow();
        // `data-key` je Spalte (04.10.2026, Edgar: „merke dir die Spaltenbreiten"): `TabellenBreiten` und `TabellenSortierung` merken unter diesem Schlüssel,
        // sonst unter dem Spaltenindex — dann rutschten gezogene Breiten auf die falsche Spalte, sobald eine Spalte dazukommt (wie mit Verzeichnis und
        // Dateiname).
        for (const [schluessel, text] of Engine2d3dKleiderrenderlaeufe.SPALTEN) {
            const zelle = document.createElement('th');
            zelle.textContent = text;
            zelle.dataset.key = schluessel;
            if (Engine2d3dKleiderrenderlaeufe.OHNE_SORT.includes(schluessel)) zelle.dataset.sortAus = '1';
            kopf.appendChild(zelle);
        }
        const koerper = tabelle.createTBody();
        if (nr && !liste.some(l => Number(l.nr) === nr)) this._laufzeile(koerper.insertRow(), nr, aktiv);      // neuer Lauf: noch keine Zeile, die vorläufige steht oben
        for (const lauf of liste) this._zeile(koerper.insertRow(), lauf, Number(lauf.nr) === nr ? aktiv : null);
        rahmen.appendChild(tabelle);
        this.feld.append(titel, rahmen);
        this._fortschritt(aktiv);
    }

    // ------------------------------------------------------------------ Anzeige „läuft"

    /** Die Anzeige „läuft" anlegen (ein Block je Tabelle) und ihr Element zurückgeben; ihr Inhalt kommt von `_fortschritt`. */
    _neueAnzeige() {
        this._anzeige = new Engine2d3dKleiderLaufanzeige();
        return this._anzeige.block;
    }

    /** Prozent, Schritt, vergangene Zeit und Warteschlange in die Anzeige schreiben — ohne die Tabelle neu zu bauen (der Zustand kommt im Takt). */
    _fortschritt(r) {
        if (r && this._anzeige) this._anzeige.zeigen(r);
    }

    /** Die vorläufige Zeile eines Laufs, der noch keine Zeile hat: Nummer, Anzeige, Bilder und „seit wann"; der Rest bleibt leer, bis der Lauf fertig ist. */
    _laufzeile(zeile, nr, r) {
        zeile.classList.add('engine2d3dkleider-laeuft');
        zeile.dataset.nr = String(nr);
        const nummer = zeile.insertCell();
        nummer.dataset.sort = String(nr);
        nummer.textContent = `#${nr}`;
        zeile.insertCell().appendChild(this._neueAnzeige());
        if (r && r.bilder) zeile.insertCell().textContent = `${r.bilder} (${String(r.sekunden).replace('.', ',')} s)`;
        while (zeile.cells.length < Engine2d3dKleiderrenderlaeufe.SPALTEN.length) zeile.insertCell();
        const wann = zeile.cells[Engine2d3dKleiderrenderlaeufe.SPALTEN.findIndex(([schluessel]) => schluessel === 'gelaufen')];
        wann.dataset.sort = String(Date.now());
        wann.textContent = r && r.start ? `läuft seit ${Engine2d3dKleiderlaufzeit.uhr(new Date(r.start * 1000))}` : 'läuft';
    }

    _adresse(name) {
        return this.seite.dateiAdresse('ergebnis', name);
    }

    /** @param aktiv der Render-Stand, wenn DIESER Lauf gerade neu gerechnet wird (Knopf „Neu"), sonst null: Die Zeile wird hervorgehoben und trägt die Anzeige „läuft". */
    _zeile(zeile, lauf, aktiv = null) {
        zeile.dataset.nr = String(lauf.nr);
        const video = document.createElement('a');
        video.href = this._adresse(lauf.video);
        video.target = '_blank';
        video.textContent = `#${lauf.nr}`;
        video.title = `Video ansehen (${(lauf.bytes / 1048576).toFixed(1)} MB)`;
        const nummer = zeile.insertCell();
        nummer.dataset.sort = String(lauf.nr);
        nummer.appendChild(video);
        const aktion = zeile.insertCell();
        aktion.appendChild(this._neuKnopf(lauf.nr, 'Neu'));
        if (aktiv) {
            zeile.classList.add('engine2d3dkleider-laeuft');
            aktion.appendChild(this._neueAnzeige());
        }
        const bilder = zeile.insertCell();
        bilder.dataset.sort = String(lauf.bilder);
        bilder.textContent = `${lauf.bilder} (${String(lauf.sekunden).replace('.', ',')} s)`;
        zeile.insertCell().textContent = `${lauf.groesse} · ${lauf.spp}`;
        const dauer = zeile.insertCell();
        dauer.dataset.sort = String(lauf.dauer_s);
        dauer.title = `${lauf.dauer_s} s von der Anfrage bis zum fertigen Video (Figurcache, Stoff, Bilder, Ton)`;
        dauer.textContent = Engine2d3dKleiderlaufzeit.dauer(lauf.dauer_s);
        // Wann der Lauf gelaufen ist (04.10.2026, Edgar: „eine neue Spalte mit dem Datum und Uhrzeit … wann die Render Jobs gelaufen sind"): `zeit` ist der Moment, in dem
        // der Lauf fertig abgelegt wurde (`Engine2d3dKleiderrenderlaeufe.eintragen`); der Beginn steht im Hinweis (fertig minus Dauer von der Anfrage bis zum Video).
        const wann = zeile.insertCell();
        const fertig = Engine2d3dKleiderlaufzeit.millisekunden(lauf.zeit);
        wann.dataset.sort = String(fertig);
        wann.textContent = Engine2d3dKleiderlaufzeit.datum(lauf.zeit);
        if (fertig) {
            wann.title = `Fertig um ${Engine2d3dKleiderlaufzeit.uhr(new Date(fertig))}, gestartet um `
                + `${Engine2d3dKleiderlaufzeit.uhr(new Date(fertig - (Number(lauf.dauer_s) || 0) * 1000))} (Dauer ${Engine2d3dKleiderlaufzeit.dauer(lauf.dauer_s)})`;
        }
        // Pfad und Dateiname als Text, damit man sie markieren und kopieren kann (04.10.2026, Edgar: „eine Spalte mit dem Pfad des Directory und
        // eine weitere mit dem Dateinamen"); die Zellen brechen lange Pfade um, statt die Tabelle breiter zu ziehen.
        for (const text of [lauf.verzeichnis || '', lauf.video || '']) {
            const zelle = zeile.insertCell();
            zelle.className = 'engine2d3dkleider-pfadzelle';
            zelle.title = text;
            zelle.textContent = text;
        }
        const bogen = zeile.insertCell();
        if (lauf.blatt) {
            const link = document.createElement('a');
            link.href = this._adresse(lauf.blatt);
            link.target = '_blank';
            const bild = document.createElement('img');
            bild.src = this._adresse(lauf.blatt);
            bild.alt = `Bogen des Laufs ${lauf.nr}`;
            bild.className = 'engine2d3dkleider-laufbogen';
            link.appendChild(bild);
            bogen.appendChild(link);
        }
        zeile.insertCell().textContent = lauf.anmerkung || '';
    }
}
