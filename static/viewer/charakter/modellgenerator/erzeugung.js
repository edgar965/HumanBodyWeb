/**
 * Modellerzeugung — aus der Konfiguration ein Netz bauen und als Charakter in
 * die Szene stellen.
 *
 * Aus modellgenerator_ui.js herausgeloest (Umbau 16.08.2026). Die drei
 * Zeitgeber-Variablen (`_mgRegenTimer`, `_mgRegenBusy`, `_mgDirtyTimer`) lagen
 * lose auf Modulebene und sind jetzt Klassenfelder — sonst waeren sie beim
 * Aufteilen auf der falschen Seite gelandet.
 */
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { generateModelMesh, generateRigBoneMesh } from '../state.js';
import { generateCharacterId } from '../utils.js';
import { Modellbauzustand } from './zustand.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/** Wartezeit, bis eine Reglerbewegung als abgeschlossen gilt (ms). */
const RUHEZEIT = 400;

export class Modellerzeugung {
    /** Laeuft gerade ein Neuaufbau? */
    static _beschaeftigt = false;
    /** Kam waehrenddessen eine weitere Anforderung? */
    static _nachholen = false;
    /** Zeitgeber fuer die verzoegerte Aenderungsmarke. */
    static _ruheZeitgeber = null;

    /**
     * Neuaufbau anfordern.
     *
     * Zwei Bremsen: Die Aenderungsmarke wird erst gesetzt, wenn der Benutzer
     * den Regler losgelassen hat (sonst ein Schnappschuss je Pixel), und
     * waehrend eines laufenden Aufbaus wird hoechstens EIN weiterer gemerkt.
     */
    static anfordern() {
        if (!Modellbauzustand.charakterId) return;   // ohne Charakter kein Neuaufbau
        if (Modellerzeugung._ruheZeitgeber) {
            clearTimeout(Modellerzeugung._ruheZeitgeber);
        }
        Modellerzeugung._ruheZeitgeber = setTimeout(() => {
            Modellerzeugung._ruheZeitgeber = null;
            fn.markDirty?.('Modell-Aenderung');
        }, RUHEZEIT);

        if (Modellerzeugung._beschaeftigt) {
            Modellerzeugung._nachholen = true;
            return;
        }
        Modellerzeugung._beschaeftigt = true;
        requestAnimationFrame(() => {
            Modellerzeugung.charakterBauen();
            Modellerzeugung._beschaeftigt = false;
            if (Modellerzeugung._nachholen) {
                Modellerzeugung._nachholen = false;
                Modellerzeugung.anfordern();
            }
        });
    }

    /** Netz aus der Konfiguration bauen; null, wenn nichts sichtbar ist. */
    static netzBauen() {
        const konfig = Modellbauzustand.konfig;
        if (!konfig) {
            Protokoll.warnung('erzeugung', 'Model Generator: missing config');
            return null;
        }
        if (Modellbauzustand.skelettart === 'rig' && Modellbauzustand.rigKnochen) {
            return generateRigBoneMesh(Modellbauzustand.rigKnochen, konfig,
                                       state.rigifySkeletonData, state.skinWeightData)
                   || null;
        }
        if (!state.rigifySkeletonData || !state.skinWeightData) {
            Protokoll.warnung('erzeugung', 'Model Generator: missing skeleton data');
            return null;
        }
        return generateModelMesh(state.rigifySkeletonData, state.skinWeightData,
                                 konfig) || null;
    }

    /** Netz bauen und als Charakter in die Szene setzen. */
    static charakterBauen() {
        const ergebnis = Modellerzeugung.netzBauen();
        if (!ergebnis) return;

        // Zwischengespeicherte Knochenmarkierungen zeigen auf das alte Netz.
        fn._clearBoneHighlightCache();
        const alt = Modellerzeugung._altenCharakterEntfernen();

        const id = generateCharacterId();
        const konfig = JSON.parse(JSON.stringify(Modellbauzustand.konfig));
        konfig.type = 'generated_model';
        konfig.skeleton_type = Modellbauzustand.skelettart;

        const inst = new fn.CharacterInstance(id, konfig);
        inst.presetName = Modellbauzustand.konfig.name || 'Generiertes Modell';
        inst.presetKey = alt.presetKey;
        inst.bodyType = Modellbauzustand.skelettart === 'rig' ? 'Rig Bones'
                                                              : 'DEF Skeleton';
        inst.bodyMesh = ergebnis.mesh;
        if (ergebnis.skeleton) {
            inst.rigifySkeleton = ergebnis.skeleton;
            inst.isSkinned = true;
        }
        inst.group.add(ergebnis.mesh);
        if (alt.position) inst.group.position.copy(alt.position);

        state.characters.set(id, inst);
        state.scene.add(inst.group);
        Modellbauzustand.charakterId = id;

        fn.updateCharacterListUI();
        fn.updateVertexCount();
        fn.selectCharacter(id);
        Protokoll.debug('Modellbau', 'Model Generator: created '
            + (Modellbauzustand.skelettart === 'rig' ? 'Mesh' : 'SkinnedMesh')
            + ` with ${ergebnis.mesh.geometry.attributes.position.count} vertices `
            + `as character "${inst.presetName}"`);
    }

    /** Vorherige Fassung entfernen und ihre Lage merken. */
    static _altenCharakterEntfernen() {
        const id = Modellbauzustand.charakterId;
        if (!id || !state.characters.has(id)) return { position: null, presetKey: null };
        const alt = state.characters.get(id);
        const gemerkt = { position: alt.group.position.clone(),
                          presetKey: alt.presetKey || null };
        fn.deleteCharacter(id);
        Modellbauzustand.charakterId = null;
        return gemerkt;
    }
}
