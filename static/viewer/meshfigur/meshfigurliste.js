import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from '../mesh/meshoptionenformular.js';
import { Zeilenwahl } from '../../js/auftraege/zeilenwahl.js';

/**
 * Meshfigurliste — Reiter „Mesh to 3D" auf „Modell aus Dateien" (Edgar, 27.09.2026): Formular
 * (Name, EIN Netz samt OBJ-Beilagen, Optionen aus dem Katalog) und Tabelle der Aufträge — gebaut
 * wie `Meshliste`, das Optionsformular ist dasselbe (`Meshoptionenformular`).
 */
export class Meshfigurliste {

    static ANLEGEN = '/api/meshfigur/anlegen/';
    static LOESCHEN = '/api/meshfigur/loeschen/';
    static NETZ = /\.(glb|gltf|obj|ply|stl|off)$/i;
    static BEILAGE = /\.(mtl|png|jpe?g|bin|webp|tga|bmp)$/i;

    static aufbauen() {
        const katalogFeld = document.getElementById('meshfigur-katalog');
        if (!katalogFeld) return null;
        const liste = new Meshfigurliste(JSON.parse(katalogFeld.textContent));
        liste.formularBinden();
        liste.tabelleBinden();
        return liste;
    }

    constructor(katalog) {
        this.katalog = katalog;
        this.dateien = [];
    }

    // ---------------------------------------------------------- Formular

    formularBinden() {
        const form = document.getElementById('meshfigur-form');
        const eingabe = document.getElementById('meshfigur-dateien');
        const ablage = document.getElementById('meshfigur-ablage');
        const optionen = document.getElementById('meshfigur-optionen');
        if (!form || !eingabe || !ablage || !optionen) {
            this.melden('Formular „Mesh to 3D" unvollständig — Seite neu laden', true);
            return;
        }
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
        for (const d of neue) {
            if (Meshfigurliste.NETZ.test(d.name)) {
                this.dateien = this.dateien.filter(x => !Meshfigurliste.NETZ.test(x.name));
                this.dateien.unshift(d);
                const name = document.getElementById('meshfigur-name');
                if (name && !name.value.trim()) name.value = d.name.replace(/\.[^.]+$/, '').split('_')[0];
            } else if (Meshfigurliste.BEILAGE.test(d.name)) {
                this.dateien.push(d);
            }
        }
        this.liste();
        this.melden();
    }

    liste() {
        const feld = document.getElementById('meshfigur-dateiliste');
        if (!feld) return;
        feld.innerHTML = '';
        for (const d of this.dateien) {
            const zeile = document.createElement('div');
            zeile.className = 'meshfigur-datei';
            const netz = Meshfigurliste.NETZ.test(d.name);
            zeile.innerHTML = `<i class="fas ${netz ? 'fa-cube' : 'fa-paperclip'}"></i> `;
            zeile.appendChild(document.createTextNode(`${d.name} (${(d.size / 1048576).toFixed(1)} MB)`));
            const weg = document.createElement('button');
            weg.type = 'button';
            weg.className = 'mesh-fotoentfernen';
            weg.title = 'Entfernen';
            weg.textContent = '×';
            weg.addEventListener('click', () => { this.dateien = this.dateien.filter(x => x !== d); this.liste(); this.melden(); });
            zeile.appendChild(weg);
            feld.appendChild(zeile);
        }
    }

    melden(text, fehler = false) {
        const m = document.getElementById('meshfigur-meldung');
        if (!m) return;
        const netz = this.dateien.find(d => Meshfigurliste.NETZ.test(d.name));
        m.textContent = text ?? (netz ? `Netz: ${netz.name}` : '');
        m.classList.toggle('hb-schlecht', fehler);
    }

    async anlegen() {
        const name = document.getElementById('meshfigur-name').value.trim();
        const netz = this.dateien.filter(d => Meshfigurliste.NETZ.test(d.name));
        if (!name) { this.melden('Bitte einen Namen angeben', true); return; }
        if (netz.length !== 1) { this.melden('Bitte genau ein Netz wählen (GLB, OBJ, PLY, STL, OFF)', true); return; }
        const daten = new FormData();
        daten.append('name', name);
        daten.append('optionen', JSON.stringify(Meshoptionenformular.lesen(document.getElementById('meshfigur-optionen'))));
        for (const d of this.dateien) daten.append('netz', d, d.name);
        const knopf = document.getElementById('meshfigur-anlegen');
        knopf.disabled = true;
        this.melden('Netz wird hochgeladen …');
        try {
            const antwort = await Serverabruf.formular(Meshfigurliste.ANLEGEN, daten);
            if (antwort.error) throw new Error(antwort.error);
            window.location.href = antwort.url;
        } catch (fehler) {
            this.melden(`Anlegen fehlgeschlagen: ${fehler.message}`, true);
            knopf.disabled = false;
        }
    }

    // ----------------------------------------------------------- Tabelle

    tabelleBinden() {
        const tabelle = document.querySelector('#meshfigur-liste table');
        if (!tabelle) return;
        const knopf = document.getElementById('meshfigur-bulk-delete');
        const zaehler = document.getElementById('meshfigur-bulk-count');
        this.wahl = new Zeilenwahl(tabelle, anzahl => {
            if (knopf) knopf.disabled = anzahl === 0;
            if (zaehler) zaehler.textContent = String(anzahl);
        });
        this.wahl.binden();
        // Eigenes Kopfkästchen (`#meshfigur-select-all`) — drei Tabellen stehen zugleich im DOM,
        // `Zeilenwahl` kennt nur `#select-all` (siehe `Meshliste.tabelleBinden`).
        document.getElementById('meshfigur-select-all')?.addEventListener('click', () => {
            const alle = this.wahl.kaesten();
            this.wahl.alleSetzen(!(alle.length > 0 && alle.every(k => k.checked)));
            this.wahl.nachziehen();
        });
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
        if (!window.confirm(`${ids.length} Figur(en) löschen? Gespeicherte Modelle und die Ablage in MeshTo3D bleiben.`)) return;
        try {
            const antwort = await Serverabruf.senden(Meshfigurliste.LOESCHEN, { ids });
            if (antwort.error) throw new Error(antwort.error);
            window.location.reload();
        } catch (fehler) {
            window.alert(`Löschen fehlgeschlagen: ${fehler.message}`);
        }
    }
}
