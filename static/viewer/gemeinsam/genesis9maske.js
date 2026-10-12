import { Genesis9texturen } from './genesis9texturen.js';
import { Hautverdeckung } from './hautverdeckung.js';
import { Anatomiehaut } from './anatomiehaut.js';
import { Protokoll } from './protokoll.js';

/**
 * Genesis9maske — nach einem reinen Materialwechsel (Haut, Augen, Brauen, Makeup) die Hautverdeckung neu rechnen (11.10.2026).
 *
 * Edgar (Bild, „cute girl DAZ" auf dunkler Haut): ein heller, rosa Rand rings um das Scham-Stück. Gemessen im Chrome nach `hautSetzen`:
 * der neue Körper hat KEINE Maske — voller Dreiecksindex (201.248 statt 199.808), kein `indexVoll`, kein `nahtf` — und der Rand des Stücks
 * (`hautfarbe`, `Stueckhaut`) trägt noch die Farbe der alten Haut (198/145/128 statt 99/70/55 auf „G9 Feminine Skin 04"). Ursache: seit
 * 22.09.2026 baut ein Materialwechsel das Skelett nicht mehr neu (`Genesis9Modell.koerperAufbauen`, `skelettFrisch = false`); die Hautverdeckung
 * hört aber nur auf Stück- und Skelettereignis — der frische Körper blieb ohne Loch unter dem Stück, ohne Naht und mit alter Randfarbe.
 *
 * HIER: Nach dem Bau wartet diese Klasse auf alle Bilder (die Randfarbe liest die Karten der NEUEN Haut; vorher bekäme sie die Farbe des
 * Materials, weiß) und plant die Verdeckung neu (`Hautverdeckung.planen`: Ruhezeit, Rechnung im Worker, ohne Stück fast nichts). Ein
 * überholter Bau (`_lauf` weitergezählt) meldet nichts.
 *
 * DIE EINE NACHARBEIT FÜR ALLE WECHSEL (12.10.2026, `Genesis9Modell.materialWechseln`): Dieselbe Stelle lässt auch das Anatomie-Stück der neuen Haut folgen
 * (`Anatomiehaut.nachziehen`). Der Aufruf aus dem Einhängen (`Genesis9ersatz.nachziehen`) kam, bevor der Körper in `inst.bodyMesh` stand, und ein zweiter Wechsel während
 * eines laufenden Abgleichs schloss sich dem ersten an; hier steht der frische Körper, und ein unveränderter Stand tut nichts.
 */
export class Genesis9maske {

    /** Die Verdeckung der Figur nach einem Materialwechsel neu planen und das Anatomie-Stück der Haut folgen lassen, sobald alle Bilder da sind. */
    static nachMaterialwechsel(inst) {
        const lauf = inst._lauf;
        return Genesis9texturen.wartenAufAlle()
            .then(() => {
                if (lauf !== inst._lauf || !inst.bodyMesh) return;
                Hautverdeckung.planen(inst);
                Anatomiehaut.nachziehen(inst);
            })
            .catch(fehler => Protokoll.warnung('Genesis9maske', `Verdeckung nach Materialwechsel: ${fehler.message}`));
    }
}
