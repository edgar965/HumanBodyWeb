/**
 * OberflaecheGLSL — die Shader-Stücke der Oberflächenbindung und der
 * Kapselkollision (Konzept Fitting, Schichten 2 und 3, 21.09.2026).
 *
 * KÖRPERLAGE: `koerperlage.js` zeichnet den gehäuteten Körper je Bild als
 * Punkte in zwei Gleitkomma-Texturen (Lage, Normale; Texel = Punktnummer).
 * Der Stoff-Vertex-Shader liest je Punkt seine drei Körperecken daraus:
 *
 *     q = u·A + v·B + w·C,  n = normalize(u·nA + v·nB + w·nC)
 *     tief = min(d, LUFT) − (transformed − q)·n
 *     tief > 0  →  transformed += tief · n
 *
 * — NACH `skinning_vertex`, im selben lokalen Raum (Körper und Stoff hängen
 * in derselben Gruppe an demselben Skelett; `transformed` ist bei beiden die
 * gehäutete Lage vor `modelMatrix`).
 *
 * NUR HINAUS, NIE HINZIEHEN (24.09.2026, Edgar: Haut durch das G9 Base Shirt,
 * `001_ShyrinKurz_smplx` Bild 229; die Bindung war seit 23.09. aus). Die erste
 * Fassung SETZTE jeden gebundenen Punkt auf `q + d·n` — jeder Punkt für sich
 * auf die Fußoberfläche, der Sneaker verlor seine Form, die Sohle riss. Jetzt
 * bleibt der Stoff beim Skinning und wird nur dort herausgeschoben, wo er
 * TIEFER liegt als in Ruhe (höchstens `uLuft` unter der Haut): In Ruhe ist
 * `tief` ≤ 0, nichts bewegt sich; ein Schuh über dem Fuß bleibt starr, ein
 * Punkt, der beim Beugen in den Rücken taucht, dehnt den Stoff nach außen.
 * Zwei Grenzen gegen falsche Zuordnung: tiefer als `uTiefGrenze` oder seitlich
 * weiter als `uSeitGrenze` von seinem Dreieck ist der Punkt woanders
 * (durch ein dünnes Glied gefahren, Tangentialebene verlassen) — er bleibt.
 *
 * KAPSELN (Schicht 3): was nicht voll gebunden ist, wird aus den Kapseln der
 * Gliedmaßen gedrückt — elliptischer Kegel wie `Stoffkoerper.hinaus`, aber
 * ohne Iteration: liegt der Punkt in der Ellipse (im Maß der Halbachsen plus
 * Abstand), wird sein Querversatz radial auf den Rand skaliert.
 *
 * FREMDE GLIEDMASSEN (22.09.2026, Fund Edgar: Spagat-Animation, der Arm
 * dringt in den angehobenen Oberschenkel ein, die Jeans zeigt an der Stelle
 * einen hellen Fleck — durchscheinende Armhaut): Die Kapselschleife lief
 * bis dahin NUR für `mischung <= 0` (freie Punkte) — ein an die Beinoberfläche
 * GEBUNDENER Jeans-Punkt (`mischung > 0`, „Durchdringen ist konstruktiv
 * unmöglich") wurde nie geprüft, auch wenn ihn ein FREMDER Körperteil (Arm)
 * durchquert: Die Bindung schützt nur vor dem EIGENEN Körper darunter.
 * Jetzt läuft die Schleife für JEDEN Punkt, aber eine Kapsel wirkt nur auf
 * Punkte einer ANDEREN Gliedmaßen-Gruppe (`bindgruppe` vs. `uKapselGruppe`,
 * `Koerperzuordnung.GRUPPEN`) — sonst genau der alte Fehler von vorher
 * (halbgebundene Punkte 3,8 cm aus dem eigenen Bein gedrückt, siehe unten).
 */
export class OberflaecheGLSL {

    /** Höchstzahl Kapseln im Shader (`Stoffkapseln.HOECHSTENS`). */
    static KAPSELN = 32;

