import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Zielnetzlive — das Zielnetz vom Server, je Reglerzug neu geformt, für alle Sichten.
 *
 * Herausgelöst aus `Proportionen3d` (20.09.2026): die Modellsicht oben auf
 * der Seite und das 3D-Popup im Dialog zeigen DASSELBE Netz — eine Anfrage je
 * Zug, nicht zwei. Jede Änderung (Pfeil im Bild, Zahl, Schieber) ruft
 * `nachziehen()`: die aktuellen Werte gehen gebündelt (`WARTEN_MS`) an
 * `zielnetz3d/`, die Antwort geht an alle Zuhörer (`zuhoeren(fn)`). Läuft
 * gerade eine Anfrage, wartet die nächste, bis sie zurück ist (kein Stau).
 * Die erste Antwort bringt Dreiecke und Gewicht mit; sie bleiben hier
 * (`netz`), damit eine Sicht, die später dazukommt, das Netz bauen kann.
 * Der Server formt dasselbe wie der Lauf: Umriss der Fotos (einmal abgelegt)
 * plus die Eingaben — kein Modell-Lauf, nichts wird gespeichert.
 */
export class Zielnetzlive {

    static WARTEN_MS = 120;

    /**
     * @param auftrag  `Bildmodellauftrag` (Adresse)
     * @param werte    `() => {schluessel: cm}` — die aktuellen Eingaben (der Dialog)
     */
    constructor(auftrag, werte) {
        this.auftrag = auftrag;
        this.werte = werte;
        this.zuhoerer = [];
        this.netz = null;          // {dreiecke, gewicht} der ersten Antwort
        this.bericht = {};         // {schluessel: {vorher, ziel, nachher}} in cm
        this.antwort = null;       // die letzte Antwort (Punkte)
        this.text = '';
        this._warte = null;
        this._laeuft = false;
        this._nochmal = false;
    }

    get aktiv() { return this.zuhoerer.length > 0; }

    /** `fn(antwort, netz, text)` — nach jeder Antwort; die letzte sofort, wenn es eine gibt. */
    zuhoeren(fn) {
        this.zuhoerer.push(fn);
        if (this.antwort) fn(this.antwort, this.netz, this.text);
    }

    vergessen(fn) { this.zuhoerer = this.zuhoerer.filter(f => f !== fn); }

    /** Nach jeder Änderung: gebündelt holen. Ohne Zuhörer passiert nichts. */
    nachziehen(sofort = false) {
        if (!this.aktiv) return;
        clearTimeout(this._warte);
        this._warte = setTimeout(() => this.holen(), sofort ? 0 : Zielnetzlive.WARTEN_MS);
    }

    async holen() {
        if (this._laeuft) { this._nochmal = true; return; }
        this._laeuft = true;
        const werte = this.werte();
        try {
            const t = performance.now();
            const antwort = await Serverabruf.senden(this.auftrag.adresse('zielnetz3d/'),
                { proportionen: werte, netz: !this.netz });
            if (antwort.error) throw new Error(antwort.error);
            if (antwort.dreiecke) this.netz = { dreiecke: antwort.dreiecke, gewicht: antwort.gewicht };
            this.antwort = antwort;
            this.bericht = antwort.bericht || {};
            const n = Object.keys(werte).length;
            this.text = `Zielnetz mit Umriss${n ? ` und ${n} Vorgabe${n === 1 ? '' : 'n'}` : ''} — `
                + `${(antwort.anzahl || 0).toLocaleString('de-DE')} Punkte, ${antwort.hoehe_cm} cm, `
                + `Server ${antwort.dauer_ms} ms, gesamt ${Math.round(performance.now() - t)} ms`;
            for (const fn of this.zuhoerer) fn(antwort, this.netz, this.text);
        } catch (fehler) {
            this.text = `Zielnetz nicht geformt: ${fehler.message}`;
            for (const fn of this.zuhoerer) fn(null, this.netz, this.text);
        } finally {
            this._laeuft = false;
            if (this._nochmal) { this._nochmal = false; this.holen(); }
        }
    }

    /** Nach einem Lauf ist die Grundlage neu: Netz vergessen, beim nächsten Zug ganz holen. */
    zuruecksetzen() {
        this.netz = null;
        this.antwort = null;
        this.bericht = {};
    }
}
