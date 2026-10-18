/**
 * Genesis9hautrauschenGLSL — die Shader-Stücke der zweiten Reglerwelle der Hautebenen (18.10.2026, Edgar: „neue Regler … Sommersprossen, Falten, Farbfehler, Farbton usw.
 * … möglichst viele Regler"). Eingesetzt von `Genesis9hautebenenGLSL` (Farbe hinter `alphamap_fragment`, Beulen hinter `normal_fragment_maps`).
 *
 * RAUSCHEN IM RAUM statt in der UV: Teint, Pigment, Weißflecken, Äderchen und Cellulite lesen ein Wertrauschen an der Lage im Objektraum (`vHtLage`, Ruhelage in Metern,
 * aus `position`) — ohne Nähte an den Rändern der UV-Inseln, und Zentimeter sind Zentimeter auf jeder Kachel. Die PUNKTE (Muttermale, Pickel, Aknenarben) bleiben in der UV wie die
 * Sommersprossen (`g9Punkte`, Umrechnung über `uHtMeterUV`): Punkte aus Zellen im Raum träfen die Fläche nur, wenn ihr Mittelpunkt näher als ihr Radius an ihr liegt — bei 2 mm
 * Radius in 8-cm-Zellen nur ~5 % der Zellen.
 *
 * GEBIETE ohne Karte: Kopf, Rumpf, Arme, Beine über die Materialgruppe (`uHtF5.y`: 0, 1, 2, 3) und die Höhe über dem Boden als Anteil der Körperhöhe (`uHtF5.zw`: Höhe, Boden);
 * Wangen/Nase und Augenringe aus der Gebietskarte (B, A, `G9hautebenen` Fassung 2).
 *
 * BEULEN (Cellulite, Aknenarben, erhabene Pickel): eine Höhe in Metern, daraus die Normale über die Bildschirmableitungen nach Mikkelsen („Bump Mapping Unparametrized Surfaces
 * on the GPU", 2010) — die Form, die Three in `perturbNormalArb` nutzt, hier mit UNnormierten Ableitungen der Lage, damit die Steigung in Metern je Meter stimmt und nicht vom Abstand
 * der Kamera abhängt. Was kleiner als ein Bildpunkt wird, blendet aus (`fwidth`), sonst flimmert es.
 *
 * Alle Stärken, Größen und Farben hier sind GESETZT (Augenmaß), an keinem Foto gemessen. GEMESSEN ist nur die Verteilung von `g9Fbm` (18.10.2026, 200.000 Zufallspunkte, dieselbe Formel
 * in JS im Chrome): Mittel 0,500, Streuung 0,114, Quantile 10 % 0,351 · 75 % 0,580 · 90 % 0,649 · 97 % 0,711 · 99 % 0,754 — daran hängen die Schwellen (Pigment ab 0,58, Weißflecken
 * 0,75 … 0,45, Teint ±1 bei ±0,17).
 *
 * Uniforms (je vier in einem vec4, `Genesis9hautebenen.einrichten`):
 *   uHtF1  Farbton, Olivton, Sättigung, Helligkeit       uHtF2  Struktur, Teint, Pigment, Weißflecken
 *   uHtF3  Fleckengröße, Muttermale, Male-Größe, Pickel   uHtF4  Äderchen, Wangenröte, Augenringe, Sommersprossen-Dichte
 *   uHtF5  Sommersprossen-Ausbreitung, Teil, Höhe, Boden  uHtB1  Cellulite, Aknenarben, Pickel (Relief), —
 */
export class Genesis9hautrauschenGLSL {

    static UNIFORMS = `
uniform vec4 uHtF1;
uniform vec4 uHtF2;
uniform vec4 uHtF3;
uniform vec4 uHtF4;
uniform vec4 uHtF5;
uniform vec4 uHtB1;
varying vec3 vHtLage;
float g9Hash3( vec3 p ) {
    p = fract( p * 0.3183099 + 0.1 );
    p *= 17.0;
    return fract( p.x * p.y * p.z * ( p.x + p.y + p.z ) );
}
/* Wertrauschen 0..1 (Gitter 1, glatt interpoliert). */
float g9Rauschen( vec3 x ) {
    vec3 i = floor( x );
    vec3 f = fract( x );
    f = f * f * ( 3.0 - 2.0 * f );
    return mix( mix( mix( g9Hash3( i ), g9Hash3( i + vec3( 1.0, 0.0, 0.0 ) ), f.x ),
                     mix( g9Hash3( i + vec3( 0.0, 1.0, 0.0 ) ), g9Hash3( i + vec3( 1.0, 1.0, 0.0 ) ), f.x ), f.y ),
                mix( mix( g9Hash3( i + vec3( 0.0, 0.0, 1.0 ) ), g9Hash3( i + vec3( 1.0, 0.0, 1.0 ) ), f.x ),
                     mix( g9Hash3( i + vec3( 0.0, 1.0, 1.0 ) ), g9Hash3( i + vec3( 1.0, 1.0, 1.0 ) ), f.x ), f.y ), f.z );
}
/* Vier Oktaven, 0..1, Mittel 0,5. */
float g9Fbm( vec3 x ) {
    float s = 0.0;
    float a = 0.5;
    for ( int i = 0; i < 4; i ++ ) {
        s += a * g9Rauschen( x );
        x = x * 2.03 + 11.7;
        a *= 0.5;
    }
    return s / 0.9375;
}
/* Normale aus einer Höhe in Metern (Mikkelsen 2010, unnormierte Ableitungen). */
vec3 g9Beule( vec3 p, vec3 n, float h, float seite ) {
    vec3 sx = dFdx( p );
    vec3 sy = dFdy( p );
    vec3 r1 = cross( sy, n );
    vec3 r2 = cross( n, sx );
    float det = dot( sx, r1 ) * seite;
    if ( abs( det ) < 1e-16 ) return n;
    vec3 grad = sign( det ) * ( dFdx( h ) * r1 + dFdy( h ) * r2 );
    return normalize( abs( det ) * n - grad );
}
`;