    static UNIFORMS = `
uniform float uOberflaecheAn;
uniform sampler2D uKoerperLage;
uniform sampler2D uKoerperNormale;
uniform float uLageBreite;
uniform float uLuft;
uniform float uTiefGrenze;
uniform float uSeitGrenze;
uniform float uKapselAn;
uniform float uKapselAbstand;
uniform int uKapselAnzahl;
uniform vec4 uKapseln[${4 * OberflaecheGLSL.KAPSELN}];
attribute vec3 bindung;
attribute vec3 bary;
attribute float bindabstand;
attribute float mischung;
attribute float bindgruppe;

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

    static FRAGMENT_UNIFORMS = `
uniform float uNormaleAusFlaeche;
`;

    /**
     * Nach `normal_fragment_begin`: die Normale zur Flächennormale ziehen, wo die
     * gehäutete Punktnormale von ihr abweicht (Achsel, Ellbogen, Leiste — dort
     * mischt ein Punkt Knochen, die sich gegeneinander drehen). Bis 25° Abweichung
     * (dot ≥ 0,9) bleibt die glatte Normale, ab 60° (dot ≤ 0,5) gilt die Fläche.
     * Die Flächennormale aus den Ableitungen der Sichtlage ist dieselbe, die Three
     * bei `flatShading` nimmt; sie zeigt wie `normal` zur Kamera.
     */
    static FRAGMENT = `
#include <normal_fragment_begin>
if (uNormaleAusFlaeche > 0.5) {
    vec3 flach = normalize(cross(dFdx(vViewPosition), dFdy(vViewPosition)));
    normal = normalize(mix(flach, normal, smoothstep(0.5, 0.9, dot(normal, flach))));
}
`;

    /** Nach `skinning_vertex`: aus der Oberfläche hinausdrücken, dann Kapseln. */
    static VERTEX = `
#include <skinning_vertex>
if (uOberflaecheAn > 0.5 && mischung > 0.0 && bindung.x >= 0.0) {
    vec3 q = bary.x * g9Lage(bindung.x) + bary.y * g9Lage(bindung.y) + bary.z * g9Lage(bindung.z);
    vec3 n = normalize(bary.x * g9Normale(bindung.x) + bary.y * g9Normale(bindung.y) + bary.z * g9Normale(bindung.z));
    vec3 o = transformed - q;
    float hoehe = dot(o, n);
    float tief = min(bindabstand, uLuft) - hoehe;
    if (tief > 0.0 && tief < uTiefGrenze && length(o - hoehe * n) < uSeitGrenze) {
        transformed += tief * n;
    }
}
// FREIE Punkte werden von JEDER Kapsel gedrueckt; GEBUNDENE (mischung > 0) nur,
// wenn der Punkt SELBST einer Gliedmasse gehoert (bindgruppe > 0, z. B. Jeans
// auf dem Bein) UND die Kapsel einer ANDEREN Gliedmasse ist (Spagat, Arm im
// Oberschenkel, 21.09.2026). Ruempfe/Kopf-gebundene Punkte (bindgruppe == 0,
// z. B. das Hemd an Brust und Ruecken) werden NIE von einer Kapsel gedrueckt —
// sonst reisst die Schulternaht: ein Hemdpunkt an der Schulter ist an einen
// Rumpfknochen gebunden (bindgruppe 0), die direkt angrenzende Schulter-Kapsel
// zaehlt als „fremd" und drueckte ihn 22.09.2026 aus der Naht (Edgars Bild:
// Loch am Aermelansatz), waehrend die Nachbarpunkte auf dem Arm (bindgruppe
// ARM, von ihrer eigenen Kapsel ausgenommen) an Ort blieben.
if (uKapselAn > 0.5) {
    for (int k = 0; k < ${OberflaecheGLSL.KAPSELN}; k++) {
        if (k >= uKapselAnzahl) break;
        vec4 ka = uKapseln[4 * k], kb = uKapseln[4 * k + 1], ku = uKapseln[4 * k + 2], kr = uKapseln[4 * k + 3];
        if (mischung > 0.0 && bindgruppe < 0.5) continue;
        if (mischung > 0.0 && bindgruppe > 0.5 && abs(ka.w - bindgruppe) < 0.5) continue;
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
