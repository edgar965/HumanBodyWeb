/**
 * EigenkleidschnittGLSL — der Fragment-Teil des Shaders eines eigenen Stücks (Stufe K2a, 25.10.2026 spät; Edgar: „es fehlt der Ausschnitt am Hals, der soll z.b. wie
 * bei einem T-shirt sein können, rund mit saum, oder V-förmig“, „ggf. kragen konfiguration mit knöpfen“, „Die Drapierung / faltenbildung müsste ausgefeilter sein“).
 *
 * KANTE JE PIXEL (`kkKante`, Meter, > 0 = Stoff): aus den Körperkoordinaten, die der Vertex-Shader weiterreicht (Höhe h, Anteil t, x der Ruhelage, vorn = cos des
 * Umfangswinkels, Kettenmerkmale) — dieselbe Rechnung für jedes Netz, das diese vier Größen je Punkt hat. Die Kante ist die Nullstelle einer stetigen Funktion,
 * also eine glatte Kurve, keine Treppe aus Dreiecken oder Kettengrenzen:
 *   Oberteil  Saum unten (S − h)·L_Rumpf (nicht an Armen) · Ärmel (Ä − t)·L_Arm (Arm und Rumpf an der Schulter, nicht Beine) · Ausschnitt `kkHals`
 *   Hose      Bund (h − B)·L_Rumpf · Hosenbein (B_L − t)·L_Bein (nur Beine)
 * AUSSCHNITT `kkHals`: Tiefe(x) = Tiefe·Form(|x| ÷ halbe Breite), vorn die gewählte Form, hinten rund, dazwischen nach dem Umfangswinkel überblendet; außerhalb der
 * Breite Tiefe 0 = Halsansatz (der Hals bleibt frei). Formen: 0 rund (Halbellipse), 1 V (gerade), 2 U (flacher Boden, steile Seiten), 3 Boot (fast waagrecht),
 * 4 Stehkragen (Stoff um den Hals bis zur Kragenhöhe). Gemessen wird seit 25.10.2026 nachts ab dem HALSANSATZ je Umfangswinkel (`vKkAnsatz`,
 * `Koerperkoordinatenpunkte.ansatz`), nicht mehr ab der Ebene durch das Halsgelenk — die lag bei DamiraAlt seitlich 5,2 cm darunter, und außerhalb der Breite
 * schnitt der Ausschnitt quer über den Trapezmuskel (Haut oben auf den Schultern, Saumband drumherum).
 * SAUMBAND: wo der Abstand zur Kante unter der Saumbreite liegt — eigene Helligkeit, eine Wulst (Höhe `WULST_M`, über die Normale) und eine Steppnaht bei 80 %;
 * die Ränder des Bands über `fwidth` geglättet.
 * KNOPFLEISTE (nur Oberteil, vorn): Leiste der Breite `uKkKragen.w` vom Ausschnitt abwärts, Knöpfe als gezeichnete Kreise (Radius `KNOPF_M`) mit Wölbung über die
 * Normale — keine eigene Geometrie. Ein umgelegter Polo- oder Hemdkragen braucht eigene Geometrie und ist NICHT gebaut (nächste Stufe).
 * FALTEN: waagrecht (Welle über y der Ruhelage, Phase und Stärke aus Wertrauschen; anfangs über Anteil × Kettenlänge — die sprang an der Kettengrenze und zeichnete
 * dichte Streifen in die Leiste, Mann1); wo die Brücke hängt (`vKkFall.x`, Fall-Hub in m), senkrecht — sie hängen von der Brücke nach unten. Als Normalenstörung über
 * die Bildschirmableitungen wie Threes Bump-Mapping. Maße GESETZT (Augenmaß).
 * SCHULTERFLECKEN (25.10.2026 nachts, Edgar: hellere und dunklere Flecken oben an den Schultern): Die waagrechte Welle läuft über y der Ruhelage — auf der fast
 * waagrechten Schulteroberseite ändert sich y kaum, dort blieb nur die Rauschphase übrig und zeichnete Flecken statt Falten, unter dem fast streifend
 * einfallenden Hauptlicht (von vorn, 0,4/1,6/6,5) als hell/dunkel. Seither verschwinden die Falten, wo die Ruhenormale nach oben zeigt (`vKkOben` 0,45…0,75).
 * Gemessen an DamiraAlt (`ProjektTemp/_wegwerf/eigenkleider/k2b_hilfen.js`, `K.diff`: Bildpunkte, die sich zwischen Falten 35 % und 0 um mehr als 6 ändern):
 * Ansicht von oben 12.178 → 4.850, von vorn 48.708 → 34.629, die Schulteroberseiten danach ohne Änderung. Die Brücke wirkt dort nicht (Differenzbild
 * Ausbreitung 30 cm gegen 0: Schultern unverändert), Haut sticht nicht durch (Differenzbild mit/ohne Körper aus der Kamera der Seite: Stoff ohne Änderung).
 * Der zweite Grund für helle Stellen oben an den Schultern war freiliegende Haut über dem Trapezmuskel (Ausschnitt ab Halsansatz, siehe AUSSCHNITT).
 * RELIEF (`uKkRelief`, Stoffregler „Relief“): Faktor auf Wulst, Steppnaht, Knöpfe und Falten — wie „Relief“ am Daz-Stück die eigene Normalkarte.
 * SOCKEN (`uKkArt` 3): Bündchen (t − B)·L_Bein an Beinpunkten; der Fuß ist ganz Stoff.
 */
