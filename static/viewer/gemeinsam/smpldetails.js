import { Detailfarben } from './detailfarben.js';
import { Koerperdetails } from './koerperdetails.js';
import { Netzentsorgung } from './netzentsorgung.js';
import { Protokoll } from './protokoll.js';
import { Smpldetailhaut } from './smpldetailhaut.js';
import { Smplmundbau } from './smplmundbau.js';
import { Smplwimpernbau } from './smplwimpernbau.js';

/**
 * Smpldetails — Augen, Wimpern, Brauen, Mund und Nägel einer SMPL-X-Figur.
 *
 * WARUM (Edgar, 25.09.2026: „mach auch Augen/Augenbrauen/Mund/Nägel"): Die
 * Felder sind DIESELBEN wie bei HumanBody (`Koerperdetails.VORGABE`,
 * Bedienung `scene/detailbedienung.js`), damit derselbe Bereich im Reiter
 * beide Figurarten bedient. Umgesetzt wird anders, weil SMPL-X ein Netz mit
 * Fototextur ist: Lippen, Nägel, Augen und Brauen im Hautshader
 * (`Smpldetailhaut`), Wimpern und Mundinnenraum als eigene Netze
 * (`Smplwimpernbau`, `Smplmundbau`) am Skelett der Figur.
 *
 * Nur für echte SMPL-X-Körper (UV-geteiltes Netz, `inst._uvUrsprung`) —
 * GarmentCodes eigene Referenzkörper haben weder UV noch Mundloch.
 */
export class Smpldetails {

    /** Nach dem Bau der Figur: Wimpern und Mund dazu, Details anwenden. */
    static async bauen(inst, punkte, dreiecke, haut) {
        Smpldetails.abbauen(inst);
        if (!inst._uvUrsprung || !inst.skelett) return;
        try {
            inst._mund = Smplmundbau.bauen(inst.group, inst.skelett, punkte, dreiecke, haut);
            inst._wimpernPunkte = punkte;
            inst._wimpern = Smplwimpernbau.bauen(inst.group, inst.skelett, punkte,
                                                 inst.details.wimpern_laenge);
        } catch (fehler) {
            Protokoll.warnung('Smpldetails', `Mund/Wimpern nicht gebaut: ${fehler.message}`);
        }
        await Smpldetails.anwenden(inst);
    }

    /** Die eigenen Netze wieder abnehmen (vor einem Neubau). */
    static abbauen(inst) {
        for (const netz of [inst._wimpern, ...Object.values(inst._mund || {})]) {
            if (!netz) continue;
            netz.parent?.remove(netz);
            Netzentsorgung.baum(netz);
        }
        inst._wimpern = null;
        inst._mund = null;
    }

    /**
     * Farben, Glanz und Längen auf Haut, Wimpern und Mund — sofort, ohne Server
     * (außer der Brauenkarte, die `Brauendecal` je Reglerstand zeichnet).
     * @param feld  das geänderte Feld (null = alles)
     */
    static async anwenden(inst, feld = null) {
        if (!inst.bodyMesh || !inst._uvUrsprung) return;
        const d = inst.details;
        if (feld === 'wimpern_laenge' && inst._wimpernPunkte) {
            inst._wimpern?.parent?.remove(inst._wimpern);
            if (inst._wimpern) Netzentsorgung.baum(inst._wimpern);
            inst._wimpern = Smplwimpernbau.bauen(inst.group, inst.skelett, inst._wimpernPunkte,
                                                 d.wimpern_laenge);
        }
        const farbe = (name) => (Detailfarben.istFarbe(d[name]) ? d[name] : Detailfarben.VORGABE[name]);
        inst._wimpern?.material.color.set(farbe('wimpern'));
        if (inst._mund) {
            inst._mund.zaehne.material.color.set(farbe('zaehne'));
            inst._mund.zunge.material.color.set(farbe('zunge'));
            inst._mund.hoehle.material.color.set(farbe('zunge')).multiplyScalar(0.3);
        }
        // Fehlt Maske oder Brauenkarte, bleibt die Figur, wie sie ist — ein
        // Detail darf den Bau nicht scheitern lassen.
        try {
            await Smpldetailhaut.anwenden(inst.bodyMesh, d, inst.geschlecht);
        } catch (fehler) {
            Protokoll.warnung('Smpldetails', `Hautdetails nicht angewandt: ${fehler.message}`);
        }
    }

    /** Die Details aus Modelldaten (Feld `details`), wie bei HumanBody. */
    static aus(daten) {
        return Koerperdetails.aus(daten);
    }
}
