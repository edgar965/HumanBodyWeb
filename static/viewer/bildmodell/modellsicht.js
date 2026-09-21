/**
 * Modellsicht — oben auf der Auftragsseite: 3D links, das Bild mit den Pfeilen rechts, die Maße als Schieber.
 *
 * Edgar (20.09.2026, abends): „Ich habe es schon ein paar Mal in Auftrag
 * gegeben, ich brauche eine Modell-View mit 3D links, 2D rechts. Rechts habe
 * ich alle Pfeile. Wenn ich die Regler ändere, dann ändert sich gleich das 3D
 * Modell links. … Am besten oben, wo das 3D-View ist, ein neues 2D view und
 * den anpassbaren Reglern."
 *
 * Kein Popup mehr nötig: die Sicht ist immer da. Links die `Ansicht3d` (das
 * Zielnetz als Käfig, das jedem Zug folgt — oder das gerechnete Modell mit
 * Haut, ein Klick), rechts EIN Bild aus der Wahl (`#modell-bildwahl`: jedes
 * Hauptfoto mit Maßstab und jede gerenderte Ziel-Ansicht) mit den Maßlinien
 * und Griffen (`Proportionenbildtab`) und daneben die Liste aller Maße
 * (`Proportionenliste`: ⤓ ins Bild, ×), rechts außen die 19 Maße als
 * Schieber (`Proportionen3dregler`). Zustand und Rechnung liegen im
 * `Proportionendialog` (eine zweite Sicht darauf, `anmelden`); jede Änderung
 * — Pfeil, Zahl, Schieber, hier oder im Popup — ruft `nachziehen()`: Schieber
 * auf den Stand, das Zielnetz über die geteilte `Zielnetzlive` holen, und die
 * 3D-Ansicht springt auf „Ziel", damit man sieht, was man tut. Die gewählte
 * Quelle bleibt im `localStorage`. Die Knöpfe unten: Alle Vorgaben löschen,
 * Übernehmen, Übernehmen und neu berechnen (`Proportionenuebernahme`), „Groß"
 * öffnet dasselbe Bild im Popup.
 */
import { Proportionen3dregler } from './proportionen3dregler.js';
import { Proportionenbildtab } from './proportionenbildtab.js';
import { Proportionenliste } from './proportionenliste.js';
import { Proportionenuebernahme } from './proportionenuebernahme.js';

export class Modellsicht {

    static MERKER = 'bildmodell.modellsicht.quelle';
    static ANSICHT = { vorn: 'vorn', seite: 'Seite', hinten: 'hinten', dreiviertel: 'dreiviertel', kopf: 'Kopf' };

