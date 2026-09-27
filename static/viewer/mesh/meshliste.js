import { Auftragduplizieren } from '../gemeinsam/auftragduplizieren.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from './meshoptionenformular.js';
import { Zeilenwahl } from '../../js/auftraege/zeilenwahl.js';

/**
 * Meshliste — Reiter „Mesh" auf „Modell aus Dateien" (Edgar, 26.09.2026): Formular
 * (Name, Fotos mit Rollen, Optionen aus dem Katalog) + Tabelle der Aufträge, wie
 * `Bildmodellliste`, aber mit Foto-Rollen statt Genesis-Bildtypen.
 */
export class Meshliste {

    static ANLEGEN = '/api/mesh/anlegen/';
    static LOESCHEN = '/api/mesh/loeschen/';
    static BILD = /\.(jpe?g|png|webp|bmp|tiff?)$/i;

    static aufbauen() {
        const katalogFeld = document.getElementById('mesh-katalog');
        if (!katalogFeld) return null;
        const liste = new Meshliste(JSON.parse(katalogFeld.textContent));
        liste.formularBinden();
        liste.tabelleBinden();
        return liste;
    }

    constructor(katalog) {
        this.katalog = katalog;
        this.dateien = [];
        this.rollen = new Map();
    }

    // --------------------------------------------------------- Formular

    formularBinden() {
        const form = document.getElementById('mesh-form');
        const eingabe = document.getElementById('mesh-dateien');
        const ablage = document.getElementById('mesh-ablage');
        const optionen = document.getElementById('mesh-optionen');
        if (!form || !eingabe || !ablage || !optionen) return;
        Meshoptionenformular.bauen(optionen, this.katalog);
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
        const bilder = neue.filter(d => Meshliste.BILD.test(d.name));
        this.dateien.push(...bilder);
        const feld = document.getElementById('mesh-vorschauen');
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
            for (const eintrag of this.katalog.rollen) {
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
        this.melden();
    }

    melden(text, fehler = false) {
        const m = document.getElementById('mesh-meldung');
        if (!m) return;
        m.textContent = text ?? (this.dateien.length ? `${this.dateien.length} Foto(s) gewählt` : '');
        m.classList.toggle('hb-schlecht', fehler);
    }

    async anlegen() {
        const name = document.getElementById('mesh-name').value.trim();
        if (!name) { this.melden('Bitte einen Namen angeben', true); return; }
        if (!this.dateien.length) { this.melden('Bitte mindestens ein Foto wählen', true); return; }
        const rollen = {};
        for (const d of this.dateien) if (this.rollen.has(d)) rollen[d.name] = this.rollen.get(d);
        const optionen = Meshoptionenformular.lesen(document.getElementById('mesh-optionen'));
        const daten = new FormData();
        daten.append('name', name);
        daten.append('optionen', JSON.stringify(optionen));
        daten.append('rollen', JSON.stringify(rollen));
        for (const d of this.dateien) daten.append('bilder', d, d.name);
        const knopf = document.getElementById('mesh-anlegen');
        knopf.disabled = true;
        this.melden(`${this.dateien.length} Foto(s) werden hochgeladen …`);
        try {
            const antwort = await Serverabruf.formular(Meshliste.ANLEGEN, daten);
            if (antwort.error) throw new Error(antwort.error);
            window.location.href = antwort.url;
        } catch (fehler) {
            this.melden(`Anlegen fehlgeschlagen: ${fehler.message}`, true);
            knopf.disabled = false;
        }
    }

    // ---------------------------------------------------------- Tabelle

    tabelleBinden() {
        const tabelle = document.querySelector('#mesh-liste table');
        if (!tabelle) return;
        const knopf = document.getElementById('mesh-bulk-delete');
        const zaehler = document.getElementById('mesh-bulk-count');
        this.wahl = new Zeilenwahl(tabelle, anzahl => {
            if (knopf) knopf.disabled = anzahl === 0;
            if (zaehler) zaehler.textContent = String(anzahl);
            this.duplikat?.anzeigen(anzahl);
        });
        this.duplikat = new Auftragduplizieren('mesh', 'mesh-duplizieren', 'mesh-duplizieren-count', this.wahl);
        this.wahl.binden();
        // `Zeilenwahl` sucht das Kopfkästchen fest unter `#select-all` — auf dieser Seite
        // stehen ZWEI Tabellen (Reiter 3D und Mesh) zugleich im DOM, ein zweites `#select-all`
        // wäre eine ungültige Doppel-ID. Das Mesh-Kopfkästchen (`#mesh-select-all`) verdrahten
        // wir deshalb selbst, mit derselben Logik.
        const kopf = document.getElementById('mesh-select-all');
        kopf?.addEventListener('click', () => {
            const alle = this.wahl.kaesten();
            const voll = alle.length > 0 && alle.every(k => k.checked);
            this.wahl.alleSetzen(!voll);
            this.wahl.nachziehen();
        });
        tabelle.addEventListener('click', e => {
            const zeile = e.target.closest('tr[data-id]');
            // `select` gehört dazu: sonst öffnet der Klick auf „Kopf/Körper" die Auftragsseite,
            // bevor man einen Wert wählen kann.
            if (!zeile || e.target.closest('input, a, button, select')) return;
            const link = zeile.querySelector('a[href]');
            if (link) window.location.href = link.getAttribute('href');
        });
        // Kopf/Körper direkt in der Zeile umstellen — ohne Neuberechnung (Edgar, 27.09.2026).
        tabelle.addEventListener('change', e => {
            const feld = e.target.closest('select.mesh-verwendung');
            if (feld) this.verwendungSetzen(feld);
        });
        knopf?.addEventListener('click', () => this.loeschen());
    }

    /** Kopf/Körper eines Auftrags speichern. Scheitert es, springt das Feld auf den alten
     *  Wert zurück — ein stehen gebliebener neuer Wert würde etwas behaupten, was der Server
     *  nicht hat. */
    async verwendungSetzen(feld) {
        const vorher = feld.dataset.vorher || '';
        feld.disabled = true;
        try {
            await Serverabruf.senden(`/api/mesh/${feld.dataset.id}/verwendung/`, { verwendung: feld.value });
            feld.dataset.vorher = feld.value;
            const titel = feld.options[feld.selectedIndex]?.textContent || '';
            feld.title = titel;
            feld.closest('td')?.setAttribute('data-sort', feld.value);
        } catch (fehler) {
            if (vorher) feld.value = vorher;
            window.alert(`Kopf/Körper konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
        } finally {
            feld.disabled = false;
        }
    }

    async loeschen() {
        const ids = this.wahl.kennungen();
        if (!ids.length) return;
        if (!window.confirm(`${ids.length} Mesh(es) löschen?`)) return;
        const antwort = await Serverabruf.senden(Meshliste.LOESCHEN, { ids });
        if (antwort.error) { window.alert(antwort.error); return; }
        window.location.reload();
    }
}
