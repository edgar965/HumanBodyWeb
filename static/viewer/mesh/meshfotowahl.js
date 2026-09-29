/**
 * Meshfotowahl — Bilder aussuchen: Dateidialog ODER ganzer Ordner (29.09.2026).
 *
 * Edgar: „möchte ich die Fotos der Vorlage ersetzen können (Datei suche - auswahl dialog
 * und Ordner auswahl, dann werden mir alle Bilder gelistet) - bei Bereich „Fotos"".
 *
 * Zwei Wege in EINEM Fenster:
 *   • „Dateien wählen" — der gewohnte Dialog, mehrere Bilder auf einmal.
 *   • „Ordner wählen"  — `webkitdirectory`: der Browser reicht ALLE Dateien des Ordners
 *     (samt Unterordnern) herein; hier bleiben die Bilder übrig, jedes mit Vorschau und
 *     Häkchen. So sucht man nicht im Dateidialog nach dem richtigen Bild, sondern sieht es.
 *
 * Der Browser gibt dabei nie einen Pfad heraus, nur die Dateien selbst — ein Ordner lässt
 * sich also nicht „verknüpfen", seine Bilder werden beim Übernehmen hochgeladen.
 *
 * Aufruf (Promise auf ein Array von `File`, leer = abgebrochen):
 *     const dateien = await Meshfotowahl.oeffnen({ mehrfach: true, titel: 'Fotos hinzufügen' });
 */
export class Meshfotowahl {

    static ENDUNGEN = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'];
    /** Vorschauen kosten Speicher — bei sehr großen Ordnern wird die Liste begrenzt. */
    static HOECHSTENS = 300;

    static istBild(datei) {
        const name = (datei?.name || '').toLowerCase();
        return Meshfotowahl.ENDUNGEN.some((endung) => name.endsWith(endung));
    }

    static oeffnen(wahl = {}) {
        return new Meshfotowahl(wahl).zeigen();
    }

    constructor({ mehrfach = true, titel = 'Bilder wählen', uebernehmen = 'Übernehmen' } = {}) {
        this.mehrfach = mehrfach;
        this.titel = titel;
        this.uebernehmenText = uebernehmen;
        this.dateien = [];
        this.gewaehlt = new Set();
        this._urls = [];
    }

    zeigen() {
        return new Promise((fertig) => {
            this.fertig = fertig;
            this._bauen();
            document.body.appendChild(this.schicht);
        });
    }

    // ------------------------------------------------------------- Aufbau

    _bauen() {
        this.schicht = document.createElement('div');
        this.schicht.className = 'mesh-fotowahl-schicht';
        this.schicht.addEventListener('click', (ereignis) => {
            if (ereignis.target === this.schicht) this._schliessen([]);
        });

        const fenster = document.createElement('div');
        fenster.className = 'mesh-fotowahl';
        fenster.innerHTML = `<h3>${this.titel}</h3>`;

        const knoepfe = document.createElement('div');
        knoepfe.className = 'mesh-fotowahl-knoepfe';
        knoepfe.append(this._quelle('Dateien wählen', 'fa-images', false),
                       this._quelle('Ordner wählen', 'fa-folder-open', true));
        this.hinweis = document.createElement('span');
        this.hinweis.className = 'hb-hinweis';
        this.hinweis.textContent = 'Noch nichts gewählt.';
        knoepfe.appendChild(this.hinweis);

        this.liste = document.createElement('div');
        this.liste.className = 'mesh-fotowahl-liste';

        const fuss = document.createElement('div');
        fuss.className = 'mesh-fotowahl-fuss';
        this.uebernehmen = document.createElement('button');
        this.uebernehmen.type = 'button';
        this.uebernehmen.className = 'btn btn-primary btn-sm';
        this.uebernehmen.disabled = true;
        this.uebernehmen.innerHTML = `<i class="fas fa-check"></i> <span>${this.uebernehmenText}</span>`;
        this.uebernehmen.addEventListener('click', () => this._schliessen(this._auswahl()));
        const abbruch = document.createElement('button');
        abbruch.type = 'button';
        abbruch.className = 'btn btn-secondary btn-sm';
        abbruch.innerHTML = '<i class="fas fa-times"></i> <span>Abbrechen</span>';
        abbruch.addEventListener('click', () => this._schliessen([]));
        fuss.append(this.uebernehmen, abbruch);

        fenster.append(knoepfe, this.liste, fuss);
        this.schicht.appendChild(fenster);
    }

