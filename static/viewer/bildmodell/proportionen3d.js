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
 * Schieber (`Proportionen3dregler`). Das Netz kommt von der geteilten
 * `Zielnetzlive` des Dialogs — dieselbe Antwort wie für die Modellsicht oben
 * auf der Seite (seit 20.09.2026 abends), eine Anfrage je Zug. Der Dialog ruft
 * nach jeder Änderung `nachziehen()`: Schieber auf den Stand, die Anfrage
 * stellt `Zielnetzlive` (gebündelt, eine in der Luft).
 */
import { Proportionen3dbuehne } from './proportionen3dbuehne.js';
import { Proportionen3dregler } from './proportionen3dregler.js';

export class Proportionen3d {

    /**
     * @param feld      das Fenster (`#proportionen-3d`, im Dialog)
     * @param auftrag   `Auftrag` (Adresse, Zustand)
     * @param katalog   `{proportionen}`
     * @param dialog    der `Proportionendialog` (Werte, Ziel, `wertGeschoben`, `live`)
     */
    constructor(feld, auftrag, katalog, dialog) {
        this.feld = feld;
        this.auftrag = auftrag;
        this.dialog = dialog;
        this.buehne = null;
        this._hoerer = null;
        if (!this.feld) return;
        this.text = this.feld.querySelector('.bildmodell-3dtext');
        this.regler = new Proportionen3dregler(this.feld.querySelector('.bildmodell-3dregler'), katalog,
            (k, cm) => this.dialog.wertGeschoben(k, cm));
        this.feld.querySelector('[data-tat="3d-schliessen"]')?.addEventListener('click', () => this.schliessen());
        this.feld.querySelector('[data-tat="3d-gitter"]')?.addEventListener('change', e => this.buehne?.gitterZeigen(e.target.checked));
    }

    get offen() { return !!this.feld && !this.feld.hidden; }

    get bericht() { return this.dialog.live ? this.dialog.live.bericht : {}; }

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
        if (this.dialog.live && !this._hoerer) {
            this._hoerer = (antwort, netz, text) => this._antwort(antwort, netz, text);
            this.dialog.live.zuhoeren(this._hoerer);
        }
        this.nachziehen(true);
    }

    schliessen() {
        if (!this.feld) return;
        this.feld.hidden = true;
        this.buehne?.anhalten();
        if (this.dialog.live && this._hoerer) { this.dialog.live.vergessen(this._hoerer); this._hoerer = null; }
    }

    umschalten() { if (this.offen) this.schliessen(); else this.oeffnen(); }

    /** Nach jeder Änderung im Dialog: Schieber nachziehen, Netz neu formen lassen. */
    nachziehen(sofort = false) {
        if (!this.offen) return;
        this.regler.aktualisieren(this.dialog.werte(), this.dialog.daten().ziel || {}, this.bericht);
        this.dialog.live?.nachziehen(sofort);
    }

    _antwort(antwort, netz, text) {
        if (antwort && this.buehne) this.buehne.setzen(antwort, netz);
        this.regler.aktualisieren(this.dialog.werte(), this.dialog.daten().ziel || {}, this.bericht);
        this._melden(text);
    }
}
