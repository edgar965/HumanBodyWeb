/**
 * Meshgenesisansichtgedaechtnis — merkt die Schaltknöpfe der Seite „Mesh-Genesis“ für das nächste Öffnen (16.10.2026, Edgar: „Merke dir die Einstellungen der Buttons (Textur usw) sobald ich sie gesetzt habe für das
 * nächste Mal“): die Ansichtsart (Oberfläche, Drahtnetz, Textur …) und den Knopf „Rig“. Beide gelten für alle Zeilen und alle Jobs, also EIN Eintrag.
 *
 * Auf dem Server (`/api/ui-prefs/`, Schlüssel `meshgenesis_ansicht` in `AppSettings.ui_prefs`), nicht im `localStorage`: was nur im Browser liegt, hängt an Adresse, Rechner und Profil und ist weg, wenn der Browser
 * die Websitedaten löscht — genau das war Edgars Klage bei der Tabelle von „2D3D Kleider“ („du merkst dir immer noch nicht …“, `Engine2d3dKleiderlaeufelayout`, dasselbe Muster).
 * Die Seite holt den Stand einmal beim Start (`laden`), jeder Klick schickt ihn ganz zurück (`merken`).
 *
 * Seit 17.10.2026 (Edgar: „du merkst dir nicht die letzte Ansicht, z.B. Toggle Pose aus“) auch: „Ziel als Geist“ (`geist`), die Filter der Probenwahl (`nurPruefung`, `schlechtZuerst`), je Job die
 * zuletzt gewählte Probe (`probe: {job: nr}`) und je Job der gewählte Weg zum Rig (`weg: {job: schluessel}` — „Rig → A-Pose → Netz“, „Netz direkt“, „Rig allein“). Viele Klicks kurz hintereinander
 * (Pfeiltasten in der Probenwahl) gehen als EINE Anfrage (`WARTE_MS`).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Meshgenesisansichtgedaechtnis {
    static ADRESSE = '/api/ui-prefs/';
    static SCHLUESSEL = 'meshgenesis_ansicht';
    static WARTE_MS = 400;
    static EREIGNIS = 'meshgenesis-ansicht';
    static _stand = {};
    static _uhr = null;

    /** Der gemerkte Stand (nur lesen). */
    static get stand() {
        return Meshgenesisansichtgedaechtnis._stand;
    }

    /** Einen Eintrag je Job ändern (`probe`, `weg`), die der anderen Jobs bleiben. */
    static merkenJeJob(art, job, wert) {
        const alt = Meshgenesisansichtgedaechtnis._stand[art];
        Meshgenesisansichtgedaechtnis.merken({ [art]: { ...(alt && typeof alt === 'object' ? alt : {}), [job]: wert } });
    }

    /** `{modus?: string, rig?: boolean, geist?, nurPruefung?, schlechtZuerst?, probe?, weg?}` vom Server; wirft nie — ohne Antwort gelten die Vorgaben der Seite. */
    static async laden() {
        try {
            const vorlieben = await Serverabruf.json(Meshgenesisansichtgedaechtnis.ADRESSE);
            const stand = vorlieben?.[Meshgenesisansichtgedaechtnis.SCHLUESSEL];
            Meshgenesisansichtgedaechtnis._stand = stand && typeof stand === 'object' ? stand : {};
        } catch (fehler) {
            console.warn('Mesh-Genesis: gemerkte Ansicht nicht geladen — es gelten die Vorgaben', fehler);
            Meshgenesisansichtgedaechtnis._stand = {};
        }
        return Meshgenesisansichtgedaechtnis._stand;
    }

    /**
     * Einen Teil des Stands ändern (`{modus}` oder `{rig}`), den Rest behalten, und den ganzen Eintrag an den Server schicken (der Server ersetzt nur diesen Schlüssel).
     * Seit 28.10.2026 meldet es den Teil auch auf `document` (`EREIGNIS`): Zeilen mit eigenen Knöpfen (Testseite: `Meshgenesismeshanpassung` über `Meshgenesistestansicht`) folgen so einem Klick in der anderen.
     */
    static merken(teil) {
        const g = Meshgenesisansichtgedaechtnis;
        g._stand = { ...g._stand, ...teil };
        document.dispatchEvent(new CustomEvent(g.EREIGNIS, { detail: teil }));
        clearTimeout(g._uhr);
        g._uhr = setTimeout(() => {
            Serverabruf.senden(g.ADRESSE, { [g.SCHLUESSEL]: g._stand }).catch(fehler => console.warn('Mesh-Genesis: Ansicht nicht gemerkt', fehler));
        }, g.WARTE_MS);
    }
}
