/**
 * Mesh3dseite — die Jobseite „Mesh-3D“ (11.10.2026): fragt den Zustand des Auftrags im Takt und verteilt ihn an die Karten.
 *
 * Ein Auftrag ist ein Modell-Import (`Blendimportlauf`); der Zustand kommt von `/api/mesh3d/<kennung>/zustand/` (`Mesh3dzustand`). Jede Karte ist ein eigenes Modul mit
 * `zeigen(z)` und zeichnet nur neu, wenn sich ihr Teil des Zustands geändert hat. Fehler zeigt das Fehlerband, bis jemand OK klickt (`gemeinsam/fehlerband.js`).
 * Ein verdeckter Tab fragt nicht (`document.hidden`): dort `window.__mesh3d.aktualisieren()` von Hand rufen.
 */
import { Fehlerband } from '../gemeinsam/fehlerband.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3dbuehne } from './mesh3dbuehne.js';
import { Mesh3dfigur } from './mesh3dfigur.js';
import { Mesh3dhaut } from './mesh3dhaut.js';
import { Mesh3diterationen } from './mesh3diterationen.js';
import { Mesh3dkopie } from './mesh3dkopie.js';
import { Mesh3dlauf } from './mesh3dlauf.js';
import { Mesh3dmodell } from './mesh3dmodell.js';
import { Mesh3dpose } from './mesh3dpose.js';
import { Mesh3dquelle } from './mesh3dquelle.js';
import { Mesh3drollen } from './mesh3drollen.js';
import { Mesh3dsegmentierung } from './mesh3dsegmentierung.js';
import { Mesh3dstuecke } from './mesh3dstuecke.js';
import { Mesh3dvarianten } from './mesh3dvarianten.js';

export class Mesh3dseite {
    static TAKT_LAUFT_MS = 2000;
    static TAKT_RUHT_MS = 6000;

    static starten(kennung, format) {
        const seite = new Mesh3dseite(kennung, format);
        window.__mesh3d = seite;
        seite.aktualisieren();
        return seite;
    }

    constructor(kennung, format) {
        this.kennung = kennung;
        this.format = format;
        this.zustand = null;
        this.fehlerband = new Fehlerband();
        this.lauf = new Mesh3dlauf(this);
        this.buehne = new Mesh3dbuehne(this);
        this.quelle = new Mesh3dquelle(this);
        // Die Karte „Empfehlungen und Varianten“ steht hinter der Bühne: sie schaltet die „Ausgabe“ über der 3D-Ansicht (`buehne.ausgabeWaehlen`).
        this.karten = [this.lauf, this.buehne, this.quelle, new Mesh3dvarianten(this), new Mesh3drollen(), new Mesh3dsegmentierung(this), new Mesh3dpose(this), new Mesh3dfigur(), new Mesh3dstuecke(),
            new Mesh3dhaut(), new Mesh3dmodell(this), new Mesh3diterationen()];
        this._timer = null;
        this._laeuft = false;
        // Kopie dieses Auftrags (ohne / mit allen Daten): danach geht es auf die Seite der Kopie.
        this.kopie = new Mesh3dkopie(() => [this.kennung], [
            { knopf: 'auftrag-kopie-ohne', mitDaten: false }, { knopf: 'auftrag-kopie-alles', mitDaten: true }], true);
    }

    async aktualisieren() {
        window.clearTimeout(this._timer);
        try {
            const z = await Serverabruf.json(`/api/mesh3d/${this.kennung}/zustand/`);
            this.zustand = z;
            this.fehlerband.auftrag({ status: z.status, error: z.fehler });
            document.title = `Mesh-3D · ${z.name}`;
            this._weg(z);
            for (const karte of this.karten) await karte.zeigen(z);
            this._laeuft = z.status === 'laeuft';
        } catch (fehler) {
            this.fehlerband.lesefehler(`Zustand nicht lesbar: ${fehler.message}`);
        }
        this._timer = window.setTimeout(() => { if (!document.hidden) this.aktualisieren(); else this._takt(); }, this._laeuft ? Mesh3dseite.TAKT_LAUFT_MS : Mesh3dseite.TAKT_RUHT_MS);
    }

    /** Eine Einstellung des Auftrags setzen (`POST …/einstellungen/`, nicht während eines Laufs) und die Felder der Karte „Quelle und Einstellungen“ neu aufbauen — für die Empfehlungen der Karte „Varianten“. */
    async einstellungSetzen(werte) {
        const antwort = await Serverabruf.senden(`/api/mesh3d/${this.kennung}/einstellungen/`, { werte });
        if (antwort.error) throw new Error(antwort.error);
        this.quelle._gebaut = false;
        await this.aktualisieren();
    }

    /** Weg „netz“ (ein verschmolzenes Netz, `Blendimportweg`): die Karten des Wegs „teile“ — Netze und Rollen, Kleider und Haar, Haut — gibt es nicht, sie bleiben weg. */
    _weg(z) {
        for (const id of ['rollen-karte', 'stuecke-karte', 'haut-karte']) document.getElementById(id).hidden = z.weg === 'netz';    }

    /** Im verdeckten Tab wartet der Takt, statt zu fragen. */
    _takt() {
        this._timer = window.setTimeout(() => (document.hidden ? this._takt() : this.aktualisieren()), Mesh3dseite.TAKT_RUHT_MS);
    }
}
