import { Gewebe } from './gewebe.js';

/**
 * StoffshaderGLSL — die Shader-Stücke von `Stoffshader` (25.10.2026): Bindung als Mikro-Normale, Glanz und Glanzsaum.
 *
 * BINDUNG: dieselben Höhenfelder wie die gerechneten Kacheln (`gewebe.js` Leinwand, `gewebearten.js` Köper, Jersey, Satin), hier je
 * Pixel an der UV des Stücks statt als Bild — `p = uv · stoffDichte` ist die Lage in Fäden. Neu ist die Narbung (Leder): ein
 * Zellenrauschen (Worley F2 − F1), die Rillen liegen an den Zellgrenzen. Die Steigung aus zentralen Differenzen kippt die Normale
 * NACH der Normalkarte des Stücks (vor `clearcoat_normal_fragment_begin`): Daz' eigene Normalen und die gebackenen Falten (`G9faltenkarte`,
 * `bild.falten_*`) bleiben darunter erhalten — bis 25.10.2026 ERSETZTE das Gewebe die Normalkarte (`Stoffwerte.gewebe`), und mit ihr
 * die Falten. Die Neigung folgt der Kachel: Schritt in x = −½ · Struktur · ∂h/∂Faden, wie `Gewebe.normalfeld` mit `normalScale` = Struktur.
 * Die Tangenten rechnet `stoffTangenten` wie Threes `getTangentFrame` (die gibt es nur MIT Normalkarte).
 *
 * KEIN FLIMMERN: Liegt ein Faden unter ~1,7 Bildpunkten (`fwidth(p)` > 0,6), blendet die Bindung aus (ab 0,25 weich) — sonst entsteht ein
 * Moiré mit dem Pixelraster, wie es die Mip-Stufe der Kachel mittelte (`Gewebe.KACHEL_M`).
 *
 * GLANZSAUM über Threes eigenen Sheen-Pfad: `USE_SHEEN` wird definiert, wo das Material es nicht schon tut (`MeshStandardMaterial`, Physical
 * mit `sheen` 0); die Farbe setzt der Eingriff hinter `lights_physical_fragment` (vor `lights_fragment_begin`) auf Stoff- oder eigene Farbe
 * × Saum. Ohne Saum bleibt `material.sheenColor` 0 — dann ändert der Pfad nichts (`sheenEnergyComp` = 1). GLANZ = Faktor auf
 * `specularColor` und `specularF90` (F90 gedeckelt bei 1): Daz' `Glossy Layered Weight`, das Three nur am Physical-Material als
 * `specularIntensity` kennt.
 */
export class StoffshaderGLSL {

    static VERTEX_KOPF = 'varying vec2 vStoffUv;\n';
    static VERTEX = '#include <uv_vertex>\n\tvStoffUv = uv;';

    static FRAGMENT_KOPF = `#ifndef USE_SHEEN
#define USE_SHEEN
#endif
uniform float stoffArt;
uniform float stoffDichte;
uniform float stoffStaerke;
uniform float stoffSpiegel;
uniform float stoffSaum;
uniform float stoffSaumStreuung;
uniform float stoffSaumEigen;
uniform vec3 stoffSaumFarbe;
varying vec2 vStoffUv;
`;

