import * as THREE from 'three';

/**
 * Randleuchten — der Stil `rand` der Auswahlanzeige (`auswahlaura.js`): ein
 * Fresnel-Leuchten am Umriss des Objekts selbst, wie Spiele Anklickbares zeigen.
 *
 * Je Netz eine HÜLLE als Kind: dieselbe Geometrie, dasselbe Skelett (`bind` mit der
 * `bindMatrix` des Netzes), additiv, ohne Tiefenschreiben, `LessEqual` — sie folgt
 * Pose, Morph und Hautverdeckung, weil sie deren Puffer teilt. Was ein Material erst
 * im Shader verschiebt (Oberflächenbindung, bis ~1 cm), kennt sie nicht; dort liegt
 * das Leuchten minimal daneben.
 */
export class Randleuchten {

    static AUSWAHL = { farbe: 0xb84400, staerke: 1.3, potenz: 3.0, grund: 0.0 };
    static HOVER = { farbe: 0xffe8c8, staerke: 0.8, potenz: 3.5, grund: 0.0 };
    /** Netz → Hülle. */
    static _huellen = new Map();

    /** Die Hüllen auf genau diese Netze legen (Auswahl vor Hover); `faktor` 0 = aus. */
    static setzen(auswahl, hover, faktor = 1) {
        const soll = new Map();
        for (const n of auswahl) soll.set(n, Randleuchten.AUSWAHL);
        // Hover zuletzt: das Stück unter der Maus leuchtet hell, auch in der Auswahl.
        for (const n of hover) soll.set(n, Randleuchten.HOVER);
        for (const [netz, huelle] of Randleuchten._huellen) {
            if (soll.has(netz) && netz.geometry === huelle.geometry) continue;
            huelle.parent?.remove(huelle);
            huelle.material.dispose();
            Randleuchten._huellen.delete(netz);
        }
        for (const [netz, art] of soll) {
            let huelle = Randleuchten._huellen.get(netz);
            if (!huelle) {
                huelle = Randleuchten._huelle(netz);
                Randleuchten._huellen.set(netz, huelle);
            }
            const u = huelle.material.uniforms;
            u.uFarbe.value.set(art.farbe);
            u.uStaerke.value = art.staerke * faktor;
            u.uPotenz.value = art.potenz;
            u.uGrund.value = art.grund * faktor;
        }
    }

    static _huelle(netz) {
        const material = new THREE.ShaderMaterial({
            uniforms: { uFarbe: { value: new THREE.Color() }, uStaerke: { value: 1 },
                        uPotenz: { value: 2 }, uGrund: { value: 0 } },
            vertexShader: Randleuchten.VERTEX,
            fragmentShader: Randleuchten.FRAGMENT,
            transparent: true, depthWrite: false, depthFunc: THREE.LessEqualDepth,
            blending: THREE.AdditiveBlending, side: THREE.FrontSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
        });
        const huelle = netz.isSkinnedMesh ? new THREE.SkinnedMesh(netz.geometry, material)
                                          : new THREE.Mesh(netz.geometry, material);
        if (netz.isSkinnedMesh && netz.skeleton) {
            huelle.bindMode = netz.bindMode;
            huelle.bind(netz.skeleton, netz.bindMatrix);
        }
        huelle.name = 'randleuchten';
        huelle.userData.randleuchten = true;
        huelle.raycast = () => {};          // nie selbst getroffen
        huelle.frustumCulled = netz.frustumCulled;
        huelle.renderOrder = 10;
        huelle.castShadow = huelle.receiveShadow = false;
        netz.add(huelle);                   // Einheitslage: dieselbe Weltmatrix wie das Netz
        return huelle;
    }

    static VERTEX = `
        #include <common>
        #include <skinning_pars_vertex>
        varying vec3 vNormale;
        varying vec3 vBlick;
        void main() {
            #include <beginnormal_vertex>
            #include <skinbase_vertex>
            #include <skinnormal_vertex>
            #include <defaultnormal_vertex>
            #include <begin_vertex>
            #include <skinning_vertex>
            #include <project_vertex>
            vNormale = normalize(transformedNormal);
            vBlick = normalize(-mvPosition.xyz);
        }`;

    static FRAGMENT = `
        uniform vec3 uFarbe;
        uniform float uStaerke;
        uniform float uPotenz;
        uniform float uGrund;
        varying vec3 vNormale;
        varying vec3 vBlick;
        void main() {
            float rand = pow(1.0 - abs(dot(normalize(vNormale), normalize(vBlick))), uPotenz);
            float w = clamp(rand * uStaerke + uGrund, 0.0, 1.0);
            gl_FragColor = vec4(uFarbe * w, 1.0);   // additiv: SrcAlpha 1, die Stärke steckt in w
        }`;
}
