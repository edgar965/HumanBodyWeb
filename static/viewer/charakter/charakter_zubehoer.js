/**
 * Charakterzubehoer — Stoff, Kleidung, Haare und MakeHuman-Proxys eines
 * Charakters nachladen.
 *
 * Aus character.js herausgeloest (Umbau 16.08.2026): Die Klasse
 * CharacterInstance hatte 537 Zeilen, davon 220 nur fuer das Nachladen von
 * Zubehoer. Als statische Methoden mit dem Charakter als erstem Parameter
 * bleibt der Ablauf lesbar, ohne die Klasse weiter aufzublaehen.
 */

import * as THREE from 'three';
import { state, gltfLoader } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _applyGarmentRegionOffsets,
         _computeGarmentRegionWeights } from './kleidung_anpassen.js';
import { Kleidungszustand } from './kleidungszustand.js';
import { _skinifyHairGroup, _skinifyMesh, convertInstToSkinned } from './skeleton.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Netzgeometrie } from '../gemeinsam/netzgeometrie.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { Kleiderwerkstoff } from '../gemeinsam/kleiderwerkstoff.js';
import { Kleiderfrage } from '../gemeinsam/kleiderfrage.js';
import { applyHairColor } from '../character_core.js';

export class Charakterzubehoer {

    /**
     * Die Regler-Werte der Figur an die Abfrage anhaengen.
     *
     * BEFUND `doppelcode` (30.08.2026): Die zwei Schleifen standen zweimal in
     * dieser Datei — einmal fuer Stoffvorlagen, einmal fuer Kleidungsstuecke.
     *
     * NULLWERTE BLEIBEN DRAUSSEN, und das ist kein Sparen: Der Server nimmt
     * fuer jeden NICHT genannten Regler seine Vorgabe, und die ist 0. Wer alle
     * 207 Morphs mitschickt, macht aus jeder Kleideranfrage eine Adresse von
     * mehreren Kilobyte — bei jedem Reglerzug.
     */
    static morphparameter(inst, params) {
        for (const [name, wert] of Object.entries(inst.morphs)) {
            if (wert !== 0) params.set(`morph_${name}`, wert);
        }
        for (const [name, wert] of Object.entries(inst.meta)) {
            if (wert !== 0) params.set(`meta_${name}`, wert);
        }
    }

    static async proxys(inst) {
        const list = inst._pendingMHProxies || [];
        inst._pendingMHProxies = [];
        for (const entry of list) {
            if (!entry || !entry.id) continue;
            try { await fn._fitMHProxyOnInst(inst, entry.id, entry); }
            catch (e) { Protokoll.warnung('charakter_zubehoer', 'MH proxy load failed:', entry.id, e); }
        }
    }

    static async stoff(inst) {
        for (const [key, mesh] of Object.entries(inst.clothMeshes)) {
            inst.group.remove(mesh);
            mesh.geometry.dispose();
            mesh.material.dispose();
        }
        inst.clothMeshes = {};

        if (!inst.cloth || inst.cloth.length === 0) return;
        const isMale = inst.bodyType.startsWith('Male_');
        if (isMale) return;

        if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
            convertInstToSkinned(inst);
        }

