import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';

/**
 * Projektfeld — das Auswahlfeld "Vorgabeprojekt" der Studio-Einstellungen mit
 * den Projektdateien aus dem eingestellten Ordner fuellen.
 *
 * Herausgeloest aus settings_bvh_studio.html (Umbau 16.08.2026): eine sofort
 * ausgefuehrte anonyme Funktion mit zwei ungepruefen `fetch`-Aufrufen
 * hintereinander. Der Ordner steht selbst in den Vorgaben, deshalb die zwei
 * Abrufe: erst die Vorgaben, dann die Dateiliste.
 */
export class Projektfeld {

    static VORGABEN = '/api/ui-prefs/';
    static LISTE = '/api/studio/project-list/';
    /** Endung, die im Anzeigenamen entfaellt. */
    static ENDUNG = /\.studio\.json$/i;

    /**
     * @param {string} feldId    Kennung des <select>
     * @param {string} gewaehlt  Name, der ausgewaehlt sein soll
     */
    static async fuellen(feldId, gewaehlt) {
        const feld = document.getElementById(feldId);
        if (!feld) return null;
        return new Projektfeld(feld, gewaehlt).fuellen();
    }

    constructor(feld, gewaehlt) {
        this.feld = feld;
        this.gewaehlt = gewaehlt;
    }

    async fuellen() {
        for (const name of await this.namen()) {
            const eintrag = new Option(name, name);
            if (name === this.gewaehlt) eintrag.selected = true;
            this.feld.appendChild(eintrag);
        }
        // Auch ohne Liste soll der gespeicherte Name im Feld stehen.
        if (!this.feld.value && this.gewaehlt) this.feld.value = this.gewaehlt;
        return this;
    }

    /** Projektnamen im eingestellten Ordner; leer, wenn nichts erreichbar ist. */
    async namen() {
        try {
            const vorgaben = await Serverabruf.json(Projektfeld.VORGABEN);
            const ordner = vorgaben.studio_project_path || '';
            const daten = await Serverabruf.json(
                `${Projektfeld.LISTE}?dir=${encodeURIComponent(ordner)}`);
            return (daten.files || []).map(
                datei => datei.name.replace(Projektfeld.ENDUNG, ''));
        } catch (fehler) {
            Protokoll.warnung('Einstellungen',
                              'Projektliste nicht ladbar:', fehler.message);
            return [];
        }
    }
}