    /** Teil der Figur und Höhe über dem Boden (Anteil der Körperhöhe) — für Farbe und Beulen. */
    static GEBIET = `
    float htTeil = uHtF5.y;
    float htKopf = 1.0 - step( 0.5, htTeil );
    float htRumpf = step( 0.5, htTeil ) * ( 1.0 - step( 1.5, htTeil ) );
    float htArme = step( 1.5, htTeil ) * ( 1.0 - step( 2.5, htTeil ) );
    float htBeine = step( 2.5, htTeil );
    float htY = ( vHtLage.y - uHtF5.w ) / max( uHtF5.z, 0.5 );
`;

    /** Hautstruktur: das Verhältnis Textur zu ihrem weichgezeichneten Mittel (Mip-Stufe +4) hoch k — k < 0 glättet, k > 0 betont; der Mittelwert bleibt. */
    static STRUKTUR = `
#ifdef USE_MAP
    if ( uHtF2.x != 0.0 ) {
        vec3 htB = texture2D( map, vMapUv ).rgb;
        vec3 htM = texture2D( map, vMapUv, 4.0 ).rgb;
        htL *= pow( clamp( htB / max( htM, vec3( 0.003 ) ), 0.25, 4.0 ), vec3( uHtF2.x ) );
    }
#endif
`;

    /** Farbton (Drehung um die Grauachse, ±0,35 rad), Olivton (bei gleicher Helligkeit), Sättigung, Helligkeit (±0,8 Blenden). */
    static TON = `
    if ( uHtF1.x != 0.0 ) {
        float htW = uHtF1.x * 0.35;
        vec3 htK = vec3( 0.57735 );
        htL = max( htL * cos( htW ) + cross( htK, htL ) * sin( htW ) + htK * dot( htK, htL ) * ( 1.0 - cos( htW ) ), vec3( 0.0 ) );
    }
    if ( uHtF1.y > 0.0 ) {
        vec3 htO = htL * vec3( 0.90, 1.0, 0.72 );
        htO *= dot( htL, vec3( 0.2126, 0.7152, 0.0722 ) ) / max( dot( htO, vec3( 0.2126, 0.7152, 0.0722 ) ), 1e-4 );
        htL = mix( htL, htO, uHtF1.y );
    }
    if ( uHtF1.z != 0.0 ) htL = max( mix( vec3( dot( htL, vec3( 0.2126, 0.7152, 0.0722 ) ) ), htL, 1.0 + uHtF1.z ), vec3( 0.0 ) );
    htL *= exp2( uHtF1.w * 0.8 );
`;

    /** Teint (wolkig rot/hell), Wangen- und Nasenröte mit Couperose (Gebiet B), Augenringe (Gebiet A), Äderchen (Grate des Rauschens). */
    static TEINT = `
    if ( uHtF2.y > 0.0 ) {
        float htN = clamp( ( g9Fbm( vHtLage / ( 0.035 * uHtF3.x ) ) - 0.5 ) * 6.0, -1.0, 1.0 );
        htL *= max( vec3( 1.0 ) - uHtF2.y * htN * vec3( 0.07, 0.17, 0.17 ), vec3( 0.0 ) );
    }
    if ( uHtF4.y > 0.0 ) {
        float htWr = htGebietW.b * uHtF4.y * ( 0.7 + 0.6 * g9Fbm( vHtLage / 0.003 + 4.0 ) );
        htL *= mix( vec3( 1.0 ), vec3( 1.0, 0.68, 0.68 ), clamp( htWr, 0.0, 1.0 ) );
    }
    if ( uHtF4.z > 0.0 ) htL *= mix( vec3( 1.0 ), vec3( 0.64, 0.54, 0.62 ), clamp( htGebietW.a * uHtF4.z, 0.0, 1.0 ) );
    if ( uHtF4.x > 0.0 ) {
        // Die Linien sind die Höhenlinie 0,5 des Rauschens (voll bis 0,003 daneben, aus bei 0,015); mit 0,012 und (0,78; 0,85; 0,98) waren sie am Handrücken kaum zu sehen.
        float htAd = 1.0 - smoothstep( 0.003, 0.015, abs( g9Fbm( vHtLage / 0.025 + 9.0 ) - 0.5 ) );
        htAd *= 0.35 * htKopf + 0.7 * htRumpf + htArme + htBeine;
        htL *= mix( vec3( 1.0 ), vec3( 0.66, 0.78, 0.96 ), clamp( htAd * uHtF4.x, 0.0, 1.0 ) );
    }
`;

