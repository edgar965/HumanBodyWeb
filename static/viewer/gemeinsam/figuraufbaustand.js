/**
 * Figuraufbaustand — läuft der Nachzug auf die volle Stufe noch?
 *
 * WARUM (26.09.2026, Edgar: „aktiviere export nur wenn die Figur ganz geladen
 * ist"): Eine Genesis-9-Figur kommt in zwei Zügen (`Genesis9aufbau`): erst der
 * Käfig, dann im Hintergrund die volle Stufe. Zwischen beiden steht die Figur
 * vollständig in der Szene und sieht auf den ersten Blick fertig aus — sie hat
 * nur ein Sechzehntel ihrer Dreiecke (zwei Unterteilungsstufen). Wer in diesem
 * Fenster exportiert, bekommt STILL das grobe Netz: gemessen 49.552 statt
 * 792.828 Körperdreiecke, 110 MB statt 261 MB, ohne Meldung und ohne Fehler.
 *
 * `inst.fein` ist zwar ein Promise, das man abwarten KANN, aber es hinterlässt
 * keinen Zustand: ein Dialog kann nicht sehen, ob es noch offen ist, und nach
 * einem Reglerzug (`koerperAufbauen`) gibt es das Promise gar nicht. Deshalb
 * hier ein Zähler je Figur, synchron lesbar (`laeuft`), plus ein Ereignis, an
 * dem die Bedienung hängt — dasselbe Muster wie `Stueckereignis`.
 *
 * Der Export wartet zusätzlich selbst (`Modellexport.exportieren`); die Sperre
 * im Dialog ist die sichtbare Hälfte, das Warten die verlässliche.
 */
export class Figuraufbaustand {

    static EREIGNIS = 'figur-aufbaustand';

    /** Ein Zug beginnt — jeder `beginnen` braucht sein `beenden`. */
    static beginnen(inst) {
        if (!inst) return;
        inst._aufbauZuege = (inst._aufbauZuege || 0) + 1;
        Figuraufbaustand._melden(inst);
    }

    static beenden(inst) {
        if (!inst) return;
        inst._aufbauZuege = Math.max(0, (inst._aufbauZuege || 0) - 1);
        Figuraufbaustand._melden(inst);
    }

    /** Synchron: baut die Figur gerade noch auf? */
    static laeuft(inst) {
        return !!(inst && inst._aufbauZuege > 0);
    }

    /**
     * Abwarten, bis die Figur steht — auch wenn gerade nichts läuft.
     * Nimmt `inst.fein` mit, falls ein Zug vor dieser Klasse gestartet wurde.
     */
    static async warten(inst) {
        if (!inst) return;
        // Wer wartet, braucht die feine Stufe JETZT: Der Aufbau nach Ruhe (`Genesis9aufbau._haeppchen`) wartet dann nicht mehr.
        inst._feinDringend = true;
        if (inst.fein) await Promise.resolve(inst.fein).catch(() => {});
        // `_grobHalt`: Der Nutzer hat „grob" gewählt (`Genesis9aufbau.stufeSetzen`) und der Export ist deshalb gesperrt —
        // das ist kein Aufbau, auf den man warten könnte.
        while (Figuraufbaustand.laeuft(inst) && !inst._grobHalt) {
            await new Promise((weiter) => setTimeout(weiter, 100));
        }
    }

    static _melden(inst) {
        if (typeof document === 'undefined' || !document.dispatchEvent) return;
        document.dispatchEvent(new CustomEvent(Figuraufbaustand.EREIGNIS, {
            detail: { id: inst.id, laeuft: Figuraufbaustand.laeuft(inst) },
        }));
    }
}
