/**
 * Genesis9hautteileGLSL — Hautfarbe und Tattoo je Körperteil im Shader der Hautebenen (25.10.2026, Edgar: „bei den Reglern für die einzelnen Körperteile mach jeweils auch Regler
 * für die Textur“, dann „pro Körperteil brauche ich die Texturregler, z.B. Nase, Augen, Rumpf“). Werte und Uniforms: `Genesis9hautteile`; eingesetzt von `Genesis9hautebenenGLSL`
 * (Farbe nach dem Ton, Tattoo vor der Schminke-Mischung).
 *
 * TEILKARTE (`uHtTeile`, `G9hautteile` Fassung 4): 24 Kanäle in sechs 512er-Teilbildern, 3 Spalten × 2 Zeilen — Teilbild k in Spalte k % 3, Zeile k / 3 (Zeile 0 oben im Bild,
 * also v von 0,5 bis 1). Die UV wird je Teilbild eineinhalb Texel nach innen geklemmt (sonst filterte das Nachbarteilbild herein; Mip-Stufen sind aus).
 * HAUTFARBE: htL × Σ w·F (Rest bis 1 ohne Faktor) — F je Teil aus `Genesis9hautteile.rechnen`.
 * TATTOO: bis zu sechs Ebenen (`uHtTatA` Deckung, Größe m, Schwelle der Fläche, Stil; `uHtTatB` Tinte linear, Muster; `uHtTatC` Modus −2 ganze Haut / −3 Teile der Bitmaske in w,
 * gespiegelt in z). Rauschen im Objektraum (`vHtLage`, Ruhelage in Metern — haftet an der Haut unter Morphs und Pose, keine UV-Nähte): Ranken = Höhenlinie 0,5 eines zweistufigen
 * Wertrauschens, Flächen = über 0,56; Flecken aus `g9Fbm` auf 4,5-facher Größe über der Schwelle. Kanten über `fwidth` geglättet — deshalb wird in der Schleife nur über
 * Uniforms gesprungen (Ableitungen sind in ungleichförmigem Ablauf undefiniert). Linienbreite und Fleckenmaßstab GESETZT (Augenmaß), nicht gemessen.
 */
export class Genesis9hautteileGLSL {

    static UNIFORMS = `
uniform float uHtTeilAn;
uniform sampler2D uHtTeile;
uniform vec3 uHtTeilF[ 24 ];
uniform vec4 uHtTatA[ 6 ];
uniform vec4 uHtTatB[ 6 ];
uniform vec4 uHtTatC[ 6 ];
uniform vec4 uHtTeilE[ 120 ];
uniform float uHtTeilEAn;
/* Summe der Anteile aller Teile, deren Bit in \`maske\` steht (Bit i = Teil i). */
float g9TeilMaske( vec4 t[ 6 ], int maske ) {
    float w = 0.0;
    for ( int i = 0; i < 6; i ++ ) {
        int b = maske >> ( 4 * i );
        w += dot( t[ i ], vec4( float( b & 1 ), float( ( b >> 1 ) & 1 ), float( ( b >> 2 ) & 1 ), float( ( b >> 3 ) & 1 ) ) );
    }
    return w;
}
/* Rankenrauschen: zwei Stufen Wertrauschen, 0..1. */
float g9Ranke( vec3 p ) {
    return ( g9Rauschen( p ) + 0.5 * g9Rauschen( p * 2.03 + 11.7 ) ) / 1.5;
}
`;

    /**
     * Teilkarte lesen — am ANFANG des Farbblocks (seit 26.10.2026; vorher erst nach dem Ton): `htTk` die Anteile der 24 Kanäle, `htTs` ihre Summe, `htTe[5]` die Zuschläge der
     * Hautmerkmale je Teil (`Genesis9hautteilmerkmale`), gewichtet mit den Anteilen. `htTe` steht außerhalb des Blocks (die Beulen lesen es hinter `normal_fragment_maps`).
     */
    static LESEN = `
    vec4 htTk[ 6 ];
    float htTs = 0.0;
    for ( int i = 0; i < 6; i ++ ) htTk[ i ] = vec4( 0.0 );
#ifdef USE_MAP
    if ( uHtTeilAn > 0.5 ) {
        vec2 htTu = clamp( HT_UV, vec2( 0.003 ), vec2( 0.997 ) );
        for ( int i = 0; i < 6; i ++ ) {
            float htSp = float( i - ( i / 3 ) * 3 );
            float htZe = float( i / 3 );
            htTk[ i ] = texture2D( uHtTeile, vec2( ( htSp + htTu.x ) / 3.0, ( htTu.y + 1.0 - htZe ) * 0.5 ) );
            htTs += dot( htTk[ i ], vec4( 1.0 ) );
        }
        if ( uHtTeilEAn > 0.5 ) {
            for ( int i = 0; i < 6; i ++ ) {
                for ( int c = 0; c < 4; c ++ ) {
                    float htTw = htTk[ i ][ c ];
                    if ( htTw <= 0.0 ) continue;
                    int htKb = ( 4 * i + c ) * 5;
                    for ( int j = 0; j < 5; j ++ ) htTe[ j ] += htTw * uHtTeilE[ htKb + j ];
                }
            }
            for ( int j = 0; j < 5; j ++ ) htTe[ j ] /= max( htTs, 1.0 );
        }
    }
#endif
`;