    /** Ein Knopf samt verstecktem `<input type="file">` — mit oder ohne `webkitdirectory`. */
    _quelle(beschriftung, ikon, ordner) {
        const feld = document.createElement('input');
        feld.type = 'file';
        feld.multiple = true;
        feld.style.display = 'none';
        if (ordner) {
            feld.webkitdirectory = true;
            feld.setAttribute('webkitdirectory', '');
        } else {
            feld.accept = 'image/*';
        }
        feld.addEventListener('change', () => this._aufnehmen(Array.from(feld.files || []), ordner));
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-secondary btn-sm';
        knopf.innerHTML = `<i class="fas ${ikon}"></i> <span>${beschriftung}</span>`;
        knopf.addEventListener('click', () => feld.click());
        const huelle = document.createElement('span');
        huelle.append(knopf, feld);
        return huelle;
    }

    // ------------------------------------------------------------- Liste

    _aufnehmen(dateien, ausOrdner) {
        const bilder = dateien.filter(Meshfotowahl.istBild);
        const zuviel = bilder.length > Meshfotowahl.HOECHSTENS;
        this.dateien = bilder.slice(0, Meshfotowahl.HOECHSTENS);
        this.gewaehlt = new Set();
        // Aus dem Dateidialog ist die Auswahl schon getroffen — dort sind alle angehakt.
        // Aus einem Ordner kommt oft viel mehr, als gemeint war: nichts vorwählen.
        if (!ausOrdner) this.dateien.forEach((_, i) => this.gewaehlt.add(i));
        this.hinweis.textContent = bilder.length
            ? `${bilder.length} Bild(er) gefunden${zuviel ? `, die ersten ${Meshfotowahl.HOECHSTENS} werden gezeigt` : ''}.`
            : 'Keine Bilder darin gefunden.';
        this._listeZeichnen();
    }

    _listeZeichnen() {
        this._urlsFreigeben();
        this.liste.innerHTML = '';
        this.dateien.forEach((datei, i) => {
            const karte = document.createElement('label');
            karte.className = 'mesh-fotowahl-karte';
            const haken = document.createElement('input');
            haken.type = this.mehrfach ? 'checkbox' : 'radio';
            haken.name = 'mesh-fotowahl';
            haken.checked = this.gewaehlt.has(i);
            haken.addEventListener('change', () => {
                if (!this.mehrfach) this.gewaehlt.clear();
                if (haken.checked) this.gewaehlt.add(i); else this.gewaehlt.delete(i);
                if (!this.mehrfach) this._listeZeichnen();
                this._standAktualisieren();
            });
            const url = URL.createObjectURL(datei);
            this._urls.push(url);
            const bild = document.createElement('img');
            bild.src = url;
            bild.loading = 'lazy';
            bild.alt = datei.name;
            const name = document.createElement('span');
            name.className = 'mesh-fotowahl-name';
            // `webkitRelativePath` zeigt den Weg im gewählten Ordner — bei gleichnamigen
            // Bildern aus Unterordnern ist der Dateiname allein nicht unterscheidbar.
            name.textContent = datei.webkitRelativePath || datei.name;
            name.title = name.textContent;
            karte.append(haken, bild, name);
            this.liste.appendChild(karte);
        });
        this._standAktualisieren();
    }

    _standAktualisieren() {
        this.uebernehmen.disabled = this.gewaehlt.size === 0;
        const anzahl = this.gewaehlt.size;
        this.uebernehmen.querySelector('span').textContent =
            anzahl > 1 ? `${this.uebernehmenText} (${anzahl})` : this.uebernehmenText;
    }

    _auswahl() {
        return Array.from(this.gewaehlt).sort((a, b) => a - b).map((i) => this.dateien[i]);
    }

    // ------------------------------------------------------------- Schluss

    _urlsFreigeben() {
        this._urls.forEach((url) => URL.revokeObjectURL(url));
        this._urls = [];
    }

    _schliessen(ergebnis) {
        this._urlsFreigeben();
        this.schicht.remove();
        this.fertig(ergebnis);
    }
}
