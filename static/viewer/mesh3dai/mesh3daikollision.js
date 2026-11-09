/**
 * Mesh3daikollision — die Stücke der bewegten Ergebnisfigur aus fremden Gliedern schieben (31.10.2026 nachts, Edgar: „Haare durch Körper, Hände durch Kleider … Schreibe allgemeinen Code so dass
 * diese Tests grün sind“; venus „haare gehen durch die Beine“, ballerina_bunt „arm geht immer noch durch den Rock“).
 *
 * Ein Stück hängt an den Knochen seines Trägers (Haar am Kopf, Rock an Becken und Schenkeln); ein Glied, an dem es nicht hängt, fährt in der Bewegung durch es hindurch. Die Kapseln um die Glieder
 * rechnet die Kostüm-Kette aus der Figur (`KoerperKI_alle/koerperkollision.py`, `kleider_<g>/k/kapseln.json`, je Knochen Enden `a`, `b` in der Ruhe der Kinematik und Halbmesser `ra`, `rb`).
 * Je Bild bewegt sich jede Kapsel starr mit ihrem Knochen; im Vertex-Shader des Stücks wird ein Punkt senkrecht zur Achse nach außen geschoben, um so viel, wie er tiefer in der Kapsel liegt als
 * in der Ruhe (`position`), mal (1 − Gewicht am Knochen der Kapsel / `FREMD_MAX`), über alle Kapseln zusammen höchstens `DECKEL_M` — der Reihe nach, wie `Koerperkollision.schieben`
 * auf dem Server (alle Tanz-Prüfungen messen dasselbe,
 * `Kostuemtanzbilder.stueck`). Fassung 2 (01.11.2026 nachts, Zacken am Tutu): vorher ganzer Punkt auf die Hülle, harter Schnitt an `FREMD_MAX`, Achse aus der Hauptrichtung der Punkte.
 * Gilt für jede Bewegung, ohne Vorausrechnung je Animation. Das Standbild (Haltung der KI) bleibt unberührt: es wird nicht über diese Materialien gezeichnet.
 * Schubregel 3 (01.11.2026, Edgar zu ballerina_bunt: „Die rechte Hand geht durch das Tutu … dass es nach unten schwenkt“): senkrecht zur Achse schob der Rand einer Fläche zur Seite, und
 * um den Arm blieb ein Loch. Jetzt längs der Normale des Stücks (`objectNormal`, gehäutet) weg von der Seite, auf der die Kapsel in der Ruhe lag (`normal`, `position`; lag sie in der Ebene,
 * entscheidet ihre Bewegung längs der Normale), um die Tiefe ihrer Vorderseite über der Fläche, voll bis zum Halbmesser, glatt auslaufend bis Halbmesser + `WEICH_M` — eine Delle statt
 * eines Lochs; höchstens `DECKEL_NORMALE_M`. Dieselbe Regel wie `Koerperkollision._schub_normale` (die Tanz-Prüfungen geben die Normalen mit).
 * VERWORFEN (01.11.2026, gemessen auf dem Server): die Stücke reißen („Stück gedehnt“ ballerina Oberteil 0 → 87.237 Kanten, venus Haar 0 → 35.710) — `SCHUB_FASSUNG` bleibt 2 wie
 * `Koerperkollision.SCHUB_FASSUNG`; der Zweig `kollisionNormale` rechnet nur mit `kapseln.regel.schub_fassung` 3.
 * Fassung 3 (05.11.2026, Edgar: „fixe die offenen punkte im Tanz“): erlaubt ist die Tiefe, die ein Punkt in der Ruhe UND in der Haltung der KI hat, wenn die Kapseln sie tragen (`kapseln.haltung`, `dreh`,
 * `versch` je Knochen in der Reihenfolge der Kinematik): der Punkt in der Haltung steht im Attribut `kollisionStand`, die Enden der Kapsel in `kollisionAH`/`kollisionBH`. Ohne `haltung` (Fassung 2) nur die Ruhe.
 */
import * as THREE from 'three';

