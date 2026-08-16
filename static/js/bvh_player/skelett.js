/**
 * Spielerskelett — BVH laden, Koerperlinien zeichnen, Bewegung abspielen.
 *
 * Aus bvh_player.js herausgeloest (Umbau 16.08.2026).
 *
 * Gezeichnet werden nur die Koerperknochen des erkannten Formats, nicht der
 * ganze Baum: Ein SkeletonHelper wuerde alle 164 Knochen malen, darunter Finger
 * und Gesicht, und die Ansicht zustellen.
 */
import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { Skelettformat } from './skelettformate.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';

export class Spielerskelett {
    constructor(szene) {
        this.szene = szene;
        this.format = Skelettformat.vorgabe();
        this.knochen = {};
        this.wurzel = null;
        this.linien = null;
        this.mischer = null;
        this.aktion = null;
        this.klipdauer = 0;
    }

    get sichtbar() {
        return !!(this.wurzel && this.wurzel.visible);
    }

    /** BVH laden. Gibt ein Versprechen auf die Klipdauer zurueck. */
    laden(url) {
        return new Promise((fertig, fehlgeschlagen) => {
            new BVHLoader().load(url, (ergebnis) => {
                this._uebernehmen(ergebnis);
                fertig(this.klipdauer);
            }, undefined, fehlgeschlagen);
        });
    }

    _uebernehmen(ergebnis) {
        Protokoll.debug('bvh_player', 'BVH loaded, bones:', ergebnis.skeleton.bones.length);
        this.wurzel = ergebnis.skeleton.bones[0];
        this.szene.scene.add(this.wurzel);
        for (const knochen of ergebnis.skeleton.bones) {
            this.knochen[knochen.name] = knochen;
        }
        const namen = new Set(Object.keys(this.knochen));
        this.format = Skelettformat.erkennen(namen);
        this._abgleichMelden(namen);

        this._linienBauen();
        this._gelenkeBauen(ergebnis.skeleton.bones);
        this._bewegungBauen(ergebnis.clip);

        this.szene.ausrichten(this.wurzel, this.format);
        // Erst zeigen, wenn der Benutzer abspielt.
        this.wurzel.visible = false;
        this.linien.visible = false;
    }

    _abgleichMelden(namen) {
        const { da, fehlt } = this.format.abgleich(namen);
        Protokoll.debug('bvh_player', `Detected ${this.format.name} format`);
        Protokoll.debug('bvh_player', `Bones matched: ${da.length}/`
                    + `${this.format.reihenfolge.length}`, da);
        if (fehlt.length) console.warn('[bvh_player] Bones MISSING:', fehlt);
        window.__bvhDebug = { matched: da, missing: fehlt,
                              allBones: [...namen], bodyBoneMap: this.knochen };
    }

    _linienBauen() {
        const geo = new THREE.BufferGeometry();
        const punkte = new Float32Array(this.format.verbindungen.length * 2 * 3);
        geo.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
        this.linien = new THREE.LineSegments(geo, new THREE.LineBasicMaterial(
            { color: 0x16c784, linewidth: 2 }));
        this.szene.scene.add(this.linien);
        this.linienNachziehen();
    }

    _gelenkeBauen(alleKnochen) {
        const material = new THREE.MeshBasicMaterial({ color: 0xe94560 });
        const kugel = new THREE.SphereGeometry(1.5, 8, 8);
        for (const knochen of alleKnochen) {
            if (this.format.namen.has(knochen.name)) {
                knochen.add(new THREE.Mesh(kugel, material));
            }
        }
    }

    _bewegungBauen(klip) {
        this.mischer = new THREE.AnimationMixer(this.wurzel);
        this.aktion = this.mischer.clipAction(klip);
        // Einmal abspielen und am Ende stehenbleiben — sonst springt die
        // Bewegung am Klipende sichtbar zurueck.
        this.aktion.setLoop(THREE.LoopOnce);
        this.aktion.clampWhenFinished = true;
        this.aktion.play();
        this.klipdauer = klip.duration;
        // Bild 0 anwenden, damit die Knochen ihre Bewegungslage haben und
        // nicht die Ruhelage aus den BVH-Offsets.
        this.mischer.setTime(0);
        this.wurzel.updateWorldMatrix(true, true);
    }

    /** Linienenden auf die aktuellen Knochenpositionen setzen. */
    linienNachziehen() {
        if (!this.linien || !this.wurzel) return;
        const punkte = this.linien.geometry.attributes.position;
        const a = new THREE.Vector3(), b = new THREE.Vector3();
        let i = 0;
        for (const [vater, kind] of this.format.verbindungen) {
            const kv = this.knochen[vater], kk = this.knochen[kind];
            if (kv && kk) {
                kv.getWorldPosition(a);
                kk.getWorldPosition(b);
                punkte.setXYZ(i, a.x, a.y, a.z);
                punkte.setXYZ(i + 1, b.x, b.y, b.z);
            }
            i += 2;
        }
        punkte.needsUpdate = true;
    }

    /** Auf einen Zeitpunkt stellen. Gibt false zurueck, wenn dahinter. */
    zeitSetzen(sekunden) {
        if (!this.mischer || this.klipdauer <= 0) return false;
        if (sekunden >= this.klipdauer) return false;
        if (this.aktion?.paused) {          // nach Klipende erneut freigeben
            this.aktion.reset();
            this.aktion.play();
        }
        this.mischer.setTime(sekunden);
        return true;
    }

    sichtbarkeit(an) {
        if (this.linien) this.linien.visible = an;
        if (this.wurzel) this.wurzel.visible = an;
        if (an) this.linienNachziehen();
    }

    /** Bilddauer einer Bewegung — aus dem Klip, sonst aus der Bildrate. */
    bilddauer(fps) {
        return this.aktion?.getClip().tracks[0]?.times?.[1] || (1 / fps);
    }

    tempo(wert) {
        if (this.aktion) this.aktion.timeScale = wert;
    }

    /** Weltposition eines Knochens oder null. */
    position(name, ziel) {
        const knochen = this.knochen[name];
        if (!knochen) return null;
        knochen.getWorldPosition(ziel);
        return ziel;
    }
}