export class EigenkleidschnittGLSL {

    static WULST_M = 0.0012;
    static KNOPF_M = 0.0055;
    static FALTENABSTAND_M = 0.03;
    static FALTENTIEFE_M = 0.0015;

    static KOPF = `
uniform float uKkArt;
uniform vec4 uKkSaum;
uniform vec4 uKkHals;
uniform vec4 uKkKragen;
uniform vec4 uKkBand;
uniform vec3 uKkLaenge;
uniform float uKkFalten;
uniform float uKkFaltenAbstand;
uniform float uKkFaltenTiefe;
uniform float uKkRelief;
varying vec4 vKkKoord;
varying vec4 vKkKette;
varying vec4 vKkFall;
varying vec3 vKkLage;
varying float vKkHub;
varying float vKkOben;
varying float vKkAnsatz;
float kkHash( vec3 p ) {
    p = fract( p * 0.3183099 + 0.1 );
    p *= 17.0;
    return fract( p.x * p.y * p.z * ( p.x + p.y + p.z ) );
}
float kkRauschen( vec3 x ) {
    vec3 i = floor( x );
    vec3 f = fract( x );
    f = f * f * ( 3.0 - 2.0 * f );
    return mix( mix( mix( kkHash( i ), kkHash( i + vec3( 1.0, 0.0, 0.0 ) ), f.x ), mix( kkHash( i + vec3( 0.0, 1.0, 0.0 ) ), kkHash( i + vec3( 1.0, 1.0, 0.0 ) ), f.x ), f.y ),
                mix( mix( kkHash( i + vec3( 0.0, 0.0, 1.0 ) ), kkHash( i + vec3( 1.0, 0.0, 1.0 ) ), f.x ), mix( kkHash( i + vec3( 0.0, 1.0, 1.0 ) ), kkHash( i + vec3( 1.0 ) ), f.x ), f.y ), f.z );
}
float kkForm( float u, float form ) {
    float v = clamp( u, 0.0, 1.0 );
    float s = form < 0.5 ? sqrt( 1.0 - v * v ) : ( form < 1.5 ? 1.0 - v : ( form < 2.5 ? sqrt( 1.0 - v * v * v * v ) : 1.0 - pow( v, 6.0 ) ) );
    return u >= 1.0 ? 0.0 : s;
}
float kkHals( float h, float x, float vorn ) {
    float u = abs( x ) / max( 0.5 * uKkHals.w, 0.001 );
    float tiefe = mix( uKkHals.z * kkForm( u, 0.0 ), uKkHals.y * kkForm( u, uKkHals.x ), smoothstep( -0.35, 0.35, vorn ) );
    float ab = h - vKkAnsatz;                                  // Höhe unter dem Halsansatz dieses Umfangswinkels
    return uKkHals.x > 3.5 ? ab * uKkLaenge.x + uKkKragen.x : ( ab - tiefe ) * uKkLaenge.x;
}
float kkKante( float h, float t, float x, float vorn, vec4 k ) {
    float f = 1.0;
    if ( uKkArt < 1.5 ) {
        if ( k.y < 0.5 ) f = min( f, ( uKkSaum.x - h ) * uKkLaenge.x );
        if ( k.z < 0.5 ) f = min( f, ( uKkSaum.y - t ) * uKkLaenge.y );
        f = min( f, kkHals( h, x, vorn ) );
        if ( k.x + k.y + k.z + k.w < 0.5 ) f = -1.0;
    } else if ( uKkArt < 2.5 ) {
        f = min( f, ( h - uKkSaum.x ) * uKkLaenge.x );
        if ( k.z > 0.5 ) f = min( f, ( uKkSaum.y - t ) * uKkLaenge.z );
        if ( k.x + k.z < 0.5 ) f = -1.0;
    } else {
        if ( k.z > 0.5 ) f = min( f, ( t - uKkSaum.x ) * uKkLaenge.z );      // Socken: Bündchen; k.w = Fuß (siehe EigenkleidGLSL)
        if ( k.z + k.w < 0.5 ) f = -1.0;
    }
    return f;
}
`;

