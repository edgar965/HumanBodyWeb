/**
 * Vorschau — laedt eine retargetete Animation ins Vorschaufenster (Taste A).
 *
 * Aus project.js herausgeloest (Umbau 16.08.2026). Das Fenster selbst
 * (DOM, Renderer, Kamera, Freigabe) liegt in vorschau_fenster.js; hier steht
 * nur, WAS gezeigt wird: Rig2-Modell holen, Retarget-Daten in einen
 * AnimationClip uebersetzen, optional glaetten, abspielen.
 */
import * as THREE from 'three';
import { fn } from '../gemeinsam/registrierung.js';
import { sharedState } from '../character_core.js?v=1';
import { _gaussSmooth, _gaussFilter } from './werkzeug_glaettung.js';
import { generateRigBoneMesh } from '../modellbau/rignetz.js';
import { Vorschaufenster } from './vorschau_fenster.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

const ss = sharedState;

export class Vorschau {
    /** Welche Animation gerade zu sehen ist — auch fuer fn.getPreviewInfo(). */
    static kategorie = null;
    static name = null;

    static async oeffnen(kategorie, name) {
        Vorschau.kategorie = kategorie;
        Vorschau.name = name;
        Vorschaufenster.sicherstellen();
        Vorschaufenster.zeigen(`${kategorie} / ${name}`);
        Vorschaufenster.leeren();
        try {
            await Vorschau._laden(kategorie, name);
        } catch (e) {
            console.error('[Preview] Load failed:', e);
            Vorschaufenster.meldung(`Fehler: ${e.message}`);
        }
    }

    static async _laden(kategorie, name) {
        const url = `/api/retarget/?category=${encodeURIComponent(kategorie)}`
                  + `&name=${encodeURIComponent(name)}`;
        const r = await fetch(url);
        if (!r.ok) throw new Error(`Retarget API: ${r.status} ${r.statusText}`);
        const data = await r.json();
        if (!data.tracks || !data.frame_count) {
            Vorschaufenster.meldung('Fehler: Keine Animationsdaten');
            return;
        }
        Protokoll.debug('Preview', `Retarget loaded: ${data.frame_count} frames, `
                    + `${Object.keys(data.tracks).length} bones`);

        if (!ss.rigifySkeletonData || !ss.skinWeightData) {
            Vorschaufenster.meldung('Fehler: Skeleton-Daten nicht geladen');
            return;
        }
        const modell = await Vorschau._modellBauen();
        if (!modell) {
            Vorschaufenster.meldung('Fehler: Modell konnte nicht geladen werden');
            return;
        }

        const clip = Vorschau._klipBauen(data, modell.skelett);
        if (_gaussSmooth.active) {
            for (const t of clip.tracks) {
                _gaussFilter(t.values, t.getValueSize(), _gaussSmooth.sigma);
            }
            fn.serverLog('gauss_preview', `${name} sigma=${_gaussSmooth.sigma}`);
        }

        Vorschaufenster.camera.position.set(0, 1.0, 3);
        Vorschaufenster.controls.target.set(0, 0.85, 0);
        Vorschaufenster.controls.update();

        Vorschaufenster.mixer = new THREE.AnimationMixer(modell.netz);
        Vorschaufenster.action = Vorschaufenster.mixer.clipAction(clip);
        Vorschaufenster.action.play();
        Vorschau._schleifeStarten(data.frame_count, data.frame_count / data.duration);
        Protokoll.debug('Preview', 'Rig2 model + retargeted animation ready');
    }

    /**
     * Rig2-Modell in die Vorschauszene bauen.
     *
     * Gibt {netz, skelett} zurueck oder null. Knochennamen werden von Punkt auf
     * Unterstrich umgeschrieben, weil Three.js das in Namen ebenfalls tut und
     * die Keyframe-Spuren sonst kein Ziel finden.
     */
    static async _modellBauen() {
        let rigKnochen = null;
        try {
            const resp = await fetch('/api/character/rig/');
            if (resp.ok) rigKnochen = await resp.json();
        } catch (e) { /* ohne Rig-Daten kein generiertes Modell */ }

        const modellDaten = await Serverabruf.json('/api/character/model/Rig2/');
        if (!rigKnochen || modellDaten.type !== 'generated_model') return null;

        const ergebnis = generateRigBoneMesh(rigKnochen, modellDaten,
                                             ss.rigifySkeletonData, ss.skinWeightData);
        if (!ergebnis?.mesh || !ergebnis?.skeleton) return null;

        const skelett = ergebnis.skeleton;
        if (skelett.skeleton) {
            for (const bone of skelett.skeleton.bones) {
                bone.name = bone.name.replace(/\./g, '_');
            }
        }
        const neu = {};
        for (const [k, v] of Object.entries(skelett.boneByName)) {
            neu[k.replace(/\./g, '_')] = v;
        }
        skelett.boneByName = neu;

        const behaelter = new THREE.Group();
        behaelter.userData._preview = true;
        behaelter.add(ergebnis.mesh);
        Vorschaufenster.scene.add(behaelter);
        return { netz: ergebnis.mesh, skelett };
    }

    static _klipBauen(data, skelett) {
        const spuren = [];
        for (const [knochen, werte] of Object.entries(data.tracks)) {
            const bone = skelett.boneByName[knochen.replace(/\./g, '_')];
            if (!bone) continue;
            spuren.push(new THREE.QuaternionKeyframeTrack(
                bone.name + '.quaternion', data.times, werte));
        }
        if (data.position_track) {
            const bone = skelett.boneByName[data.position_track.bone.replace(/\./g, '_')];
            if (bone) {
                spuren.push(new THREE.VectorKeyframeTrack(
                    bone.name + '.position', data.times, data.position_track.values));
            }
        }
        return new THREE.AnimationClip('preview', data.duration, spuren);
    }

    static _schleifeStarten(gesamtBilder, fps) {
        const anzeige = document.getElementById('preview-frame');
        if (anzeige) anzeige.textContent = `0 / ${gesamtBilder}`;
        if (Vorschaufenster.animId) cancelAnimationFrame(Vorschaufenster.animId);
        Vorschaufenster.clock.start();

        function zeichnen() {
            Vorschaufenster.animId = requestAnimationFrame(zeichnen);
            if (!Vorschaufenster.modal
                || Vorschaufenster.modal.style.display === 'none') return;
            if (Vorschaufenster.mixer) {
                Vorschaufenster.mixer.update(Vorschaufenster.clock.getDelta());
            }
            Vorschaufenster.controls.update();
            Vorschaufenster.renderer.render(Vorschaufenster.scene,
                                            Vorschaufenster.camera);
            if (Vorschaufenster.action && anzeige) {
                const f = Math.round(Vorschaufenster.action.time * fps);
                anzeige.textContent = `${f} / ${gesamtBilder}`;
            }
        }
        zeichnen();
    }
}

fn.previewAnimation = Vorschau.oeffnen;
fn.getPreviewInfo = () => ({ category: Vorschau.kategorie, name: Vorschau.name });