    /**
     * @param auftrag  `Bildmodellauftrag`
     * @param katalog  `{proportionen}`
     * @param dialog   `Proportionendialog` — hält Quellen, Lagen, Eingaben, `live`
     * @param ansicht  `Ansicht3d` — bekommt das Zielnetz (`zielSetzen`)
     */
    constructor(auftrag, katalog, dialog, ansicht) {
        this.auftrag = auftrag;
        this.katalog = katalog || {};
        this.dialog = dialog;
        this.ansicht = ansicht;
        this.wahl = document.getElementById('modell-bildwahl');
        this.text = document.getElementById('modell-livetext');
        this._stand = null;
        this._laufstand = null;
        if (!this.wahl || !dialog || !dialog.dialog) return;
        this.bild = new Proportionenbildtab(document.getElementById('modell-bildtab'), this.katalog,
            (id, k, linie) => dialog.lageGezogen(id, k, linie), k => dialog.markerLoeschen(k, this.quelleId));
        this.liste = new Proportionenliste(document.getElementById('modell-bildliste'), this.katalog, this.bild,
            (k, punkt) => dialog.markerSetzen(k, punkt, true, this.quelleId), k => dialog.markerLoeschen(k, this.quelleId),
            k => { this.bild.aktiv = k; dialog.nachzeichnen(); }, () => dialog.alleSetzen(this.quelleId));
        dialog.anmelden(this.bild, this.liste);
        this.regler = new Proportionen3dregler(document.getElementById('modell-regler'), this.katalog,
            (k, cm) => dialog.wertGeschoben(k, cm));
        this.wahl.addEventListener('change', () => this.quelleWaehlen(this.wahl.value, true));
        this._knoepfe();
        dialog.zuhoeren(() => this.nachziehen());
        dialog.live.zuhoeren((antwort, netz, text) => this._antwort(antwort, netz, text));
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    get quelleId() { return this.bild && this.bild.quelle ? this.bild.quelle.id : null; }

    _melden(t) { if (this.text) this.text.textContent = t; }

    _knoepfe() {
        const feld = document.getElementById('modell-knoepfe');
        if (!feld) return;
        feld.querySelector('[data-tat="alle-loeschen"]')?.addEventListener('click', () => this.dialog.alleLoeschen());
        feld.querySelector('[data-tat="uebernehmen"]')?.addEventListener('click', () => Proportionenuebernahme.uebernehmen(this.dialog, false));
        feld.querySelector('[data-tat="rechnen"]')?.addEventListener('click', () => Proportionenuebernahme.uebernehmen(this.dialog, true));
        document.getElementById('modell-gross')?.addEventListener('click', () => this.dialog.oeffnen(this.quelleId, this.bild.aktiv));
    }

    // ------------------------------------------------------------ Zeigen

    zeigen(z) {
        this.dialog.quellenAufbauen();
        const quellen = Object.keys(this.dialog.quellen);
        const stand = JSON.stringify([quellen, ((z.ergebnis || {}).proportionen || {}).stand || '', z.status]);
        if (stand !== this._stand) {
            this._stand = stand;
            this._wahlFuellen();
            this.quelleWaehlen(this.quelleId || this._gemerkt() || Modellsicht.erste(this.dialog.quellen), false);
            this.regler.fuellen(this.dialog.werte(), this.dialog.daten().ziel || {}, this.dialog.live.bericht);
        }
        // Das Zielnetz holen, sobald es eines gibt — und neu, wenn ein Lauf fertig ist (nicht bei jeder Nachfrage im Lauf).
        const laufstand = JSON.stringify([z.status, ((z.ergebnis || {}).ziel || {}).hoehe_ziel_cm, ((z.ergebnis || {}).anpassung || {}).punkte_rms_mm]);
        if (laufstand === this._laufstand) return;
        this._laufstand = laufstand;
        if (z.status === 'laeuft') { this._melden('Lauf läuft — das Zielnetz kommt, wenn er fertig ist.'); return; }
        if ((z.ergebnis || {}).ziel) this.dialog.live.nachziehen(true);
        else this._melden('Noch kein Zielnetz — erst „Starten" (Schritt Zielnetz).');
    }

    /** Die erste Quelle: ein Foto von vorn, sonst irgendein Foto, sonst eine Ziel-Ansicht. */
    static erste(quellen) {
        const alle = Object.values(quellen);
        const foto = alle.find(q => q.art === 'foto' && q.ansicht === 'vorn') || alle.find(q => q.art === 'foto');
        return (foto || alle[0] || {}).id || null;
    }

    _gemerkt() {
        try { return localStorage.getItem(Modellsicht.MERKER); } catch (e) { return null; }
    }

    _wahlFuellen() {
        const alt = this.wahl.value;
        this.wahl.replaceChildren();
        const gruppen = { foto: document.createElement('optgroup'), ziel: document.createElement('optgroup') };
        gruppen.foto.label = 'Fotos';
        gruppen.ziel.label = 'Ziel (gerendert, vorher)';
        for (const q of Object.values(this.dialog.quellen)) {
            const o = document.createElement('option');
            o.value = q.id;
            o.textContent = q.art === 'foto'
                ? `${Modellsicht.ANSICHT[q.ansicht] || q.ansicht || '?'} · ${q.datei}`
                : `Ziel ${Modellsicht.ANSICHT[q.ansicht] || q.ansicht}`;
            gruppen[q.art].appendChild(o);
        }
        for (const g of Object.values(gruppen)) if (g.children.length) this.wahl.appendChild(g);
        if (alt && this.dialog.quellen[alt]) this.wahl.value = alt;
    }

    /** Das Bild rechts: Quelle `id` mit ihren Lagen; `merken` legt die Wahl im localStorage ab. */
    quelleWaehlen(id, merken) {
        const q = (id && this.dialog.quellen[id]) || this.dialog.quellen[Modellsicht.erste(this.dialog.quellen)];
        if (!q) { this.bild.zeigen(null); this.liste.zeigen({}, new Set(), () => undefined, null); return; }
        this.wahl.value = q.id;
        this.bild.zeigen(q, this.dialog.lagen[q.id] || {}, this.dialog.eingaben, this.dialog.daten().ziel || {}, null);
        this.dialog.nachzeichnen();
        if (merken) { try { localStorage.setItem(Modellsicht.MERKER, q.id); } catch (e) { /* ohne Merker */ } }
    }

    // ---------------------------------------------------------- Änderung

    /** Nach jeder Änderung (Dialog): Schieber auf den Stand, Zielnetz holen, 3D auf „Ziel". */
    nachziehen() {
        this.regler.aktualisieren(this.dialog.werte(), this.dialog.daten().ziel || {}, this.dialog.live.bericht);
        if (this.ansicht && this.ansicht.was !== 'ziel' && this.ansicht.kaefig) this.ansicht.wasZeigen('ziel', false);   // nicht merken: automatisch, keine Wahl
        this.dialog.live.nachziehen();
    }

    _antwort(antwort, netz, text) {
        if (antwort && this.ansicht) this.ansicht.zielSetzen(antwort, netz);
        this.regler.aktualisieren(this.dialog.werte(), this.dialog.daten().ziel || {}, this.dialog.live.bericht);
        this._melden(text);
    }
}
