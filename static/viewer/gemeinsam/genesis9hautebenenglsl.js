import { Genesis9hautrauschenGLSL } from './genesis9hautrauschenglsl.js';

/**
 * Genesis9hautebenenGLSL — die Shader-Stücke der Hautebenen (17.10.2026, Edgar: „Hautton, Sommersprossen, Altersflecken, graue Haare, Muskel- und Fettzeichnung").
 *
 * FARBE (Hautton, Rötung, Sommersprossen, Altersflecken) steht hinter `alphamap_fragment`, also NACH Textur, Texturmischung und Schminke und VOR `lights_physical_fragment`
 * (dort liest Three `diffuseColor`). Wo Schminke liegt (`g9Schminke`), bleibt die Haut darunter unberührt: ein Lippenstift wird nicht braun getupft.
 *
 * HAUTTON: `albedo^(1 + k·t)` im linearen Raum. Mehr Melanin absorbiert stärker — dunkler UND gesättigter, weil die Kanäle ungleich dunkel werden (Beer-Lambert:
 * Durchlässigkeit^Dicke). Ein Faktor auf die Farbe würde sie nur dunkler machen. t > 0 dunkler, t < 0 heller; k = 0,55 gesetzt (Augenmaß, Chrome).
 * Wirkt relativ auf jeden Hautsatz — ein heller Satz wird mit t = 1 mittelbraun, ein dunkler mit t = −1 hell, nicht umgekehrt gleich.
 *
 * PUNKTE (Sommersprossen, Altersflecken): ein Gitter aus Zellen, je Zelle höchstens ein Punkt an gewürfelter Stelle mit gewürfeltem Radius (`g9Punkte`) — Auflösung unbegrenzt,
 * nichts liegt im Bild. WO sie sitzen, sagt die Gebietskarte (`G9hautebenen`: R Sommersprossen, G Altersflecken); wie groß eine Zelle in UV ist, rechnet `uHtMeterUV`
 * (Meter je UV-Einheit der Kachel) aus Millimetern um — der Kopf hat eine kleinere Kachelfläche als der Rumpf.
 *
 * ZEICHNUNG (Muskel, Fett): wie die Falten (`Genesis9hautGLSL.FALTEN`) eine Normalenschicht per Reoriented Normal Mapping über `mapN`; die Karte trägt BEIDE Normalen in
 * einem Bild (R/G Muskel, B/A Fett), die Gewichte sind Uniforms.
 *
 * ZWEITE WELLE (18.10.2026): Struktur, Farbton, Olivton, Sättigung, Helligkeit, Teint, Wangenröte, Augenringe, Äderchen, Pigment, Muttermale, Weißflecken, Pickel und die
 * Beulenschicht (Cellulite, Aknenarben) stehen in `Genesis9hautrauschenGLSL`; hier werden sie in die Farbe und hinter `normal_fragment_maps` eingesetzt. Jeder Teil ist mit
 * seinem Uniform abgeschaltet, solange der Regler auf 0 steht.
 */
export class Genesis9hautebenenGLSL {

    static UNIFORMS = `
uniform float uHtTon;
uniform float uHtRoetung;
uniform float uHtSommer;
uniform float uHtAlter;
uniform float uHtGroesseS;
uniform float uHtMeterUV;
uniform float uHtGebietAn;
uniform sampler2D uHtGebiet;
float g9Hash( vec2 p ) { return fract( sin( dot( p, vec2( 127.1, 311.7 ) ) ) * 43758.5453 ); }
vec2 g9Hash2( vec2 p ) { return fract( sin( vec2( dot( p, vec2( 127.1, 311.7 ) ), dot( p, vec2( 269.5, 183.3 ) ) ) ) * 43758.5453 ); }
/* Punktmuster: Zellen der Kantenlänge \`zelle\` (UV), Radius als Anteil der Zelle, \`anteil\` der Zellen trägt einen Punkt. 0..1. */
float g9Punkte( vec2 uv, float zelle, float radius, float anteil ) {
    vec2 p = uv / zelle;
    vec2 i = floor( p );
    vec2 f = fract( p );
    float best = 0.0;
    for ( int y = -1; y <= 1; y ++ ) {
        for ( int x = -1; x <= 1; x ++ ) {
            vec2 g = vec2( float( x ), float( y ) );
            vec2 c = i + g;
            float da = step( g9Hash( c + 17.3 ), anteil );
            float r = radius * ( 0.55 + 0.9 * g9Hash( c + 3.1 ) );
            float d = length( g + g9Hash2( c ) - f );
            best = max( best, da * ( 1.0 - smoothstep( r * 0.45, r, d ) ) );
        }
    }
    return best;
}
`;

