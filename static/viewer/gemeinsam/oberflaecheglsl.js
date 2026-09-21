/**
 * OberflaecheGLSL — die Shader-Stücke der Oberflächenbindung und der
 * Kapselkollision (Konzept Fitting, Schichten 2 und 3, 21.09.2026).
 *
 * KÖRPERLAGE: `koerperlage.js` zeichnet den gehäuteten Körper je Bild als
 * Punkte in zwei Gleitkomma-Texturen (Lage, Normale; Texel = Punktnummer).
 * Der Stoff-Vertex-Shader liest je Punkt seine drei Körperecken daraus:
 *
 *     q = u·A + v·B + w·C + d · normalize(u·nA + v·nB + w·nC)
 *     transformed = mix(transformed, q, mischung)
 *
 * — NACH `skinning_vertex`, im selben lokalen Raum (Körper und Stoff hängen
 * in derselben Gruppe an demselben Skelett; `transformed` ist bei beiden die
 * gehäutete Lage vor `modelMatrix`).
 *
 * KAPSELN (Schicht 3): was nicht voll gebunden ist, wird aus den Kapseln der
 * Gliedmaßen gedrückt — elliptischer Kegel wie `Stoffkoerper.hinaus`, aber
 * ohne Iteration: liegt der Punkt in der Ellipse (im Maß der Halbachsen plus
 * Abstand), wird sein Querversatz radial auf den Rand skaliert.
 */
export class OberflaecheGLSL {

    /** Höchstzahl Kapseln im Shader (`Stoffkapseln.HOECHSTENS`). */
    static KAPSELN = 32;

    static UNIFORMS = `
uniform float uOberflaecheAn;
uniform sampler2D uKoerperLage;
uniform sampler2D uKoerperNormale;
uniform float uLageBreite;
uniform float uKapselAn;
uniform float uKapselAbstand;
uniform int uKapselAnzahl;
uniform vec4 uKapseln[${4 * OberflaecheGLSL.KAPSELN}];
attribute vec3 bindung;
attribute vec3 bary;
attribute float bindabstand;
attribute float mischung;

vec3 g9Lage(float nummer) {
    int i = int(nummer + 0.5);
    int w = int(uLageBreite);
    return texelFetch(uKoerperLage, ivec2(i - (i / w) * w, i / w), 0).xyz;
}
vec3 g9Normale(float nummer) {
    int i = int(nummer + 0.5);
    int w = int(uLageBreite);
    return texelFetch(uKoerperNormale, ivec2(i - (i / w) * w, i / w), 0).xyz;
}
`;

    /** Nach `skinning_vertex`: Oberfläche mischen, dann Kapseln. */
    static VERTEX = `
#include <skinning_vertex>
if (uOberflaecheAn > 0.5 && mischung > 0.0 && bindung.x >= 0.0) {
    vec3 q = bary.x * g9Lage(bindung.x) + bary.y * g9Lage(bindung.y) + bary.z * g9Lage(bindung.z);
    vec3 n = normalize(bary.x * g9Normale(bindung.x) + bary.y * g9Normale(bindung.y) + bary.z * g9Normale(bindung.z));
    transformed = mix(transformed, q + bindabstand * n, mischung);
}
// Nur FREIE Punkte (in Ruhe > FERN von der Haut): die Kapseln sind 90. Perzentil der
// Haut, also 1–4 cm ueber ihr — halbgebundene Punkte drueckten sie um 3,8 cm heraus
// (gemessen an der Jeans, 21.09.2026), die Oberflaeche haelt sie ohnehin.
if (uKapselAn > 0.5 && mischung <= 0.0) {
    for (int k = 0; k < ${OberflaecheGLSL.KAPSELN}; k++) {
        if (k >= uKapselAnzahl) break;
        vec4 ka = uKapseln[4 * k], kb = uKapseln[4 * k + 1], ku = uKapseln[4 * k + 2], kr = uKapseln[4 * k + 3];
        vec3 ab = kb.xyz - ka.xyz;
        float L = length(ab);
        if (L < 1e-4) continue;
        vec3 d = ab / L;
        float t = clamp(dot(transformed - ka.xyz, d), 0.0, L);
        vec3 c = ka.xyz + d * t;
        vec3 o = transformed - c;
        vec3 e1 = normalize(ku.xyz - d * dot(ku.xyz, d));
        vec3 e2 = cross(d, e1);
        float s = t / L;
        float ru = mix(kr.x, kr.z, s) + uKapselAbstand;
        float rw = mix(kr.y, kr.w, s) + uKapselAbstand;
        float x = dot(o, e1) / ru, y = dot(o, e2) / rw, z = dot(o, d);
        float m2 = x * x + y * y;
        if (m2 < 1.0 && m2 > 1e-8) {
            // Radial auf den Rand der Ellipse — der Axialanteil (an den Kappen) bleibt.
            float m = sqrt(m2);
            vec3 quer = o - d * z;
            transformed = c + d * z + quer / m;
        }
    }
}
`;
}
