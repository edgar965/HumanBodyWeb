import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Posenanwendung } from './posenanwendung.js';
import { Absatzdrehung } from './garmentcode_absatzdrehung.js';

/**
 * GarmentcodeAbsatz — die Figur auf den Absatz stellen, sobald sie einen
 * Schuh mit Absatz trägt.
 *
 * WARUM (11.09.2026, Edgar: „mach das: Absatz/Plateau braucht einen
 * gebeugten Fuss"): Ein Schuh mit Absatz wird auf dem GEBEUGTEN Fuss
 * simuliert und in der Ruhelage an die Figur gebunden (`schuh/
 * absatzdrapierung.py`). In der A-Pose steht der Absatz deshalb unter dem
 * Boden und die Ferse im Schuhboden — erst wenn Fuss und Zehen um den
 * Beugewinkel gedreht sind und die Figur um die Hebung steigt, sitzt er.
 * Dieselben Gelenke wie beim Bau: Der Fuss dreht um den Kopf von
 * `DEF-foot`, die Zehen drehen um den Kopf von `DEF-toe` zurück — und um
 * die Sprengung des Schuhs weiter (`shoe.toe_spring`: die Zehenspitze
 * zeigt nach oben, auch bei flachem Schuh). Die Drehung selbst rechnet
 * `Absatzdrehung` (`garmentcode_absatzdrehung.js`).
 *
 * ZWEI QUELLEN, EINE VORRANGIG: Die Regler des Reiters
 * (`garmentcode_absatzregler.js`, `vorschau()`) stellen die Figur sofort
 * auf den Absatz, den sie zeigen — vor jedem Bau (Edgar, 11.09.2026:
 * „ein Regler, der auch gleich die Pose ändert"). Ohne Vorschau gilt der
 * getragene Schuh. Was gerade steht, trägt einen Schlüssel aus Winkel,
 * Sprengung und Hub; ändert sich das Ziel, wird abgesetzt und neu
 * gestellt — sonst bliebe ein Regler ohne Wirkung, solange die Figur
 * schon auf irgendeinem Absatz steht.
 *
 * WIE ES DAS STÜCK FINDET: Die Stücke hängen als `gc_<vorlage>` in
 * `inst.clothMeshes` (`garmentcode_anziehen.js`); die Zahlen kommen vom
 * Server (`/api/garmentcode/absatz/`), nicht aus der Rig-Datei — die
 * schreibt eine Datei der parallelen Sitzung. Geprüft wird im Takt, weil
 * das Einhängen kein Ereignis auslöst; ein Blick in ein Objekt alle zwei
 * Sekunden kostet nichts. Ein Takt wartet auf Serverantworten; solange
 * einer läuft, beginnt kein zweiter — zwei Takte, die beide „noch nicht
 * gestellt" sehen, stellten dieselbe Figur zweimal (Vorsorge; die
 * doppelte Hebung, die am 11.09.2026 gemessen wurde, kam aus der
 * gespeicherten Lage, siehe `anstellen`). Nach `TAKT_STAU_MS` gilt ein
 * hängender Takt als verloren.
 */
export class GarmentcodeAbsatz {

    static TAKT_MS = 2000;
    static TAKT_STAU_MS = 30000;

    constructor() {
        /** inst -> {schluessel, drehungen: [[knochen, quat]], hub} */
        this.stand = new Map();
        /** inst -> info aus den Reglern (Vorrang vor dem getragenen Schuh) */
        this.vorschauen = new Map();
        /** netz -> Promise der Serverantwort */
        this.antworten = new WeakMap();
        this.takt = null;
        /** Beginn des laufenden Takts, 0 = keiner. */
        this.seit = 0;
        /** Kam während eines Takts eine Vorschau, läuft danach gleich einer. */
        this.nachholen = false;
    }

    starten() {
        if (this.takt) return;
        this.takt = setInterval(() => this._takt(), GarmentcodeAbsatz.TAKT_MS);
    }

    async _takt() {
        if (this.seit && Date.now() - this.seit < GarmentcodeAbsatz.TAKT_STAU_MS) return;
        this.seit = Date.now();
        try {
            await this.pruefen();
        } catch (fehler) {
            Protokoll.warnung('GarmentCode', `Absatz: ${fehler.message}`);
        } finally {
            this.seit = 0;
            if (this.nachholen) {
                this.nachholen = false;
                this._takt();
            }
        }
    }

    // ---------------------------------------------------------------- Takt