    /**
     * Die Farbe. `frei` ist der Anteil, der nicht unter Schminke liegt (`g9Schminke`, wenn die Haut Schminke trägt). Reihenfolge: Struktur (an der Textur), Hautton, Rötung, Farbton …
     * Helligkeit, Teint/Röte/Augenringe/Äderchen, Sommersprossen und Altersflecken, Pigment, Muttermale, Weißflecken, Pickel. `htPickel` und `htGebietW` stehen außerhalb des
     * Blocks, die Beulenschicht liest sie später.
     */
    static farbe(mitSchminke) {
        const R = Genesis9hautrauschenGLSL;
        return `
float htPickel = 0.0;
vec4 htGebietW = vec4( 0.0 );
{
    vec3 htC = diffuseColor.rgb;
    float htFrei = ${mitSchminke ? '1.0 - g9Schminke' : '1.0'};
${R.GEBIET}
    vec3 htL = htC;
${R.STRUKTUR}
    htL = pow( max( htL, vec3( 0.0005 ) ), vec3( 1.0 + 0.55 * uHtTon ) );
    float htLuma = dot( htL, vec3( 0.2126, 0.7152, 0.0722 ) );
    htL = mix( htL, htL * vec3( 1.10, 0.90, 0.88 ), max( uHtRoetung, 0.0 ) );
    htL = mix( htL, mix( htL, vec3( htLuma ) * vec3( 1.04, 1.0, 0.98 ), 0.6 ), max( -uHtRoetung, 0.0 ) );
${R.TON}
#ifdef USE_MAP
    if ( uHtGebietAn > 0.5 ) htGebietW = texture2D( uHtGebiet, vMapUv );
#endif
${R.TEINT}
#ifdef USE_MAP
    if ( uHtGebietAn > 0.5 && uHtSommer > 0.0 ) {
        float htS = g9Punkte( vMapUv, 0.006 / uHtMeterUV, 0.28 * uHtGroesseS, uHtF4.w ) * mix( htGebietW.r, 1.0, uHtF5.x ) * uHtSommer;
        htL *= mix( vec3( 1.0 ), vec3( 0.58, 0.40, 0.30 ), clamp( htS, 0.0, 1.0 ) );
    }
    if ( uHtGebietAn > 0.5 && uHtAlter > 0.0 ) {
        float htA = g9Punkte( vMapUv + vec2( 7.7, 2.3 ), 0.018 / uHtMeterUV, 0.36, 0.55 ) * htGebietW.g * uHtAlter;
        htL *= mix( vec3( 1.0 ), vec3( 0.72, 0.56, 0.42 ), clamp( htA, 0.0, 1.0 ) );
    }
#endif
${R.FLECKEN}
    diffuseColor.rgb = mix( htC, htL, htFrei );
}
`;
    }

