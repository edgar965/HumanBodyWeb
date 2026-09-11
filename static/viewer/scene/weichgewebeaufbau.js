/**
 * Weichgewebeaufbau — was `Weichgewebe` EINMAL je Figur anlegt.
 *
 * Aus `weichgewebe.js` abgeteilt (11.09.2026, Dateigrenze): der Aufbau der
 * Rechenkörper, das `zuschlag`-Attribut und der Shader-Patch. Der Takt je
 * Bild bleibt drüben.
 *
 * ALLE gehäuteten Kleidungsstücke der Figur kommen mit, nicht nur die von
 * GarmentCode: Vorlagen-Cloth (`tpl_`), Garderobe (`gar_`) und MakeHuman-
 * Proxys (`mh_`) hängen am selben Skelett und bekommen denselben Zuschlag.
 * Ein starres Netz (ohne `skinIndex`) bleibt außen vor — es bewegt sich
 * ohnehin nicht mit.
 *
 * JEDES STÜCK BEKOMMT EINE STOFFGRENZE gegen den Körper derselben Figur
 * (`gemeinsam/stoffgrenze.js`): Der Zuschlag wird je Bild so gekürzt, dass
 * 6 mm zur Haut bleiben — die Rechnung des Server-Wegs, seit heute auch
 * hier. Bis dahin bekam Kleidung die halbe Stärke, weil die Grenze fehlte.
 */
