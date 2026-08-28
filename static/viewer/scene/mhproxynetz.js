import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _charQueryParams } from './utils.js';
import { _skinifyMesh, convertInstToSkinned } from './skeleton.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Netzgeometrie } from '../gemeinsam/netzgeometrie.js';

/**
 * Mhproxynetz — ein MakeHuman-Proxy anfragen und als Netz in die Figur hängen.
 *
 * Herausgelöst aus `mhproxy_anpassen.js` (247 Zeilen). Hier steckt die
 * Umrechnung, und die hat drei Fallen:
 *
 * DIE EINHEITEN DER REGLER SIND NICHT DIE DES SERVERS
 * ===================================================
 *     Abstand      Millimeter  ->  Meter    (/1000)
 *     Steifigkeit  Prozent     ->  0…1      (/100)
 *     Maßstab      Prozent     ->  Faktor   (/100)
 *     Höhe         Millimeter  ->  Meter    (/1000)
 *     Schiebeweg   Millimeter  ->  Millimeter (unverändert!)
 * Wer eine davon vergisst, bekommt ein Kleidungsstück, das tausendfach zu weit
 * oder gar nicht anliegt.
 *
 * BLENDER-ACHSEN SIND NICHT DIE VON THREE.JS
 * ==========================================
 * `blenderToThreeCoords` dreht Punkte UND Normalen (Z-oben -> Y-oben). Nur die
 * Punkte zu drehen ergibt ein Netz, das an der richtigen Stelle sitzt und
 * falsch beleuchtet ist — der klassische „schwarze Rock".
 *
 * DAS ALTE NETZ MUSS WIRKLICH WEG
 * ===============================
 * `remove` allein reicht nicht: Geometrie und Material liegen im Grafikspeicher,
 * bis `dispose()` sie freigibt. Bei einem Regler, der jede 400 ms neu anpasst,
 * sind das in einer Minute 150 Netze.
 */
export class Mhproxynetz {

    static ENDPUNKT = '/api/character/mh-proxy-fit/';

    /** Reglerwert -> Serverwert: (Feldname, Teiler, Stellen, Vorgabe). */
    static UMRECHNUNG = [
        ['offset', 1000, 4, 0],
        ['stiffness', 100, 2, 50],
        ['scale', 100, 3, 100],
        ['y_offset', 1000, 4, 0],
    ];

    constructor(inst, kennung, werte) {
        this.inst = inst;
        this.kennung = kennung;
        this.werte = werte || {};
        this.farbe = new THREE.Color(this.werte.color || '#4d5980');
    }

    get schluessel() {
        return `mh_${this.kennung}`;
    }

    // ------------------------------------------------------------------ Anfrage

    parameter() {
        const felder = _charQueryParams(this.inst);
        felder.set('garment_id', this.kennung);
        felder.set('color_r', this.farbe.r.toFixed(3));
        felder.set('color_g', this.farbe.g.toFixed(3));
        felder.set('color_b', this.farbe.b.toFixed(3));
        for (const [name, teiler, stellen, vorgabe] of Mhproxynetz.UMRECHNUNG) {
            const wert = this.werte[name] ?? vorgabe;
            felder.set(name, (wert / teiler).toFixed(stellen));
        }
        // Millimeter bleiben Millimeter — die einzige Ausnahme.
        felder.set('push_dist', String(this.werte.push_dist ?? 3));
        felder.set('use_mh_body', '1');
        felder.set('tpose_displacement',
                   this.werte.tpose_disp ?? window._mhTposeDisplacement ?? '1');
        return felder;
    }

    /** Anpassen: anfragen, Netz bauen, in die Figur hängen. */
    async anpassen() {
        if (!this.inst.isSkinned && state.rigifySkeletonData
                && state.skinWeightData) {
            convertInstToSkinned(this.inst);
        }
        let daten;
        try {
            daten = await Serverabruf.json(
                `${Mhproxynetz.ENDPUNKT}?${this.parameter()}`);
        } catch (fehler) {
            Protokoll.fehler('mhproxy', 'Anpassen fehlgeschlagen', fehler);
            return null;
        }
        if (daten.error) {
            Protokoll.warnung('mhproxy', 'MH proxy fit error:', daten.error);
            return null;
        }
        this.altesNetzWeg();
        const netz = this.netzBauen(daten);
        this.einhaengen(netz, daten);
        Protokoll.debug('MH', `fit: ${this.kennung} (${daten.vertex_count} verts)`);
        fn.markDirty?.(`MH ${this.kennung}`);
        return netz;
    }

