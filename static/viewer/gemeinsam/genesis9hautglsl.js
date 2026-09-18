/**
 * Genesis9hautGLSL — die Shader-Stücke, die `Genesis9haut` in Threes
 * `MeshStandardMaterial`/`MeshPhysicalMaterial` einhängt (aus
 * `genesis9haut.js` ausgelagert, 18.09.2026 abends — die Datei stand bei
 * 252 Zeilen, die Glitzer-Normalen und der Klarlack kamen dazu).
 *
 * DURCHLICHT: Barré-Brisebois & Bouchard (GDC 2011) hinter
 * `lights_fragment_end` — Deklarationen VOR der ausgerollten Lichtschleife
 * (Three kopiert den Rumpf je Licht in denselben Block: „redefinition").
 *
 * SCHMINKE: `mix(diffuseColor, farbe, gewicht)` hinter `map_fragment`
 * (PBRSkin `weighted_layer`), Rauheit hinter `roughnessmap_fragment`
 * (R Faktor, G Ersatzwert, B Ersatzgewicht).
 *
 * NORMALEN an Stelle von `normal_fragment_maps` (Tangentenraum-Fall):
 * 1. Glitzer-Normalen der Schminke (Snow Queen 03/08): Daz' LIE legt sie
 *    mit `blend_overlay` ÜBER die Normalenkarte der Haut — im Bildraum
 *    0..1, je Kanal W3C-Overlay, gemischt mit dem Alpha der Ebene
 *    (`uSchminkeNormalenModus` 1 = overlay, 0 = ersetzen).
 * 2. 8K-Detailnormalen: Reoriented Normal Mapping wie MDLs
 *    `base::blend_normals` (n1.z += 1, n2.xy negiert, n1·dot/n1.z − n2).
 *
 * KLARLACK: Irays `top_coat_color` tönt die Klarlackschicht
 * (`pbr_skin.mdl`: `ggx(tint: top_coat_color)`) — Three kennt keine
 * Klarlackfarbe, deshalb der Faktor `uKlarlackFarbe` am Clearcoat-Anteil
 * der Ausgabe (`KLARLACK_ALT` → `KLARLACK_NEU`).
 */
export class Genesis9hautGLSL {

    static VERZERRUNG = 0.2;
    static POTENZ = 4.0;
    static MASS = 0.3;
    static AMBIENT = 0.0;

    static SCHMINKE = `
#ifdef USE_MAP
    {
        vec4 schminkeFarbe = texture2D( uSchminkeFarbe, vMapUv );
        g9Schminke = texture2D( uSchminkeGewicht, vMapUv ).r * uSchminkeAn;
        diffuseColor.rgb = mix( diffuseColor.rgb, schminkeFarbe.rgb, g9Schminke );
    }
#endif
`;

    static RAUHEIT = `
#ifdef USE_MAP
    {
        vec3 schminkeRauheit = texture2D( uSchminkeRauheit, vMapUv ).rgb;
        roughnessFactor *= mix( 1.0, schminkeRauheit.r, g9Schminke );
        roughnessFactor = mix( roughnessFactor, schminkeRauheit.g, schminkeRauheit.b * uSchminkeAn );
    }
#endif
`;

    /** Glitzer-Normalen (Overlay im Bildraum) über der Hautnormale — vor `mapN`. */
    static GLITZER = `
        vec4 glitzer = texture2D( uSchminkeNormalen, vNormalMapUv );
        vec3 ueberlagert = mix( 2.0 * basisN * glitzer.xyz,
                                1.0 - 2.0 * ( 1.0 - basisN ) * ( 1.0 - glitzer.xyz ),
                                step( 0.5, basisN ) );
        ueberlagert = mix( glitzer.xyz, ueberlagert, uSchminkeNormalenModus );
        basisN = mix( basisN, ueberlagert, glitzer.a * uSchminkeNormalenAn );
`;

    /** 8K-Detailnormalen als RNM über `mapN` — schreibt `normal`. */
    static DETAIL = `
        vec3 n1 = normalize( mapN );
        vec3 detailN = texture2D( uDetailNormalen, vNormalMapUv ).xyz * 2.0 - 1.0;
        vec3 n2 = normalize( mix( vec3( 0.0, 0.0, 1.0 ), detailN, uDetailGewicht * uDetailAn ) );
        n1.z += 1.0;
        n2.xy = -n2.xy;
        vec3 gemischt = n1 * dot( n1, n2 ) / n1.z - n2;
        normal = normalize( tbn * gemischt );
`;

    static OHNE_DETAIL = `
        normal = normalize( tbn * mapN );
`;

    /** Der Ersatz für `normal_fragment_maps`, je nach Zusätzen zusammengesetzt. */
    static normalen(mitGlitzer, mitDetail) {
        return `
#if defined( USE_NORMALMAP_TANGENTSPACE )
    {
        vec3 basisN = texture2D( normalMap, vNormalMapUv ).xyz;
${mitGlitzer ? Genesis9hautGLSL.GLITZER : ''}
        vec3 mapN = basisN * 2.0 - 1.0;
        mapN.xy *= normalScale;
${mitDetail ? Genesis9hautGLSL.DETAIL : Genesis9hautGLSL.OHNE_DETAIL}
    }
#else
    #include <normal_fragment_maps>
#endif
`;
    }

    static KLARLACK_ALT = '( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;';
    static KLARLACK_NEU = '( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat * uKlarlackFarbe;';

    static DURCHLICHT = `
#if NUM_DIR_LIGHTS > 0
    {
        vec3 durchlicht = vec3( 0.0 );
        vec3 lichtweg;
        float staerke;
        #pragma unroll_loop_start
        for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
            lichtweg = normalize( directionalLights[ i ].direction + geometryNormal * ${Genesis9hautGLSL.VERZERRUNG.toFixed(2)} );
            staerke = pow( saturate( dot( geometryViewDir, -lichtweg ) ), ${Genesis9hautGLSL.POTENZ.toFixed(1)} ) * ${Genesis9hautGLSL.MASS.toFixed(2)};
            durchlicht += directionalLights[ i ].color * ( staerke + ${Genesis9hautGLSL.AMBIENT.toFixed(2)} );
        }
        #pragma unroll_loop_end
        reflectedLight.directDiffuse += durchlicht * uDurchlichtFarbe * uDurchlicht * vDuenne * diffuseColor.rgb;
    }
#endif
`;
}
