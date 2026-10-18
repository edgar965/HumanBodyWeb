import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Modellansichten } from './modellansichten.js';

/**
 * Modellexportordner — Ordner und Dateiname des Exportdialogs (Edgar, 18.10.2026): „Der Exportordner soll
 * A:\3DTools\3DObjects\modelsExport + <Modellname> sein als Default, aber änderbar, mit Folder Suchen Dialog, und
 * Datei ändern. Die Dateinamen so wie das Modell, die jpg zzgl. _vorne, _links, _rechts, _hinten."
 *
 * Der Dialog schreibt GENAU in den angezeigten Ordner (`direkt`), gleichnamige Dateien werden überschrieben —
 * deshalb steht VOR dem Export im Dialog, welche das wären. Keine Rückfrage per `confirm()`: Die blockiert die Seite,
 * und die Liste im Dialog sagt dasselbe, bevor man klickt.
 *
 * „Suchen …" öffnet das Windows-Fenster „Ordner suchen" über den Server (`core/dienste/ordnersuche.py`) — der
 * Browser selbst bekommt aus einer Ordnerwahl keinen Pfad.
 */
export class Modellexportordner {

    static VORGABE = '/api/character/modellexport/vorgabe/';
    static VORHANDEN = '/api/character/modellexport/vorhanden/';
    static SUCHE = '/api/character/modellexport/ordnersuche/';
    //: Die Hauptdateien je Format. Die Bildkarten von OBJ und DAE tragen Materialnamen und stehen nicht darin.
    static ENDUNGEN = {
        json: ['.json'], glb: ['.glb'], blend: ['.blend'], fbx: ['.fbx'], jpg: Modellansichten.endungen(),
        obj: ['.obj', '.mtl'], ply: ['.ply'], stl: ['.stl'], dae: ['.dae'],
    };
    static WARTEN_MS = 300;

    /**
     * @param felder  {ordner, name, knopf, vorhanden} — die Elemente des Dialogs
     * @param formate () => ['glb', …] — die angehakten Formate
     */
    constructor(felder, formate) {
        this.felder = felder;
        this.formate = formate;
        this._uhr = null;
        this._stand = 0;
        felder.knopf?.addEventListener('click', () => this.suchen());
        for (const feld of [felder.ordner, felder.name]) {
            feld?.addEventListener('input', () => this.pruefenBald());
        }
    }

    /** Ordner und Name für eine Figur vorbelegen: `<Vorgabe>/<Modellname>`, Dateiname = Modellname. */
    async vorbelegen(modellname) {
        this.felder.name.value = modellname;
        this.felder.ordner.value = '';
        try {
            const antwort = await Serverabruf.json(`${Modellexportordner.VORGABE}?name=${encodeURIComponent(modellname)}`);
            this.felder.ordner.value = antwort.ordner || '';
        } catch {
            this.felder.ordner.value = '';
        }
        this.pruefen();
    }

    /** Das Fenster „Ordner suchen" — der Knopf ist gesperrt, solange es offen ist. */
    async suchen() {
        const knopf = this.felder.knopf;
        if (knopf) knopf.disabled = true;
        try {
            const antwort = await Serverabruf.senden(Modellexportordner.SUCHE, { start: this.felder.ordner.value.trim() });
            if (antwort.ordner) {
                this.felder.ordner.value = antwort.ordner;
                this.pruefen();
            }
        } catch (fehler) {
            this._zeigen([], `Ordnersuche fehlgeschlagen: ${fehler.message || fehler}`);
        } finally {
            if (knopf) knopf.disabled = false;
        }
    }

    pruefenBald() {
        clearTimeout(this._uhr);
        this._uhr = setTimeout(() => this.pruefen(), Modellexportordner.WARTEN_MS);
    }

    /** Fragt den Server, welche der Dateien schon im Ordner liegen. Ältere Antworten werden verworfen. */
    async pruefen() {
        const ordner = this.felder.ordner.value.trim();
        const name = this.felder.name.value.trim();
        const endungen = this.formate().flatMap((f) => Modellexportordner.ENDUNGEN[f] || []);
        const stand = ++this._stand;
        if (!ordner || !name || !endungen.length) { this._zeigen([]); return; }
        try {
            const antwort = await Serverabruf.senden(Modellexportordner.VORHANDEN, { ordner, name, endungen });
            if (stand === this._stand) this._zeigen(antwort.vorhanden || [], antwort.error);
        } catch {
            if (stand === this._stand) this._zeigen([]);
        }
    }

    _zeigen(vorhanden, fehler = '') {
        const feld = this.felder.vorhanden;
        if (!feld) return;
        feld.textContent = fehler
            ? fehler
            : vorhanden.length ? `Liegt schon im Ordner und wird überschrieben: ${vorhanden.join(', ')}` : '';
        feld.hidden = !feld.textContent;
    }
}
