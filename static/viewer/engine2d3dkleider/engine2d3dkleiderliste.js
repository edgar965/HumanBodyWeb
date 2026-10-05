import { Auftragduplizieren } from '../gemeinsam/auftragduplizieren.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Zeilenwahl } from '../../js/auftraege/zeilenwahl.js';
import { Engine2d3dKleiderkiwahl } from './engine2d3dkleiderkiwahl.js';
import { Engine2d3dKleiderkopie } from './engine2d3dkleiderkopie.js';
import { Engine2d3dKleiderqualitaet } from './engine2d3dkleiderqualitaet.js';
import { Engine2d3dKleiderweiter } from './engine2d3dkleiderweiter.js';

/**
 * Engine2d3dKleiderliste — die Seite „2D3D Kleider": das Formular „Neuer Auftrag" (Name, Fotos mit Rollen) und die Tabelle der
 * Aufträge (Duplizieren, Löschen).
 *
 * Das Formular ist das des Reiters „Mesh" (`Meshliste.formularBinden`) ohne die Optionen: Sie stehen auf der Auftragsseite und
 * werden dort sofort gespeichert. Der Auftrag startet nicht von selbst (`starten=0`) — gerechnet wird mit „Neu berechnen" auf seiner
 * Seite. Die Tabelle ist die von BlenderModel (`Blendermodellliste.tabelleBinden`).
 */
export class Engine2d3dKleiderliste {

    static ANLEGEN = '/api/engine2d3dkleider/anlegen/';
    static LOESCHEN = '/api/engine2d3dkleider/loeschen/';
    static BILD = /\.(jpe?g|png|webp|bmp|tiff?)$/i;

    static aufbauen() {
        if (!document.getElementById('engine2d3dkleider-liste')) return null;
        const rollenFeld = document.getElementById('engine2d3dkleider-rollen');
        const liste = new Engine2d3dKleiderliste(rollenFeld ? JSON.parse(rollenFeld.textContent) : []);
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
        const form = document.getElementById('engine2d3dkleider-form');
        const eingabe = document.getElementById('engine2d3dkleider-dateien');
        const ablage = document.getElementById('engine2d3dkleider-ablage');
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
        const bilder = neue.filter(d => Engine2d3dKleiderliste.BILD.test(d.name));
        this.dateien.push(...bilder);
        const feld = document.getElementById('engine2d3dkleider-vorschauen');
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
        document.getElementById('engine2d3dkleider-dateien').value = '';
        this.melden();
    }

    melden(text, fehler = false) {
        const m = document.getElementById('engine2d3dkleider-meldung');
        if (!m) return;
        m.textContent = text ?? (this.dateien.length ? `${this.dateien.length} Foto(s) gewählt` : '');
        m.classList.toggle('hb-schlecht', fehler);
    }

    async anlegen() {
        const name = document.getElementById('engine2d3dkleider-name').value.trim();
        // Fotos und Körper aus einem Auftrag „Mesh to 3D" (Kennung) — dann sind eigene Fotos nicht nötig (30.09.2026).
        const meshfigur = (document.getElementById('engine2d3dkleider-meshfigur')?.value || '').trim();
        if (!name) { this.melden('Bitte einen Namen angeben', true); return; }
        if (!this.dateien.length && !meshfigur) { this.melden('Bitte mindestens ein Foto wählen oder einen Auftrag „Mesh to 3D" nennen', true); return; }
        const rollen = {};
        for (const d of this.dateien) if (this.rollen.has(d)) rollen[d.name] = this.rollen.get(d);
        const daten = new FormData();
        daten.append('name', name);
        daten.append('rollen', JSON.stringify(rollen));
        daten.append('starten', '0');
        if (meshfigur) daten.append('meshfigur', meshfigur);
        for (const d of this.dateien) daten.append('bilder', d, d.name);
        const knopf = document.getElementById('engine2d3dkleider-anlegen');
        knopf.disabled = true;
        this.melden(this.dateien.length ? `${this.dateien.length} Foto(s) werden hochgeladen …` : 'Auftrag wird angelegt …');
        try {
            const antwort = await Serverabruf.formular(Engine2d3dKleiderliste.ANLEGEN, daten);
            if (antwort.error) throw new Error(antwort.error);
            window.location.href = antwort.url;
        } catch (fehler) {
            this.melden(`Anlegen fehlgeschlagen: ${fehler.daten?.error || fehler.message}`, true);
            knopf.disabled = false;
        }
    }

    // ----------------------------------------------------------- Tabelle

    tabelleBinden() {
        const tabelle = document.querySelector('#engine2d3dkleider-liste table');
        if (!tabelle) return;
        const knopf = document.getElementById('engine2d3dkleider-bulk-delete');
        const zaehler = document.getElementById('engine2d3dkleider-bulk-count');
        this.wahl = new Zeilenwahl(tabelle, anzahl => {
            if (knopf) knopf.disabled = anzahl === 0;
            if (zaehler) zaehler.textContent = String(anzahl);
            this.duplikat?.anzeigen(anzahl);
            this.kopie?.anzeigen(anzahl);
            this.weiter?.anzeigen(anzahl);
        });
        this.duplikat = new Auftragduplizieren('engine2d3dkleider', 'engine2d3dkleider-duplizieren',
            'engine2d3dkleider-duplizieren-count', this.wahl);
        this.kopie = new Engine2d3dKleiderkopie(this.wahl);
        this.weiter = new Engine2d3dKleiderweiter(this.wahl);
        this.wahl.binden();
        // Eigenes Kopfkästchen (`#engine2d3dkleider-select-all`): `Zeilenwahl` kennt nur `#select-all`, und die anderen Bereiche
        // haben eigene Kennungen, damit keine doppelte ID entsteht.
        document.getElementById('engine2d3dkleider-select-all')?.addEventListener('click', () => {
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
        // „Qualität Mesh" / „Qualität 3D": Handwertung direkt in der Zeile, ohne Neuberechnung (03.10.2026).
        Engine2d3dKleiderqualitaet.binden(tabelle);
        // „KI": die Wahl des Formmodells (TRELLIS.2 / Pixal3D / Pixal3D Mehrbild) direkt in der Zeile (03.10.2026).
        Engine2d3dKleiderkiwahl.binden(tabelle);
        knopf?.addEventListener('click', () => this.loeschen());
    }

    async loeschen() {
        const ids = this.wahl.kennungen();
        if (!ids.length) return;
        if (!window.confirm(`${ids.length} Auftrag/Aufträge löschen? Gespeicherte Modelle und die Ablage in 2D3D Kleider bleiben.`)) return;
        try {
            const antwort = await Serverabruf.senden(Engine2d3dKleiderliste.LOESCHEN, { ids });
            if (antwort.error) throw new Error(antwort.error);
            window.location.reload();
        } catch (fehler) {
            window.alert(`Löschen fehlgeschlagen: ${fehler.message}`);
        }
    }
}