    /**
     * Den Zusatz in den Shader: Uniforms eintragen, Deklarationen hinter `common`, die Farbe hinter `alphamap_fragment`, die Beulen hinter `normal_fragment_maps` (die Normalenschichten
     * setzt `Genesis9hautGLSL.normalen` — sie ersetzt danach nur die Zeile `#include <normal_fragment_maps>`, die Beulen bleiben dahinter). Die Lage im Objektraum (`vHtLage`) kommt aus
     * `position`. `ebenen` ist `zusatz.hautebenen` (`{uniforms, zeichnung, mimik}`).
     */
    static einhaengen(shader, ebenen, mitSchminke) {
        Object.assign(shader.uniforms, ebenen.uniforms);
        shader.vertexShader = shader.vertexShader
            .replace('#include <common>', '#include <common>\nvarying vec3 vHtLage;')
            .replace('#include <begin_vertex>', '#include <begin_vertex>\nvHtLage = position;');
        shader.fragmentShader = shader.fragmentShader
            .replace('#include <common>', '#include <common>\n' + Genesis9hautebenenGLSL.UNIFORMS + Genesis9hautrauschenGLSL.UNIFORMS
                + (ebenen.zeichnung ? Genesis9hautebenenGLSL.ZEICHNUNG_UNIFORMS : '') + (ebenen.mimik ? Genesis9hautebenenGLSL.MIMIK_UNIFORMS : ''))
            .replace('#include <alphamap_fragment>', '#include <alphamap_fragment>\n' + Genesis9hautebenenGLSL.farbe(mitSchminke))
            .replace('#include <normal_fragment_maps>', '#include <normal_fragment_maps>\n' + Genesis9hautrauschenGLSL.BEULEN);
    }

    static ZEICHNUNG_UNIFORMS = `
uniform float uHtMuskel;
uniform float uHtFett;
uniform float uHtZStaerke;
uniform sampler2D uHtZeichnung;
`;

    /** MIMIKFALTEN (`Genesis9mimikfalten`): der Atlas der 27 FACS-Detail-Normalen (6 Spalten × 5 Zeilen, oben links Zelle 0) und ein Gewicht je Zelle. */
    static MIMIK_UNIFORMS = `
uniform sampler2D uHtMimikAtlas;
uniform float uHtMimikW[ 27 ];
uniform float uHtMimikStaerke;
`;

    /**
     * Summe `Σ Gewicht · Normale(x, y)` über die Zellen mit Gewicht > 0 (Kopfkachel, Zellen 512²), als RNM über `mapN`. Die Zelle (s, z) liegt im Bild von oben links; v = 1 ist oben im Bild
     * (wie bei den Falten): v im Atlas = 1 − (z + 1 − v) / 5. Der Rand der Zelle wird geklemmt, sonst mischt das Filtern die Nachbarzelle herein.
     */
    static MIMIK = `
        vec2 htMk = vec2( 0.0 );
        for ( int i = 0; i < 27; i ++ ) {
            float htW = uHtMimikW[ i ];
            if ( htW > 0.001 ) {
                float htZ = float( i / 6 );
                float htS = float( i - ( i / 6 ) * 6 );
                vec2 htUv = clamp( vNormalMapUv, 0.002, 0.998 );
                vec2 htA = vec2( ( htS + htUv.x ) / 6.0, 1.0 - ( htZ + 1.0 - htUv.y ) / 5.0 );
                htMk += ( texture2D( uHtMimikAtlas, htA ).rg * 2.0 - 1.0 ) * htW;
            }
        }
        vec3 htMn = normalize( vec3( htMk * uHtMimikStaerke, 1.0 ) );
        vec3 htMn1 = normalize( mapN );
        htMn1.z += 1.0;
        htMn.xy = -htMn.xy;
        mapN = htMn1 * dot( htMn1, htMn ) / htMn1.z - htMn;
`;

    /** Die Normalenschicht: Muskel- und Fettsteigung über `mapN` (RNM, wie die Falten). */
    static ZEICHNUNG = `
        vec4 htZ = texture2D( uHtZeichnung, vNormalMapUv );
        vec2 htSteil = ( ( htZ.rg * 2.0 - 1.0 ) * uHtMuskel + ( htZ.ba * 2.0 - 1.0 ) * uHtFett ) * uHtZStaerke;
        vec3 htN = normalize( vec3( htSteil, 1.0 ) );
        vec3 htN1 = normalize( mapN );
        htN1.z += 1.0;
        htN.xy = -htN.xy;
        mapN = htN1 * dot( htN1, htN ) / htN1.z - htN;
`;
}
