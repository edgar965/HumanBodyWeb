import { Reitergedaechtnis } from './reitergedaechtnis.js';
import { garmentcodePreset } from './garmentcode_preset.js';

/**
 * Was im GarmentCode-Reiter zuletzt eingestellt war.
 *
 * AUFTRAG (Edgar, 09.09.2026): „merke dir die letzten Einstellungen auf allen
 * Tabs, z.B. GarmentCode, so dass sie beim nächsten Aufruf angeklickt sind."
 *
 * WARUM NICHT ÜBER DIE DOM-FELDER wie der Rest des Reiters
 * =======================================================
 * `Reitergedaechtnis` merkt Felder mit einer `id`. Die 71 Reglerzeilen haben
 * keine — sie tragen einen `data-pfad`, und ihre Werte führt
 * `garmentcodeRegler` in `this.werte`: die ABWEICHUNGEN von den Vorgaben des
 * Servers, und genau die gehen an den Server. Zwei Buchführungen für dieselbe
 * Zahl liefen auseinander, sobald ein Preset oder ein Vorlagenwechsel nur
 * eine von beiden anfasst.
 *
 * JE VORLAGE GETRENNT: `sleeve.cuff.cuff_len` gibt es bei einem Rock nicht.
 * Ein Wert ohne Regler wäre ein stiller Eintrag in `werte`, den der Server
 * mitgeschickt bekäme — und dort würde er verworfen, ohne dass jemand es
 * merkt.
 *
 * DIE HÄKCHEN GEHÖREN DAZU. „Angeklickt" ist wörtlich gemeint: Wenn die Werte
 * eines Presets wiederhergestellt werden, muss auch sein Kästchen stehen.
 * Sonst behauptet die Oberfläche „nichts eingestellt", während die Regler auf
 * „eng anliegend" stehen — die Umkehrung des Falls, für den `pruefen()` im
 * Preset-Modul gebaut wurde.
 */
export class Garmentcodegedaechtnis {

    /** Wo die aktiven Voreinstellungen einer Vorlage liegen. */
    static presetSchluessel(vorlage) {
        return `garmentcode/presets:${vorlage}`;
    }

    /** Reglerwerte und Häkchen dieser Vorlage merken. */
    static merken(regler) {
        const vorlage = regler?.fuerVorlage;
        if (!vorlage) return false;
        Reitergedaechtnis.gcWerteMerken(vorlage, regler.werte);
        Reitergedaechtnis.setzen(
            Garmentcodegedaechtnis.presetSchluessel(vorlage),
            garmentcodePreset.aktiveListe());
        return true;
    }

    /**
     * Die gemerkten Werte setzen — OHNE Bauanstoß.
     *
     * `regler.mehrereSetzen` wäre falsch: Es ruft
     * `GarmentcodeLive.angestossen()`, und beim Seitenstart gibt es noch
     * keinen Schnitt, auf den sich ein Bau beziehen könnte.
     *
     * @returns Anzahl der gesetzten Regler
     */
    static anwenden(regler, vorlage) {
        let gesetzt = 0;
        for (const [pfad, wert] of Object.entries(
                Reitergedaechtnis.gcWerte(vorlage))) {
            // Nur Pfade, die es in DIESER Vorlage gibt. `vorgaben` steht
            // nach dem Zeichnen und ist die verlässliche Liste.
            if (!(pfad in regler.vorgaben)) continue;
            regler.werte[pfad] = wert;
            if (regler.nachziehen[pfad]) regler.nachziehen[pfad](wert);
            gesetzt += 1;
        }
        garmentcodePreset.anhaken(Reitergedaechtnis.holen(
            Garmentcodegedaechtnis.presetSchluessel(vorlage), []));
        return gesetzt;
    }
}
