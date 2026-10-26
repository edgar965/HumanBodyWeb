import { EigenkleidGLSL } from './eigenkleidglsl.js';

/**
 * EigenkragenGLSL — der Vertex-Teil des Kragens (`Eigenkragen`, 25.10.2026 nachts). Der Fragment-Teil ist der gewöhnliche Standard-Shader plus Stoff (`Stoffshader`).
 *
 * ZWEI SCHRITTE vor dem Skinning, in der Ruhelage: (1) der Randpunkt wird wie die Schale verschoben — derselbe Text (`EigenkleidGLSL.VERTEX`) mit denselben Uniforms
 * des Oberteils, also derselbe Sitz und dieselbe Brücke: der Kragen setzt genau auf der Kante der Schale an; (2) `kgVersatz` legt den Kragenpunkt darauf, aus dem
 * Anteil r quer zum Rand und den Richtungen der Spalte (`Eigenkragengeometrie`):
 *   Stehkragen   r·Höhe den Hals hinauf (u = Richtung der Sehne `kgOben`), Abstand zum Hals (q = Normale senkrecht zu u) über das erste Drittel eingeblendet.
 *   umgelegt     Steg (`STEG` × Höhe) hinauf bis r = `R_STEG`, Falz als Halbkreis (`RUNDUNG`) bis `R_FALZ`, dann hinab: erst über dem Steg (außen um Abstand + 2·Rundung),
 *                unter dem Rand auf der Haut entlang (`kgF1…3`, Polygonzug, darüber hinaus verlängert) mit `LUFT` über dem Stoff. Länge des umgelegten Teils = Höhe +
 *                Spitzenlänge × Gewicht der Spitze (an den vorderen Enden 1) — so entstehen die Spitzen.
 * Die Normale folgt der Fläche (Steg +q, Falz dreht über u nach −q, unten −q senkrecht zur Laufrichtung) — die Rückseite dreht Three über `faceDirection`.
 * Maße GESETZT (Augenmaß), nicht gemessen.
 */
export class EigenkragenGLSL {

    static SCHLUESSEL = 'eigenkragen-1';
    static STEG = 0.55;
    static R_STEG = 0.3;
    static R_FALZ = 0.42;
    static RUNDUNG_M = 0.0025;
    static LUFT_M = 0.002;

    static get KOPF() {
        const z = v => v.toFixed(4);
        return `${EigenkleidGLSL.VERTEX_KOPF}
attribute vec4 kgLage;
attribute vec3 kgOben;
attribute vec3 kgF1;
attribute vec3 kgF2;
attribute vec3 kgF3;
uniform vec4 uKgGestalt;
vec3 kgFall( float e ) {
    float e1 = length( kgF1 ), e2 = e1 + length( kgF2 - kgF1 ), e3 = e2 + length( kgF3 - kgF2 );
    if ( e <= e1 ) return kgF1 * ( e / max( e1, 1e-5 ) );
    if ( e <= e2 ) return mix( kgF1, kgF2, ( e - e1 ) / max( e2 - e1, 1e-5 ) );
    return mix( kgF2, kgF3, ( e - e2 ) / max( e3 - e2, 1e-5 ) );
}
vec3 kgVersatz( vec3 n, out vec3 normale ) {
    vec3 u = dot( kgOben, kgOben ) > 1e-10 ? normalize( kgOben ) : vec3( 0.0, 1.0, 0.0 );     // Sehne den Hals hinauf
    vec3 q = n - dot( n, u ) * u;                                                                 // quer dazu nach außen
    q = dot( q, q ) > 1e-8 ? normalize( q ) : n;
    float r = kgLage.x, hoehe = uKgGestalt.y, abst = uKgGestalt.w;
    normale = q;
    if ( uKgGestalt.x < 1.5 ) return u * ( r * hoehe ) + q * ( abst * smoothstep( 0.0, 0.3, r ) );
    float steg = ${z(EigenkragenGLSL.STEG)} * hoehe, rho = ${z(EigenkragenGLSL.RUNDUNG_M)};
    if ( r < ${z(EigenkragenGLSL.R_STEG)} ) {
        float d = r / ${z(EigenkragenGLSL.R_STEG)};
        return u * ( d * steg ) + q * ( abst * smoothstep( 0.0, 0.3, d ) );
    }
    if ( r < ${z(EigenkragenGLSL.R_FALZ)} ) {
        float th = 3.14159265 * ( r - ${z(EigenkragenGLSL.R_STEG)} ) / ${z(EigenkragenGLSL.R_FALZ - EigenkragenGLSL.R_STEG)};
        normale = normalize( q * cos( th ) + u * sin( th ) );
        return u * ( steg + rho * sin( th ) ) + q * ( abst + rho * ( 1.0 - cos( th ) ) );
    }
    float dd = ( r - ${z(EigenkragenGLSL.R_FALZ)} ) / ${z(1 - EigenkragenGLSL.R_FALZ)} * ( hoehe + uKgGestalt.z * kgLage.y );
    float aussen = abst + 2.0 * rho;
    normale = -q;
    if ( dd <= steg ) return u * ( steg - dd ) + q * aussen;
    float e = dd - steg;
    vec3 p = kgFall( e );
    vec3 lauf = kgFall( e + 0.002 ) - p;
    lauf = dot( lauf, lauf ) > 1e-12 ? normalize( lauf ) : -u;
    vec3 quer = n - dot( n, lauf ) * lauf;
    quer = dot( quer, quer ) > 1e-8 ? normalize( quer ) : n;
    normale = -quer;
    return p + mix( q * aussen, quer * ${z(EigenkragenGLSL.LUFT_M)}, smoothstep( 0.0, 0.015, e ) );
}
`;
    }

    /** Nach `morphnormal_vertex`: die verschweißte Ruhenormale (wie die Schale), dann Versatz und Normale des Kragenpunkts. */
    static NORMALE = `
if ( dot( kkNormal, kkNormal ) > 0.25 ) objectNormal = kkNormal;
vec3 kkNormale = objectNormal;
vec3 kgNormale;
vec3 kgV = kgVersatz( normalize( kkNormale ), kgNormale );
objectNormal = kgNormale;
`;

    /** Den Shader patchen; `u` = Uniforms des Oberteils (Sitz, Brücke …) und des Kragens (`uKgGestalt`). → fehlende Stellen. */
    static patchen(shader, u) {
        Object.assign(shader.uniforms, EigenkleidGLSL.VORGABEN(), u);
        const fehlt = [];
        const stellen = [['common', EigenkragenGLSL.KOPF], ['morphnormal_vertex', EigenkragenGLSL.NORMALE],
            ['morphtarget_vertex', `${EigenkleidGLSL.VERTEX}\ntransformed += kgV;\n`]];
        for (const [name, text] of stellen) {
            const neu = EigenkleidGLSL.nach(shader.vertexShader, name, text);
            if (neu === null) fehlt.push(name); else shader.vertexShader = neu;
        }
        return fehlt;
    }
}
