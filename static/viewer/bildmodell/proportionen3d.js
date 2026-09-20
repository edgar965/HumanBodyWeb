/**
 * Proportionen3d — das 3D-Popup zum Proportionen-Popup: das Zielnetz folgt den Pfeilen.
 *
 * Edgar (20.09.2026): „brauche ich eine Möglichkeit, das 3D Modell interaktiv
 * anzupassen wenn ich die Pfeile ändere. also sowas wie die Morph slider bei
 * Genesis … ein neues Popup, mit dem ich das Genesis Modell sehe, das ich mit
 * diesen Pfeilen als Morph Slider modellieren kann? Dann sehe ich nämlich
 * gleich die ‚Donauwellen' oder andere Fehler."
 *
 * Ein schwebendes Fenster IM Proportionen-Dialog (der ist modal — ein zweiter
 * `<dialog>` daneben wäre unbedienbar), rechts am Bildschirmrand, vergrößerbar:
 * oben das Zielnetz (`Proportionen3dbuehne`), darunter die 19 Maße als
 * Schieber (`Proportionen3dregler`). Jede Änderung — Pfeil im Bild, Zahl in
 * der Tabelle, Schieber hier — ruft `nachziehen()`: die aktuellen Werte gehen
 * gebündelt (120 ms) an `zielnetz3d/`, die Antwort tauscht die Punkte. Läuft
 * gerade eine Anfrage, wartet die nächste, bis sie zurück ist (kein Stau).
 * Der Server formt dasselbe wie der Lauf: Umriss der Fotos (einmal abgelegt)
 * plus die Eingaben — kein Modell-Lauf, nichts wird gespeichert.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Proportionen3dbuehne } from './proportionen3dbuehne.js';
import { Proportionen3dregler } from './proportionen3dregler.js';

export class Proportionen3d {

    static WARTEN_MS = 120;

    /**
     * @param feld      das Fenster (`#proportionen-3d`, im Dialog)
     * @param auftrag   `Auftrag` (Adresse, Zustand)
     * @param katalog   `{proportionen}`
     * @param dialog    der `Proportionendialog` (Werte, Ziel, `wertGeschoben`)
     */
    constructor(feld, auftrag, katalog, dialog) {
        this.feld = feld;
        this.auftrag = auftrag;
        this.dialog = dialog;
        this.buehne = null;
        this.bericht = {};
        this._warte = null;
        this._laeuft = false;
        this._nochmal = false;
        this._netzDa = false;
        if (!this.feld) return;
        this.text = this.feld.querySelector('.bildmodell-3dtext');
        this.regler = new Proportionen3dregler(this.feld.querySelector('.bildmodell-3dregler'), katalog,
            (k, cm) => this.dialog.wertGeschoben(k, cm));
        this.feld.querySelector('[data-tat="3d-schliessen"]')?.addEventListener('click', () => this.schliessen());
        this.feld.querySelector('[data-tat="3d-gitter"]')?.addEventListener('change', e => this.buehne?.gitterZeigen(e.target.checked));
    }

    get offen() { return !!this.feld && !this.feld.hidden; }

    _melden(t) { if (this.text) this.text.textContent = t; }

    oeffnen() {
        if (!this.feld) return;
        if (!this.buehne) {
            try { this.buehne = new Proportionen3dbuehne(this.feld.querySelector('canvas')); }
            catch (fehler) { this._melden(`Keine 3D-Ansicht: ${fehler.message}`); }
        }
        this.feld.hidden = false;
        this.buehne?.starten();
        this.regler.fuellen(this.dialog.werte(), this.dialog.daten().ziel || {}, this.bericht);
        this.nachziehen(true);
    }

    schliessen() {
        if (!this.feld) return;
        this.feld.hidden = true;
        this.buehne?.anhalten();
    }

    umschalten() { if (this.offen) this.schliessen(); else this.oeffnen(); }

    /** Nach jeder Änderung im Dialog: Schieber nachziehen, Netz neu formen lassen. */
    nachziehen(sofort = false) {
        if (!this.offen) return;
        this.regler.aktualisieren(this.dialog.werte(), this.dialog.daten().ziel || {}, this.bericht);
        clearTimeout(this._warte);
        this._warte = setTimeout(() => this._holen(), sofort ? 0 : Proportionen3d.WARTEN_MS);
    }

    async _holen() {
        if (this._laeuft) { this._nochmal = true; return; }
        this._laeuft = true;
        const werte = this.dialog.werte();
        try {
            const t = performance.now();
            const antwort = await Serverabruf.senden(this.auftrag.adresse('zielnetz3d/'),
                { proportionen: werte, netz: !this._netzDa });
            if (antwort.error) throw new Error(antwort.error);
            if (this.buehne) {
                if (!this._netzDa && antwort.dreiecke) { this.buehne.netzSetzen(antwort); this._netzDa = true; }
                else this.buehne.punkteSetzen(antwort);
            }
            this.bericht = antwort.bericht || {};
            this.regler.aktualisieren(werte, this.dialog.daten().ziel || {}, this.bericht);
            const n = Object.keys(werte).length;
            this._melden(`Zielnetz mit Umriss${n ? ` und ${n} Vorgabe${n === 1 ? '' : 'n'}` : ''} — `
                + `${(antwort.anzahl || 0).toLocaleString('de-DE')} Punkte, ${antwort.hoehe_cm} cm, `
                + `Server ${antwort.dauer_ms} ms, gesamt ${Math.round(performance.now() - t)} ms`);
        } catch (fehler) {
            this._melden(`Zielnetz nicht geformt: ${fehler.message}`);
        } finally {
            this._laeuft = false;
            if (this._nochmal) { this._nochmal = false; this._holen(); }
        }
    }
}