export class Mesh3daikollision {
    static MAX = 96;
    static FREMD_MAX = 0.2;
    /** höchster Schub eines Punkts über alle Kapseln (m), wie `Koerperkollision.DECKEL_M` — gilt, wenn `kapseln.regel.deckel_m` fehlt */
    static DECKEL_M = 0.04;
    /** Schubregel wie `Koerperkollision.SCHUB_FASSUNG` (3 verworfen, Docstring), `WEICH_M`, `DECKEL_NORMALE_M` */
    static SCHUB_FASSUNG = 2;
    static WEICH_M = 0.12;
    static DECKEL_NORMALE_M = 0.30;

    static KOPF = `
uniform vec3 kollisionA[KOLLISION_ZAHL];
uniform vec3 kollisionB[KOLLISION_ZAHL];
uniform vec3 kollisionA0[KOLLISION_ZAHL];
uniform vec3 kollisionB0[KOLLISION_ZAHL];
uniform vec2 kollisionR[KOLLISION_ZAHL];
uniform float kollisionKnochen[KOLLISION_ZAHL];
#ifdef KOLLISION_HALTUNG
attribute vec3 kollisionStand;
uniform vec3 kollisionAH[KOLLISION_ZAHL];
uniform vec3 kollisionBH[KOLLISION_ZAHL];
#endif
`;

    static RUMPF = `
#ifdef USE_SKINNING
vec3 kollisionStart = transformed;
bool kollisionNormale = KOLLISION_REGEL == 3 && length(normal) > 1e-6 && length(objectNormal) > 1e-6;
vec3 kollisionN0 = kollisionNormale ? normalize(normal) : vec3(0.0);
vec3 kollisionN = kollisionNormale ? normalize(objectNormal) : vec3(0.0);
for (int i = 0; i < KOLLISION_ZAHL; i++) {
    float eigen = dot(skinWeight, vec4(equal(skinIndex, vec4(kollisionKnochen[i]))));
    float fremd = clamp(1.0 - eigen / KOLLISION_FREMD, 0.0, 1.0);
    if (fremd <= 0.0) continue;
    vec3 ab0 = kollisionB0[i] - kollisionA0[i];
    float t0 = clamp(dot(position - kollisionA0[i], ab0) / max(dot(ab0, ab0), 1e-12), 0.0, 1.0);
    vec3 c0 = kollisionA0[i] + t0 * ab0;
    float rad0 = mix(kollisionR[i].x, kollisionR[i].y, t0);
    vec3 ab = kollisionB[i] - kollisionA[i];
    float t = clamp(dot(transformed - kollisionA[i], ab) / max(dot(ab, ab), 1e-12), 0.0, 1.0);
    vec3 c = kollisionA[i] + t * ab;
    float rad = mix(kollisionR[i].x, kollisionR[i].y, t);
    if (kollisionNormale) {
        float ent0 = dot(c0 - position, kollisionN0);
        float ent = dot(c - transformed, kollisionN);
        float quer = length((c - transformed) - ent * kollisionN);
        float seite = abs(ent0) >= rad0 ? sign(ent0) : sign(ent0 - ent);
        if (seite == 0.0) seite = 1.0;
        float tief0 = max(rad0 - seite * ent0, 0.0);
        float p = clamp((rad + KOLLISION_WEICH - quer) / KOLLISION_WEICH, 0.0, 1.0);
        float schub = max(rad - seite * ent - tief0, 0.0) * fremd * p * p * (3.0 - 2.0 * p);
        transformed -= seite * kollisionN * schub;
        continue;
    }
    float tief0 = max(rad0 - length(position - c0), 0.0);
#ifdef KOLLISION_HALTUNG
    vec3 abH = kollisionBH[i] - kollisionAH[i];
    float tH = clamp(dot(kollisionStand - kollisionAH[i], abH) / max(dot(abH, abH), 1e-12), 0.0, 1.0);
    tief0 = min(tief0, max(mix(kollisionR[i].x, kollisionR[i].y, tH) - length(kollisionStand - (kollisionAH[i] + tH * abH)), 0.0));
#endif
    vec3 v = transformed - c;
    float d = length(v);
    float schub = (rad - d - tief0) * fremd;
    if (schub > 0.0 && d > 1e-9) transformed += v / d * schub;
}
float kollisionDeckel = kollisionNormale ? KOLLISION_DECKEL_NORMALE : KOLLISION_DECKEL;
vec3 kollisionSchub = transformed - kollisionStart;
transformed = kollisionStart + kollisionSchub * (kollisionDeckel / max(length(kollisionSchub), kollisionDeckel));
#endif
`;

