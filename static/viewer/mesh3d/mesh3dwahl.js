/**
 * Mesh3dwahl — „Datei wählen …“ und „Ordner wählen …“ im Formular „Neuer Auftrag“ (11.10.2026).
 *
 * Edgar: „den Import eines neuen Meshes vergessen“. Der Browser verrät den Pfad einer gewählten Datei nicht — also lädt er sie hoch (`POST /api/mesh3d/hochladen/`, `Mesh3deingang`): eine oder mehrere
 * Dateien (OBJ mit MTL und Bildern) oder ein ganzer Ordner (`webkitdirectory`, der Weg im Ordner geht als `pfade` mit, damit eine OBJ ihre MTL wiederfindet). Die Antwort nennt die Datei, die der
 * Auftrag liest; `beiHochgeladen(antwort)` trägt sie in das Feld „Pfad“ ein. Ein Auftrag entsteht hier nicht — dafür bleibt „Auftrag anlegen“.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Mesh3dwahl {
    static ADRESSE = '/api/mesh3d/hochladen/';
    /** Beilagen, die der Dateidialog neben der Netzdatei zeigt (der Server filtert ohnehin: `Mesh3deingang.BEILAGEN`). */
    static BEILAGEN = ['.mtl', '.png', '.jpg', '.jpeg', '.webp', '.tga', '.bmp', '.tif', '.tiff', '.dds'];

    /**
     * @param {HTMLElement} ziel Behälter (`#mesh3d-wahl`): Knöpfe, versteckte Dateifelder und die Meldungszeile werden hier gebaut
     * @param {(antwort: object) => void} beiHochgeladen
     */
    constructor(ziel, beiHochgeladen) {
        this.ziel = ziel;
        this.beiHochgeladen = beiHochgeladen;
        this.format = 'blend';
        ziel.innerHTML = `
            <button type="button" class="btn btn-secondary btn-sm" data-wahl="datei"><i class="fas fa-file-import"></i> <span>Datei wählen …</span></button>
            <button type="button" class="btn btn-secondary btn-sm" data-wahl="ordner"><i class="fas fa-folder-open"></i> <span>Ordner wählen …</span></button>
            <span class="hb-hinweis" data-meldung></span>
            <input type="file" hidden multiple data-eingabe="datei">
            <input type="file" hidden multiple webkitdirectory data-eingabe="ordner">`;
        this.meldung = ziel.querySelector('[data-meldung]');
        for (const art of ['datei', 'ordner']) {
            const knopf = ziel.querySelector(`[data-wahl="${art}"]`);
            const eingabe = ziel.querySelector(`[data-eingabe="${art}"]`);
            knopf.addEventListener('click', () => eingabe.click());
            eingabe.addEventListener('change', () => this.hochladen(eingabe));
        }
    }

    /** Das Format wählt, welche Datei der Dateidialog anbietet. */
    setzen(format) {
        this.format = format;
        this.ziel.querySelector('[data-eingabe="datei"]').accept = [`.${format}`, ...Mesh3dwahl.BEILAGEN].join(',');
        this.meldung.textContent = '';
    }

    async hochladen(eingabe) {
        const dateien = [...eingabe.files];
        eingabe.value = '';
        if (!dateien.length) return;
        const mb = dateien.reduce((s, d) => s + d.size, 0) / 1e6;
        const form = new FormData();
        form.append('format', this.format);
        form.append('pfade', JSON.stringify(dateien.map(d => d.webkitRelativePath || '')));
        for (const d of dateien) form.append('dateien', d, d.name);
        this.ziel.querySelectorAll('button').forEach(b => { b.disabled = true; });
        this.meldung.classList.remove('fehlertext');
        this.meldung.textContent = `Lade ${dateien.length} Datei(en) hoch (${mb.toFixed(1)} MB) …`;
        try {
            const antwort = await Serverabruf.formular(Mesh3dwahl.ADRESSE, form);
            if (antwort.error) throw new Error(antwort.error);
            this.meldung.textContent = `Hochgeladen: ${antwort.hauptdateien.join(', ')} (${antwort.anzahl} Datei(en), ${antwort.mb} MB`
                + `${antwort.ausgelassen ? `, ${antwort.ausgelassen} andere ausgelassen` : ''}).`;
            this.beiHochgeladen(antwort);
        } catch (fehler) {
            this.meldung.classList.add('fehlertext');
            this.meldung.textContent = `Nicht hochgeladen: ${fehler.daten?.error || fehler.message}`;
        } finally {
            this.ziel.querySelectorAll('button').forEach(b => { b.disabled = false; });
        }
    }
}