    async pruefen() {
        for (const inst of state.characters.values()) {
            const info = this.vorschauen.has(inst)
                ? this.vorschauen.get(inst)
                : (await this._absatzschuh(inst))?.info;
            const ziel = info && (info.winkel_grad > 0 || info.sprengung_grad > 0)
                ? info : null;
            const bisher = this.stand.get(inst);
            if (bisher && (!ziel || bisher.schluessel !== this.schluessel(ziel))) {
                this.absetzen(inst);
            }
            if (ziel && !this.stand.has(inst)) {
                this.anstellen(inst, ziel);
            }
        }
    }

    /**
     * Die Regler zeigen einen Absatz: sofort so stellen. `info` wie vom
     * Server (`winkel_grad`, `hebung_cm`, `sprengung_grad`, `plateau_cm`),
     * null nimmt die Vorschau zurück — dann gilt wieder der Schuh.
     */
    vorschau(inst, info) {
        if (info) this.vorschauen.set(inst, info);
        else this.vorschauen.delete(inst);
        if (this.seit) this.nachholen = true;
        return this._takt();
    }

    /** Woran sich ein Stand von einem anderen unterscheidet. */
    schluessel(info) {
        return [info.winkel_grad, info.sprengung_grad || 0,
                info.hebung_cm, info.plateau_cm || 0]
            .map((z) => Number(z).toFixed(3)).join('|');
    }

    /** Das erste getragene GarmentCode-Stück mit Absatz — oder null. */
    async _absatzschuh(inst) {
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            if (!schluessel.startsWith('gc_') || !netz?.userData?.gcStueck) continue;
            const info = await this._info(netz);
            if (info && (info.winkel_grad > 0 || info.sprengung_grad > 0)) {
                return { netz, info };
            }
        }
        return null;
    }

    _info(netz) {
        if (!this.antworten.has(netz)) {
            const stueck = encodeURIComponent(netz.userData.gcStueck);
            this.antworten.set(netz, Serverabruf.jsonOderNull(
                `/api/garmentcode/absatz/?stueck=${stueck}`));
        }
        return this.antworten.get(netz);
    }

    // ------------------------------------------------------------ Anstellen

    anstellen(inst, info) {
        const skelett = Posenanwendung.skelett(inst);
        if (!skelett) {
            Protokoll.debug('GarmentCode', 'Absatz: Figur ohne Skelett, noch nicht gestellt');
            return false;
        }
        const winkel = info.winkel_grad * Math.PI / 180;
        const sprengung = (info.sprengung_grad || 0) * Math.PI / 180;
        const drehungen = Absatzdrehung.drehen(inst, skelett, winkel, sprengung);
        const hub = (info.hebung_cm + info.plateau_cm) / 100;
        // Der Hub steht auch am Objekt: `Character._lage` zieht ihn beim
        // Speichern ab, sonst käme er mit jedem Laden noch einmal dazu.
        inst.group.position.y += hub;
        inst.group.userData.absatzHub = hub;
        this.stand.set(inst, { schluessel: this.schluessel(info), drehungen, hub });
        Protokoll.info('GarmentCode',
            `Absatz ${info.absatz_cm} cm: Fuss um ${info.winkel_grad.toFixed(1)}° `
            + `gebeugt, Zehen um ${(info.sprengung_grad || 0).toFixed(1)}° gehoben, `
            + `Figur um ${(hub * 100).toFixed(1)} cm gehoben (${drehungen.length} Knochen)`);
        return true;
    }

    // ------------------------------------------------------------- Absetzen

    absetzen(inst) {
        const stand = this.stand.get(inst);
        if (!stand) return;
        Absatzdrehung.zuruecknehmen(stand.drehungen);
        const skelett = Posenanwendung.skelett(inst);
        if (skelett) skelett.bones[0].updateWorldMatrix(true, true);
        inst.group.position.y -= stand.hub;
        inst.group.userData.absatzHub = 0;
        this.stand.delete(inst);
        Protokoll.info('GarmentCode', 'Absatz abgesetzt: Figur steht wieder flach');
    }
}

export const garmentcodeAbsatz = new GarmentcodeAbsatz();
garmentcodeAbsatz.starten();
// Für Messungen aus der Konsole (`__garmentcodeAbsatz.stand`, `.pruefen()`):
// dieselbe Handhabe wie `window.__characters` in `pose_apply.js`.
window.__garmentcodeAbsatz = garmentcodeAbsatz;