    /**
     * Die Uniforms der Hautebenen mit den Zuschlägen ÜBERDECKEN (lokale Namen gleich den Uniforms; der Initialisierer liest noch das Uniform — GLSL ES 3.00, 4.2.2). Platz in
     * `htTe`: [0] Ton, Rötung, Farbton, Olivton · [1] Sättigung, Helligkeit, Struktur, Teint · [2] Äderchen, Sommersprossen, Altersflecken, Pigment · [3] Weißflecken, Muttermale,
     * Pickel, Cellulite · [4] Aknenarben. Sommersprossen, Altersflecken, Pickel, Cellulite und Aknenarben stehen an ihrer Stelle (Gebiet), nicht hier.
     */
    static SCHATTEN = `
    float uHtTon = uHtTon + htTe[ 0 ].x;
    float uHtRoetung = uHtRoetung + htTe[ 0 ].y;
    vec4 uHtF1 = uHtF1 + vec4( htTe[ 0 ].z, htTe[ 0 ].w, htTe[ 1 ].x, htTe[ 1 ].y );
    vec4 uHtF2 = uHtF2 + vec4( htTe[ 1 ].z, htTe[ 1 ].w, htTe[ 2 ].w, htTe[ 3 ].x );
    vec4 uHtF3 = uHtF3 + vec4( 0.0, htTe[ 3 ].y, 0.0, 0.0 );
    vec4 uHtF4 = uHtF4 + vec4( htTe[ 2 ].x, 0.0, 0.0, 0.0 );
`;

    /** Die Hautfarbe je Teil auflegen (im Farbblock nach dem Ton; die Teilkarte hat `LESEN` gelesen, `htTk` liest das Tattoo weiter unten). */
    static FARBE = `
#ifdef USE_MAP
    if ( uHtTeilAn > 0.5 ) {
        vec3 htTf = vec3( 0.0 );
        for ( int i = 0; i < 6; i ++ ) {
            htTf += htTk[ i ].x * uHtTeilF[ 4 * i ] + htTk[ i ].y * uHtTeilF[ 4 * i + 1 ] + htTk[ i ].z * uHtTeilF[ 4 * i + 2 ] + htTk[ i ].w * uHtTeilF[ 4 * i + 3 ];
        }
        htL *= ( htTf + vec3( max( 1.0 - htTs, 0.0 ) ) ) / max( htTs, 1.0 );
    }
#endif
`;

    /** Die Tattoos (vor der Mischung mit der Schminke). */
    static TATTOO = `
#ifdef USE_MAP
    if ( uHtTeilAn > 0.5 ) {
        for ( int i = 0; i < 6; i ++ ) {
            vec4 htQa = uHtTatA[ i ];
            if ( htQa.x <= 0.0 ) continue;
            vec4 htQb = uHtTatB[ i ];
            vec4 htQc = uHtTatC[ i ];
            float htQw = htQc.x < -2.5 ? g9TeilMaske( htTk, int( htQc.w + 0.5 ) ) : 1.0;          // −2 = ganze Haut, −3 = Teile der Bitmaske
            vec3 htQp = vHtLage;
            if ( htQc.z > 0.5 ) htQp.x = abs( htQp.x );
            htQp = htQp / htQa.y + htQb.w * vec3( 1.731, 2.417, 3.119 );
            float htQf = smoothstep( htQa.z, htQa.z + 0.03, g9Fbm( htQp * 0.22 + 19.0 ) );
            float htQn = g9Ranke( htQp );
            float htQaa = fwidth( htQn ) + 1e-4;
            float htQs = htQa.w < 0.5 ? 1.0 - smoothstep( 0.035 - htQaa, 0.035 + htQaa, abs( htQn - 0.5 ) )
                                      : smoothstep( 0.56 - htQaa, 0.56 + htQaa, htQn );
            htL = mix( htL, htQb.rgb, clamp( htQa.x * htQw * htQf * htQs, 0.0, 1.0 ) );
        }
    }
#endif
`;
}
