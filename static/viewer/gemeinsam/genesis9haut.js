import * as THREE from 'three';
import { Genesis9hautGLSL } from './genesis9hautglsl.js';

/**
 * Genesis9haut — Zusätze auf `MeshStandardMaterial`/`MeshPhysicalMaterial`:
 * das Durchscheinen der Haut (PBRSkin-Translucency), die Schminke
 * (PBRSkin-Makeup), die 8K-Detailnormalen und der Klarlack (Top Coat).
 * Die Shader-Stücke stehen in `genesis9hautglsl.js`.
 *
 * DURCHLICHT — WAS DAZ HAT UND THREE NICHT (17.09.2026): PBRSkin streut
 * Licht unter der Haut (Iray-SSS); `Translucency Weight` 0,85 und
 * `Transmitted Color` [0,98, 0,48, 0,35] stehen im Preset
 * (`Genesis9/durchlicht.py`). Three.js hat dafür nichts — Ohren und
 * Nasenflügel bleiben im Gegenlicht schwarz. Die Näherung: Barré-Brisebois
 * & Bouchard, „Approximating Translucency …" (GDC 2011):
 *
 *     H = normalize(L + N · verzerrung)
 *     I = pow(saturate(dot(V, −H)), potenz) · mass
 *     durchlicht += Lichtfarbe · (I + ambient) · dünne
 *
 * `dünne` (0..1, Attribut `dicke`) kommt vom Server (`Genesis9/dicke.py`).
 * Verzerrung 0,2, Potenz 4, Maß 0,3, Ambient 0 — Anzeigewerte, keine
 * Daz-Werte (mit 0,05 Ambient leuchtete das ganze Gesicht rot; Sichtproben
 * 17.09.2026). Nur für Richtungslichter; wer kein `dicke`-Attribut hat
 * (Anhänge, Kleidung), bekommt keinen Zusatz.
 *
 * SCHMINKE (18.09.2026): PBRSkin mischt sein Makeup als Schicht über die
 * Diffusfarbe — `pbr_skin.mdl`: `weighted_layer(weight: makeup_weight,
 * layer: diffuse(makeup_color), base: diffuse)`, die Rauheit wird
 * `roughness · lerp(1, makeup_roughness_mult, makeup_weight)`. Der Server
 * legt die Ebenen zu Bildern zusammen (`Genesis9/ebenen.py`: Farbe,
 * Gewicht, Rauheit, Glanz `_k.png`, Glitzer-Normalen `_n.png`) und gibt
 * Zahlen mit (`werte`: `klarlackfarbe`, `klarlackbump`, `normalenmodus`).
 * Bis die Bilder da sind, halten 1×1-Platzhalter die Sampler.
 *
 * KLARLACK (abends): Irays Top Coat ist `custom_curve_layer(weight,
 * ggx(tint: top_coat_color), normal: blend_normals(normal, base_bump,
 * top_coat_bump_weight))` (`pbr_skin.mdl`). Three: `clearcoatMap` (das
 * Glanzbild), die Farbe als Faktor am Clearcoat-Anteil (`uKlarlackFarbe`),
 * der Bump-Weight als `clearcoatNormalMap` = Hautnormale mit Skalierung =
 * Weight (ohne Karte nimmt Three die glatte Geometrienormale = Weight 0).
 *
 * FALLE: Three rollt die Lichtschleife aus (`unroll_loop`) — Deklarationen
 * im Rumpf stehen danach dreimal im selben Block. Variablen davor deklarieren.
 */
export class Genesis9haut {

    /**
     * @param material  MeshStandardMaterial der Gruppe
     * @param werte     `{gewicht, farbe: [r, g, b]}` aus dem Preset (sRGB)
     */
    static durchlicht(material, werte) {
        const farbe = new THREE.Color().setRGB(werte.farbe[0], werte.farbe[1], werte.farbe[2],
                                               THREE.SRGBColorSpace);
        const gewicht = Number(werte.gewicht) || 0;
        Genesis9haut._zusatz(material).durchlicht = { gewicht, farbe };
        Genesis9haut._einhaengen(material);
        return material;
    }