    static SCHNITT = `
float kkF = kkKante( vKkKoord.x, vKkKoord.y, vKkKoord.z, vKkKoord.w, vKkKette );
if ( kkF < 0.0 ) discard;
if ( ! gl_FrontFacing && vKkHub > 0.002 ) discard;     // über einer überhängenden Mulde faltet die waagrechte Projektion Dreiecke um — die Vorderseiten decken die Stelle
float kkAa = max( fwidth( kkF ), 1e-5 );
float kkB = uKkBand.x;
float kkBand = kkB > 0.0 ? 1.0 - smoothstep( kkB - kkAa, kkB + kkAa, kkF ) : 0.0;
float kkStich = kkB > 0.0 ? 1.0 - smoothstep( 0.0, 1.5 * kkAa, abs( kkF - 0.8 * kkB ) ) : 0.0;
float kkHf = kkBand * WULST * sin( 3.14159265 * clamp( kkF / max( kkB, 1e-4 ), 0.0, 1.0 ) );
float kkLeiste = 0.0;
float kkLeisteRand = 0.0;
float kkKnopf = 0.0;
if ( uKkArt < 1.5 && uKkKragen.z > 0.5 && uKkKragen.y > 0.0 && vKkKoord.w > 0.3 ) {
    float kkYm = ( vKkKoord.x - vKkAnsatz - ( uKkHals.x > 3.5 ? 0.0 : uKkHals.y ) ) * uKkLaenge.x;
    float kkLang = uKkKragen.y * uKkLaenge.x;
    float kkW = 0.5 * uKkKragen.w;
    float kkAx = abs( vKkKoord.z );
    if ( kkYm > -0.004 && kkYm < kkLang ) {
        kkLeiste = 1.0 - smoothstep( kkW - 0.0008, kkW + 0.0008, kkAx );
        kkLeisteRand = 1.0 - smoothstep( 0.0003, 0.0009, abs( kkAx - kkW + 0.0015 ) );
        float kkAbst = kkLang / uKkKragen.z;
        float kkD = length( vec2( kkAx, kkYm - ( floor( kkYm / kkAbst ) + 0.5 ) * kkAbst ) );
        kkKnopf = 1.0 - smoothstep( KNOPF - 0.0008, KNOPF, kkD );
        kkHf += 0.0012 * kkKnopf * sqrt( max( 0.0, 1.0 - kkD * kkD / ( KNOPF * KNOPF ) ) ) + 0.0004 * kkLeiste;
    }
}
if ( uKkFalten > 0.0 ) {
    float kkWaag = 1.0 - smoothstep( 0.45, 0.75, vKkOben );          // nach oben zeigende Fläche (Schulteroberseite): keine Falten, siehe Kopf
    float kkHang = smoothstep( 0.002, 0.02, vKkFall.x );
    float kkQuer = sin( 6.2831853 * ( vKkFall.w / uKkFaltenAbstand + 1.4 * kkRauschen( vKkLage * 22.0 ) ) ) * smoothstep( 0.2, 0.8, kkRauschen( vKkLage * 9.0 + 7.3 ) );
    float kkU = vKkLage.x * abs( vKkFall.z ) + vKkLage.z * abs( vKkFall.y );
    float kkSenk = sin( 6.2831853 * ( kkU / ( 0.8 * uKkFaltenAbstand ) + 0.8 * kkRauschen( vKkLage * vec3( 30.0, 5.0, 30.0 ) ) ) );
    kkHf += uKkFalten * uKkFaltenTiefe * mix( kkQuer, kkSenk * ( 0.6 + 0.8 * kkHang ), kkHang ) * ( 1.0 - kkBand ) * kkWaag;
}
kkHf *= uKkRelief;
`;

    static FARBE = `
diffuseColor.rgb *= ( 1.0 + uKkBand.y * kkBand ) * ( 1.0 - 0.18 * kkStich ) * ( 1.0 - 0.08 * kkLeiste ) * ( 1.0 - 0.3 * kkLeisteRand );
diffuseColor.rgb = mix( diffuseColor.rgb, diffuseColor.rgb * 0.25 + 0.02, kkKnopf );
`;

    static RELIEF = `
{
    vec3 kkDx = dFdx( - vViewPosition );
    vec3 kkDy = dFdy( - vViewPosition );
    vec3 kkR1 = cross( kkDy, normal );
    vec3 kkR2 = cross( normal, kkDx );
    float kkDet = dot( kkDx, kkR1 );
    vec3 kkGrad = sign( kkDet ) * ( dFdx( kkHf ) * kkR1 + dFdy( kkHf ) * kkR2 );
    normal = normalize( abs( kkDet ) * normal - kkGrad );
}
`;

    /** `[[#include-Name, Text]]` für `EigenkleidGLSL.patchen` — in dieser Reihenfolge im Fragment-Shader. */
    static get STELLEN() {
        const zahl = v => v.toFixed(6);
        const schnitt = EigenkleidschnittGLSL.SCHNITT.replaceAll('WULST', zahl(EigenkleidschnittGLSL.WULST_M)).replaceAll('KNOPF', zahl(EigenkleidschnittGLSL.KNOPF_M));
        return [['common', EigenkleidschnittGLSL.KOPF], ['clipping_planes_fragment', schnitt], ['color_fragment', EigenkleidschnittGLSL.FARBE],
            ['normal_fragment_maps', EigenkleidschnittGLSL.RELIEF]];
    }
}
