import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Posenanwendung } from './posenanwendung.js';
import { Stueckereignis } from './garmentcode_stueckereignis.js';

/**
 * GarmentcodeAbsatz — ein angezogener Absatzschuh wird zur Pose der Figur.
 *
 * WARUM SO DÜNN (Edgar, 11.09.2026: „der Betrachter soll bei einem
 * Absatzschuh gar nichts tun, sondern das Programm soll die Pose ändern!"):
 * Die erste Fassung drehte die Fussknochen selbst, alle zwei Sekunden
 * nachgesehen, Vorzeichen per Probedrehung. Jetzt rechnet der Server die
 * Beugung in die Pose (`core/dienste/absatzpose.py`); hier steht nur
 * noch, WANN: Wird ein GarmentCode-Stück angezogen oder abgelegt
 * (`gc-stueck`, aus `garmentcode_anziehen.js`), fragt dieses Modul den
 * Absatz des Stücks ab (`/api/garmentcode/absatz/`) und gibt ihn an die
 * Posenanwendung — die holt die Pose der Figur neu, mit Absatz.
 *
 * Die Zahlen kommen vom Server, nicht aus der Rig-Datei — die schreibt
 * eine Datei der parallelen Sitzung.
 */
export class GarmentcodeAbsatz {

    constructor() {
        /** netz -> Promise der Serverantwort */
        this.antworten = new WeakMap();
    }

    einhaengen() {
        Stueckereignis.hoeren((detail) => {
            this.nachStueck(detail).catch((fehler) =>
                Protokoll.warnung('GarmentCode', `Absatz: ${fehler.message}`));
        });
    }

    /** Ein Stück kam dazu oder ging: den Absatz der Figur neu bestimmen. */
    async nachStueck({ inst, stueck, angezogen }) {
        if (!inst) return;
        const quelle = inst.absatz?.quelle || '';
        // Eine Regler-Vorschau bleibt, bis die Vorlage wechselt; ein Schuh,
        // der abgelegt wird, nimmt seinen Absatz mit.
        if (quelle === 'regler') return;
        if (!angezogen && quelle !== `schuh:${stueck}`) return;
        await this.vomSchuh(inst);
    }

    /** Den Absatz aus den getragenen Stücken setzen — oder keinen. */
    async vomSchuh(inst) {
        const schuh = await this._absatzschuh(inst);
        const info = schuh
            ? { ...schuh.info, quelle: `schuh:${schuh.netz.userData.gcStueck}` }
            : null;
        return Posenanwendung.absatzSetzen(inst, info);
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
}

export const garmentcodeAbsatz = new GarmentcodeAbsatz();
garmentcodeAbsatz.einhaengen();