    /** Die Schminke ankündigen — die Bilder kommen mit `schminkeBilder`. */
    static schminke(material) {
        const zusatz = Genesis9haut._zusatz(material);
        zusatz.schminke = {
            uSchminkeAn: { value: 0 },
            uSchminkeFarbe: { value: Genesis9haut.platzhalter(0, 0, 0, THREE.SRGBColorSpace) },
            uSchminkeGewicht: { value: Genesis9haut.platzhalter(0, 0, 0) },
            // R = Rauheitsfaktor (255 = 1), G = Ersatzwert, B = Ersatzgewicht.
            uSchminkeRauheit: { value: Genesis9haut.platzhalter(255, 0, 0) },
            // Glitzer-Normalen (RGBA, Alpha = Ebene); Modus 1 = Overlay, 0 = Ersatz.
            uSchminkeNormalenAn: { value: 0 },
            uSchminkeNormalenModus: { value: 1 },
            uSchminkeNormalen: { value: Genesis9haut.platzhalter(128, 128, 255, THREE.NoColorSpace, 0) },
        };
        Genesis9haut._einhaengen(material);
        return material;
    }

    /** Die Detailnormalen ankündigen (`gewicht` = Daz' Detail Weight); Bild folgt mit `detailBild`. */
    static detail(material, gewicht = 1) {
        const zusatz = Genesis9haut._zusatz(material);
        zusatz.detail = {
            uDetailAn: { value: 0 },
            uDetailGewicht: { value: Number.isFinite(gewicht) ? gewicht : 1 },
            uDetailNormalen: { value: Genesis9haut.platzhalter(128, 128, 255) },
        };
        Genesis9haut._einhaengen(material);
        return material;
    }

    static detailBild(material, bild) {
        const d = material.userData.genesis9?.detail;
        if (!d || !bild) return;
        d.uDetailNormalen.value = bild;
        d.uDetailAn.value = 1;
    }

    /** Geladene Bilder einhängen; an, sobald Farbe und Gewicht da sind. */
    static schminkeBilder(material, bilder) {
        const s = material.userData.genesis9?.schminke;
        if (!s) return;
        if (bilder.farbe) { bilder.farbe.colorSpace = THREE.SRGBColorSpace; s.uSchminkeFarbe.value = bilder.farbe; }
        if (bilder.gewicht) s.uSchminkeGewicht.value = bilder.gewicht;
        if (bilder.rauheit) s.uSchminkeRauheit.value = bilder.rauheit;
        if (bilder.glanz) Genesis9haut.glanzBild(material, bilder.glanz);
        if (bilder.normalen) { s.uSchminkeNormalen.value = bilder.normalen; s.uSchminkeNormalenAn.value = 1; }
        s.uSchminkeAn.value = (s.uSchminkeFarbe.value.isDataTexture || s.uSchminkeGewicht.value.isDataTexture) ? 0 : 1;
    }

    /**
     * Klarlack (R), Klarlackrauheit (G) und Metall (B) — EIN Bild auf Threes
     * `clearcoatMap` (.x), `clearcoatRoughnessMap` (.y), `metalnessMap` (.b);
     * die Faktoren auf 1, das Bild ist der Kanal (Daz' LIE ersetzt ihn ebenso).
     */
    static glanzBild(material, bild) {
        if (!material.isMeshPhysicalMaterial || !bild) return;
        material.clearcoat = 1; material.clearcoatMap = bild;
        material.clearcoatRoughness = 1; material.clearcoatRoughnessMap = bild;
        material.metalness = 1; material.metalnessMap = bild;
        material.needsUpdate = true;
    }

    /**
     * Die Zahlen der Schminke (`werte` vom Server): Top Coat Color als Faktor
     * am Klarlack, Top Coat Bump Weight als Skalierung der Hautnormale in der
     * Klarlackschicht, der Modus der Glitzer-Normalen.
     */
    static glanzWerte(material, werte) {
        const zusatz = Genesis9haut._zusatz(material);
        if (zusatz.schminke && werte.normalenmodus) {
            zusatz.schminke.uSchminkeNormalenModus.value = werte.normalenmodus === 'overlay' ? 1 : 0;
        }
        if (material.isMeshPhysicalMaterial && Array.isArray(werte.klarlackfarbe)) {
            const f = werte.klarlackfarbe;
            zusatz.klarlack = { uKlarlackFarbe: { value: new THREE.Color().setRGB(f[0], f[1], f[2], THREE.SRGBColorSpace) } };
            Genesis9haut._einhaengen(material);
        }
        if (material.isMeshPhysicalMaterial && werte.klarlackbump > 0) {
            zusatz.klarlackbump = werte.klarlackbump;
            Genesis9haut.klarlackNormalen(material);
        }
    }

