/**
 * Mesh3dneu — das Formular „Neuer Auftrag“ der Liste Mesh-3D (11.10.2026).
 *
 * Vier Formate (Blender, OBJ, FBX, GLB), je mit den gemerkten Werten des Modell-Imports (`Blendimporteinstellungen.laden`): gezeigt werden nur Pfad,
 * Name und Grundfigur — alles andere übernimmt der Auftrag mit den gemerkten Werten und ist auf seiner Seite einstellbar. „Auftrag anlegen“
 * (`POST /api/mesh3d/anlegen/`) startet nichts; danach geht es auf die Seite des Auftrags.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3dfelder } from './mesh3dfelder.js';
import { Mesh3dwahl } from './mesh3dwahl.js';

export class Mesh3dneu {
    static FORMATE = [['blend', 'Blender (.blend)'], ['fbx', 'FBX'], ['obj', 'OBJ'], ['glb', 'GLB']];
    /** Die Felder, die das Formular zeigt; die übrigen Werte kommen unverändert vom Server. */
    static ZEIGEN = ['pfad', 'name', 'eigener_name', 'basis'];

    static aufbauen() {
        const neu = new Mesh3dneu();
        neu.waehlen('blend');
        return neu;
    }

    constructor() {
        this.leiste = document.getElementById('mesh3d-formate');
        this.felder = document.getElementById('mesh3d-felder');
        this.quelle = document.getElementById('mesh3d-quelle');
        this.knopf = document.getElementById('mesh3d-anlegen');
        this.meldung = document.getElementById('mesh3d-meldung');
        this.format = 'blend';
        this.katalog = {};
        for (const [schluessel, titel] of Mesh3dneu.FORMATE) {
            const knopf = document.createElement('button');
            knopf.type = 'button';
            knopf.setAttribute('role', 'tab');
            knopf.dataset.format = schluessel;
            knopf.textContent = titel;
            knopf.addEventListener('click', () => this.waehlen(schluessel));
            this.leiste.appendChild(knopf);
        }
        this.knopf.addEventListener('click', () => this.anlegen());
        // Neues Netz von der Platte: Datei oder Ordner hochladen, der Pfad der gelesenen Datei kommt ins Feld „Pfad“ (Edgar: „den Import eines neuen Meshes vergessen“).
        this.wahl = new Mesh3dwahl(document.getElementById('mesh3d-wahl'), antwort => this.hochgeladen(antwort));
    }

    hochgeladen(antwort) {
        if (this.werte) this.werte.pfad = antwort.pfad;
        const feld = this.felder.querySelector('[data-schluessel="pfad"]');
        if (feld) feld.value = antwort.pfad;
        this.pruefen();
    }

    async waehlen(format) {
        this.format = format;
        this.wahl.setzen(format);
        this.leiste.querySelectorAll('button').forEach(k => k.setAttribute('aria-selected', String(k.dataset.format === format)));
        this.meldung.textContent = '';
        try {
            if (!this.katalog[format]) this.katalog[format] = await Serverabruf.json(`/api/character/blendimport/einstellungen/?format=${encodeURIComponent(format)}`);
        } catch (fehler) {
            this.felder.replaceChildren();
            this.quelle.textContent = `Katalog nicht lesbar: ${fehler.message}`;
            return;
        }
        const daten = this.katalog[format];
        this.werte = { ...daten.werte };
        const sichtbar = daten.optionen.filter(o => Mesh3dneu.ZEIGEN.includes(o.schluessel));
        Mesh3dfelder.bauen(this.felder, sichtbar, this.werte, () => this.pruefen());
        this.pruefen();
    }

    /** Die gezeigten Felder über die gemerkten Werte legen. */
    werteLesen() {
        return { ...this.werte, ...Mesh3dfelder.lesen(this.felder) };
    }

    /** Welche Datei gelesen wird und wie die Figur heißt — sichtbar, bevor ein Auftrag entsteht (derselbe Endpunkt wie der Dialog der Charakter-Seite). */
    async pruefen() {
        const werte = this.werteLesen();
        this.quelle.classList.remove('fehlertext');
        if (!werte.pfad) { this.quelle.textContent = 'Ordner oder Datei angeben.'; return null; }
        try {
            const q = await Serverabruf.senden('/api/character/blendimport/pruefen/', { ...werte, format: this.format });
            const andere = q.kandidaten.slice(1).map(k => k.datei).join(', ');
            this.quelle.textContent = `Liest ${q.kandidaten[0].datei} (${q.kandidaten[0].mb} MB) — Figur „${q.name}“${andere ? ` · nicht gelesen: ${andere}` : ''}`;
            return q;
        } catch (fehler) {
            this.quelle.textContent = fehler.message;
            this.quelle.classList.add('fehlertext');
            return null;
        }
    }

    async anlegen() {
        this.knopf.disabled = true;
        this.meldung.textContent = 'Wird angelegt …';
        try {
            const antwort = await Serverabruf.senden('/api/mesh3d/anlegen/', { format: this.format, werte: this.werteLesen() });
            if (antwort.error) throw new Error(antwort.error);
            window.location.href = `/mesh-3D/${antwort.kennung}/`;
        } catch (fehler) {
            this.meldung.textContent = `Nicht angelegt: ${fehler.message}`;
            this.knopf.disabled = false;
        }
    }
}
