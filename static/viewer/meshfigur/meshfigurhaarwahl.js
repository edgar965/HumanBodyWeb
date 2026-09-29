import { Meshfigurhaarobjekt } from './meshfigurhaarobjekt.js';

/**
 * Meshfigurhaarwahl — welches Haar die Figur der Bühne trägt (29.09.2026, Edgar: „das haar soll aber etwas
 * natürlicher anschauen" → „mach a-b, c als option parallel").
 *
 *     frisur   die Frisur aus Schritt „frisur" (Daz oder „Haar Eigen", `ergebnis.frisur.kleidung`) — ein
 *              Stück der Garderobe, das die Figur beim Bau selbst anzieht (`Genesis9Modell.kleidung`)
 *     netz     das Haar aus dem Netz (`ergebnis/haar.glb`)
 *     karten   die Haarkarten aus seiner Schale (`ergebnis/haarkarten.glb`)
 *
 * Angeboten wird nur, was es gibt; die Vorgabe ist die erste davon (Frisur vor Netz). **Kein Haar** ist
 * seit dem 29.09.2026 kein Wert dieses Feldes mehr, sondern das Kästchen „Haare" daneben
 * (`Meshfigurschalter` → `sichtbarkeit`) — sonst gäbe es zwei Wege, dasselbe abzuschalten.
 *
 * Der Export der Seite nimmt, was sichtbar ist — die Wahl gilt also auch für die GLB. Die Netze der Frisur
 * kommen nach dem Bau nach (die Figur zieht sie im Hintergrund an); `anwenden` läuft deshalb bei jedem
 * Stand der Seite mit.
 */
export class Meshfigurhaarwahl {

    static TEXTE = { netz: 'Haar aus dem Netz', karten: 'Haarkarten aus dem Netz' };

    constructor(seite, melden) {
        this.feld = document.getElementById('buehne-haarwahl');
        this.huelle = document.getElementById('buehne-haarwahl-feld');
        this.netz = new Meshfigurhaarobjekt(seite, melden,
                                            { name: 'Haar aus dem Netz', datei: e => (e.haar || {}).objekt });
        this.karten = new Meshfigurhaarobjekt(seite, melden, {
            name: 'Haarkarten', datei: e => (e.frisur || {}).karten, karten: true,
        });
        this.modell = null;
        this.frisur = null;
        this.gewaehlt = null;
        this.an = true;
        this.vorhanden = false;
        this._stand = null;
        this.feld?.addEventListener('change', () => { this.gewaehlt = this.feld.value; this.anwenden(); });
    }

    /** Das Kästchen „Haare" — aus heißt: keine der Quellen ist zu sehen. */
    sichtbarkeit(an) {
        this.an = an;
        this.anwenden();
    }

    /** Die Frisur für die Figur (`kleidung` des Modells) — leer ohne Wahl. */
    static kleidung(z) {
        return (((z || {}).ergebnis || {}).frisur || {}).kleidung || {};
    }

    zeigen(z, gruppe) {
        const e = z.ergebnis || {};
        this.frisur = (e.frisur || {}).wahl || null;
        this.netz.zeigen(z, gruppe);
        this.karten.zeigen(z, gruppe);
        this._optionen();
        this.anwenden();
    }

    anhaengen(modell) {
        this.modell = modell;
        this.netz.anhaengen(modell.group);
        this.karten.anhaengen(modell.group);
        this.anwenden();
    }

    _optionen() {
        if (!this.feld) return;
        const da = { frisur: Boolean(this.frisur), netz: this.netz.vorhanden, karten: this.karten.vorhanden };
        const werte = Object.keys(da).filter(k => da[k]);
        this.vorhanden = werte.length > 0;
        const stand = JSON.stringify([werte, this.frisur?.name]);
        if (stand !== this._stand) {
            this._stand = stand;
            this.feld.innerHTML = '';
            for (const w of werte) {
                const option = document.createElement('option');
                option.value = w;
                option.textContent = w === 'frisur' ? `Frisur: ${this.frisur.name}` : Meshfigurhaarwahl.TEXTE[w];
                this.feld.appendChild(option);
            }
        }
        if (this.huelle) this.huelle.hidden = werte.length <= 1;
        this.feld.value = this.gewaehlt && werte.includes(this.gewaehlt) ? this.gewaehlt : werte[0];
    }

    anwenden() {
        const w = this.an ? (this.feld?.value || 'frisur') : '';
        this.netz.sichtbar(w === 'netz');
        this.karten.sichtbar(w === 'karten');
        const kennung = this.frisur?.kennung;
        for (const [schluessel, netz] of Object.entries(this.modell?.clothMeshes || {})) {
            if (!kennung || !schluessel.startsWith(`${kennung}/`)) continue;
            netz.traverse(o => { if (o.isMesh) o.visible = w === 'frisur'; });
        }
    }
}
