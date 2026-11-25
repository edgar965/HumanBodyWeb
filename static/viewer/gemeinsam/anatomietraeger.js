import { Meshgenesisanatomiehuelle } from '../meshgenesis/meshgenesisanatomiehuelle.js';

/**
 * Anatomietraeger — ein Stück eines gespeicherten Modells, das die Anatomie trägt, zeigt sie wie Foto-/Mesh-Genesis: verdeckt, nicht drapiert (24.11.2026).
 *
 * Edgar, 24.11.2026: „EdgarNeu laden im Charakter dauert ewig, das muss in 2 s laden, fixe!!“. Gemessen (py-spy am Server): Die Hose aus Foto-Genesis (97.235 Punkte) kam
 * mit der Daz-Anatomie als `getragen` in die Stückrechnung, und der Drapierer (`G9anatomiedrapierung`) löste ein System mit 17.334 Unbekannten iterativ, eine Lösung stand
 * nach 49.716 Schritten noch aus. Warum der Körper bei Edgar 11,2 s brauchte, ist damit NICHT erklärt (neben laufender Drapierung: 1,86 s). Auf Foto-Genesis wird dasselbe Stück nicht
 * drapiert: es trägt die Anatomie (`Kleideranatomie.getragen`, Zeile `traegt_anatomie`), und `Meshgenesisanatomiehuelle` zeichnet das Anatomie-Stück nicht (Edgar
 * 20.11.2026 zum Drapieren über das Glied: „Schlauch“). Seit heute speichert „Als Modell speichern“ diese Entscheidung je Stück (`figur.kleidung[k].traegt_anatomie`,
 * `Meshgenesistestmodell._stueck`); der Server nimmt die Anatomie dann aus `getragen` (`G9anatomiedrapierung.ohne_anatomie`), und hier bleibt sie verborgen,
 * solange die Kleider an sind und ein solches Stück getragen wird — dieselbe Klasse wie auf Foto-Genesis.
 */
export class Anatomietraeger {

    /** `inst.anatomieGetragen` für Figuren, die es nicht selbst setzen (Foto-Genesis und Mesh-Genesis setzen eigene). */
    static einrichten(inst) {
        if (!inst || inst.anatomieGetragen) return;
        inst.anatomieGetragen = () => inst.kleiderSichtbar !== false && Object.values(inst.kleidung || {}).some(w => w?.traegt_anatomie === true);
    }

    /** Sichtbarkeit der Anatomie-Stücke nach dem Stand von `inst.anatomieGetragen` setzen, die Hautverdeckung nur bei einer Änderung neu planen. */
    static planen(inst) {
        Anatomietraeger.einrichten(inst);
        Meshgenesisanatomiehuelle.planen(inst, true);
    }
}
