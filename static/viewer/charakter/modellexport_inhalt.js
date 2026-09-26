import { state } from './state.js';

/**
 * Modellexportinhalt — was exportiert wird, und die Warnungen dazu.
 *
 * KÖRPER GEGEN ASSETS: „Körper" ist `inst.bodyMesh` plus alles, was UNTER
 * ihm hängt (z. B. fest sitzende Detailnetze); „Assets" ist alles andere
 * Sichtbare unter `inst.group` — Haare, Kleidung, GarmentCode-Stücke,
 * MakeHuman-Proxys. Jede Figurart hängt ihre Teile so an (`character.js`,
 * `hair.js`, `cloth.js`, `garmentcode_anziehen.js`, `mhproxynetz.js`) —
 * geprüft, nicht vermutet.
 */
export const STATISCHE_FORMATE = ['obj', 'ply', 'stl'];
export const GERIGGTE_FORMATE = ['glb', 'blend', 'dae'];

export class Modellexportinhalt {

    /** Alle sichtbaren Meshes — Körper zuerst, Assets danach (wenn gewählt). */
    static objekte(inst, { assets = true } = {}) {
        const koerper = [];
        const zubehoer = [];
        const gehoertZumKoerper = (obj) => {
            for (let p = obj; p; p = p.parent) {
                if (p === inst.bodyMesh) return true;
                if (p === inst.group) return false;
            }
            return false;
        };
        inst.group.traverse((obj) => {
            if (!obj.isMesh || obj.visible === false) return;
            (gehoertZumKoerper(obj) ? koerper : zubehoer).push(obj);
        });
        if (!koerper.length && inst.bodyMesh && inst.bodyMesh.visible !== false) koerper.push(inst.bodyMesh);
        return assets ? [...koerper, ...zubehoer] : koerper;
    }

    /**
     * Die Wurzel-Knochen aller Skelette unter den gegebenen Meshes — OHNE sie
     * schreibt `GLTFExporter` für jedes Gelenk `joints: null` statt eines
     * Knoten-Index (Fund 26.09.2026: Blender lehnte die GLB deshalb mit
     * „Couldn't parse glTF" ab — `skeleton.bones` hängen NICHT unter den
     * Meshes selbst, der Exporter braucht sie als EIGENE Objekte im
     * übergebenen Array, um sie mit einem Knoten-Index zu versehen).
     */
    static skelettWurzeln(objekte) {
        const wurzeln = new Set();
        for (const obj of objekte) {
            if (!obj.isSkinnedMesh || !obj.skeleton || !obj.skeleton.bones.length) continue;
            let wurzel = obj.skeleton.bones[0];
            while (wurzel.parent && wurzel.parent.isBone) wurzel = wurzel.parent;
            wurzeln.add(wurzel);
        }
        return [...wurzeln];
    }

    /** Zustand der aktiven Animation, bezogen auf DIESE Figur. */
    static animationsstand(inst) {
        const aktiv = !!(state.currentAction && state._animatedCharId === inst.id);
        const fremdId = state.currentAction && state._animatedCharId && state._animatedCharId !== inst.id
            ? state._animatedCharId : null;
        return {
            aktiv,
            fremd: !!fremdId,
            fremdname: fremdId ? (state.characters.get(fremdId)?.presetName || fremdId) : null,
            clip: aktiv ? state.currentAction.getClip() : null,
        };
    }

    /** Warnungen zur gewählten Optionen-Kombination — vor dem Export, live im Dialog. */
    static warnungen(inst, optionen) {
        const { formate, rig, textur, animation } = optionen;
        const warnungen = [];
        const statisch = formate.filter((f) => STATISCHE_FORMATE.includes(f));
        const anim = Modellexportinhalt.animationsstand(inst);

        if (animation) {
            if (anim.fremd) {
                warnungen.push(`Die aktive Animation gehört zu „${anim.fremdname}" — sie wird nicht exportiert.`);
            } else if (!anim.aktiv) {
                warnungen.push('Keine Animation aktiv — es wird die gewählte Pose exportiert.');
            } else if (statisch.length) {
                warnungen.push(
                    `${statisch.join(', ').toUpperCase()} kann keine Animation speichern — dort wird die `
                    + 'gewählte Pose exportiert.'
                );
            }
        }
        if (!rig && formate.some((f) => GERIGGTE_FORMATE.includes(f))) {
            warnungen.push('Rig ist aus — auch GLB/.blend/DAE bekommen ein starres Netz ohne Skelett.');
        }
        if (textur && formate.includes('stl')) {
            warnungen.push('STL kann keine Textur speichern — das Netz bleibt ohne Bildkarte.');
        }
        warnungen.push(...Modellexportinhalt._texturwarnungen(inst, textur));
        return warnungen;
    }

    static _texturwarnungen(inst, textur) {
        if (!textur) return [];
        const warnungen = [];
        for (const obj of Modellexportinhalt.objekte(inst)) {
            const werkstoffe = Array.isArray(obj.material) ? obj.material : [obj.material];
            for (const werkstoff of werkstoffe) {
                if (werkstoff && werkstoff.isShaderMaterial) {
                    warnungen.push(
                        `„${obj.name || 'Teil'}" hat einen eigenen Shader — dessen Bildkarten kommen `
                        + 'beim Export eventuell nicht mit.'
                    );
                }
            }
        }
        return warnungen;
    }
}
