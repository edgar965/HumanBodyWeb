import { Auftragduplizieren } from '../gemeinsam/auftragduplizieren.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Zeilenwahl } from '../../js/auftraege/zeilenwahl.js';

/**
 * Haarengineliste — die Seite „Haar Engine": das Formular „Neuer Auftrag" (Name, Fotos mit Rollen) und die Tabelle der
 * Aufträge (Duplizieren, Löschen).
 *
 * Das Formular ist das des Reiters „Mesh" (`Meshliste.formularBinden`) ohne die Optionen: Sie stehen auf der Auftragsseite und
 * werden dort sofort gespeichert. Der Auftrag startet nicht von selbst (`starten=0`) — gerechnet wird mit „Neu berechnen" auf seiner
 * Seite. Die Tabelle ist die von BlenderModel (`Blendermodellliste.tabelleBinden`).
 */
export class Haarengineliste {

    static ANLEGEN = '/api/haarengine/anlegen/';
    static LOESCHEN = '/api/haarengine/loeschen/';
    static BILD = /\.(jpe?g|png|webp|bmp|tiff?)$/i;

    static aufbauen() {
        if (!document.getElementById('haarengine-liste')) return null;
        const rollenFeld = document.getElementById('haarengine-rollen');
        const liste = new Haarengineliste(rollenFeld ? JSON.parse(rollenFeld.textContent) : []);
        liste.formularBinden();
        liste.tabelleBinden();
        return liste;
    }

    /** @param rollen [{wert, text}] — die Rollen der Bildauswahl (`Meshoptionen.ROLLEN`) */
    constructor(rollen) {
        this.rollenListe = rollen;
        this.dateien = [];
        this.rollen = new Map();
    }

    // --------------------------------------------------------- Formular

    formularBinden() {
        const form = document.getElementById('haarengine-form');
        const eingabe = document.getElementById('haarengine-dateien');
        const ablage = document.getElementById('haarengine-ablage');
        if (!form || !eingabe || !ablage) return;
        eingabe.addEventListener('change', () => this.dateienHinzufuegen([...eingabe.files]));
        ablage.addEventListener('dragover', e => { e.preventDefault(); ablage.classList.add('aktiv'); });
        ablage.addEventListener('dragleave', () => ablage.classList.remove('aktiv'));
        ablage.addEventListener('drop', e => {
            e.preventDefault();
            ablage.classList.remove('aktiv');
            this.dateienHinzufuegen([...e.dataTransfer.files]);
        });
        form.addEventListener('submit', e => { e.preventDefault(); this.anlegen(); });
    }

    dateienHinzufuegen(neue) {
        const bilder = neue.filter(d => Haarengineliste.BILD.test(d.name));
        this.dateien.push(...bilder);
        const feld = document.getElementById('haarengine-vorschauen');
        for (const d of bilder) {
            const karte = document.createElement('div');
            karte.className = 'mesh-fotokarte';
            const bild = document.createElement('img');
            bild.className = 'mesh-vorschau';
            bild.title = d.name;
            bild.src = URL.createObjectURL(d);
            bild.addEventListener('load', () => URL.revokeObjectURL(bild.src), { once: true });
            const rolle = document.createElement('select');
            rolle.className = 'viewer-select mesh-rollenwahl';
            for (const eintrag of this.rollenListe) {
                const option = document.createElement('option');
                option.value = eintrag.wert;
                option.textContent = eintrag.text;
                rolle.appendChild(option);
            }
            rolle.addEventListener('change', () => this.rollen.set(d, rolle.value));
            const entfernen = document.createElement('button');
            entfernen.type = 'button';
            entfernen.className = 'mesh-fotoentfernen';
            entfernen.title = 'Entfernen';
            entfernen.textContent = '×';
            entfernen.addEventListener('click', () => {
                this.dateien = this.dateien.filter(x => x !== d);
                this.rollen.delete(d);
                karte.remove();
                this.melden();
            });
            karte.append(bild, rolle, entfernen);
            feld.appendChild(karte);
        }
        // Dieselbe Datei nach dem Entfernen noch einmal wählen können: das Feld vergisst seine Auswahl.
        document.getElementById('haarengine-dateien').value = '';
        this.melden();
    }

