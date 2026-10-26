import { Dazschnittwerte } from './dazschnittwerte.js';

/**
 * DazschnittGLSL — der Shader-Eingriff an den Materialien eines Daz-Stücks: Schnitt je Pixel, Saumband, Kragen und Knopfleiste als Abziehbild (Stufe K2c,
 * 25.10.2026). Die Kante ist `Dazschnittwerte.kante` (dort Formeln und Bedeutung), hier Zeichen für Zeichen dieselbe Rechnung — der Browser schneidet damit die
 * Flächen aus dem Index (ganz jenseits) UND der Shader die Pixel (an der Kante): eine glatte Kurve statt einer Treppe aus Dreiecken.
 *
 * EINGANG je Punkt zwei Attribute des Stücks (`Dazschnittkoord`): `dkKoord` (Kette, Anteil, Rumpfhöhe, Umfangswinkel — die Körperkoordinaten der Haut, an die
 * der Punkt gebunden ist) und `dkLage` (x der Ruhelage für die Breite des Ausschnitts; Rumpfhöhe des Halsansatzes unter dem Umfangswinkel, ab der der Ausschnitt
 * misst — `Koerperkoordinatenpunkte.ansatz`). Wie bei den eigenen Stücken ATTRIBUTE, kein `texelFetch` (an UV-Nähten
 * riss es damit auf, K2a). Als Varyings weitergereicht; geschnitten wird je Pixel.
 *
 * ABZIEHBILDER (keine Geometrie, Edgar: Kragen an Daz-Stücken nur als Textur/Normalenkarte): Saumband an den neuen Schnittkanten (Helligkeit, Wulst, Steppnaht —
 * wie `EigenkleidschnittGLSL`), Kragenband entlang des Ausschnitts (aufliegende Platte `KRAGEN_M` mit Kante und Steppnaht), Knopfleiste vorn ab der Tiefe des
 * Ausschnitts mit gezeichneten Knöpfen. Relief als Normalenstörung über die Bildschirmableitungen wie Threes Bump-Mapping. Maße GESETZT (Augenmaß).
 * Namen mit `dk`/`uDk`/`vDk` — die Materialien tragen weitere Eingriffe (`Stoffshader`, `Oberflaechenbindung`) über `Shaderpatch`.
 */
export class DazschnittGLSL {

    static SCHLUESSEL = 'dazschnitt';
    static FASSUNG = '3';
    static WULST_M = 0.0012;
    static KRAGEN_M = 0.0015;
    static KNOPF_M = 0.0055;

    static VERTEX_KOPF = `
attribute vec4 dkKoord;
attribute vec2 dkLage;
varying vec4 vDkKoord;
varying vec4 vDkKette;
varying vec3 vDkKette2;
`;

    static VERTEX = `
{
    float dkK = floor( dkKoord.x + 0.5 );
    vDkKoord = vec4( dkKoord.z, dkKoord.y, dkLage.x, cos( 6.2831853 * dkKoord.w ) );
    vDkKette = vec4( dkK > 1.5 && dkK < 3.5 ? 1.0 : 0.0, dkK > 3.5 && dkK < 5.5 ? 1.0 : 0.0, dkK > 7.5 && dkK < 9.5 ? 1.0 : 0.0, dkK > 9.5 && dkK < 11.5 ? 1.0 : 0.0 );
    vDkKette2 = vec3( ( abs( dkK - 1.0 ) < 0.5 || ( dkK > 5.5 && dkK < 7.5 ) ) ? 1.0 : 0.0, dkK > 0.5 ? 1.0 : 0.0, dkLage.y );
}
`;

