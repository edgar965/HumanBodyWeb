/**
 * Charakterkoerper — Koerpernetz neu berechnen, aus einer Modellkonfiguration
 * bauen, Hautfarbe setzen.
 *
 * Aus character.js herausgeloest (Umbau 16.08.2026).
 */

import { state } from './state.js';
import { base64ToFloat32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { Netzpunkte } from '../gemeinsam/netzpunkte.js';
import { Hautfarbe } from '../gemeinsam/hautfarbe.js';
import { _charQueryParams } from './utils.js';
import { generateModelMesh, generateRigBoneMesh } from './state.js';
import { Modellbauzustand } from './modellgenerator/zustand.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';

export class Charakterkoerper {

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

        if (!Netzpunkte.aktualisieren(inst.bodyMesh, data)) {
            if (inst.bodyMesh) {
                Netzentsorgung.entfernen(inst.group, inst.bodyMesh);
                inst.bodyMesh = null;
            }
            await inst.load();
        }
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
