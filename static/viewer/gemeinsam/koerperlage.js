import * as THREE from 'three';
import { Stoffkapseln } from './stoffkapseln.js';
import { Protokoll } from './protokoll.js';

/**
 * Koerperlage — der gehäutete Körper je Bild als Textur, für die
 * Oberflächenbindung der Kleidung (Konzept Fitting, Schicht 2, 21.09.2026).
 *
 * WARUM AUF DER GPU: Der Körper hat 104.480 Browserpunkte (Stufe 1, mit
 * Strg+Alt+H 410.202); ihn je Bild auf der CPU zu häuten kostete 15–26 ms
 * (`Genesis9strangtreffer`, Viola) — das ganze Bildbudget. Hier häutet ihn
 * die GPU ein zweites Mal, als PUNKTE: jeder Punkt landet im Texel seiner
 * Nummer (`punktnummer`), Lage und Normale in zwei Gleitkomma-Zielen
 * (`RGBA32F`, `NearestFilter`), ein Zeichenaufruf je Ziel. Der Stoff-Shader
 * liest daraus mit `texelFetch` (`oberflaecheglsl.js`).
 *
 * DERSELBE LOKALE RAUM: Threes Skinning liefert `transformed` in dem Raum,
 * in dem das Netz an sein Skelett gebunden ist (`bindMatrixInverse`);
 * Körper und Stoff hängen in derselben Gruppe an demselben Skelett, also
 * ist die Lage des Körpers unmittelbar die Zielgröße im Stoff-Shader.
 * Der Punkt-Zeichner ist ein `THREE.Points`, das sich als `SkinnedMesh`
 * ausgibt (`isSkinnedMesh`, `skeleton`, `bindMatrix`) — der Renderer setzt
 * dann `USE_SKINNING` und die Knochentextur, mehr braucht es nicht.
 *
 * EINMAL JE BILD: `sichern` läuft aus `onBeforeRender` des ersten Stücks,
 * das gezeichnet wird, und merkt sich `renderer.info.render.frame`; weitere
 * Stücke derselben Figur finden die Texturen fertig. Ein Render innerhalb
 * von `onBeforeRender` ist erlaubt (Threes `Reflector` tut dasselbe); das
 * Ziel wird danach zurückgesetzt.
 *
 * KAPSELN (Schicht 3) laufen im selben Takt mit: die Gliedmaßenkapseln des
 * Stoffschwungs (`Stoffkapseln`), aus dem Weltraum in den lokalen Raum der
 * Figur gebracht, als Uniform-Feld für die Kollision im Stoff-Shader.
 */
export class Koerperlage {

    /** inst -> Stand ({ziele, punkte, kapseln, bild}) */
    static _staende = new WeakMap();
    static _kamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    static _szene = new THREE.Scene();

    static stand(inst) {
        let s = Koerperlage._staende.get(inst);
        if (!s) { s = { ziele: null, punkte: null, breite: 0, bild: -1, kapseln: null, kapselwerte: null, anzahl: 0 }; Koerperlage._staende.set(inst, s); }
        return s;
    }

    /**
     * Die Texturen dieses Bildes sicherstellen — einmal je Bild und Figur.
     * @returns {{lage: THREE.Texture, normale: THREE.Texture, breite: number}|null}
     */
    static sichern(renderer, inst) {
        const koerper = inst?.bodyMesh;
        if (!koerper?.isSkinnedMesh || !koerper.skeleton) return null;
        const s = Koerperlage.stand(inst);
        const bild = renderer.info.render.frame;
        if (s.bild === bild && s.ziele && s.quelle === koerper.geometry) return Koerperlage._ergebnis(s);
        Koerperlage._vorbereiten(s, koerper);
        Koerperlage._attributeNachziehen(s, koerper.geometry);
        const zielAlt = renderer.getRenderTarget();
        const autoClearAlt = renderer.autoClear;
        renderer.autoClear = true;
        for (const modus of [0, 1]) {
            s.punkte.material.uniforms.uModus.value = modus;
            renderer.setRenderTarget(s.ziele[modus]);
            renderer.render(Koerperlage._szene, Koerperlage._kamera);
        }
        renderer.setRenderTarget(zielAlt);
        renderer.autoClear = autoClearAlt;
        Koerperlage._kapseln(s, inst, koerper);
        // NACH den eigenen Renderlaeufen lesen: jeder zaehlt den Bildzaehler hoch;
        // das naechste Stueck desselben Bildes findet dann denselben Stand vor.
        s.bild = renderer.info.render.frame;
        return Koerperlage._ergebnis(s);
    }

    static _ergebnis(s) {
        return { lage: s.ziele[0].texture, normale: s.ziele[1].texture, breite: s.breite,
                 kapseln: s.kapselwerte, anzahl: s.anzahl };
    }