    static KOPF = `
uniform vec4 uDkHals;
uniform vec4 uDkSaum;
uniform vec4 uDkBand;
uniform vec4 uDkLeiste;
uniform vec3 uDkLaenge;
varying vec4 vDkKoord;
varying vec4 vDkKette;
varying vec3 vDkKette2;
float dkForm( float u, float form ) {
    float v = clamp( u, 0.0, 1.0 );
    float s = form < 0.5 ? sqrt( 1.0 - v * v ) : ( form < 1.5 ? 1.0 - v : ( form < 2.5 ? sqrt( 1.0 - v * v * v * v ) : 1.0 - pow( v, 6.0 ) ) );
    return u >= 1.0 ? 0.0 : s;
}
float dkHals( float h, float x, float vorn ) {
    float u = abs( x ) / max( 0.5 * uDkHals.w, 0.001 );
    float tiefe = mix( uDkHals.z * dkForm( u, 0.0 ), uDkHals.y * dkForm( u, uDkHals.x ), smoothstep( -0.35, 0.35, vorn ) );
    return ( h - tiefe ) * uDkLaenge.x;
}
float dkKante( float h, float t, float x, float vorn, vec4 k, vec3 k2 ) {
    if ( k2.y < 0.5 ) return 1.0;
    float f = 1.0;
    float glied = max( k.x, k.z );
    float unten = max( k.y, k.w );
    if ( uDkSaum.x < 50.0 && glied < 0.5 ) f = min( f, ( uDkSaum.x - h ) * uDkLaenge.x );
    if ( uDkSaum.y < 50.0 && unten < 0.5 ) {
        float achsel = k2.x > 0.5 ? max( 0.0, h - ACHSEL_H ) * uDkLaenge.x * ACHSEL_STEIGUNG : 0.0;
        f = min( f, k.z > 0.5 ? -1.0 : ( uDkSaum.y - t ) * uDkLaenge.y + achsel );
    }
    if ( uDkSaum.z > -50.0 && glied < 0.5 ) f = min( f, ( h - uDkSaum.z ) * uDkLaenge.x );
    if ( uDkSaum.w < 50.0 && unten > 0.5 ) f = min( f, k.w > 0.5 ? -1.0 : ( uDkSaum.w - t ) * uDkLaenge.z );
    if ( uDkHals.x > -0.5 && k2.x > 0.5 ) f = min( f, dkHals( h - k2.z, x, vorn ) );      // ab dem Halsansatz dieses Umfangswinkels
    return f;
}
`;

    static SCHNITT = `
float dkF = dkKante( vDkKoord.x, vDkKoord.y, vDkKoord.z, vDkKoord.w, vDkKette, vDkKette2 );
if ( dkF < 0.0 ) discard;
float dkAa = max( fwidth( dkF ), 1e-5 );
float dkB = uDkBand.x;
float dkBand = dkB > 0.0 ? 1.0 - smoothstep( dkB - dkAa, dkB + dkAa, dkF ) : 0.0;
float dkStich = dkB > 0.0 ? 1.0 - smoothstep( 0.0, 1.5 * dkAa, abs( dkF - 0.8 * dkB ) ) : 0.0;
float dkHf = dkBand * WULST * sin( 3.14159265 * clamp( dkF / max( dkB, 1e-4 ), 0.0, 1.0 ) );
float dkKragen = 0.0;
float dkKragenRand = 0.0;
if ( uDkHals.x > -0.5 && uDkBand.z > 0.0 && vDkKette2.x > 0.5 ) {
    float dkFh = dkHals( vDkKoord.x - vDkKette2.z, vDkKoord.z, vDkKoord.w );
    float dkAh = max( fwidth( dkFh ), 1e-5 );
    dkKragen = ( 1.0 - smoothstep( uDkBand.z - dkAh, uDkBand.z + dkAh, dkFh ) ) * step( 0.0, dkFh );
    dkKragenRand = dkKragen * ( 1.0 - smoothstep( 0.0, 1.5 * dkAh, abs( dkFh - 0.85 * uDkBand.z ) ) );
    dkHf += KRAGEN * dkKragen * ( 1.0 - smoothstep( 0.9 * uDkBand.z, uDkBand.z, dkFh ) ) * smoothstep( 0.0, 0.08 * uDkBand.z, dkFh );
}
float dkLeiste = 0.0;
float dkLeisteRand = 0.0;
float dkKnopf = 0.0;
if ( uDkLeiste.x > 0.5 && vDkKoord.w > 0.3 && vDkKette2.x > 0.5 ) {
    float dkYm = ( vDkKoord.x - vDkKette2.z - uDkHals.y ) * uDkLaenge.x;
    float dkLang = uDkLeiste.y * uDkLaenge.x;
    float dkW = 0.5 * uDkLeiste.z;
    float dkAx = abs( vDkKoord.z );
    if ( dkYm > -0.004 && dkYm < dkLang ) {
        dkLeiste = 1.0 - smoothstep( dkW - 0.0008, dkW + 0.0008, dkAx );
        dkLeisteRand = 1.0 - smoothstep( 0.0003, 0.0009, abs( dkAx - dkW + 0.0015 ) );
        float dkAbst = dkLang / uDkLeiste.x;
        float dkD = length( vec2( dkAx, dkYm - ( floor( dkYm / dkAbst ) + 0.5 ) * dkAbst ) );
        dkKnopf = 1.0 - smoothstep( KNOPF - 0.0008, KNOPF, dkD );
        dkHf += 0.0012 * dkKnopf * sqrt( max( 0.0, 1.0 - dkD * dkD / ( KNOPF * KNOPF ) ) ) + 0.0004 * dkLeiste;
    }
}
`;