    /** Die Höhenfelder (0..1) über der Lage in Fäden; nach dem `#include <common>` (dort steht `PI`). */
    static FUNKTIONEN = `
const float STOFF_A = ${Gewebe.AMPLITUDE.toFixed(3)};
const float STOFF_D = ${Gewebe.DICKE.toFixed(3)};
float stoffKreuzung( float welleK, float welleS, vec2 rund ) {
    return ( max( STOFF_A * welleK + STOFF_D * rund.x, STOFF_A * welleS + STOFF_D * rund.y ) + STOFF_A ) / ( 2.0 * STOFF_A + STOFF_D );
}
float stoffLeinwand( vec2 p ) {
    vec2 f = floor( p );
    vec2 rund = sin( PI * ( p - f ) );
    float vK = mod( f.x, 2.0 ) < 0.5 ? 1.0 : -1.0;
    float vS = mod( f.y, 2.0 ) < 0.5 ? 1.0 : -1.0;
    return stoffKreuzung( vK * cos( PI * ( p.y - 0.5 ) ), -vS * cos( PI * ( p.x - 0.5 ) ), rund );
}
float stoffKoeper( vec2 p ) {
    vec2 f = floor( p );
    vec2 rund = sin( PI * ( p - f ) );
    float welleK = cos( 2.0 * PI * ( mod( p.y - f.x, 3.0 ) - 1.0 ) / 3.0 );
    float welleS = cos( 2.0 * PI * ( mod( p.x - f.y, 3.0 ) - 1.5 ) / 3.0 );
    return stoffKreuzung( welleK, welleS, rund );
}
float stoffJersey( vec2 p ) {
    vec2 q = fract( p );
    float d = abs( abs( q.x - 0.5 ) - 0.35 * q.y ) / sqrt( 1.1225 );
    float k = min( 1.0, d / 0.16 );
    return sqrt( 1.0 - k * k );
}
float stoffSatin( vec2 p ) {
    return sin( PI * fract( p.x ) );
}
vec2 stoffZufall( vec2 z ) {
    return fract( sin( vec2( dot( z, vec2( 127.1, 311.7 ) ), dot( z, vec2( 269.5, 183.3 ) ) ) ) * 43758.5453 );
}
float stoffNarbung( vec2 p ) {
    vec2 f = floor( p );
    vec2 r = p - f;
    float d1 = 8.0;
    float d2 = 8.0;
    for ( int j = -1; j <= 1; j ++ ) {
        for ( int i = -1; i <= 1; i ++ ) {
            vec2 o = vec2( float( i ), float( j ) );
            vec2 c = o + 0.1 + 0.8 * stoffZufall( f + o ) - r;
            float d = dot( c, c );
            if ( d < d1 ) { d2 = d1; d1 = d; } else if ( d < d2 ) { d2 = d; }
        }
    }
    return smoothstep( 0.0, 0.35, sqrt( d2 ) - sqrt( d1 ) );
}
float stoffHoehe( vec2 p ) {
    if ( stoffArt < 1.5 ) return stoffLeinwand( p );
    if ( stoffArt < 2.5 ) return stoffKoeper( p );
    if ( stoffArt < 3.5 ) return stoffJersey( p );
    if ( stoffArt < 4.5 ) return stoffSatin( p );
    return stoffNarbung( p );
}
mat3 stoffTangenten( vec3 augpunkt, vec3 n, vec2 uv ) {
    vec3 q0 = dFdx( augpunkt );
    vec3 q1 = dFdy( augpunkt );
    vec2 st0 = dFdx( uv );
    vec2 st1 = dFdy( uv );
    vec3 q1perp = cross( q1, n );
    vec3 q0perp = cross( n, q0 );
    vec3 t = q1perp * st0.x + q0perp * st1.x;
    vec3 b = q1perp * st0.y + q0perp * st1.y;
    float det = max( dot( t, t ), dot( b, b ) );
    float s = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
    return mat3( t * s, b * s, n );
}
`;

    static NORMALE = `
    if ( stoffArt > 0.5 && stoffStaerke > 0.0 ) {
        vec2 stoffP = vStoffUv * stoffDichte;
        vec2 stoffFw = fwidth( stoffP );
        float stoffSicht = 1.0 - smoothstep( 0.25, 0.6, max( stoffFw.x, stoffFw.y ) );
        if ( stoffSicht > 0.0 ) {
            const float stoffE = 0.04;
            vec2 stoffG = vec2( stoffHoehe( stoffP + vec2( stoffE, 0.0 ) ) - stoffHoehe( stoffP - vec2( stoffE, 0.0 ) ),
                                stoffHoehe( stoffP + vec2( 0.0, stoffE ) ) - stoffHoehe( stoffP - vec2( 0.0, stoffE ) ) ) / ( 2.0 * stoffE );
            mat3 stoffTbn = stoffTangenten( - vViewPosition, normal, vStoffUv );
            #if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
                stoffTbn[ 0 ] *= faceDirection;
                stoffTbn[ 1 ] *= faceDirection;
            #endif
            normal = normalize( normal - 0.5 * stoffStaerke * stoffSicht * ( stoffG.x * stoffTbn[ 0 ] + stoffG.y * stoffTbn[ 1 ] ) );
        }
    }
`;

    static LICHT = `
    material.specularColor = min( material.specularColor * stoffSpiegel, vec3( 1.0 ) );
    material.specularF90 = min( material.specularF90 * stoffSpiegel, 1.0 );
    #ifdef USE_SHEEN
        if ( stoffSaum > 0.0 ) {
            material.sheenColor = ( stoffSaumEigen > 0.5 ? stoffSaumFarbe : diffuseColor.rgb ) * stoffSaum;
            material.sheenRoughness = clamp( stoffSaumStreuung, 0.07, 1.0 );
        }
    #endif
`;

    /** Den Shader umschreiben — rein über Text (in Node prüfbar). Fehlt eine Stelle, bleibt der Text dort, wie er war; `stellen` zählt die getroffenen. */
    static einsetzen(shader) {
        let stellen = 0;
        const ersetzen = (quelle, marke, neu) => {
            if (!quelle.includes(marke)) return quelle;
            stellen += 1;
            return quelle.replace(marke, neu);
        };
        shader.vertexShader = StoffshaderGLSL.VERTEX_KOPF + ersetzen(shader.vertexShader, '#include <uv_vertex>', StoffshaderGLSL.VERTEX);
        let f = StoffshaderGLSL.FRAGMENT_KOPF + shader.fragmentShader;
        f = ersetzen(f, '#include <common>', '#include <common>\n' + StoffshaderGLSL.FUNKTIONEN);
        f = ersetzen(f, '#include <clearcoat_normal_fragment_begin>', StoffshaderGLSL.NORMALE + '#include <clearcoat_normal_fragment_begin>');
        f = ersetzen(f, '#include <lights_fragment_begin>', StoffshaderGLSL.LICHT + '#include <lights_fragment_begin>');
        shader.fragmentShader = f;
        return stellen;
    }
}
