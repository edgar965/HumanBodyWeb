import { THREE } from './state.js';
import { state } from './state.js';
import { Groessenangleich } from '../gemeinsam/groessenangleich.js';
import { UmaFigur } from './uma/umafigur.js';

/**
 * Figurplatzierung — wo eine neu geladene Figur steht und wie groß sie ist.
 *
 * WARUM (Edgar, 06.09.2026): „beim Laden eines neuen Modells, immer mit der
 * gleichen Größe wie das andere, und nicht gleiche Position." Bisher setzten
 * beide Ladewege `x = anzahl * 0.8` und ließen die Größe, wie sie kam — eine
 * UMA-Figur von 2,05 m stand dann neben einer HumanBody-Figur von 1,75 m,
 * und wer zwei Figuren nacheinander lud, bekam sie teils ineinander.
 *
 * Vorgabe seither: dieselbe sichtbare Höhe wie die Figur, die schon da ist,
 * und 1,5 m rechts daneben. Beides ist im Dialog änderbar.
 *
 * Gemessen wird je Figurart verschieden, weil die Bounding-Box das Skinning
 * NICHT sieht: Bei einer UMA-Figur steckt die Form in den Knochen, und die
 * Box lieferte für zwei verschieden große Figuren dieselbe Zahl. Dort misst
 * `UmaFigur.hoehe` über `applyBoneTransform`. Bei einer HumanBody-Figur sind
 * die Morphs im Netz eingerechnet (der Server liefert verformte Punkte), da
 * genügt die Box.
 */
export class Figurplatzierung {

    /** Abstand zur Nachbarfigur in Metern. */
    static ABSTAND_M = 1.5;

    /**
     * Die Figur, an der sich eine neue ausrichtet: die zuletzt hinzugefügte.
     * `null`, wenn die Szene leer ist — dann steht die neue im Ursprung.
     */
    static vorbild(ausser = null) {
        let letzte = null;
        for (const inst of state.characters.values()) {
            if (inst !== ausser) letzte = inst;
        }
        return letzte;
    }

    /** Sichtbare Höhe einer Figur in Metern; 0, wenn nichts zu messen ist. */
    static hoehe(inst) {
        if (!inst?.group) return 0;
        inst.group.updateMatrixWorld(true);
        if (inst.netze?.length) {
            // UMA: die Form steckt in den Knochen, die Box sieht sie nicht.
            const ueber_knochen = UmaFigur.hoehe(inst.netze);
            if (ueber_knochen > 0) return ueber_knochen;
        }
        const kasten = new THREE.Box3().setFromObject(inst.group);
        if (!isFinite(kasten.min.y) || !isFinite(kasten.max.y)) return 0;
        const hoch = kasten.max.y - kasten.min.y;
        return hoch > 0 ? hoch : 0;
    }

    /**
     * Was der Dialog vorschlägt: rechts neben der vorhandenen Figur, auf
     * deren Höhe gebracht.
     */
    static vorgaben() {
        const vorbild = Figurplatzierung.vorbild();
        return {
            x: vorbild ? Number((vorbild.group.position.x
                                 + Figurplatzierung.ABSTAND_M).toFixed(2)) : 0,
            angleichen: Boolean(vorbild),
            vorbildHoehe: vorbild ? Figurplatzierung.hoehe(vorbild) : 0,
        };
    }

    /**
     * Nach dem Laden anwenden: Position setzen und, wenn gewünscht, die Figur
     * auf die Höhe des Vorbilds skalieren.
     *
     * @param inst  die neue Figur (bereits geladen — vorher hat sie keine Größe)
     * @param wahl  `{x, angleichen}` aus dem Dialog; fehlt sie, gelten die Vorgaben
     */
    static anwenden(inst, wahl = null) {
        const werte = { ...Figurplatzierung.vorgaben(), ...(wahl || {}) };
        inst.group.position.set(Number(werte.x) || 0, 0, 0);
        if (!werte.angleichen) return 1;
        const faktor = Groessenangleich.faktor(Figurplatzierung.hoehe(inst),
                                               werte.vorbildHoehe);
        if (faktor === 1) return 1;
        inst.group.scale.setScalar(faktor);
        inst.group.updateMatrixWorld(true);
        return faktor;
    }
}