        for (const c of inst.cloth) {
            try {
                const method = c.method || 'template';
                const params = new URLSearchParams();
                params.set('method', method);
                params.set('body_type', inst.bodyType);

                let key;
                if (method === 'builder') {
                    params.set('region', c.region || 'TOP');
                    params.set('looseness', c.looseness !== undefined ? c.looseness : 0.5);
                    key = `bld_${c.region || 'TOP'}`;
                } else if (method === 'primitive') {
                    params.set('prim_type', c.prim_type || 'PRIM_SKIRT');
                    params.set('segments', c.segments || 32);
                    params.set('length', c.length !== undefined ? c.length : 0.5);
                    params.set('flare', c.flare !== undefined ? c.flare : 0.5);
                    key = `prim_${c.prim_type || 'PRIM_SKIRT'}`;
                } else {
                    const tpl = c.template || 'TPL_TSHIRT';
                    params.set('template', tpl);
                    params.set('tightness', c.tightness !== undefined ? c.tightness : 0.5);
                    params.set('segments', c.segments || 32);
                    if (c.top_extend) params.set('top_extend', c.top_extend);
                    if (c.bottom_extend) params.set('bottom_extend', c.bottom_extend);
                    key = `tpl_${tpl}`;
                }

                Charakterzubehoer.morphparameter(inst, params);

                const data = await Serverabruf.json(`/api/character/cloth/?${params}`);
                if (data.error) { Protokoll.warnung('charakter_zubehoer', 'Cloth error:', data.error); continue; }

                const geo = Netzgeometrie.bauen(data, THREE);

                const matColor = c.color ? new THREE.Color(c.color) : new THREE.Color(0.5, 0.5, 0.6);
                const mat = new THREE.MeshStandardMaterial({
                    color: matColor, roughness: 0.8, metalness: 0.0,
                    side: THREE.DoubleSide,
                });

                const mesh = _skinifyMesh(geo, mat, inst, data);
                inst.clothMeshes[key] = mesh;
                inst.group.add(mesh);
            } catch (e) {
                Protokoll.fehler('charakter_zubehoer', 'Stoff nicht angelegt', e);
            }
        }
    }

    static async kleidung(inst) {
        if (!inst.garments || inst.garments.length === 0) return;

        if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
            convertInstToSkinned(inst);
        }

        const params = new URLSearchParams();
        params.set('body_type', inst.bodyType);
        Charakterzubehoer.morphparameter(inst, params);

        // NEBENEINANDER (09.09.2026, Edgar: „laden der Szene dauert sehr
        // lange, bis zu 10 s"): Jede Anpassung ist ein eigener Serverlauf und
        // liegt auf dem kritischen Pfad — die Figur erscheint erst mit der
        // letzten. Gemessen, drei Stücke, je zwei Läufe im Wechsel:
        // nacheinander 1,85 / 2,00 s, nebeneinander 1,08 / 1,73 s.
        const antworten = await Promise.all(inst.garments.map(
            (g) => Serverabruf.json(
                `/api/character/garment/fit/?${
                    Kleiderfrage.fuer(params, g, THREE.Color)}`)
                .then((daten) => ({ g, daten }))
                .catch((fehler) => ({ g, fehler }))));

        for (const { g, daten: data, fehler } of antworten) {
            try {
                if (fehler) throw fehler;
                if (data.error) {
                    Protokoll.warnung('charakter_zubehoer', 'Garment load error:', data.error);
                    continue;
                }

                const vertBuf = Netzgeometrie.punkte(data.vertices);
                const geo = Netzgeometrie.bauen(
                    { vertices: data.vertices, faces: data.faces }, THREE);

                const mat = Kleiderwerkstoff.bauen(
                    THREE, g.color, g.roughness, g.metalness);

                const mesh = _skinifyMesh(geo, mat, inst, data);
                const key = `gar_${g.id}`;
                inst.clothMeshes[key] = mesh;
                inst.group.add(mesh);
                inst.garmentOrigPositions[key] = new Float32Array(vertBuf);
                // Hier stand `[color.r, color.g, color.b]` mit einer
                // Variablen `color`, die es nicht gibt (09.09.2026).
                inst.garmentState[key] = Kleidungszustand.ausJson({ ...g });
                // Zustand, Gewichte, Verschiebung — in dieser Reihenfolge;
                // ohne die letzte Zeile lag das Netz unverschoben da
                // (gemessen 09.09.2026: 0 statt 70 mm).
                _computeGarmentRegionWeights(inst, key);
                _applyGarmentRegionOffsets(inst, key);
            } catch (e) {
                Protokoll.fehler('charakter_zubehoer',
                                 `„${g.id}" nicht angezogen`, e);
            }
        }
    }

    static async haare(inst) {
        if (inst.hairMesh) {
            Netzentsorgung.entfernen(inst.group, inst.hairMesh);
            inst.hairMesh = null;
        }

        if (!inst.hairStyle || !inst.hairStyle.url) return;

        return new Promise((resolve) => {
            gltfLoader.load(inst.hairStyle.url, (gltf) => {
                let hairGroup = gltf.scene;

                if (inst.isSkinned && inst.rigifySkeleton) {
                    hairGroup = _skinifyHairGroup(hairGroup, inst);
                }

                inst.hairMesh = hairGroup;

                // `applyHairColor` prueft die Farbe selbst und tut nichts,
                // wenn es sie nicht gibt (28.08.2026, Befund `doppelcode`).
                applyHairColor(inst.hairMesh, inst.hairStyle.color,
                               state.hairColorData);

                inst.group.add(inst.hairMesh);
                resolve(undefined);
            }, undefined, (err) => {
                Protokoll.warnung('charakter_zubehoer', 'Failed to load hair:', err);
                resolve(undefined);
            });
        });
    }
}

// In der Registrierung angemeldet, damit skeleton.js die Haare nachladen kann,
// ohne diese Datei zu importieren: charakter_zubehoer.js holt sich seinerseits
// `convertInstToSkinned` von dort — ein direkter Import waere ein Ring.
fn.charakterHaare = (inst) => Charakterzubehoer.haare(inst);