    /** Haltung der KI je Knochen im Rahmen der Figur: Map Nummer im Skelett → M = A · H · A⁻¹ (H aus `kapseln.haltung`, A = `abbildung`), oder null ohne `haltung`. @param namen Knochen wie die Kinematik */
    static haltung(kapseln, namen, nummer, abbildung) {
        const h = kapseln?.haltung;
        if (!h?.dreh || !h?.versch || !namen) return null;
        const a = abbildung ? new THREE.Matrix4().compose(abbildung.verschiebung, abbildung.quaternion, new THREE.Vector3(1, 1, 1)) : new THREE.Matrix4();
        const ai = a.clone().invert();
        const aus = new Map();
        namen.forEach((name, j) => {
            const i = nummer.get(name), d = h.dreh[j], v = h.versch[j];
            if (i === undefined || !d || !v) return;
            const m = new THREE.Matrix4().set(d[0][0], d[0][1], d[0][2], v[0], d[1][0], d[1][1], d[1][2], v[1], d[2][0], d[2][1], d[2][2], v[2], 0, 0, 0, 1);
            aus.set(i, a.clone().multiply(m).multiply(ai));
        });
        return aus;
    }

    /** Die Punkte des Stücks in der Haltung der KI (Float32Array 3 × N): dieselbe Häutung wie der Shader, mit den Matrizen aus `haltung`. */
    static stand(geo, matrizen) {
        const p = geo.getAttribute('position').array, si = geo.getAttribute('skinIndex').array, sw = geo.getAttribute('skinWeight').array;
        const aus = new Float32Array(p.length);
        for (let n = 0, n3 = 0, n4 = 0; n3 < p.length; n++, n3 += 3, n4 += 4) {
            const x = p[n3], y = p[n3 + 1], z = p[n3 + 2];
            let ax = 0, ay = 0, az = 0;
            for (let k = 0; k < 4; k++) {
                const w = sw[n4 + k];
                if (w <= 0) continue;
                const m = matrizen.get(si[n4 + k]);
                if (!m) {
                    ax += w * x; ay += w * y; az += w * z;
                    continue;
                }
                const e = m.elements;
                ax += w * (e[0] * x + e[4] * y + e[8] * z + e[12]);
                ay += w * (e[1] * x + e[5] * y + e[9] * z + e[13]);
                az += w * (e[2] * x + e[6] * y + e[10] * z + e[14]);
            }
            aus[n3] = ax; aus[n3 + 1] = ay; aus[n3 + 2] = az;
        }
        return aus;
    }

