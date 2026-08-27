import { Gesichtswerte } from './gesichtswerte.js';

/**
 * Rechnet die Ausdruckswerte in Drehungen je Gesichtsknochen um.
 *
 * Ein Knochen bekommt Beiträge aus mehreren Ausdrücken (das Kinn etwa aus
 * Kieferöffnung UND Lächeln), deshalb wird aufsummiert statt gesetzt. Die Werte
 * sind Euler-Winkel in Blenders lokalem System — die Umrechnung nach Three.js
 * macht der Aufrufer.
 *
 * Aus facial_expression.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`).
 */
export class Gesichtsdrehungen {
    constructor() {
        /** @type {Object<string, number[]>} Knochenname -> [rx, ry, rz] */
        this.je_knochen = {};
    }

    /**
     * @param {number[]} vektor die zehn SMPL-X-Ausdruckswerte
     * @returns {Gesichtsdrehungen}
     */
    static aus(vektor) {
        const drehungen = new Gesichtsdrehungen();
        const w = new Gesichtswerte(vektor);
        drehungen._kiefer(w);
        drehungen._lippen(w);
        drehungen._brauen(w);
        drehungen._wangen(w);
        drehungen._lider(w);
        drehungen._nase(w);
        return drehungen;
    }

    _dazu(name, rx, ry, rz) {
        if (!this.je_knochen[name]) this.je_knochen[name] = [0, 0, 0];
        this.je_knochen[name][0] += rx;
        this.je_knochen[name][1] += ry;
        this.je_knochen[name][2] += rz;
    }

    _kiefer(w) {
        const kiefer = w.mal('jawOpen');
        this._dazu('DEF-jaw', kiefer, 0, 0);
        // Das Kinn folgt dem Kiefer abgeschwächt.
        this._dazu('DEF-chin', kiefer * 0.3, 0, 0);
        this._dazu('DEF-chin.001', kiefer * 0.15, 0, 0);
    }

    _lippen(w) {
        const laecheln = w.mal('smile');
        const heben = w.mal('lipUp');
        const winkel = w.mal('lipCorner');
        this._dazu('DEF-lip.T.L', -heben, 0, 0);
        this._dazu('DEF-lip.T.R', -heben, 0, 0);
        this._dazu('DEF-lip.T.L.001', -laecheln * 0.5, 0,
                   -laecheln * 0.3 - winkel * 0.5);
        this._dazu('DEF-lip.T.R.001', -laecheln * 0.5, 0,
                   laecheln * 0.3 + winkel * 0.5);
        this._dazu('DEF-lip.B.L.001', laecheln * 0.3, 0,
                   -laecheln * 0.3 - winkel * 0.5);
        this._dazu('DEF-lip.B.R.001', laecheln * 0.3, 0,
                   laecheln * 0.3 + winkel * 0.5);
    }

    _brauen(w) {
        const b = w.brauen;
        // Die untere Brauenreihe folgt am stärksten, nach außen klingt sie ab.
        for (const seite of ['L', 'R']) {
            this._dazu(`DEF-brow.B.${seite}`, b, 0, 0);
            this._dazu(`DEF-brow.B.${seite}.001`, b * 0.8, 0, 0);
            this._dazu(`DEF-brow.B.${seite}.002`, b * 0.6, 0, 0);
            this._dazu(`DEF-brow.T.${seite}`, b * 0.5, 0, 0);
            this._dazu(`DEF-brow.T.${seite}.001`, b * 0.5, 0, 0);
        }
    }

    _wangen(w) {
        const backe = w.mal('cheekPuff');
        this._dazu('DEF-cheek.B.L', 0, 0, -backe);
        this._dazu('DEF-cheek.B.R', 0, 0, backe);
        this._dazu('DEF-cheek.T.L', 0, 0, -backe * 0.5);
        this._dazu('DEF-cheek.T.R', 0, 0, backe * 0.5);
    }

    _lider(w) {
        for (const seite of ['L', 'R']) {
            this._dazu(`DEF-lid.T.${seite}.001`, w.oberlid, 0, 0);
            this._dazu(`DEF-lid.T.${seite}.002`, w.oberlid, 0, 0);
            this._dazu(`DEF-lid.B.${seite}.001`, w.unterlid, 0, 0);
            this._dazu(`DEF-lid.B.${seite}.002`, w.unterlid, 0, 0);
        }
    }

    _nase(w) {
        const ruempfen = w.mal('noseWrinkle') * 0.5;
        this._dazu('DEF-nose.L', 0, 0, -ruempfen);
        this._dazu('DEF-nose.R', 0, 0, ruempfen);
        this._dazu('DEF-nose.001', ruempfen, 0, 0);
    }
}
