/**
 * Exportleisterendergedaechtnis — die Einstellungen des Blocks „Rendern" der Exportleiste für das nächste Öffnen (01.11.2026, Edgar: „beim rendern tab merke dir die letzten Einstellungen,
 * immer das ganze Video und immer mit Ton“): Kamera, Größe (Auswahl, Breite, Höhe), Physik, Proben je Pixel. Nicht die Länge (immer die ganze BVH, `Exportleisterender`) und nicht
 * Ordner und Datei (je Modell vorbelegt).
 *
 * Auf dem Server (`/api/ui-prefs/`, Schlüssel `exportleiste_render` in `AppSettings.ui_prefs`) wie `Mesh3daiansichtgedaechtnis`, nicht im `localStorage` — EIN Eintrag für alle
 * Exportleisten (Mesh3D-AI, 2D3D Kleider …). Geladen einmal beim Aufbau (`laden`), jede Änderung schickt den ganzen Eintrag (`merken`, mehrere kurz hintereinander als eine Anfrage).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Exportleisterendergedaechtnis {
    static ADRESSE = '/api/ui-prefs/';
    static SCHLUESSEL = 'exportleiste_render';
    static WARTE_MS = 400;

    /** `felder`: `{name: Eingabefeld}` in der Reihenfolge, in der sie gesetzt werden (die Größenwahl vor Breite und Höhe). */
    constructor(felder) {
        this.felder = felder;
        this._uhr = null;
        for (const feld of Object.values(felder)) feld.addEventListener('change', () => this.merken());
    }

    /** Den gemerkten Stand in die Felder; wirft nie — ohne Antwort gelten die Vorgaben der Seite. Eine Wahl, die es in der Liste nicht mehr gibt, bleibt auf der Vorgabe. */
    async laden() {
        const g = Exportleisterendergedaechtnis;
        let stand = {};
        try {
            const vorlieben = await Serverabruf.json(g.ADRESSE);
            const eintrag = vorlieben?.[g.SCHLUESSEL];
            stand = eintrag && typeof eintrag === 'object' ? eintrag : {};
        } catch (fehler) {
            console.warn('Exportleiste: gemerkte Render-Einstellungen nicht geladen — es gelten die Vorgaben', fehler);
        }
        for (const [name, feld] of Object.entries(this.felder)) {
            const wert = stand[name];
            if (wert === undefined || wert === null) continue;
            if (feld.type === 'checkbox') feld.checked = !!wert;
            else if (feld.tagName !== 'SELECT' || [...feld.options].some(o => o.value === String(wert))) feld.value = String(wert);
        }
        return stand;
    }

    merken() {
        const g = Exportleisterendergedaechtnis;
        clearTimeout(this._uhr);
        this._uhr = setTimeout(() => {
            const stand = Object.fromEntries(Object.entries(this.felder).map(([name, feld]) => [name, feld.type === 'checkbox' ? feld.checked : feld.value]));
            Serverabruf.senden(g.ADRESSE, { [g.SCHLUESSEL]: stand }).catch(fehler => console.warn('Exportleiste: Render-Einstellungen nicht gemerkt', fehler));
        }, g.WARTE_MS);
    }
}
