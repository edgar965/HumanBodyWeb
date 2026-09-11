import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Posenanwendung } from './posenanwendung.js';

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
 * `DEF-foot`, die Zehen drehen um den Kopf von `DEF-toe` zurück.
 *
 * WIE ES DAS STÜCK FINDET: Die Stücke hängen als `gc_<vorlage>` in
 * `inst.clothMeshes` (`garmentcode_anziehen.js`); die Zahlen kommen vom
 * Server (`/api/garmentcode/absatz/`), nicht aus der Rig-Datei — die
 * schreibt eine Datei der parallelen Sitzung. Geprüft wird im Takt, weil
 * das Einhängen kein Ereignis auslöst; ein Blick in ein Objekt alle zwei
 * Sekunden kostet nichts.
 *
 * DIE DREHRICHTUNG WIRD GEMESSEN, NICHT ANGENOMMEN: Nach der Drehung
 * muss der Zehenkopf tiefer liegen als vorher (der Fuss senkt die
 * Zehen, dann hebt die Figur). Liegt er höher, war es die andere Seite
 * der x-Achse — dann wird umgedreht. So hängt nichts an der Frage, wohin
 * die Figur in der Szene blickt.
 */
export class GarmentcodeAbsatz {

    static TAKT_MS = 2000;
    static FUSS = ['DEF-foot.L', 'DEF-foot.R'];
    static ZEHEN = ['DEF-toe.L', 'DEF-toe.R'];

    constructor() {
        /** inst -> {netz, drehungen: [[knochen, quat]], hub} */
        this.stand = new Map();
        /** netz -> Promise der Serverantwort */
        this.antworten = new WeakMap();
        this.takt = null;
    }

    starten() {
        if (this.takt) return;
        this.takt = setInterval(() => {
            this.pruefen().catch((fehler) =>
                Protokoll.warnung('GarmentCode', `Absatz: ${fehler.message}`));
        }, GarmentcodeAbsatz.TAKT_MS);
    }

    // ---------------------------------------------------------------- Takt

    async pruefen() {
        for (const inst of state.characters.values()) {
            const schuh = await this._absatzschuh(inst);
            const bisher = this.stand.get(inst);
            if (bisher && (!schuh || bisher.netz !== schuh.netz)) {
                this.absetzen(inst);
            }
            if (schuh && !this.stand.has(inst)) {
                this.anstellen(inst, schuh);
            }
        }
    }

    /** Das erste getragene GarmentCode-Stück mit Absatz — oder null. */
    async _absatzschuh(inst) {
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            if (!schluessel.startsWith('gc_') || !netz?.userData?.gcStueck) continue;
            const info = await this._info(netz);
            if (info && info.winkel_grad > 0) return { netz, info };
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

    anstellen(inst, { netz, info }) {
        const skelett = Posenanwendung.skelett(inst);
        if (!skelett) {
            Protokoll.debug('GarmentCode', 'Absatz: Figur ohne Skelett, noch nicht gestellt');
            return false;
        }
        const winkel = info.winkel_grad * Math.PI / 180;
        const drehungen = this._drehen(inst, skelett, winkel);
        const hub = (info.hebung_cm + info.plateau_cm) / 100;
        inst.group.position.y += hub;
        this.stand.set(inst, { netz, drehungen, hub });
        Protokoll.info('GarmentCode',
            `Absatz ${info.absatz_cm} cm: Fuss um ${info.winkel_grad.toFixed(1)}° `
            + `gebeugt, Figur um ${(hub * 100).toFixed(1)} cm gehoben (${drehungen.length} Knochen)`);
        return true;
    }

    /** Fuss und Zehen drehen; liefert die Liste [knochen, lokale Drehung]. */
    _drehen(inst, skelett, winkel) {
        const Quat = skelett.bones[0].quaternion.constructor;
        const Vec3 = skelett.bones[0].position.constructor;
        const gruppe = new Quat();
        inst.group.getWorldQuaternion(gruppe);
        const achse = new Vec3(1, 0, 0).applyQuaternion(gruppe).normalize();
        const zehe = skelett.getBoneByName(Posenanwendung.jsName(GarmentcodeAbsatz.ZEHEN[0]));
        const vorher = zehe ? zehe.getWorldPosition(new Vec3()).y : null;
        let drehungen = this._anwenden(skelett, achse, winkel, Quat);
        skelett.bones[0].updateWorldMatrix(true, true);
        const nachher = zehe ? zehe.getWorldPosition(new Vec3()).y : null;
        if (vorher !== null && nachher !== null && nachher > vorher) {
            // Falsche Seite: zurück und andersherum.
            this._zuruecknehmen(drehungen);
            drehungen = this._anwenden(skelett, achse, -winkel, Quat);
            skelett.bones[0].updateWorldMatrix(true, true);
        }
        return drehungen;
    }

    _anwenden(skelett, achse, winkel, Quat) {
        const drehungen = [];
        const paare = [[GarmentcodeAbsatz.FUSS, winkel], [GarmentcodeAbsatz.ZEHEN, -winkel]];
        for (const [namen, grad] of paare) {
            for (const name of namen) {
                const knochen = skelett.getBoneByName(Posenanwendung.jsName(name));
                if (!knochen?.parent) continue;
                const welt = new Quat().setFromAxisAngle(achse, grad);
                const eltern = new Quat();
                knochen.parent.getWorldQuaternion(eltern);
                // Weltdrehung in den Elternraum übersetzt — wie
                // `Posenanwendung._oberschenkel`.
                const lokal = eltern.clone().invert().multiply(welt).multiply(eltern);
                knochen.quaternion.premultiply(lokal);
                drehungen.push([knochen, lokal]);
            }
        }
        return drehungen;
    }

    _zuruecknehmen(drehungen) {
        for (const [knochen, lokal] of drehungen) {
            knochen.quaternion.premultiply(lokal.clone().invert());
        }
    }

    // ------------------------------------------------------------- Absetzen

    absetzen(inst) {
        const stand = this.stand.get(inst);
        if (!stand) return;
        this._zuruecknehmen(stand.drehungen);
        const skelett = Posenanwendung.skelett(inst);
        if (skelett) skelett.bones[0].updateWorldMatrix(true, true);
        inst.group.position.y -= stand.hub;
        this.stand.delete(inst);
        Protokoll.info('GarmentCode', 'Absatz abgesetzt: Figur steht wieder flach');
    }
}

export const garmentcodeAbsatz = new GarmentcodeAbsatz();
garmentcodeAbsatz.starten();