import { THREE } from './state.js';
import { Weichgewebekoerper } from '../gemeinsam/weichgewebekoerper.js';
import { Knochentempo } from '../gemeinsam/knochentempo.js';
import { Stoffgrenze } from '../gemeinsam/stoffgrenze.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Weichgewebeaufbau {

    /** Der Eintrag je Figur: Skelett, Rechenkörper, Arbeitsfelder. */
    static anlegen(inst) {
        const skelett = inst.bodyMesh.skeleton;
        if (!skelett) return null;
        const b = skelett.bones.length;
        const eltern = new Int32Array(b);
        const nummer = new Map(skelett.bones.map((k, i) => [k, i]));
        for (let i = 0; i < b; i++) {
            const p = skelett.bones[i].parent;
            eltern[i] = (p && nummer.has(p)) ? nummer.get(p) : -1;
        }
        const koerper = Weichgewebeaufbau.netz(inst.bodyMesh, eltern, 1.0, null);
        if (!koerper) return null;
        const netze = [koerper];
        for (const [schluessel, netz] of Object.entries(inst.clothMeshes || {})) {
            if (!netz?.isSkinnedMesh || netz.skeleton !== skelett) continue;
            const teil = Weichgewebeaufbau.netz(netz, eltern, 1.0, koerper);
            if (teil) { teil.schluessel = schluessel; netze.push(teil); }
        }
        return {
            inst, skelett, eltern, netze,
            tempo: new Knochentempo(b), ziel: 0,
            staerke: 0, maxima: [], b,
            matrizen: new Float64Array(b * 16), gelenke: new Float64Array(b * 3),
            pos: new Float64Array(b * 3), quat: new Float64Array(b * 4),
            elternDreh: new Float64Array(b * 9),
            _m: new THREE.Matrix4(), _m2: new THREE.Matrix4(),
            _bindInv: new THREE.Matrix4(), _q: new THREE.Quaternion(),
            _v: new THREE.Vector3(), _s: new THREE.Vector3(),
        };
    }

    /**
     * Ein Netz: Rechenkörper, `zuschlag`-Attribut, gepatchtes Material.
     * `koerper` ist der Eintrag des Körpers (für die Stoffgrenze) oder null,
     * wenn dieses Netz der Körper selbst ist.
     */
    static netz(netz, eltern, anteil, koerper) {
        const geo = netz.geometry;
        const pos = geo.getAttribute('position');
        const si = geo.getAttribute('skinIndex');
        const sw = geo.getAttribute('skinWeight');
        if (!pos || !si || !sw) return null;
        const gelenkeRuhe = Weichgewebeaufbau.gelenkeRuhe(netz);
        const rechner = new Weichgewebekoerper(pos.array, si.array, sw.array,
                                               eltern, gelenkeRuhe);
        const attribut = new THREE.BufferAttribute(rechner.zuschlag, 3);
        attribut.setUsage(THREE.DynamicDrawUsage);
        geo.setAttribute('zuschlag', attribut);
        Weichgewebeaufbau.shader(netz);
        const teil = { netz, koerper: rechner, attribut, anteil, grenze: null };
        if (koerper) teil.grenze = Weichgewebeaufbau.grenze(koerper.netz, pos.array);
        return teil;
    }

    /** Die Stoffgrenze eines Stücks gegen den Körper — in RUHE gebunden. */
    static grenze(koerpernetz, stoffRuhe) {
        const geo = koerpernetz.geometry;
        const punkte = geo.getAttribute('position').array;
        let dreiecke = geo.index ? geo.index.array : null;
        if (!dreiecke) {
            // Nicht indizierte Geometrie: jedes Tripel ist ein Dreieck.
            dreiecke = new Uint32Array(punkte.length / 3);
            for (let i = 0; i < dreiecke.length; i++) dreiecke[i] = i;
        }
        const t0 = performance.now();
        const grenze = new Stoffgrenze(punkte, dreiecke, stoffRuhe);
        Protokoll.debug('weichgewebe', `Stoffgrenze: ${stoffRuhe.length / 3} Stoffpunkte an `
            + `${grenze.benutzt.length} Körperpunkten, ${(performance.now() - t0).toFixed(0)} ms`);
        return grenze;
    }

    /** Gelenke in Ruhe, im Netzraum: inverse(boneInverse) bringt den
     *  Ursprung des Knochens in den Bind-Weltraum, `bindMatrixInverse`
     *  von dort in den Netzraum. */
    static gelenkeRuhe(netz) {
        const sk = netz.skeleton;
        const aus = new Float32Array(sk.bones.length * 3);
        const m = new THREE.Matrix4(), v = new THREE.Vector3();
        for (let k = 0; k < sk.bones.length; k++) {
            m.copy(sk.boneInverses[k]).invert().premultiply(netz.bindMatrixInverse);
            v.setFromMatrixPosition(m);
            aus[3 * k] = v.x; aus[3 * k + 1] = v.y; aus[3 * k + 2] = v.z;
        }
        return aus;
    }

    static shader(netz) {
        // Der Körper trägt ein ARRAY von Materialien (Haut, Augen, Zähne,
        // Wimpern — je Materialgruppe eines); ein Kleidungsstück ein
        // einzelnes. Beide Formen, dieselbe Behandlung.
        const liste = Array.isArray(netz.material) ? netz.material : [netz.material];
        const neu = liste.map((alt) => Weichgewebeaufbau.patchen(alt));
        netz.material = Array.isArray(netz.material) ? neu : neu[0];
    }

    static patchen(alt) {
        if (!alt) return alt;
        if (alt.userData?.weichgewebe) return alt;
        // Eigenes Material: Das des Körpers ist womöglich geteilt, und ein
        // Netz ohne `zuschlag`-Attribut bekäme im Shader undefinierte Werte.
        const mat = alt.clone();
        mat.userData = { ...(alt.userData || {}), weichgewebe: true };
        mat.onBeforeCompile = (shader) => {
            shader.vertexShader = shader.vertexShader
                .replace('#include <common>', '#include <common>\nattribute vec3 zuschlag;')
                .replace('#include <skinning_vertex>',
                         '#include <skinning_vertex>\ntransformed += zuschlag;');
        };
        // Eigener Programmschlüssel: Three.js teilt kompilierte Programme
        // zwischen gleichartigen Materialien; ohne den Schlüssel bekäme ein
        // ungepatchtes Material dasselbe Programm — oder umgekehrt.
        mat.customProgramCacheKey = () => 'weichgewebe';
        mat.needsUpdate = true;
        return mat;
    }
}
