import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Zeilenwahl } from '../../js/auftraege/zeilenwahl.js';

/**
 * Bildmodellliste — das Dashboard „Modell aus Dateien".
 *
 * Neuer Auftrag: Name, Typ, Bilder (Ablagefeld mit Drag & Drop, Vorschauen
 * sofort) → POST `/api/bildmodell/anlegen/` → sofort starten → zur
 * Auftragsseite. Tabelle: Klick auf eine Zeile öffnet den Auftrag, Kästchen
 * + „Gewählte löschen" (Shift-Bereich über `Zeilenwahl`).
 */
export class Bildmodellliste {

    static ANLEGEN = '/api/bildmodell/anlegen/';
    static LOESCHEN = '/api/bildmodell/loeschen/';

    static aufbauen() {
        const liste = new Bildmodellliste();
        liste.formularBinden();
        liste.tabelleBinden();
        return liste;
    }

    constructor() {
        this.dateien = [];
    }

    // --------------------------------------------------------- Formular

    formularBinden() {
        const form = document.getElementById('bildmodell-form');
        const eingabe = document.getElementById('bildmodell-dateien');
        const ablage = document.getElementById('bildmodell-ablage');
        if (!form || !eingabe || !ablage) return;
        eingabe.addEventListener('change', () => this.dateienSetzen([...eingabe.files]));
        ablage.addEventListener('dragover', e => { e.preventDefault(); ablage.classList.add('aktiv'); });
        ablage.addEventListener('dragleave', () => ablage.classList.remove('aktiv'));
        ablage.addEventListener('drop', e => {
            e.preventDefault();
            ablage.classList.remove('aktiv');
            this.dateienSetzen([...this.dateien, ...[...e.dataTransfer.files]]);
        });
        form.addEventListener('submit', e => { e.preventDefault(); this.anlegen(); });
    }

    static BILD = /\.(jpe?g|png|webp|bmp|tiff?)$/i;
    static VIDEO = /\.(mp4|mov|webm|mkv|avi|m4v)$/i;

    dateienSetzen(dateien) {
        this.dateien = dateien.filter(d => Bildmodellliste.BILD.test(d.name) || Bildmodellliste.VIDEO.test(d.name));
        const feld = document.getElementById('bildmodell-vorschauen');
        feld.innerHTML = '';
        let videos = 0;
        for (const d of this.dateien) {
            // Ein Video als stummes, kurzes Vorschauelement — der Browser zeigt das erste Bild.
            const video = Bildmodellliste.VIDEO.test(d.name);
            const bild = document.createElement(video ? 'video' : 'img');
            bild.className = 'bildmodell-vorschau';
            bild.title = d.name;
            bild.src = URL.createObjectURL(d);
            if (video) { bild.muted = true; bild.preload = 'metadata'; videos += 1; }
            bild.addEventListener(video ? 'loadeddata' : 'load', () => URL.revokeObjectURL(bild.src), { once: true });
            feld.appendChild(bild);
        }
        const bilder = this.dateien.length - videos;
        const teile = [];
        if (bilder) teile.push(`${bilder} Bilder`);
        if (videos) teile.push(`${videos} Videos`);
        this.melden(teile.length ? `${teile.join(' und ')} gewählt` : '');
    }

    melden(text, fehler = false) {
        const m = document.getElementById('bildmodell-meldung');
        if (!m) return;
        m.textContent = text;
        m.classList.toggle('hb-schlecht', fehler);
    }

    async anlegen() {
        const name = document.getElementById('bildmodell-name').value.trim();
        if (!name) { this.melden('Bitte einen Namen angeben', true); return; }
        if (!this.dateien.length) { this.melden('Bitte Bilder wählen', true); return; }
        const daten = new FormData();
        daten.append('name', name);
        daten.append('typ', document.getElementById('bildmodell-typ').value);
        for (const d of this.dateien) daten.append('bilder', d, d.name);
        const knopf = document.getElementById('bildmodell-anlegen');
        knopf.disabled = true;
        this.melden(`${this.dateien.length} Bilder werden hochgeladen …`);
        try {
            const antwort = await Serverabruf.formular(Bildmodellliste.ANLEGEN, daten);
            if (antwort.error) throw new Error(antwort.error);
            await Serverabruf.senden(`/api/bildmodell/${antwort.id}/starten/`, { ab: 'sichtung' });
            window.location.href = antwort.url;
        } catch (fehler) {
            this.melden(`Anlegen fehlgeschlagen: ${fehler.message}`, true);
            knopf.disabled = false;
        }
    }

    // ---------------------------------------------------------- Tabelle

    tabelleBinden() {
        const tabelle = document.querySelector('#auftragsliste table');
        if (!tabelle) return;
        const knopf = document.getElementById('bulk-delete-btn');
        const zaehler = document.getElementById('bulk-count');
        this.wahl = new Zeilenwahl(tabelle, anzahl => {
            if (knopf) knopf.disabled = anzahl === 0;
            if (zaehler) zaehler.textContent = String(anzahl);
        });
        this.wahl.binden();
        tabelle.addEventListener('click', e => {
            const zeile = e.target.closest('tr[data-id]');
            if (!zeile || e.target.closest('input, a, button')) return;
            const link = zeile.querySelector('a[href]');
            if (link) window.location.href = link.getAttribute('href');
        });
        knopf?.addEventListener('click', () => this.loeschen());
    }

    async loeschen() {
        const ids = this.wahl.kennungen();
        if (!ids.length) return;
        if (!window.confirm(`${ids.length} Auftrag/Aufträge samt Bildern löschen?`)) return;
        const antwort = await Serverabruf.senden(Bildmodellliste.LOESCHEN, { ids });
        if (antwort.error) { window.alert(antwort.error); return; }
        window.location.reload();
    }
}
