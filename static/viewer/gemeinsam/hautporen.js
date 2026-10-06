import { Shaderpatch } from './shaderpatch.js';

/**
 * Hautporen — feine Hautzeichnung (Normal + AO) im Shader der Haut, einstellbar im Bereich „Haut" des Reiters „Modell".
 *
 * WARUM (Edgar, 06.10.2026: „übernimm die Poren und die Augen, wie kann man die im UI einstellen"): Das Projekt matmadness/HumanShaders (MIT/CC BY 4.0) bringt
 * drei kachelbare Karten mit Porenzeichnung (Normalkarte, im blauen Kanal die AO). Die Haut der Figur hat nur die MB-Lab-Albedo und eine gröbere Bump-Karte
 * (`Hauttextur`) — die erfundene Fleckung der Standhaut (`Standhautdetail`) ist keine Zeichnung, die man im Nahbild als Poren liest.
 *
 * Die Karte läuft DREIFACH-PLANAR über die Haut (Lage und Normale der Ruhepose, Kachelgröße in Metern): Die UV-Inseln des Körpers sind verschieden dicht
 * belegt, mit ihnen gäbe es Poren, die am Kopf drei Millimeter und am Bein zwei Zentimeter groß sind. Die Störung der Normale rechnet im Raum der Ruhepose und
 * wird mit den Achsen des Skinnings (`skinMatrix`) in den Sichtraum gedreht — sie bleibt an der Haut, wenn sich ein Glied beugt. Normal- UND Bump-Karte
 * zugleich geht in Three.js nicht (die Normalkarte verdrängt den Bump), deshalb ein eigener Eingriff in den Shader (`Shaderpatch`, verträgt sich mit Lippen,
 * Brauen und Weichgewebe). Ohne Auswahl trägt die Haut den Eingriff nicht.
 *
 * Felder (`Koerperdetails.VORGABE`): `haut_poren` (Kennung der Karte, leer = aus), `haut_poren_deckkraft` (Stärke 0..1), `haut_poren_dichte` (Faktor 0,25..3 —
 * mehr = feinere Poren). Ohne `import * as THREE` außer beim Laden einer Karte: so läuft das Modul in Node mit Attrappen (`test_js_hautporen.py`).
 */
export class Hautporen {

    static FELD = 'haut_poren';
    static STAERKE = 'haut_poren_deckkraft';
    static DICHTE = 'haut_poren_dichte';
    static SCHLUESSEL = 'hautporen';
    /** Materialgruppen der Haut (mit Censor) — wie `Hauttextur.HAUT`. */
    static HAUT = [0, 1];
    static ADRESSE = '/static/img/humanshaders/';
    /** Kantenlänge einer Kachel bei Dichte 1, Meter. */
    static KACHEL_M = 0.008;
    /** Wie stark die Stärke 1 wirkt: Ablenkung der Normale und Abdunklung durch die AO (HumanShaders: 0,3 und 0,4 als Vorgabe). */
    static RELIEF = 0.6;
    static ABDUNKLUNG = 0.8;
    /** Wert → [Anzeige, Mittel des blauen Kanals (AO) der Karte — damit der Hautton im Mittel gleich bleibt]. */
    static WAHL = [
        ['', 'Keine', 1],
        ['poren_1', 'Poren – Standard', 0.546],
        ['poren_2', 'Poren – fein', 0.515],
        ['poren_3', 'Poren – grob (Zellen)', 0.478],
    ];

    static _geladen = new Map();
    /** Netz → Nummer des jüngsten `anwenden` (überholte Läufe setzen nichts mehr). */
    static _lauf = new WeakMap();

    static eintrag(wert) {
        return Hautporen.WAHL.find(([w]) => w && w === wert) || null;
    }

    /**
     * Die Poren nach `details` auf die Haut setzen oder abnehmen.
     * @returns Promise<boolean> — true, wenn die Haut sie trägt
     */
    static async anwenden(netz, details) {
        const materialien = Array.isArray(netz?.material) ? netz.material : null;
        if (!materialien) return false;
        const lauf = (Hautporen._lauf.get(netz) || 0) + 1;
        Hautporen._lauf.set(netz, lauf);
        const eintrag = Hautporen.eintrag(details?.[Hautporen.FELD]);
        if (!eintrag) { Hautporen.entfernen(materialien); return false; }
        const karte = await Hautporen.laden(eintrag[0]);
        // Ein neuerer Aufruf (Regler gezogen, Auswahl gewechselt, während die Karte noch lud) gilt; dieser hier ist überholt.
        if (Hautporen._lauf.get(netz) !== lauf) return false;
        let eingriff = null;
        for (const g of Hautporen.HAUT) eingriff ??= materialien[g] ? Shaderpatch.eingriff(materialien[g], Hautporen.SCHLUESSEL) : null;
        if (!eingriff) {
            const uniforms = { porenKarte: { value: null }, porenStaerke: { value: 0 }, porenFliesen: { value: 1 }, porenAoMittel: { value: 1 } };
            eingriff = shader => Hautporen.patchen(shader, uniforms);
            eingriff.uniforms = uniforms;
        }
        const u = eingriff.uniforms;
        const staerke = Number(details[Hautporen.STAERKE]);
        const dichte = Number(details[Hautporen.DICHTE]);
        u.porenKarte.value = karte;
        u.porenStaerke.value = Number.isFinite(staerke) ? staerke : 0.5;
        u.porenFliesen.value = (Number.isFinite(dichte) && dichte > 0 ? dichte : 1) / Hautporen.KACHEL_M;
        u.porenAoMittel.value = eintrag[2];
        for (const g of Hautporen.HAUT) {
            if (materialien[g] && !Shaderpatch.hat(materialien[g], Hautporen.SCHLUESSEL)) Shaderpatch.anhaengen(materialien[g], Hautporen.SCHLUESSEL, eingriff);
        }
        return true;
    }

