import * as THREE from 'three';
import { Genesis9kartenwerte as Karte } from './genesis9kartenwerte.js';
import { Shaderpatch } from './shaderpatch.js';

/**
 * Genesis9glanz — Rauheit, Glanz, Klarlack, Normalenstärke und Höhe eines Daz-Materials am Physical-Material (17.11.2026, Edgar: „Glanz und
 * Rauheit je Material — ich brauche sie so wie im Original“, „Bump- und Höhenkarten … Nutze das!“).
 *
 * Der Server rechnet Irays Schichten in Threes Größen um (`Genesis9/materialglanz.py`, dort die Quellen):
 *   rauheitwert   → roughness (Daz quadriert wie Three: α = r²); mit Karte Wert × Karte wie Daz
 *   glanzgewicht  → specularIntensity (Gewicht der Glanzschicht, zugleich F90)
 *   glanzf0       → specularColor = F0 / 0,04 bei ior 1,5 (linear)
 *   glanzkarte    → specularIntensityMap — Three liest dort den ALPHA-Kanal, Daz' Karten sind Graubilder ohne Alpha: der Eingriff
 *                   `genesis9glanz` liest den Grünkanal wie bei Rauheit und Klarlackrauheit
 *   rauheitinvers → die Rauheitskarte ist eine Glanzheitskarte (Spiegel/Glanz-Modus): Rauheit = 1 − Wert × Karte
 *   klarlack, klarlackrauheit, klarlackkarte (Rotkanal), klarlackrauheitkarte (Grünkanal) → clearcoat…
 *   normalstaerke → normalScale (DirectX: y umgekehrt); eine gebackene Bumpkarte trägt beides schon im Bild
 *   hoehe, hoehe_skala, hoehe_versatz → displacementMap, -Scale, -Bias in Metern (Daz: Minimum + (Maximum − Minimum) × Karte, × Stärke)
 */
export class Genesis9glanz {

    static F0 = 0.04;
    /** Lineare Karten für das Bündel (`Genesis9netz.bildpfade`); die Glanzfarbkarte ist sRGB, wenn `glanzfarbkarte_srgb`. */
    static LINEAR = ['normalen', 'alpha', 'rauheit', 'metall', 'glanzkarte', 'klarlackkarte', 'klarlackrauheitkarte', 'hoehe'];

    /** Braucht die Gruppe das Physical-Material (Glanz oder Klarlack aus dem Material)? */
    static physisch(bilder) {
        return bilder.glanzgewicht != null || bilder.klarlack != null;
    }

    /** Die Zahlen — sofort, vor den Karten. */
    static werte(material, bilder) {
        if (Number.isFinite(bilder.rauheitwert)) {
            material.roughness = bilder.rauheitwert;
            material.userData.rauheitBasis = bilder.rauheitwert;      // Ausgangswert des einstellbaren Glanzes (`Genesis9teilmaterial._basis`)
        }
        if (Number.isFinite(bilder.hoehe_skala)) {
            material.displacementScale = bilder.hoehe_skala;
            material.displacementBias = bilder.hoehe_versatz || 0;
        }
        if (!material.isMeshPhysicalMaterial) return;
        if (Number.isFinite(bilder.glanzgewicht)) material.specularIntensity = bilder.glanzgewicht;
        const f0 = bilder.glanzf0;
        if (Array.isArray(f0) && f0.length >= 3) {
            material.ior = 1.5;
            material.specularColor.setRGB(f0[0] / Genesis9glanz.F0, f0[1] / Genesis9glanz.F0, f0[2] / Genesis9glanz.F0);
        }
        if (Number.isFinite(bilder.klarlack)) {
            material.clearcoat = bilder.klarlack;
            material.clearcoatRoughness = Number.isFinite(bilder.klarlackrauheit) ? bilder.klarlackrauheit : 0;
        }
        if (bilder.glanzkarte || bilder.rauheitinvers) Genesis9glanz._eingriff(material, Boolean(bilder.glanzkarte), Boolean(bilder.rauheitinvers));
    }

    /** Normalenstärke und DirectX-Achse, sobald die Normalenkarte liegt. */
    static normalSkala(material, bilder) {
        const s = Number.isFinite(bilder.normalstaerke) ? bilder.normalstaerke : 1;
        material.normalScale.set(s, bilder.normalenachse === -1 ? -s : s);
    }

    /** Die Karten aus dem Vorrat einhängen (`laden(pfad, danach, srgb)` wie `Genesis9netz.texturen`). */
    static karten(material, bilder, laden) {
        const setzen = (art, feld, srgb = false) => {
            if (!bilder[art]) return;
            laden(bilder[art], bild => {
                material[feld] = Karte.bild(bild, bilder, art);
                material.needsUpdate = true;
            }, srgb);
        };
        if (material.isMeshPhysicalMaterial) {
            setzen('glanzkarte', 'specularIntensityMap');
            setzen('glanzfarbkarte', 'specularColorMap', Boolean(bilder.glanzfarbkarte_srgb));
            if (Number.isFinite(bilder.klarlack)) {
                setzen('klarlackkarte', 'clearcoatMap');
                setzen('klarlackrauheitkarte', 'clearcoatRoughnessMap');
            }
        }
        if (Number.isFinite(bilder.hoehe_skala)) setzen('hoehe', 'displacementMap');
    }

    static _eingriff(material, gruen, invers) {
        const eingriff = (shader) => {
            if (gruen) {
                shader.fragmentShader = shader.fragmentShader.replace('#include <lights_physical_fragment>',
                    THREE.ShaderChunk.lights_physical_fragment.replace('vSpecularIntensityMapUv ).a', 'vSpecularIntensityMapUv ).g'));
            }
            if (invers) {
                shader.fragmentShader = shader.fragmentShader.replace('#include <roughnessmap_fragment>',
                    '#include <roughnessmap_fragment>\n\troughnessFactor = 1.0 - roughnessFactor;');
            }
        };
        eingriff.kennung = () => `${gruen ? 'g' : 'x'}${invers ? 'i' : 'x'}`;
        Shaderpatch.anhaengen(material, 'genesis9glanz', eingriff);
    }
}
