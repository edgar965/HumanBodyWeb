import { Serverabruf } from './serverabruf.js';

/**
 * Laufbalken — die Fortschrittsbalken in den Auftragstabellen wachsen mit (27.09.2026).
 *
 * Edgar: „mach fortschrittsbalken bei allen Jobs". Zwei Dinge fehlten: die Spur des
 * Balkens (er war 0 px hoch, siehe `Bildmodelltabelle._balken`) und das Nachziehen —
 * die Tabellen zeigten den Fortschritt so, wie er beim Seitenaufruf war.
 *
 * EIN Abruf je Takt für alle drei Reiter (`/api/modell-aus-dateien/laufende/`), nicht
 * einer je Zeile: Die vorhandenen `zustand/`-Endpunkte liefern Bilder, Ergebnis und
 * Pfade mit — bei zwei Sekunden Takt wäre das ein Vielfaches der nötigen Daten.
 *
 * Endet ein Lauf (er steht nicht mehr in der Antwort), wird die Seite EINMAL neu geladen:
 * Erst damit erscheinen Icon, Flächen, Dauer und die Kennzahlen der fertigen Zeile — ein
 * nur umgeschriebener Status würde eine halbe Zeile behaupten.
 *
 * Und umgekehrt (27.09.2026, Edgar: „wo ist der Job? sehe ihn nicht"): Läuft ein Auftrag,
 * der in KEINER Tabelle der Seite steht, wird ebenso neu geladen. Edgars Tab stand seit
 * der Nacht offen; ein Hashwechsel (#mesh / #meshto3d) lädt nichts nach, und die Listen
 * zeigten den Stand von 01:30. Deshalb läuft der Takt jetzt auch dann, wenn beim
 * Seitenaufruf gar nichts lief — nur langsamer (`RUHETAKT_MS`).
 *
 * Die Bereiche, für die das gilt, gibt die Seite mit (`aufbauen(['mesh', …])`): Auf einer
 * Seite, die einen Bereich gar nicht listet, wäre ein fremder Lauf sonst ein Dauerreload.
 * Dagegen zusätzlich die Marke in `sessionStorage` — je Auftrag wird höchstens einmal
 * nachgeladen.
 */
export class Laufbalken {

    static ADRESSE = '/api/modell-aus-dateien/laufende/';
    static TAKT_MS = 2000;
    /** Takt, solange auf der Seite nichts läuft — dann geht es nur um neue Aufträge. */
    static RUHETAKT_MS = 5000;
    /** Schlüssel der Marke „für diesen Auftrag wurde schon nachgeladen". */
    static MARKE = 'laufbalken_nachgeladen';
    /** Wartezeit nach einem Fehlversuch: 5 s, 10 s, 15 s … (wie `Auftragsstatus`). */
    static WARTE_MS = 5000;
    static HOECHSTWARTE_MS = 30000;
    static GRENZE = 60;
    /** Der Text neben dem Balken — länger sprengt die Spalte. */
    static TEXTLAENGE = 60;

    /** @param {string[]|null} bereiche Bereiche dieser Seite („mesh", „meshfigur",
     *  „bildmodell") — für sie wird ein neu aufgetauchter Lauf nachgeladen. */
    static aufbauen(bereiche = null) {
        return new Laufbalken(bereiche).starten();
    }

    constructor(bereiche = null) {
        this.bereiche = bereiche;
        this.fehlversuche = 0;
        this._timer = null;
    }

    /** Die Statuszellen laufender Aufträge — `Bildmodelltabelle._status` setzt das Merkmal. */
    static zellen() {
        return [...document.querySelectorAll('td[data-status="laeuft"]')];
    }

    starten() {
        if (!Laufbalken.zellen().length && !(this.bereiche || []).length) return this;
        this._planen(this._takt());
        return this;
    }

    _takt() {
        return Laufbalken.zellen().length ? Laufbalken.TAKT_MS : Laufbalken.RUHETAKT_MS;
    }

    anhalten() {
        if (this._timer) { clearTimeout(this._timer); this._timer = null; }
    }

    _planen(ms) {
        this.anhalten();
        this._timer = setTimeout(() => this.nachfragen(), ms);
    }

    async nachfragen() {
        const zellen = Laufbalken.zellen();
        let antwort;
        try {
            antwort = await Serverabruf.json(Laufbalken.ADRESSE);
            this.fehlversuche = 0;
        } catch (fehler) {
            this._fehlversuch(fehler);
            return;
        }
        const stand = new Map();
        for (const liste of Object.values(antwort || {})) {
            for (const z of liste || []) stand.set(z.id, z);
        }
        for (const zelle of zellen) {
            const id = zelle.closest('tr[data-id]')?.dataset.id;
            const z = id ? stand.get(id) : null;
            if (!z) { window.location.reload(); return; }   // Lauf beendet — die ganze Zeile ist neu
            Laufbalken.zeigen(zelle, z);
        }
        if (this._neuerLauf(antwort)) { window.location.reload(); return; }
        this._planen(this._takt());
    }

    /** Läuft ein Auftrag eines Bereichs dieser Seite, für den es keine Zeile gibt? */
    _neuerLauf(antwort) {
        let nachgeladen;
        try {
            nachgeladen = new Set(JSON.parse(sessionStorage.getItem(Laufbalken.MARKE) || '[]'));
        } catch { nachgeladen = new Set(); }
        for (const bereich of this.bereiche || []) {
            for (const z of (antwort || {})[bereich] || []) {
                if (document.querySelector(`tr[data-id="${z.id}"]`) || nachgeladen.has(z.id)) continue;
                nachgeladen.add(z.id);
                try {
                    sessionStorage.setItem(Laufbalken.MARKE, JSON.stringify([...nachgeladen]));
                } catch { /* privates Fenster — dann eben ohne Marke */ }
                return true;
            }
        }
        return false;
    }

    /** Balken und Text in einer Statuszelle setzen. `textContent` statt `innerHTML`:
     *  `progress_detail` kommt vom Server und trägt Dateinamen (Lehre aus `Auftragszeile`). */
    static zeigen(zelle, z) {
        const prozent = Math.max(0, Math.min(100, Number(z.progress || 0)));
        const fuellung = zelle.querySelector('.progress-fill-mini');
        if (fuellung) fuellung.style.width = `${prozent}%`;
        const text = zelle.querySelector('.hb-fortschritt');
        if (text) text.textContent = `${prozent} % ${(z.progress_detail || '').slice(0, Laufbalken.TEXTLAENGE)}`;
    }

    _fehlversuch(fehler) {
        this.fehlversuche += 1;
        if (this.fehlversuche >= Laufbalken.GRENZE) {
            console.warn('Laufbalken: Nachfrage aufgegeben', fehler);
            return;
        }
        this._planen(Math.min(Laufbalken.WARTE_MS * this.fehlversuche, Laufbalken.HOECHSTWARTE_MS));
    }
}
