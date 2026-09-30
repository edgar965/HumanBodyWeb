import * as THREE from 'three';
import { Shaderpatch } from './shaderpatch.js';
import { base64ToBytes } from './kodierung.js';

/**
 * Kleidfarbmischung — die Textur eines Gegenstücks in der Überlappung mischen, ohne den Server.
 *
 * Edgar, 30.09.2026: „die Textur am besten gesondert mit Regler anpassen, für das gesamte Bekleidung". „Kleidung –
 * Generisch" mischt Stücke über die Haut (`Genesis9/kleidmischung.py`): In der Überlappung steht EINE Fläche mit den
 * UV und dem Material des stärkeren Stücks. Damit die Textur des anderen dort mitmischen kann, trägt jedes Teil je
 * Gegenstück zwei Attribute (`teil.fremd`, vom Bau — `G9kleidfarbe`): die FARBE des Gegenstücks an der Stelle des
 * Punkts (3 Bytes) und wie stark die Zone dort gilt (1 Byte, außen mit weichem Auslauf). Der Shader mischt:
 *
 *     Anteil je Gegenstück  m = Regler · Deckung           (Regler `textur:<Platz>`, 0…1, Vorgabe 0)
 *     Farbe = eigene · (1 − Σ m) + Σ m · Gegenfarbe        (Σ m über 1: normiert — nie mehr als 100 %)
 *
 * Ohne Regler (Vorgabe 0) ändert sich nichts: jedes Stück trägt seine eigene Textur. Ein Reglerzug setzt nur eine
 * Uniform — kein neuer Bau, keine Anfrage. `Platz` ist der Rang des Gegenstücks in der Mischung nach Anteil
 * (`teil.fremd[i].rang`, 0 = stärkstes), also `textur:2` = das zweitstärkste Stück.
 *
 * Die Farbe steckt an den PUNKTEN des Netzes (bei Stufe 2 alle 3 mm): Die eigene Textur bleibt voll aufgelöst, die
 * des Gegenstücks nur so fein, wie das Netz auflöst — ein grobes Muster stimmt, ein feines Karo wird weicher.
 *
 * Über `Shaderpatch` (Schlüssel `kleidfremd`), wie jeder Eingriff in den Shader dieses Projekts: ein eigenes
 * `onBeforeCompile` löschte die anderen. Die Uniforms hängen am Eingriff (`Shaderpatch.eingriff`) und sind so auch
 * an Klonen dieselben.
 */
export class Kleidfarbmischung {

    static SCHLUESSEL = 'kleidfremd';
    /** So viele Gegenstücke trägt ein Teil (`HOECHSTENS` 4 Stücke, eines ist das Teil selbst). */
    static MAX = 3;
    /** Vorsatz des Reglers; danach der Platz (2 = zweitstärkstes Stück). */
    static REGLER = 'textur:';

    /**
     * Die Attribute an die Geometrie, den Eingriff an jedes Material.
     * @param {THREE.BufferGeometry} geo
     * @param {THREE.Material|THREE.Material[]} material
     * @param {Array<{rang:number, farbe:*, deckung:*}>} fremd  `teil.fremd` (base64 oder fertige Uint8Array-Sicht)
     * @returns {boolean} ob es etwas zu mischen gibt
     */
    static anlegen(geo, material, fremd) {
        const liste = (Array.isArray(fremd) ? fremd : []).slice(0, Kleidfarbmischung.MAX);
        if (!liste.length) return false;
        const uniforms = {};
        const raenge = [];
        liste.forEach((f, i) => {
            geo.setAttribute(`fremdFarbe${i}`, new THREE.BufferAttribute(base64ToBytes(f.farbe), 3, true));
            geo.setAttribute(`fremdDeckung${i}`, new THREE.BufferAttribute(base64ToBytes(f.deckung), 1, true));
            uniforms[`uFremd${i}`] = { value: 0 };
            raenge.push(Number(f.rang));
        });
        const anzahl = liste.length;
        const eingriff = (shader) => {
            Object.assign(shader.uniforms, uniforms);
            const K = Kleidfarbmischung;
            shader.vertexShader = shader.vertexShader
                .replace('#include <common>', `#include <common>\n${K._vertexDeklaration(anzahl)}`)
                .replace('#include <begin_vertex>', `#include <begin_vertex>\n${K._vertexZuweisung(anzahl)}`);
            shader.fragmentShader = shader.fragmentShader
                .replace('#include <common>', `#include <common>\n${K._fragmentDeklaration(anzahl)}`)
                .replace('#include <map_fragment>', `#include <map_fragment>\n${K._fragmentMischung(anzahl)}`);
        };
        eingriff.kennung = () => `n${anzahl}`;
        eingriff.uniforms = uniforms;
        eingriff.raenge = raenge;
        for (const m of Array.isArray(material) ? material : [material]) {
            Shaderpatch.anhaengen(m, Kleidfarbmischung.SCHLUESSEL, eingriff);
        }
        return true;
    }

