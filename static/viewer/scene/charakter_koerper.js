/**
 * Charakterkoerper — Koerpernetz neu berechnen, aus einer Modellkonfiguration
 * bauen, Hautfarbe setzen.
 *
 * Aus character.js herausgeloest (Umbau 16.08.2026).
 */

import { state } from './state.js';
import { Netzpunkte } from '../gemeinsam/netzpunkte.js';
import { Augenbrauenbau } from '../gemeinsam/augenbrauenbau.js';
import { HumanbodyModell } from '../gemeinsam/humanbodymodell.js';
import { _charQueryParams } from './utils.js';
import { Modellbauzustand } from './modellgenerator/zustand.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { Stoffvorschau } from './stoffvorschau.js';

export class Charakterkoerper {

    /**
     * Farben und Längen der Details aufs Netz UND die Augenbrauen darauf
     * setzen (12.09.2026) — die Rechnung steht seit 13.09.2026 in
     * `HumanbodyModell.detailsAnwenden` (frische Morphpunkte `neue` vor dem
     * Schreiben ins Attribut, Regler, Häutung); hier bleibt der Name, den
     * die Szene ruft, samt der Hautfarbtabelle der Seite.
     */
    static details(inst, neue = null) {
        if (!inst?.bodyMesh || !inst.details) return 0;
        if (!inst.hautfarben && Object.keys(state.skinColors).length) inst.hautfarben = state.skinColors;
        return inst.detailsAnwenden(neue);
    }

    static materialien(inst) {
        return HumanbodyModell.materialien(inst.bodyMesh);
    }

    static detailsWeg(inst) {
        Augenbrauenbau.entfernen(inst);
    }

    /**
     * Körpernetz zu den aktuellen Reglerständen neu holen.
     *
     * FEHLER 16.08.2026: `properties.js` rief nach jeder Reglerbewegung
     * `inst.reloadBody()` — eine Methode, die es seit dem Herauslösen dieser
     * Klasse aus character.js nicht mehr gab. Jede Morph- und Metaänderung im
     * Eigenschaftsfeld der Szene endete in der Konsole mit
     * "inst.reloadBody is not a function"; das Netz blieb stehen. Umgekehrt
     * wurde `neuLaden` von niemandem gerufen.
     */
    static async neuLaden(inst) {
        // `nur_punkte=1`: Dreiecke, UVs und Materialgruppen bleiben weg. Die
        // Topologie aendert sich durch Morphs nicht, und der Zweig unten setzt
        // ohnehin nur `position` und `normal`. Gemessen 16.08.2026: 5,24 MB ->
        // 2,26 MB je Reglerbewegung. Passt die Punktzahl NICHT (Wechsel der
        // Koerperart), laedt `inst.load()` unten alles vollstaendig.
        const data = await Serverabruf.json(
            `/api/character/mesh/?${_charQueryParams(inst)}&nur_punkte=1`);
        if (data.error) throw new Error(data.error);

        // Die Längen der Details (Wimpern, Fußnägel) auf die frisch gelieferten
        // Punkte — vor dem Schreiben ins Attribut, nie auf schon gestreckte.
        const details = (neue) => Charakterkoerper.details(inst, neue);
        if (!Netzpunkte.aktualisieren(inst.bodyMesh, data, inst.details ? details : null)) {
            if (inst.bodyMesh) {
                Netzentsorgung.entfernen(inst.group, inst.bodyMesh);
                inst.bodyMesh = null;
            }
            await inst.load();
        }
        // Drapierte Kleidung geht mit — HIER, nicht bei den Reglern selbst:
        // Es gibt mehrere Wege, die den Koerper aendern (Morphs, Metaregler,
        // Bauartwechsel, Voreinstellungen), und sie alle enden an dieser
        // Stelle. Einen davon zu vergessen hiesse, dass der Stoff bei genau
        // einem Regler stehen bleibt.
        Stoffvorschau.nachziehen(Charakterkoerper.stellung(inst));
    }

    /**
     * Die Stellung der Figur, wie der Stoffkanal sie braucht.
     *
     * VOLLSTAENDIG, nicht nur das Geaenderte: Der Server setzt seinen
     * Zustand daraus komplett neu. Wer nur Aenderungen schickt, liegt nach
     * dem ersten verlorenen Paket daneben, ohne dass es auffaellt.
     */
    static stellung(inst) {
        return {
            bauart: inst.bodyType || inst.body_type || 'Female_Caucasian',
            morphs: inst.morphs || {},
            meta: inst.meta || {},
        };
    }

    /**
     * Ein erzeugtes Modell (Rig1–4) — die Basis baut es (`Erzeugtesmodell`);
     * die Rig-Knochen des Generators werden vorher geladen, damit
     * `Modellbauzustand` sie für die Bearbeitung hat.
     */
    static async ausKonfiguration(inst) {
        if ((inst.generatedConfig.skeleton_type || 'def') === 'rig') {
            await Modellbauzustand.rigKnochenLaden();
        }
        await inst._erzeugt(state.rigifySkeletonData, state.skinWeightData);
        return inst;
    }

    static hautfarbe(inst, materials) {
        return inst.hautfarbe(state.skinColors, materials);
    }
}
