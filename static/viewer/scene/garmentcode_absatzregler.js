import { garmentcodeAbsatz } from './garmentcode_absatz.js';
import { garmentcodeRegler } from './garmentcode_regler.js';
import { GarmentcodeFigur } from './garmentcode_figur.js';
import { Posenanwendung } from './posenanwendung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * GarmentcodeAbsatzregler — die Regler Absatz, Plateau und Sprengung
 * stellen die Figur sofort auf den Absatz, ohne Bau.
 *
 * WARUM (Edgar, 11.09.2026: „kannst du bei denen einen Regler machen, der
 * auch gleich die Pose ändert - den Fuss anhebt?"): Bis dahin hob sich
 * der Fuss erst, wenn der gebaute Schuh angezogen war — Schnitt plus
 * Simulation, eine halbe Minute. Jetzt fragt jeder Zug am Regler den
 * Server nach der Beugung für DIESE Figur (`/api/garmentcode/absatz/
 * vorschau/`, dieselbe Rechnung wie beim Bau, 0,2 s) und gibt sie der
 * Posenanwendung (`absatzSetzen`) — die holt die Pose der Figur neu, mit
 * der Beugung darin; der Betrachter dreht nichts selbst.
 *
 * ANGEHÄNGT AM DOKUMENT, NICHT AM REGLER: Die Reglerzeilen baut
 * `garmentcode_regler.js` bei jedem Vorlagenwechsel neu; ein Zuhörer am
 * Dokument sieht sie alle, erkannt an `data-pfad` (`shoe.heel` …).
 * Entprellt wie `GarmentcodeLive`: Ein Schieber feuert 60-mal je Sekunde.
 *
 * ZURÜCK ZUM SCHUH beim Vorlagenwechsel: Die Vorschau gehört zu den
 * Reglern des gerade gewählten Stücks. Wählt man ein anderes, gilt
 * wieder, was die Figur trägt.
 */
export class GarmentcodeAbsatzregler {

    static PFADE = { 'shoe.heel': 'heel', 'shoe.platform': 'platform',
                     'shoe.toe_spring': 'toe_spring' };
    static RUHE_MS = 150;
    static ADRESSE = '/api/garmentcode/absatz/vorschau/';

    constructor() {
        this.uhr = null;
        this.laeuft = false;
        this.nachholen = false;
    }

    einhaengen() {
        document.addEventListener('input', (e) => this._bewegt(e));
        document.addEventListener('change', (e) => this._bewegt(e));
    }

    /** Ein Regler wurde bewegt — nur die drei Absatzregler zählen. */
    _bewegt(ereignis) {
        const zeile = ereignis.target?.closest?.('#gc-regler .slider-row[data-pfad]');
        if (zeile && zeile.dataset.pfad in GarmentcodeAbsatzregler.PFADE) {
            this.anstossen();
            return;
        }
        if (ereignis.target?.id === 'gc-vorlage') this.zuruecknehmen();
    }

    anstossen() {
        clearTimeout(this.uhr);
        this.uhr = setTimeout(() => this.anwenden(), GarmentcodeAbsatzregler.RUHE_MS);
    }

    zuruecknehmen() {
        clearTimeout(this.uhr);
        const figur = GarmentcodeFigur.gewaehlt();
        if (figur?.inst?.absatz?.quelle === 'regler') {
            garmentcodeAbsatz.vomSchuh(figur.inst).catch((fehler) =>
                Protokoll.warnung('GarmentCode', `Absatz: ${fehler.message}`));
        }
    }

    /** Die aktuellen Reglerwerte, wie sie an den Server gehen. */
    werte() {
        const aus = {};
        for (const [pfad, name] of Object.entries(GarmentcodeAbsatzregler.PFADE)) {
            aus[name] = Number(garmentcodeRegler.wertVon(pfad)) || 0;
        }
        return aus;
    }

    async anwenden() {
        if (this.laeuft) {
            this.nachholen = true;
            return;
        }
        const figur = GarmentcodeFigur.gewaehlt();
        if (!figur) return;
        this.laeuft = true;
        try {
            const daten = GarmentcodeFigur.formulardaten(figur);
            for (const [name, wert] of Object.entries(this.werte())) daten.append(name, wert);
            const info = await Serverabruf.formular(GarmentcodeAbsatzregler.ADRESSE, daten);
            if (info.hinweise?.length) Protokoll.debug('GarmentCode', info.hinweise.join(' · '));
            await Posenanwendung.absatzSetzen(figur.inst, { ...info, quelle: 'regler' });
        } catch (fehler) {
            Protokoll.warnung('GarmentCode', `Absatzvorschau: ${fehler.message}`);
        } finally {
            this.laeuft = false;
            if (this.nachholen) {
                this.nachholen = false;
                this.anstossen();
            }
        }
    }
}

export const garmentcodeAbsatzregler = new GarmentcodeAbsatzregler();
garmentcodeAbsatzregler.einhaengen();
