/**
 * Mesh3danimationswahlfeld — die Standardanimation eines Mesh-3D-Auftrags, zwei Auswahlfelder unter der Animationsleiste (13.10.2026).
 *
 * Edgar: „standardanimation soll bei jedem Job einstellbar sein unterhalb der Animation Controls, standard animation ist danceKurz“. Die Wahl liegt je Auftrag auf dem Server
 * (`POST /api/mesh3d/<kennung>/animation/ {bvh: "Kategorie/Name"}`, `Mesh3danimationswahl`, Vorgabe A_Results/DanceKurz); der Zustand der Seite nennt sie (`z.animation`).
 * Kategorien kommen vom Endpunkt der Wahl, die Einträge einer Kategorie von `/api/animationen/<kategorie>/?wertformat=pfad` (derselbe Bestand wie die Einstellungsseiten).
 *
 * Eine neue Wahl speichert sofort; liegt schon eine Bewegung auf der Figur, rechnet `nachWahl` sie mit der neuen Datei (sonst bliebe die Leiste bei der alten stehen) — ohne Bewegung
 * sagt die Zeile, dass der Knopf „Animation“ sie rechnet. Die Felder bleiben gesperrt, bis die Listen da sind.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Mesh3danimationswahlfeld {
    /**
     * @param {object} seite die Jobseite (`kennung`, `fehlerband`)
     * @param {(wahl: object) => Promise<void>|void} nachWahl wird nach dem Speichern gerufen (`Mesh3dbuehne` rechnet dort die Bewegung neu)
     */
    constructor(seite, nachWahl) {
        this.seite = seite;
        this.nachWahl = nachWahl;
        this.kategorie = document.getElementById('anim-wahl-kategorie');
        this.datei = document.getElementById('anim-wahl-datei');
        this.meldung = document.getElementById('anim-wahl-meldung');
        this.zustand = null;
        this._baut = null;
        this._eintraege = new Map();
        this.kategorie.addEventListener('change', () => this._kategorieGewaehlt());
        this.datei.addEventListener('change', () => this._dateiGewaehlt());
    }

    /** Der Takt der Seite: `z.animation` (`{wahl, kategorie, name, standard, fehlt}`); die Felder bauen sich einmal auf und zeigen danach die gespeicherte Wahl. */
    async zeigen(animation) {
        if (!animation) return;
        if (!this._baut) this._baut = this._aufbauen();
        await this._baut;
    }

    async _aufbauen() {
        try {
            const antwort = await Serverabruf.json(`/api/mesh3d/${this.seite.kennung}/animation/`);
            // Gibt es die gewählte Datei nicht mehr, zeigen die Felder die Vorgabe — die Zeile darunter sagt es.
            const wahl = antwort.fehlt ? antwort.standardwahl : antwort.wahl;
            const kategorie = wahl.split('/')[0];
            this.kategorie.textContent = '';
            for (const k of antwort.kategorien || []) this.kategorie.append(new Option(`${k.name} (${k.anzahl})`, k.name));
            this.kategorie.value = kategorie;
            await this._eintraegeLaden(kategorie);
            this.datei.value = wahl;
            this.zustand = antwort;
            this.kategorie.disabled = this.datei.disabled = false;
            this._text(antwort);
        } catch (fehler) {
            this._baut = null;
            this.seite.fehlerband.lesefehler(`Standardanimation nicht lesbar: ${fehler.message}`);
        }
    }

    /** Die Einträge einer Kategorie in das zweite Feld (nach Namen geordnet, wie die Bibliothek). */
    async _eintraegeLaden(kategorie) {
        if (!this._eintraege.has(kategorie)) {
            const daten = await Serverabruf.json(`/api/animationen/${encodeURIComponent(kategorie)}/?wertformat=pfad`);
            this._eintraege.set(kategorie, daten.animationen || []);
        }
        this.datei.textContent = '';
        for (const a of this._eintraege.get(kategorie)) this.datei.append(new Option(a.label, a.value));
    }

    async _kategorieGewaehlt() {
        this.datei.disabled = true;
        try {
            await this._eintraegeLaden(this.kategorie.value);
        } catch (fehler) {
            this.seite.fehlerband.meldung(`Animationen nicht lesbar: ${fehler.message}`);
        } finally {
            this.datei.disabled = false;
        }
        this.meldung.textContent = 'Eine Animation dieser Kategorie wählen.';
    }

    async _dateiGewaehlt() {
        const wert = this.datei.value;
        if (!wert) return;
        this.kategorie.disabled = this.datei.disabled = true;
        try {
            const antwort = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/animation/`, { bvh: wert });
            if (antwort.error) throw new Error(antwort.error);
            this.zustand = antwort;
            this._text(antwort);
            await this.nachWahl?.(antwort);
        } catch (fehler) {
            this.seite.fehlerband.meldung(`Standardanimation nicht gespeichert: ${fehler.daten?.error || fehler.message}`);
            if (this.zustand) this.datei.value = this.zustand.wahl;
        } finally {
            this.kategorie.disabled = this.datei.disabled = false;
        }
    }

    _text(z) {
        this.meldung.textContent = z.fehlt
            ? `„${z.wahl}“ gibt es nicht mehr in der Bibliothek — gespielt wird ${z.standardwahl}.`
            : (z.standard ? 'Vorgabe dieses Auftrags.' : `Gewählt für diesen Auftrag (Vorgabe: ${z.standardwahl}).`);
    }
}