    /**
     * Die Regler eines getragenen Stücks in die Uniforms aller seiner Netze — sofort, ohne Anfrage.
     * @param {object} inst  Figur (`clothMeshes`: Schlüssel `<kennung>/<nr>` oder `daz_<kennung>/<nr>`)
     * @param {string} kennung  Kennung des Sammeleintrags
     * @param {Object<string, number>} regler  `inst.kleidung[kennung].regler`
     * @returns {number} wie viele Netze etwas zu mischen hatten
     */
    static anwenden(inst, kennung, regler) {
        let zahl = 0;
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            if (!(schluessel.startsWith(`${kennung}/`) || schluessel.startsWith(`daz_${kennung}/`))) continue;
            for (const m of [].concat(netz?.material || [])) {
                const eingriff = Shaderpatch.eingriff(m, Kleidfarbmischung.SCHLUESSEL);
                if (!eingriff) continue;
                eingriff.raenge.forEach((rang, i) => {
                    eingriff.uniforms[`uFremd${i}`].value = Kleidfarbmischung.wert(regler, rang);
                });
                zahl++;
            }
        }
        return zahl;
    }

    /** Der Reglerwert für das Gegenstück auf `rang` (0 = stärkstes → `textur:1`, den es nicht gibt: 0). */
    static wert(regler, rang) {
        const w = Number(regler?.[`${Kleidfarbmischung.REGLER}${rang + 1}`]);
        return Number.isFinite(w) ? Math.min(1, Math.max(0, w)) : 0;
    }

    /** Ist das ein Textur-Regler? — er wirkt nur im Browser und löst keinen Neubau aus. */
    static ist(name) {
        return String(name || '').startsWith(Kleidfarbmischung.REGLER);
    }

    // ------------------------------------------------------------ GLSL

    static _je(anzahl, f) {
        return Array.from({ length: anzahl }, (_, i) => f(i)).join('\n');
    }

    static _vertexDeklaration(n) {
        return Kleidfarbmischung._je(n, i => `attribute vec3 fremdFarbe${i};\nattribute float fremdDeckung${i};\n`
            + `varying vec3 vFremdFarbe${i};\nvarying float vFremdDeckung${i};`);
    }

    static _vertexZuweisung(n) {
        return Kleidfarbmischung._je(n, i => `vFremdFarbe${i} = fremdFarbe${i};\n`
            + `vFremdDeckung${i} = fremdDeckung${i};`);
    }

    static _fragmentDeklaration(n) {
        return Kleidfarbmischung._je(n, i => `uniform float uFremd${i};\nvarying vec3 vFremdFarbe${i};\n`
            + `varying float vFremdDeckung${i};`)
            // sRGB -> linear, wie die Bilder: Three rechnet im Fragment linear.
            + '\nvec3 kfLinear(vec3 c) {'
            + ' return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c)); }';
    }

    static _fragmentMischung(n) {
        const summanden = Kleidfarbmischung._je(n, i => `  { float m = clamp(uFremd${i} * vFremdDeckung${i}, `
            + '0.0, 1.0);\n'
            + `    kfS += m; kfM += m * kfLinear(vFremdFarbe${i}); }`);
        return `{\n  float kfS = 0.0; vec3 kfM = vec3(0.0);\n${summanden}\n`
            + '  if (kfS > 1.0) { kfM /= kfS; kfS = 1.0; }\n'
            + '  diffuseColor.rgb = diffuseColor.rgb * (1.0 - kfS) + kfM;\n}';
    }
}