    /** Kapseln an ein gebundenes Stück hängen (Materialien geklont — die des Standbilds bleiben, wie sie sind). @param abbildung Rahmen der Kinematik → Rahmen der Figur oder null @param namen Knochen in der Reihenfolge der Kinematik (für `kapseln.haltung`) */
    static anbringen(mesh, kapseln, skelett, abbildung, namen = null) {
        const liste = (kapseln?.kapseln || []).slice(0, Mesh3daikollision.MAX);
        if (!liste.length || !mesh?.isSkinnedMesh || !skelett?.bones) return 0;
        const nummer = new Map(skelett.bones.map((k, i) => [k.name, i]));
        const haltung = Mesh3daikollision.haltung(kapseln, namen, nummer, abbildung);
        const ruhe = [];
        for (const k of liste) {
            const i = nummer.get(k.knochen);
            if (i === undefined) continue;
            const a = new THREE.Vector3().fromArray(k.a), b = new THREE.Vector3().fromArray(k.b);
            if (abbildung) for (const v of [a, b]) v.applyQuaternion(abbildung.quaternion).add(abbildung.verschiebung);
            const m = haltung?.get(i);
            ruhe.push({ knochen: i, a, b, ah: m ? a.clone().applyMatrix4(m) : a, bh: m ? b.clone().applyMatrix4(m) : b, r: new THREE.Vector2(k.ra, k.rb) });
        }
        if (!ruhe.length) return 0;
        if (haltung) mesh.geometry.setAttribute('kollisionStand', new THREE.BufferAttribute(Mesh3daikollision.stand(mesh.geometry, haltung), 3));
        const u = {
            kollisionA: { value: ruhe.map(k => k.a.clone()) }, kollisionB: { value: ruhe.map(k => k.b.clone()) },
            kollisionA0: { value: ruhe.map(k => k.a) }, kollisionB0: { value: ruhe.map(k => k.b) },
            kollisionR: { value: ruhe.map(k => k.r) }, kollisionKnochen: { value: ruhe.map(k => k.knochen) },
        };
        if (haltung) Object.assign(u, { kollisionAH: { value: ruhe.map(k => k.ah) }, kollisionBH: { value: ruhe.map(k => k.bh) } });
        mesh.userData.kollision = { ruhe, u };
        const zahl = ruhe.length;
        const fremd = (kapseln.regel?.fremd_max ?? Mesh3daikollision.FREMD_MAX).toFixed(4);
        const deckel = (kapseln.regel?.deckel_m ?? Mesh3daikollision.DECKEL_M).toFixed(4);
        const regel = kapseln.regel?.schub_fassung ?? Mesh3daikollision.SCHUB_FASSUNG;
        const weich = (kapseln.regel?.weich_m ?? Mesh3daikollision.WEICH_M).toFixed(4);
        const deckelNormale = (kapseln.regel?.deckel_normale_m ?? Mesh3daikollision.DECKEL_NORMALE_M).toFixed(4);
        const klonen = m => {
            const neu = m.clone();
            neu.onBeforeCompile = shader => {
                Object.assign(shader.uniforms, u);
                shader.vertexShader = shader.vertexShader
                    .replace('#include <common>', `#include <common>\n#define KOLLISION_ZAHL ${zahl}\n#define KOLLISION_FREMD ${fremd}\n#define KOLLISION_DECKEL ${deckel}\n`
                        + `#define KOLLISION_REGEL ${regel}\n#define KOLLISION_WEICH ${weich}\n#define KOLLISION_DECKEL_NORMALE ${deckelNormale}\n${haltung ? '#define KOLLISION_HALTUNG\n' : ''}${Mesh3daikollision.KOPF}`)
                    .replace('#include <skinning_vertex>', `#include <skinning_vertex>\n${Mesh3daikollision.RUMPF}`);
            };
            neu.customProgramCacheKey = () => `mesh3daikollision4_${zahl}_${fremd}_${deckel}_${regel}_${weich}_${deckelNormale}_${haltung ? 1 : 0}`;
            return neu;
        };
        mesh.material = Array.isArray(mesh.material) ? mesh.material.map(klonen) : klonen(mesh.material);
        return zahl;
    }

    /** Je Bild nach dem Mischer: jede Kapsel mit der Matrix ihres Knochens in den Raum des Stücks (wie der Shader die Punkte häutet). */
    static stellen(kleider, gruppe) {
        gruppe?.updateMatrixWorld(true);
        const m = new THREE.Matrix4();
        for (const { mesh } of kleider || []) {
            const k = mesh.userData.kollision;
            const sk = mesh.skeleton;
            if (!k || !sk) continue;
            for (let i = 0; i < k.ruhe.length; i++) {
                const r = k.ruhe[i];
                m.multiplyMatrices(sk.bones[r.knochen].matrixWorld, sk.boneInverses[r.knochen]).premultiply(mesh.bindMatrixInverse).multiply(mesh.bindMatrix);
                k.u.kollisionA.value[i].copy(r.a).applyMatrix4(m);
                k.u.kollisionB.value[i].copy(r.b).applyMatrix4(m);
            }
        }
    }
}