    /** Punkt-Zeichner und Ziele anlegen (oder erneuern, wenn der Körper neu ist). */
    static _vorbereiten(s, koerper) {
        const geo = koerper.geometry;
        if (s.quelle === geo && s.ziele) return;
        Koerperlage._freigeben(s);
        s.quelle = geo;
        const n = geo.attributes.position.count;
        const breite = Math.min(4096, Math.ceil(Math.sqrt(n)));
        const hoehe = Math.ceil(n / breite);
        if (!geo.attributes.punktnummer || geo.attributes.punktnummer.count !== n) {
            const nummern = new Float32Array(n);
            for (let i = 0; i < n; i++) nummern[i] = i;
            geo.setAttribute('punktnummer', new THREE.BufferAttribute(nummern, 1));
        }
        s.ziele = [0, 1].map(() => new THREE.WebGLRenderTarget(breite, hoehe, {
            type: THREE.FloatType, format: THREE.RGBAFormat, minFilter: THREE.NearestFilter,
            magFilter: THREE.NearestFilter, depthBuffer: false, stencilBuffer: false, generateMipmaps: false,
        }));
        const material = new THREE.ShaderMaterial({
            uniforms: { uModus: { value: 0 }, uBreite: { value: breite }, uHoehe: { value: hoehe } },
            vertexShader: Koerperlage.VERTEX, fragmentShader: Koerperlage.FRAGMENT,
            depthTest: false, depthWrite: false,
        });
        // OHNE INDEX: ein indiziertes `Points` zeichnet nur die Punkte im Index —
        // und die Hautmaske nimmt verdeckte Dreiecke heraus. Deren Texel blieben
        // leer (0, 0, 0), der gebundene Stoff schoss zum Ursprung (Sichtprobe
        // 21.09.2026: Spitzen zu einer senkrechten Linie). Eigene Geometrie, die
        // die ATTRIBUTE des Koerpers teilt, kein Index, alle Punkte.
        const lage = new THREE.BufferGeometry();
        lage.setDrawRange(0, n);
        const punkte = new THREE.Points(lage, material);
        // Als gehäutetes Netz ausgeben: Skelett und Bindung des Körpers (dieselben
        // Objekte — `bindMatrixInverse` zieht der Körper je Bild nach).
        punkte.isSkinnedMesh = true;
        punkte.skeleton = koerper.skeleton;
        punkte.bindMatrix = koerper.bindMatrix;
        punkte.bindMatrixInverse = koerper.bindMatrixInverse;
        punkte.frustumCulled = false;
        punkte.matrixAutoUpdate = false;
        s.punkte = punkte; s.breite = breite;
        Koerperlage._attributeNachziehen(s, geo);
        Koerperlage._szene.clear();
        Koerperlage._szene.add(punkte);
        Protokoll.debug('Koerperlage', `${n} Punkte in ${breite}×${hoehe} Texeln`);
    }

    static _freigeben(s) {
        for (const z of s.ziele || []) z.dispose();
        s.punkte?.material?.dispose();
        s.ziele = null; s.punkte = null; s.quelle = null;
    }

    /** Die Attribute des Koerpers teilen — je Bild, denn die Gelenkfelder
     *  (`Genesis9felder`) ersetzen die Positionsattribute. */
    static ATTRIBUTE = ['position', 'normal', 'skinIndex', 'skinWeight', 'punktnummer'];

    static _attributeNachziehen(s, geo) {
        const lage = s.punkte.geometry;
        for (const name of Koerperlage.ATTRIBUTE) {
            const a = geo.attributes[name];
            if (a && lage.attributes[name] !== a) lage.setAttribute(name, a);
        }
    }

    /**
     * Die Kapseln der Gliedmaßen im lokalen Raum der Figur, als flaches
     * vec4-Feld. Die Gruppen-ID der Kapsel (`Koerperzuordnung.GRUPPEN`)
     * reitet im sonst ungenutzten `.w` des ersten Vector4 mit — der
     * Stoff-Shader überspringt damit die eigene Gliedmaße (22.09.2026,
     * `oberflaecheglsl.js`).
     */
    static _kapseln(s, inst, koerper) {
        if (!s.kapseln) s.kapseln = Stoffkapseln.anlegen(inst);
        const kapseln = s.kapseln;
        const max = Koerperlage.KAPSELN;
        if (!s.kapselwerte) s.kapselwerte = Array.from({ length: 4 * max }, () => new THREE.Vector4());
        const welt = Stoffkapseln.bild(kapseln);
        const gruppen = Stoffkapseln.gruppen(kapseln);
        const lokal = Koerperlage._m.copy(koerper.matrixWorld).invert();
        const dreh = Koerperlage._q.setFromRotationMatrix(lokal);
        const v = Koerperlage._v;
        const je = 13;
        s.anzahl = Math.min(max, kapseln.length);
        for (let i = 0; i < s.anzahl; i++) {
            const o = je * i, w = s.kapselwerte;
            v.set(welt[o], welt[o + 1], welt[o + 2]).applyMatrix4(lokal); w[4 * i].set(v.x, v.y, v.z, gruppen[i]);
            v.set(welt[o + 3], welt[o + 4], welt[o + 5]).applyMatrix4(lokal); w[4 * i + 1].set(v.x, v.y, v.z, 0);
            v.set(welt[o + 6], welt[o + 7], welt[o + 8]).applyQuaternion(dreh); w[4 * i + 2].set(v.x, v.y, v.z, 0);
            w[4 * i + 3].set(welt[o + 9], welt[o + 10], welt[o + 11], welt[o + 12]);
        }
    }

    static KAPSELN = 32;
    static _m = new THREE.Matrix4();
    static _q = new THREE.Quaternion();
    static _v = new THREE.Vector3();

    static VERTEX = `
#include <common>
#include <skinning_pars_vertex>
attribute float punktnummer;
uniform float uModus;
uniform float uBreite;
uniform float uHoehe;
varying vec3 vWert;
void main() {
    #include <skinbase_vertex>
    #include <beginnormal_vertex>
    #include <skinnormal_vertex>
    #include <begin_vertex>
    #include <skinning_vertex>
    vWert = uModus < 0.5 ? transformed : normalize(objectNormal);
    float x = mod(punktnummer, uBreite);
    float y = floor(punktnummer / uBreite);
    gl_Position = vec4((x + 0.5) / uBreite * 2.0 - 1.0, (y + 0.5) / uHoehe * 2.0 - 1.0, 0.0, 1.0);
    gl_PointSize = 1.0;
}`;

    static FRAGMENT = `
varying vec3 vWert;
void main() { gl_FragColor = vec4(vWert, 1.0); }`;
}
