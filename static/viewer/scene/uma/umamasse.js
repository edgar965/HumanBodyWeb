import { UmaFigur } from './umafigur.js';
import { Umaanimation } from './umaanimation.js';
import { state } from '../state.js';

/**
 * Umamasse — die Größe einer UMA-Figur in Zentimetern.
 *
 * WARUM NUR NOCH MESSEN (06.09.2026): Die drei Regler Größe, Gewicht und
 * Muskeln, die hier standen, sind in die gemeinsame Reglertabelle gewandert
 * (`scene/gemeinsameregler.js`) — dort stehen sie für UMA und HumanBody an
 * derselben Stelle und feiner getrennt (Ober-/Unterkörper). Geblieben ist,
 * was nur UMA kann und was der gemeinsame Block braucht: die MESSUNG der
 * sichtbaren Höhe. `height` ist bei UMA ein Knochenmaß 0..1, kein Maß in
 * Zentimetern; die cm entstehen nur, indem man die Figur ausmisst.
 *
 * Die Regler `GEWICHT` und `MUSKELN` bleiben als Namensbündel stehen: Sie
 * sagen, welche DNA-Werte zusammengehören, und `mittel()` liest sie aus.
 */
export class Umamasse {

    static GEWICHT = ['upperWeight', 'lowerWeight', 'belly', 'waist'];
    static MUSKELN = ['upperMuscle', 'lowerMuscle'];

    /**
     * Zentimeter aus der Gelenkspanne: einmal wird die sichtbare Höhe (alle
     * Punkte durch ihre Knochen) gemessen, danach genügt das billige
     * Verhältnis der Gelenkspannen — die Regler ziehen sich sonst zäh.
     *
     * Nur in der Ruhelage messen: Läuft eine Animation, ist die Figur gebeugt
     * und die Gelenkspanne kürzer — die Anzeige sagte dann 101 cm statt 168
     * (06.09.2026). Die alte Basis gilt dann weiter.
     */
    static cm(inst) {
        const basis = Umamasse.basis(inst);
        if (!basis || !basis.gelenke) return '?';
        if (state._animatedCharId === inst.id) return Math.round(basis.cm);
        inst.group.updateMatrixWorld(true);
        return Math.round(basis.cm * Umaanimation.hoehe(inst) / basis.gelenke);
    }

    /** Die Messgrundlage, einmal je Figur und nur in der Ruhelage erneuert. */
    static basis(inst) {
        if (!inst._masseBasis || state._animatedCharId !== inst.id) {
            inst._masseBasis = {
                cm: UmaFigur.hoehe(inst.netze) * 100,
                gelenke: Umaanimation.hoehe(inst),
            };
        }
        return inst._masseBasis;
    }

    /** Mittel der genannten DNA-Werte in 0–100; 50, wenn die Rasse keinen davon kennt. */
    static mittel(inst, namen) {
        const werte = namen.filter(n => n in inst.dna).map(n => inst.dna[n]);
        return werte.length ? Math.round(werte.reduce((a, b) => a + b, 0) / werte.length * 100) : 50;
    }

    static gewicht(inst) {
        return Umamasse.mittel(inst, Umamasse.GEWICHT);
    }
}