    altesNetzWeg() {
        const altes = this.inst.clothMeshes[this.schluessel];
        if (!altes) return;
        this.inst.group.remove(altes);
        altes.geometry.dispose();      // sonst bleibt es im Grafikspeicher
        // Die TEXTUR zuerst: `material.dispose()` gibt sie NICHT mit frei
        // (Three.js-Doku: „Textures of a material don't get disposed"). Beim
        // Regler-Refit alle 400 ms sind das in einer Minute 150 Texturen im
        // Grafikspeicher. Befund aus dem Sparring mit Gemma, 18.08.2026.
        altes.material.map?.dispose();
        altes.material.dispose();
        delete this.inst.clothMeshes[this.schluessel];
    }

    // -------------------------------------------------------------------- Netz

    netzBauen(daten) {
        // Der Haken merkt sich den Punktpuffer: Er wird spaeter fuer die
        // Anpassung an die Figur gebraucht, und ein zweites Dekodieren waere
        // bei 70.000 Punkten Verschwendung.
        const geometrie = Netzgeometrie.bauen(
            daten, THREE, (puffer) => { this._punkte = puffer; });
        return _skinifyMesh(geometrie, this.werkstoff(daten), this.inst, daten);
    }

    /**
     * Material — Textur schlägt Farbe.
     *
     * Mit Textur wird die Farbe WEISS: Sie multipliziert sonst in die Textur und
     * färbt das Kleidungsstück ein zweites Mal. `polygonOffset` hält den Stoff
     * vor der Haut, sonst blitzt sie an flachen Stellen durch (Z-Fighting).
     */
    werkstoff(daten) {
        const deckkraft = (this.werte.opacity ?? 100) / 100;
        const werkstoff = new THREE.MeshStandardMaterial({
            color: this.materialfarbe(daten),
            roughness: (this.werte.roughness ?? 50) / 100,
            metalness: (this.werte.metalness ?? 0) / 100,
            side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
            transparent: deckkraft < 1, opacity: deckkraft,
        });
        this.texturNachladen(werkstoff, daten);
        return werkstoff;
    }

    materialfarbe(daten) {
        if (daten.has_texture) return new THREE.Color(1, 1, 1);
        if (daten.mat_color) {
            return new THREE.Color(daten.mat_color[0], daten.mat_color[1],
                                   daten.mat_color[2]);
        }
        return this.farbe;
    }

    /**
     * Die Textur kommt SPÄTER als das Netz — und manchmal zu spät.
     *
     * Zwischen dem Start des Ladens und dem Rückruf kann ein zweiter Fit
     * gelaufen sein; der hat das Netz von eben samt Werkstoff freigegeben
     * (`altesNetzWeg`). Wer dann `werkstoff.map = textur` setzt, hängt die
     * Textur an ein totes Material: Sie liegt im Grafikspeicher und wird nie
     * gezeichnet, und niemand gibt sie je frei.
     *
     * Deshalb der Vergleich mit dem Werkstoff, der GERADE an der Figur hängt.
     * Passt er nicht, wird die Textur sofort weggeräumt.
     * (Befund aus dem Sparring mit Nemotron, 18.08.2026.)
     */
    texturNachladen(werkstoff, daten) {
        if (!daten.has_texture || !daten.texture_name) return;
        const adresse = '/api/character/garment/texture/'
            + `${encodeURIComponent(this.kennung)}/`
            + `${encodeURIComponent(daten.texture_name)}/`;
        new THREE.TextureLoader().load(adresse, textur => {
            if (this.inst.clothMeshes[this.schluessel]?.material !== werkstoff) {
                textur.dispose();      // zu spät — das Netz ist schon ersetzt
                return;
            }
            textur.colorSpace = THREE.SRGBColorSpace;
            werkstoff.map = textur;
            werkstoff.needsUpdate = true;
        });
    }

    // -------------------------------------------------------------- Einhängen

    einhaengen(netz, daten) {
        this.inst.clothMeshes[this.schluessel] = netz;
        this.inst.group.add(netz);
        // Die Ausgangspunkte merken: Das Herausdrücken rechnet von ihnen aus,
        // sonst summiert sich jeder Klick auf.
        this.inst.garmentOrigPositions[this.schluessel] =
            new Float32Array(this._punkte);
        this.inst.mhProxies = this.inst.mhProxies || {};
        this.inst.mhProxies[this.kennung] = this.gemerkteWerte(daten);
    }

    /** Was zur Figur gespeichert wird — dieselben Namen wie die Regler. */
    gemerkteWerte(daten) {
        const farbe = this.materialfarbe(daten);
        return {
            id: this.kennung,
            color: '#' + farbe.getHexString(),
            offset: this.werte.offset ?? 0,
            stiffness: this.werte.stiffness ?? 50,
            scale: this.werte.scale ?? 100,
            y_offset: this.werte.y_offset ?? 0,
            push_dist: this.werte.push_dist ?? 3,
            roughness: this.werte.roughness ?? 50,
            metalness: this.werte.metalness ?? 0,
            opacity: this.werte.opacity ?? 100,
        };
    }
}
