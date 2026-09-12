/**
 * Charakterkoerper — Koerpernetz neu berechnen, aus einer Modellkonfiguration
 * bauen, Hautfarbe setzen.
 *
 * Aus character.js herausgeloest (Umbau 16.08.2026).
 */

import { state, THREE } from './state.js';
import { base64ToFloat32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { Netzpunkte } from '../gemeinsam/netzpunkte.js';
import { Koerperdetails } from '../gemeinsam/koerperdetails.js';
import { Augenbrauenbau } from './augenbrauenbau.js';
import { Lippenbau } from './lippenbau.js';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';
import { Hautfarbe } from '../gemeinsam/hautfarbe.js';
import { _charQueryParams } from './utils.js';
import { generateModelMesh, generateRigBoneMesh } from './state.js';
import { Modellbauzustand } from './modellgenerator/zustand.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { Stoffvorschau } from './stoffvorschau.js';

export class Charakterkoerper {

    /**
     * Farben und Längen der Details aufs Netz UND die Augenbrauen darauf
     * setzen (12.09.2026) — eine Stelle für den Bau, die frischen
     * Morphpunkte (`neue`, vor dem Schreiben ins Attribut) und die Regler.
     */
    static details(inst, neue = null) {
        if (!inst?.bodyMesh || !inst.details) return 0;
        // Haut ohne eigene Farbe trägt die der Körperart — auch wieder, wenn
        // der Nutzer sein Farbfeld zurücknimmt (`Detailfarben`, 12.09.2026).
        if (!inst.details.haut) Charakterkoerper.hautfarbe(inst, Charakterkoerper.materialien(inst));
        Koerperdetails.anwenden(inst.bodyMesh, inst.details, neue);
        return Augenbrauenbau.sicher(inst, neue);
    }

    static materialien(inst) {
        const m = inst.bodyMesh?.material;
        return Array.isArray(m) ? m : [m];
    }

    /**
     * Das Körpernetz aus der Antwort von `/api/character/mesh/` — mit der
     * Lippengruppe (12.09.2026, `Lippenbau`) und der Hautfarbe der Körperart.
     * Stand in `character.js`; die Datei darf nicht wachsen.
     */
    static netz(inst, data) {
        const netz = Koerpernetz.netz(data, THREE);
        Lippenbau.abspalten(netz, data.lippen);
        Charakterkoerper.hautfarbe(inst, Array.isArray(netz.material) ? netz.material : [netz.material]);
        return netz;
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

    static async ausKonfiguration(inst) {
        const skelType = inst.generatedConfig.skeleton_type || 'def';
        let result;

        if (skelType === 'rig') {
            await Modellbauzustand.rigKnochenLaden();
            if (!Modellbauzustand.rigKnochen) {
                throw new Error('Rig bones data not loaded');
            }
            result = generateRigBoneMesh(Modellbauzustand.rigKnochen, inst.generatedConfig, state.rigifySkeletonData,
                state.skinWeightData);
            if (result.skeleton) {
                inst.rigifySkeleton = result.skeleton;
                inst.isSkinned = true;
            }
        } else {
            if (!state.rigifySkeletonData || !state.skinWeightData) {
                throw new Error('Skeleton data not loaded');
            }
            result = generateModelMesh(state.rigifySkeletonData, state.skinWeightData, inst.generatedConfig);
            if (result.skeleton) {
                inst.rigifySkeleton = result.skeleton;
                inst.isSkinned = true;
            }
        }

        if (!result) throw new Error('No visible bones in generated model config');

        inst.bodyMesh = result.mesh;
        inst.group.add(inst.bodyMesh);
        return inst;
    }

    static hautfarbe(inst, materials) {
        if (!Object.keys(state.skinColors).length) return;
        Hautfarbe.ausKoerperart(materials[0], inst.bodyType, state.skinColors,
                                { zweites: materials[1], mitErsatz: true });
    }
}