    static FARBE = `
diffuseColor.rgb *= ( 1.0 + uDkBand.y * dkBand ) * ( 1.0 - 0.18 * dkStich ) * ( 1.0 + uDkBand.w * dkKragen ) * ( 1.0 - 0.25 * dkKragenRand )
                    * ( 1.0 - 0.08 * dkLeiste ) * ( 1.0 - 0.3 * dkLeisteRand );
diffuseColor.rgb = mix( diffuseColor.rgb, diffuseColor.rgb * 0.25 + 0.02, dkKnopf );
`;

    static RELIEF = `
{
    vec3 dkDx = dFdx( - vViewPosition );
    vec3 dkDy = dFdy( - vViewPosition );
    vec3 dkR1 = cross( dkDy, normal );
    vec3 dkR2 = cross( normal, dkDx );
    float dkDet = dot( dkDx, dkR1 );
    vec3 dkGrad = sign( dkDet ) * ( dFdx( dkHf ) * dkR1 + dFdy( dkHf ) * dkR2 );
    normal = normalize( abs( dkDet ) * normal - dkGrad );
}
`;

    /** Text hinter `#include <name>` einfügen; null, wenn es die Stelle nicht gibt. */
    static nach(quelle, name, text) {
        const marke = `#include <${name}>`;
        return quelle.includes(marke) ? quelle.replace(marke, () => `${marke}\n${text}`) : null;
    }

    /** Den Shader patchen (Eingriff für `Shaderpatch`): Uniforms `u` anhängen. → Liste der fehlenden Stellen; fehlt eine, bleibt der Shader UNVERÄNDERT
     *  (die Teile hängen aneinander: Farbe und Relief lesen, was der Schnitt rechnet). */
    static patchen(shader, u) {
        Object.assign(shader.uniforms, u);
        const zahl = v => v.toFixed(6);
        const schnitt = DazschnittGLSL.SCHNITT.replaceAll('WULST', zahl(DazschnittGLSL.WULST_M)).replaceAll('KRAGEN', zahl(DazschnittGLSL.KRAGEN_M))
            .replaceAll('KNOPF', zahl(DazschnittGLSL.KNOPF_M));
        const neu = { vertexShader: shader.vertexShader, fragmentShader: shader.fragmentShader };
        const fehlt = [];
        for (const [teil, name, text] of [['vertexShader', 'common', DazschnittGLSL.VERTEX_KOPF], ['vertexShader', 'begin_vertex', DazschnittGLSL.VERTEX],
            ['fragmentShader', 'common', DazschnittGLSL.KOPF.replaceAll('ACHSEL_STEIGUNG', zahl(Dazschnittwerte.ACHSEL_STEIGUNG))
                .replaceAll('ACHSEL_H', zahl(Dazschnittwerte.ACHSEL_H))], ['fragmentShader', 'clipping_planes_fragment', schnitt],
            ['fragmentShader', 'color_fragment', DazschnittGLSL.FARBE], ['fragmentShader', 'normal_fragment_maps', DazschnittGLSL.RELIEF]]) {
            const quelle = DazschnittGLSL.nach(neu[teil], name, text);
            if (quelle === null) fehlt.push(name); else neu[teil] = quelle;
        }
        if (!fehlt.length) Object.assign(shader, neu);
        return fehlt;
    }
}