    /** Pigmentflecken, Muttermale, Weißflecken (hellt auch Sommersprossen und Pigment darunter auf), Pickel (merkt `htPickel` für die Beulen). */
    static FLECKEN = `
    if ( uHtF2.z > 0.0 ) {
        float htPg = smoothstep( 0.58, 0.66, g9Fbm( vHtLage / ( 0.06 * uHtF3.x ) + 31.0 ) ) * uHtF2.z * ( 0.6 + 0.4 * htKopf );
        htL *= mix( vec3( 1.0 ), vec3( 0.68, 0.55, 0.45 ), clamp( htPg, 0.0, 1.0 ) );
    }
#ifdef USE_MAP
    if ( uHtF3.y > 0.0 ) {
        float htMm = g9Punkte( vMapUv + vec2( 3.1, 5.3 ), 0.05 / uHtMeterUV, 0.035 * uHtF3.z, 0.8 * uHtF3.y );
        htL *= mix( vec3( 1.0 ), vec3( 0.30, 0.20, 0.15 ), htMm );
    }
#endif
    if ( uHtF2.w > 0.0 ) {
        float htVs = mix( 0.75, 0.45, uHtF2.w );
        float htVi = smoothstep( htVs, htVs + 0.025, g9Fbm( vHtLage / ( 0.08 * uHtF3.x ) + 77.0 ) );
        // Ohne Melanin: die Albedo hoch 0,55 (das Gegenteil des Hauttons) und rosiger — die Textur bleibt erkennbar; eine feste Farbe sah im Chrome wie ein weißer Aufkleber aus.
        htL = mix( htL, min( pow( max( htL, vec3( 0.0005 ) ), vec3( 0.55 ) ) * vec3( 1.0, 0.90, 0.88 ), vec3( 0.80 ) ), htVi );
    }
#ifdef USE_MAP
    if ( uHtF3.w > 0.0 ) {
        float htPkG = 0.75 * htKopf + 0.35 * htRumpf * smoothstep( 0.62, 0.72, htY ) + 0.06 * ( htArme + htBeine + htRumpf );
        htPickel = g9Punkte( vMapUv + vec2( 9.1, 1.7 ), 0.022 / uHtMeterUV, 0.10, uHtF3.w * htPkG );
        htL *= mix( vec3( 1.0 ), vec3( 1.0, 0.60, 0.58 ), htPickel );
    }
#endif
`;

    /** Die Beulenschicht hinter `normal_fragment_maps`: Höhe in Metern, je Anteil ausgeblendet, wenn er kleiner als ein Bildpunkt wird. */
    static BEULEN = `
    if ( uHtB1.x + uHtB1.y + uHtB1.z > 0.0 ) {
${Genesis9hautrauschenGLSL.GEBIET}
        float htFw = length( fwidth( vHtLage ) );
        float htH = 0.0;
        if ( uHtB1.x > 0.0 ) {
            float htCg = ( htRumpf + htBeine ) * smoothstep( 0.28, 0.34, htY ) * ( 1.0 - smoothstep( 0.55, 0.60, htY ) );
            // Weiche Dellen: breite Schwelle (0,38 … 0,72 ≈ ±1,5 Streuungen), 14-mm-Rauschen, 1 mm tief — mit 0,50 … 0,70, 11 mm und 1,5 mm sah es im Chrome zerklüftet aus.
            htH -= uHtB1.x * htCg * 0.0010 * smoothstep( 0.38, 0.72, g9Fbm( vHtLage / 0.014 + 5.0 ) ) * ( 1.0 - smoothstep( 0.002, 0.005, htFw ) );
        }
#ifdef USE_MAP
        if ( uHtB1.y > 0.0 ) {
            float htNb = g9Punkte( vMapUv + vec2( 4.4, 8.8 ), 0.006 / uHtMeterUV, 0.32, 0.55 );
            htH -= uHtB1.y * htKopf * ( 0.35 + 0.65 * htGebietW.b ) * 0.0005 * htNb * ( 1.0 - smoothstep( 0.0006, 0.0015, htFw ) );
        }
#endif
        htH += uHtB1.z * htPickel * 0.0004 * ( 1.0 - smoothstep( 0.001, 0.003, htFw ) );
        normal = g9Beule( - vViewPosition, normal, htH, faceDirection );
    }
`;
}