    /** Den Eingriff von der Haut nehmen. @returns Zahl der Materialien, die ihn trugen */
    static entfernen(materialien) {
        let weg = 0;
        for (const g of Hautporen.HAUT) {
            if (materialien[g] && Shaderpatch.entfernen(materialien[g], Hautporen.SCHLUESSEL)) weg += 1;
        }
        return weg;
    }

    /** Eine Karte laden — einmal je Kennung; linear, kachelnd, mit Mip-Stufen. */
    static async laden(name) {
        if (Hautporen._geladen.has(name)) return Hautporen._geladen.get(name);
        const THREE = await import('three');
        const textur = await new THREE.TextureLoader().loadAsync(`${Hautporen.ADRESSE}${name}.png`);
        textur.colorSpace = THREE.NoColorSpace;
        textur.wrapS = textur.wrapT = THREE.RepeatWrapping;
        textur.anisotropy = 8;
        Hautporen._geladen.set(name, textur);
        return textur;
    }

    /** Der Eingriff in den Shader: Lage und Normale der Ruhepose sowie die Achsen des Skinnings durchreichen, im Fragment Normale und AO stören. */
    static patchen(shader, uniforms) {
        for (const name of Object.keys(uniforms)) shader.uniforms[name] = uniforms[name];
        const achsen = '\n#ifdef USE_SKINNING\n\tmat3 porenM = mat3( normalMatrix ) * mat3( skinMatrix );\n#else\n\tmat3 porenM = mat3( normalMatrix );\n#endif\n'
            + '\tvPorenX = porenM[0]; vPorenY = porenM[1]; vPorenZ = porenM[2];';
        shader.vertexShader = 'varying vec3 vPorenP; varying vec3 vPorenN; varying vec3 vPorenX; varying vec3 vPorenY; varying vec3 vPorenZ;\n'
            + shader.vertexShader
                .replace('#include <beginnormal_vertex>', '#include <beginnormal_vertex>\n\tvPorenN = objectNormal;')
                .replace('#include <begin_vertex>', '#include <begin_vertex>\n\tvPorenP = transformed;')
                .replace('#include <skinnormal_vertex>', '#include <skinnormal_vertex>' + achsen);
        const stoerung = '#include <color_fragment>\n'
            + '\tvec3 porenW = pow( abs( normalize( vPorenN ) ), vec3( 4.0 ) ); porenW /= ( porenW.x + porenW.y + porenW.z );\n'
            + '\tvec3 porenQ = vPorenP * porenFliesen;\n'
            + '\tvec4 porenTx = texture2D( porenKarte, porenQ.zy ); vec4 porenTy = texture2D( porenKarte, porenQ.xz ); vec4 porenTz = texture2D( porenKarte, porenQ.xy );\n'
            + '\tvec2 porenNx = porenTx.xy * 2.0 - 1.0; vec2 porenNy = porenTy.xy * 2.0 - 1.0; vec2 porenNz = porenTz.xy * 2.0 - 1.0;\n'
            + '\tvec3 porenD = vec3( 0.0, porenNx.y, porenNx.x ) * porenW.x + vec3( porenNy.x, 0.0, porenNy.y ) * porenW.y + vec3( porenNz.x, porenNz.y, 0.0 ) * porenW.z;\n'
            + '\tfloat porenAO = dot( vec3( porenTx.b, porenTy.b, porenTz.b ), porenW ) / porenAoMittel;\n'
            + `\tdiffuseColor.rgb *= mix( 1.0, clamp( porenAO, 0.0, 2.0 ), porenStaerke * ${Hautporen.ABDUNKLUNG.toFixed(2)} );`;
        const drehung = '#include <normal_fragment_maps>\n'
            + '\tvec3 porenV = vPorenX * porenD.x + vPorenY * porenD.y + vPorenZ * porenD.z;\n'
            + '\tporenV -= normal * dot( porenV, normal );\n'
            + `\tnormal = normalize( normal + porenV * porenStaerke * ${Hautporen.RELIEF.toFixed(2)} );`;
        shader.fragmentShader = 'uniform sampler2D porenKarte; uniform float porenStaerke; uniform float porenFliesen; uniform float porenAoMittel;\n'
            + 'varying vec3 vPorenP; varying vec3 vPorenN; varying vec3 vPorenX; varying vec3 vPorenY; varying vec3 vPorenZ;\n'
            + shader.fragmentShader
                .replace('#include <color_fragment>', stoerung)
                .replace('#include <normal_fragment_maps>', drehung);
        return shader;
    }
}
