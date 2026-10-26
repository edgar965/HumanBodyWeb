import * as THREE from 'three';
import { EigenkragenGLSL } from './eigenkragenglsl.js';
import { Eigenkragengeometrie } from './eigenkragengeometrie.js';
import { Stoffshader } from './stoffshader.js';
import { Protokoll } from './protokoll.js';

/**
 * Eigenkragen — der Kragen eines eigenen Oberteils als eigene Fläche (25.10.2026 nachts, Auftrag Edgar: „Kragen mit echter Geometrie (Polo-/Hemdkragen, Stehkragen)
 * … der Haltung folgt (Skinning wie die Schale) und Regler hat (Höhe, Spitzenlänge, Abstand vom Hals, umgelegt/stehend). Im Speicher, kein Neubau beim Reglerzug“).
 *
 * Ein `SkinnedMesh` am Skelett des Körpers, gebunden wie die Schale (`Eigenkleid.binden`: dieselbe `bindMatrix`, dieselbe Lage in der Gruppe). Das Netz baut
 * `Eigenkragengeometrie` aus der Schale — nur bei geändertem Ausschnitt, Schale oder Lücke (`_stand`); Höhe, Spitze, Abstand und Form sind Uniforms (`uKgGestalt`).
 * Das Material teilt die Uniforms des Oberteils (Sitz, Brücke: der Kragen setzt auf der Schale an) und dessen Stoff (`stueck.stoffU`, Farbe, Rauheit, Metall).
 * Die Knopfleiste bleibt gezeichnet (`EigenkleidschnittGLSL`); liegt eine an, lässt der Kragen vorn ihre Breite frei.
 */
export class Eigenkragen {

    constructor(stueck) {
        this.stueck = stueck;
        this.u = { uKgGestalt: { value: new THREE.Vector4() } };
        this.netz = null;
        this.geo = null;
        this._stand = '';
        this.material = new THREE.MeshStandardMaterial({ metalness: 0, side: THREE.DoubleSide });
        this.material.name = 'eigenkragen';
        this.material.onBeforeCompile = (shader) => {
            const fehlt = EigenkragenGLSL.patchen(shader, { ...stueck.u, ...this.u });
            Stoffshader.patchen(shader, stueck.stoffU);
            if (fehlt.length) Protokoll.warnung('Eigene Kleider', `Kragen-Shader ohne Stelle ${fehlt.join(', ')}`);
        };
        this.material.customProgramCacheKey = () => `${EigenkragenGLSL.SCHLUESSEL}|${Stoffshader.SCHLUESSEL}${Stoffshader.FASSUNG}`;
        this.stand = null;
    }

    /** Nach jedem Binden und jeder Wertänderung des Oberteils; `w` = `Eigenkleidwerte.shaderwerte('oberteil', …)`. */
    nachfuehren(w) {
        const s = this.stueck;
        this.u.uKgGestalt.value.set(...w.gestalt);
        this.material.color.setHex(w.farbe);
        this.material.roughness = w.rauheit;
        this.material.metalness = w.metall;
        if (!(w.gestalt[0] > 0.5) || !s.netz || !s.geo || s.weg) {
            if (this.netz) this.netz.visible = false;
            return;
        }
        const luecke = w.kragen[2] > 0.5 && w.kragen[1] > 0 ? w.kragen[3] : Eigenkragengeometrie.LUECKE_M;
        const ausschnitt = { form: w.hals[0], tiefe: w.hals[1], hinten: w.hals[2], breite: w.hals[3], laenge: s.u.uKkLaenge.value.x, steh: w.kragen[0] };
        const stand = [s.geo.id, ...Object.values(ausschnitt), luecke].map(String).join('|');
        if (stand !== this._stand) {
            const stoff = s.materialien.get('stoff');
            const liste = [s.netz.material].flat();
            const neu = Eigenkragengeometrie.bauen(s.geo, g => liste[g.materialIndex] === stoff, ausschnitt, luecke, s.uvMeter);
            this._stand = stand;
            this.geo?.dispose();
            this.geo = neu?.geo || null;
            this.stand = neu ? { ms: neu.ms, laengeM: neu.laenge, besetzt: neu.besetzt } : null;
            if (!neu) Protokoll.warnung('Eigene Kleider', 'Kragen: kein geschlossener Ausschnittrand gefunden — Kragen bleibt verborgen');
        }
        if (!this.geo) {
            if (this.netz) this.netz.visible = false;
            return;
        }
        this._binden(s.netz);
    }

    _binden(schale) {
        if (!this.netz) {
            this.netz = new THREE.SkinnedMesh(this.geo, this.material);
            this.netz.name = `eigenkragen_${this.stueck.inst.id}`;
            this.netz.frustumCulled = false;
            this.netz.castShadow = false;
            this.netz.receiveShadow = true;
            this.netz.raycast = () => {};
            this.netz.userData.eigenkleid = 'kragen';
        } else if (this.netz.geometry !== this.geo) {
            this.netz.geometry = this.geo;
        }
        this.netz.position.copy(schale.position);
        this.netz.quaternion.copy(schale.quaternion);
        this.netz.scale.copy(schale.scale);
        this.netz.updateMatrix();
        this.netz.bindMode = schale.bindMode;
        this.netz.bind(schale.skeleton, schale.bindMatrix);
        if (schale.parent && this.netz.parent !== schale.parent) schale.parent.add(this.netz);
        this.netz.visible = schale.visible;
    }

    verbergen() {
        if (this.netz) this.netz.visible = false;
    }

    entfernen() {
        this.netz?.parent?.remove(this.netz);
        this.netz = null;
        this.geo?.dispose();
        this.geo = null;
        this.material.dispose();
        this._stand = '';
    }
}