    /** Die Hautnormale in die Klarlackschicht, sobald beides da ist (Weight = Skalierung). */
    static klarlackNormalen(material) {
        const w = material.userData.genesis9?.klarlackbump;
        if (!w || !material.normalMap || !material.isMeshPhysicalMaterial) return;
        material.clearcoatNormalMap = material.normalMap;
        material.clearcoatNormalScale.set(w, w * Math.sign(material.normalScale.y || 1));
        material.needsUpdate = true;
    }

    static platzhalter(r, g, b, farbraum = THREE.NoColorSpace, a = 255) {
        const bild = new THREE.DataTexture(new Uint8Array([r, g, b, a]), 1, 1);
        bild.colorSpace = farbraum;
        bild.needsUpdate = true;
        return bild;
    }

    static _zusatz(material) {
        material.userData.genesis9 = material.userData.genesis9 || {};
        return material.userData.genesis9;
    }

    static _einhaengen(material) {
        const zusatz = material.userData.genesis9;
        material.onBeforeCompile = (shader) => {
            if (zusatz.durchlicht) {
                shader.uniforms.uDurchlicht = { value: zusatz.durchlicht.gewicht };
                shader.uniforms.uDurchlichtFarbe = { value: zusatz.durchlicht.farbe };
                shader.vertexShader = shader.vertexShader
                    .replace('#include <common>',
                             '#include <common>\nattribute float dicke;\nvarying float vDuenne;')
                    .replace('#include <begin_vertex>',
                             '#include <begin_vertex>\nvDuenne = dicke;');
                shader.fragmentShader = shader.fragmentShader
                    .replace('#include <common>',
                             '#include <common>\nuniform float uDurchlicht;\n'
                             + 'uniform vec3 uDurchlichtFarbe;\nvarying float vDuenne;')
                    .replace('#include <lights_fragment_end>',
                             '#include <lights_fragment_end>\n' + Genesis9hautGLSL.DURCHLICHT);
            }
            if (zusatz.detail) {
                Object.assign(shader.uniforms, zusatz.detail);
                shader.fragmentShader = shader.fragmentShader
                    .replace('#include <common>',
                             '#include <common>\nuniform float uDetailAn;\n'
                             + 'uniform float uDetailGewicht;\nuniform sampler2D uDetailNormalen;');
            }
            if (zusatz.schminke) {
                Object.assign(shader.uniforms, zusatz.schminke);
                shader.fragmentShader = shader.fragmentShader
                    .replace('#include <common>',
                             '#include <common>\nuniform float uSchminkeAn;\n'
                             + 'uniform sampler2D uSchminkeFarbe;\nuniform sampler2D uSchminkeGewicht;\n'
                             + 'uniform sampler2D uSchminkeRauheit;\nuniform sampler2D uSchminkeNormalen;\n'
                             + 'uniform float uSchminkeNormalenAn;\nuniform float uSchminkeNormalenModus;')
                    .replace('#include <map_fragment>',
                             'float g9Schminke = 0.0;\n#include <map_fragment>\n' + Genesis9hautGLSL.SCHMINKE)
                    .replace('#include <roughnessmap_fragment>',
                             '#include <roughnessmap_fragment>\n' + Genesis9hautGLSL.RAUHEIT);
            }
            if (zusatz.detail || zusatz.schminke) {
                shader.fragmentShader = shader.fragmentShader.replace(
                    '#include <normal_fragment_maps>',
                    Genesis9hautGLSL.normalen(Boolean(zusatz.schminke), Boolean(zusatz.detail)));
            }
            if (zusatz.klarlack) {
                Object.assign(shader.uniforms, zusatz.klarlack);
                shader.fragmentShader = shader.fragmentShader
                    .replace('#include <common>', '#include <common>\nuniform vec3 uKlarlackFarbe;')
                    .replace(Genesis9hautGLSL.KLARLACK_ALT, Genesis9hautGLSL.KLARLACK_NEU);
            }
        };
        // Ein anderer Schlüssel je Zusatz, sonst teilt Three das Programm.
        material.customProgramCacheKey = () => `g9haut-${
            zusatz.durchlicht ? zusatz.durchlicht.gewicht.toFixed(3) : 'x'}-${
            zusatz.schminke ? 's' : 'x'}-${zusatz.detail ? 'd' : 'x'}-${zusatz.klarlack ? 'k' : 'x'}`;
        material.needsUpdate = true;
    }
}