    melden(text, fehler = false) {
        const m = document.getElementById('haarengine-meldung');
        if (!m) return;
        m.textContent = text ?? (this.dateien.length ? `${this.dateien.length} Foto(s) gewählt` : '');
        m.classList.toggle('hb-schlecht', fehler);
    }

    async anlegen() {
        const name = document.getElementById('haarengine-name').value.trim();
        if (!name) { this.melden('Bitte einen Namen angeben', true); return; }
        if (!this.dateien.length) { this.melden('Bitte mindestens ein Foto wählen', true); return; }
        const rollen = {};
        for (const d of this.dateien) if (this.rollen.has(d)) rollen[d.name] = this.rollen.get(d);
        const daten = new FormData();
        daten.append('name', name);
        daten.append('rollen', JSON.stringify(rollen));
        daten.append('starten', '0');
        for (const d of this.dateien) daten.append('bilder', d, d.name);
        const knopf = document.getElementById('haarengine-anlegen');
        knopf.disabled = true;
        this.melden(`${this.dateien.length} Foto(s) werden hochgeladen …`);
        try {
            const antwort = await Serverabruf.formular(Haarengineliste.ANLEGEN, daten);
            if (antwort.error) throw new Error(antwort.error);
            window.location.href = antwort.url;
        } catch (fehler) {
            this.melden(`Anlegen fehlgeschlagen: ${fehler.daten?.error || fehler.message}`, true);
            knopf.disabled = false;
        }
    }

    // ----------------------------------------------------------- Tabelle

    tabelleBinden() {
        const tabelle = document.querySelector('#haarengine-liste table');
        if (!tabelle) return;
        const knopf = document.getElementById('haarengine-bulk-delete');
        const zaehler = document.getElementById('haarengine-bulk-count');
        this.wahl = new Zeilenwahl(tabelle, anzahl => {
            if (knopf) knopf.disabled = anzahl === 0;
            if (zaehler) zaehler.textContent = String(anzahl);
            this.duplikat?.anzeigen(anzahl);
        });
        this.duplikat = new Auftragduplizieren('haarengine', 'haarengine-duplizieren',
            'haarengine-duplizieren-count', this.wahl);
        this.wahl.binden();
        // Eigenes Kopfkästchen (`#haarengine-select-all`): `Zeilenwahl` kennt nur `#select-all`, und die anderen Bereiche
        // haben eigene Kennungen, damit keine doppelte ID entsteht.
        document.getElementById('haarengine-select-all')?.addEventListener('click', () => {
            const alle = this.wahl.kaesten();
            this.wahl.alleSetzen(!(alle.length > 0 && alle.every(k => k.checked)));
            this.wahl.nachziehen();
        });
        tabelle.addEventListener('click', e => {
            const zeile = e.target.closest('tr[data-id]');
            if (!zeile || e.target.closest('input, a, button, select')) return;
            const link = zeile.querySelector('a[href]');
            if (link) window.location.href = link.getAttribute('href');
        });
        knopf?.addEventListener('click', () => this.loeschen());
    }

    async loeschen() {
        const ids = this.wahl.kennungen();
        if (!ids.length) return;
        if (!window.confirm(`${ids.length} Auftrag/Aufträge löschen? Gespeicherte Modelle und die Ablage in Haar Engine bleiben.`)) return;
        try {
            const antwort = await Serverabruf.senden(Haarengineliste.LOESCHEN, { ids });
            if (antwort.error) throw new Error(antwort.error);
            window.location.reload();
        } catch (fehler) {
            window.alert(`Löschen fehlgeschlagen: ${fehler.message}`);
        }
    }
}
