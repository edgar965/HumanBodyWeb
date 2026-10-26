import { EigenkleidschnittGLSL } from './eigenkleidschnitt.js';

/**
 * EigenkleidGLSL — der Vertex-Teil des Shaders eines eigenen Stücks und das Einsetzen in `MeshStandardMaterial` (Stufe K2a, 25.10.2026). Der Fragment-Teil (Säume,
 * Ausschnitt, Saumband, Knopfleiste, Falten) steht in `EigenkleidschnittGLSL`.
 *
 * KÖRPERKOORDINATEN je Punkt aus dem Attribut `kkKoord` (Kette, Anteil vorzeichenbehaftet, Höhe, Winkel — `Koerperkoordinatenpunkte`: die Karte
 * `G9koerperkoordinaten` an der UV des Punkts gelesen, punktgenau wie `texelFetch`, und an UV-Nähten verschweißt). Bis 25.10. spät las der Vertex-Shader die Karte
 * selbst (`texelFetch`); dann bekamen die Doppel einer Naht verschiedene Ketten und die Schale riss auf (Mann1, Gesäß und Kreuz). Ein Attribut ist zugleich die
 * stückunabhängige Schnittstelle: jedes Netz mit `kkKoord` (+ `kkBruecke*`) kann diesen Shader tragen. Weitergegeben als Varyings — geschnitten wird JE PIXEL an
 * der Kurve (Edgar 25.10. spät: Halsrand „zackig ausgefranst“; vorher entschied jeder Punkt, und die Kante folgte den Dreiecken und Kettengrenzen).
 * SITZ (m, `uKkSitz`) je Punkt: Oberteil Rumpf und Beinpunkte nach Höhe oben → Mitte (0,1…0,5) → unten (0,5…0,95), Arm von „oben“ in den Ärmelwert (Anteil
 * 0…0,15); Hose Bund → Gesäß (Höhe Bund…Bund + 0,15), Bein von dort in den Beinwert erst ab Anteil 0,15…0,35. Stetig über die Kettengrenzen — ein Sprung im Sitz
 * zwischen Rumpf- und Beinpunkten zeichnete eine Treppe in die Hose (Mann1, Leiste). Socken (`uKkArt` 3, 25.10.2026 nachts): Schaft → Fuß über Beinanteil 0,9…1.
 * `vKkOben` (y der Ruhenormale) sagt dem Fragment-Teil, wo die Fläche nach oben zeigt (Schulteroberseite: dort keine waagrechten Falten, `EigenkleidschnittGLSL`).
 * BRÜCKE (`kkBruecke`, `kkBrueckeB`, Attribute der Schale, `Eigenkleidbruecke`; Regler wie der Drapierer `uKkBruecke` = Abstand m, Ausbreitung m, Glättung, Fall m je m):
 * `kkHub` blendet Hüllen- und Fallanteil nach dem Weg zur Stütze aus (über 30…100 % der Ausbreitung; Ausbreitung 0 = liegt an) und mischt Zelt und Rund nach der
 * Glättung; die Hose nimmt keinen Fall. Der Punkt wandert um den Hub waagrecht nach außen und entlang der Ruhenormale um max(Sitz − Hub, Abstand) — über der Brücke
 * liegt der Stoff also um „Abstand“ darüber, sonst im Sitz; nie unter 1 mm.
 * Beides VOR dem Skinning, mit der Ruhenormale (`objectNormal` nach `morphnormal_vertex`, bevor `skinnormal_vertex` sie dreht) — die Schale folgt jeder Haltung.
 */
export class EigenkleidGLSL {

    static SCHLUESSEL = 'eigenkleid-k3-7';

    /** Uniforms, die nach K2a dazukamen — `patchen` setzt sie, wenn der Rufer sie nicht mitbringt (ein älterer Rufer bekommt so dasselbe Bild wie vorher). */
    static VORGABEN() {
        return { uKkRelief: { value: 1 }, uKkAermelform: { value: [0, 0, 0, 0] } };
    }

    static VERTEX_KOPF = `
attribute vec4 kkKoord;
attribute vec3 kkNormal;
uniform vec3 uKkLaenge;
uniform float uKkArt;
uniform vec4 uKkSaum;
uniform vec4 uKkSitz;
uniform vec4 uKkAermelform;
uniform vec4 uKkBand;
uniform vec4 uKkBruecke;
uniform vec2 uKkLage;
attribute vec4 kkBruecke;
attribute vec4 kkBrueckeB;
attribute vec4 kkBrueckeC;
varying vec4 vKkKoord;
varying vec4 vKkKette;
varying vec4 vKkFall;
varying vec3 vKkLage;
varying float vKkHub;
varying float vKkOben;
attribute float kkAnsatz;
varying float vKkAnsatz;
/* (Hub m, Anteil des Falls daran) — siehe Kopf von eigenkleidglsl.js. n = die Ruhenormale: die Hülle ist waagrecht gerechnet, auf Flächen, die nach oben zeigen
   (Schulteroberseite), hätte sie keinen Sinn — dort blendet sie aus (im Chrome gesehen: helle Flecken zwischen Hals und Schulter, ein Zelt über dem Trapezmuskel).
   Nach unten zeigende Flächen (unter der Brust, unter dem Gesäß) behalten sie — dort hängt der Stoff. */
vec2 kkHub( vec3 n ) {
    float a = max( uKkBruecke.y, 0.001 );
    float seitlich = 1.0 - smoothstep( 0.35, 0.65, n.y / max( length( n ), 1e-6 ) );    // nur nach OBEN zeigende Flächen; unter der Brust (nach unten) bleibt sie
    float wH = 1.0 - smoothstep( 0.3 * a, a, kkBrueckeB.z );
    float wF = 1.0 - smoothstep( 0.3 * a, a, kkBrueckeB.w );
    float oben = uKkArt < 1.5 ? 1.0 : 0.0;
    float zeltF = max( kkBruecke.w - kkBruecke.z, 0.0 ) * wF * oben;
    float rundF = max( kkBrueckeB.y - kkBrueckeB.x, 0.0 ) * wF * oben;
    float an = uKkBruecke.y > 0.0005 ? 1.0 : 0.0;
    // Kleid (uKkAermelform.w = 1): an der Taillennaht liegt das Oberteil an, sonst stünde es über dem Bund des Rockteils ab (letzte 8 % Rumpf über dem Saum)
    float kkNaht = uKkAermelform.w > 0.5 && floor( kkKoord.x + 0.5 ) == 1.0 ? 1.0 - smoothstep( uKkSaum.x - 0.08, uKkSaum.x - 0.01, kkKoord.z ) : 1.0;
    // waagrechte Hülle nur auf seitlichen Flächen; der senkrechte Teil (Zelt über, Fall unter der Wölbung) auch oben auf der Brust — dort spannt er gerade
    float kkF = mix( zeltF, rundF, uKkBruecke.z );
    return an * kkNaht * vec2( mix( kkBruecke.z, kkBrueckeB.x, uKkBruecke.z ) * wH * seitlich + kkF, kkF );
}
`;

    /**
     * Die an UV-Nähten verschweißte Ruhenormale (`kkNormal`) nehmen und merken (für den Sitz) — und für das LICHT die Normale der Brücke einblenden: Über einer Mulde liegt der Stoff auf der Hülle, ihre Normale ist die
     * waagrechte Hubrichtung, im Fall darunter um den Fall nach unten geneigt. Ohne das zeichnete das Licht die Haut darunter nach (im Chrome gesehen: Unterbrustfalte
     * und Brustkontur auf dem Stoff, obwohl die Schale sie überspannte).
     */
    static get VERTEX_NORMALE() {
        return `
if ( dot( kkNormal, kkNormal ) > 0.25 ) objectNormal = kkNormal;      // an UV-Nähten verschweißt (Koerperkoordinatenpunkte.normalen)
vec3 kkNormale = objectNormal;
{
    vec2 kkHubN = kkHub( objectNormal );
    vec3 kkDirN = vec3( kkBruecke.x, 0.0, kkBruecke.y );
    // Neigung dr/dy der Stofffläche (Zelt/rund) nur, wo der senkrechte Teil (Zelt, Fall) trägt; die waagrechte Hülle allein bleibt waagrecht wie bis K3
    float kkSenk = smoothstep( 0.0, 0.002, kkHubN.y );
    vec3 kkNb = normalize( kkDirN - vec3( 0.0, mix( kkBrueckeC.x, kkBrueckeC.y, uKkBruecke.z ) * kkSenk, 0.0 ) );
    // ganz die Normale der Stofffläche: im senkrechten Teil ab 2 mm (darunter zeichnete die Hautnormale die Brustunterseite ins Licht), sonst wie bis K3 ab 25 mm —
    // 25.10.2026 nachts einmal überall 1 mm: dunkle Streifen auf Schulter und Kragen (Edgar, mit Bild)
    // nach UNTEN gewandte Haut (Brustunterseite, unter dem Gesäß) ebenfalls ab 2 mm — dort trägt oft die waagrechte Hülle, und die Hautnormale zeichnete die
    // Unterkante der Brust (T-Shirt, im Chrome gesehen 26.10.2026 0:35); die Schulteroberseite zeigt nach oben und bleibt bei 25 mm
    float kkUnten = ( 1.0 - smoothstep( -0.5, -0.15, objectNormal.y / max( length( objectNormal ), 1e-6 ) ) ) * smoothstep( 0.0, 0.002, kkHubN.x );
    float kkGanz = max( max( smoothstep( 0.0, 0.025, kkHubN.x ), kkSenk ), kkUnten );
    if ( dot( kkDirN, kkDirN ) > 0.5 ) objectNormal = normalize( mix( objectNormal, kkNb, kkGanz ) );
}
`;
    }

    static VERTEX = `
{
    float kkKette = floor( kkKoord.x + 0.5 );
    float kkT = kkKoord.y;
    float kkH = kkKoord.z;
    float kkVorn = cos( 6.2831853 * kkKoord.w );
    vec4 kkK = vec4( abs( kkKette - 1.0 ) < 0.5 ? 1.0 : 0.0, kkKette > 1.5 && kkKette < 3.5 ? 1.0 : 0.0,
                     kkKette > 3.5 && kkKette < 5.5 ? 1.0 : 0.0, kkKette > 5.5 && kkKette < 7.5 ? 1.0 : 0.0 );    // w: Hals UND Kopf (vorn führt der Kopf den Hals)
    float kkSitz;
    if ( uKkArt < 1.5 ) {
        float kkRs = kkH < 0.5 ? mix( uKkSitz.x, uKkSitz.y, smoothstep( 0.1, 0.5, kkH ) ) : mix( uKkSitz.y, uKkSitz.z, smoothstep( 0.5, 0.95, kkH ) );
        kkSitz = kkK.y > 0.5 ? mix( uKkSitz.x, uKkSitz.w, smoothstep( 0.0, 0.15, kkT ) ) : kkRs;      // Beinpunkte (Gesäß) nach Höhe wie der Rumpf: stetig an der Kettengrenze
        // Ärmel weiter zum Saum (quadratisch: hängt von der Schulter) und Längsfalten rundum, zum Saum tiefer (Edgar, 25.10.2026 nachts: „an den Ärmeln fehlt die
        // Drapierung - mehr falten, nicht so eng an den Körper“); uKkAermelform = (Weite m, Falten Anzahl, Tiefe m, –)
        float kkA = kkK.y > 0.5 ? clamp( kkT / max( uKkSaum.y, 0.05 ), 0.0, 1.0 ) : 0.0;
        kkSitz += uKkAermelform.x * kkA * kkA + uKkAermelform.z * kkA * ( 0.5 + 0.5 * sin( 6.2831853 * uKkAermelform.y * kkKoord.w ) );
    } else if ( uKkArt < 2.5 ) {
        float kkRh = mix( uKkSitz.x, uKkSitz.y, smoothstep( uKkSaum.x, uKkSaum.x + 0.15, kkH ) );
        kkSitz = kkK.z > 0.5 ? mix( kkRh, uKkSitz.z, smoothstep( 0.15, 0.35, kkT ) ) : kkRh;          // das Bein erst unter der Grenzzone (Anteil 0…0,14) zum Beinwert
    } else {
        // Socken: der Fuß (Ketten 10, 11) ist ganz bedeckt; seine Punkte tragen keinen Beinanteil (OHNE = −0,5), also bekommen sie einen hinter dem Knöchel —
        // sonst liefe der Anteil über die Dreiecke an der Grenze Bein/Fuß von 1 auf −0,5 und der Schnitt am Bündchen risse dort ein Band heraus.
        // kkK.w heißt bei Socken „Fuß“ (beim Oberteil Hals und Kopf) — der Fragment-Teil liest es so.
        kkK.w = kkKette > 9.5 && kkKette < 11.5 ? 1.0 : 0.0;
        kkT = kkK.w > 0.5 ? 1.05 : kkT;
        kkSitz = mix( uKkSitz.y, uKkSitz.x, smoothstep( 0.9, 1.0, kkT ) );
    }
    if ( uKkLage.x > 0.0 && kkH >= uKkLage.y && kkK.y < 0.5 ) kkSitz = max( kkSitz, uKkLage.x );     // Oberteil über der Hose: nie unter ihr
    vec3 kkN = normalize( kkNormale );
    vec3 kkRichtung = vec3( kkBruecke.x, 0.0, kkBruecke.y );
    vec2 kkHubV = kkHub( kkNormale );
    float kkHub = kkHubV.x;
    vKkKoord = vec4( kkH, kkT, position.x, kkVorn );
    vKkKette = kkK;
    vKkFall = vec4( kkHubV.y, kkBruecke.x, kkBruecke.y, position.y );     // Faltenkoordinate: y der Ruhelage — stetig über alle Kettengrenzen
    vKkLage = position;
    vKkHub = kkHub;
    vKkOben = kkN.y;
    vKkAnsatz = kkAnsatz;            // Höhe des Halsansatzes (Koerperkoordinatenpunkte.ansatz); fehlt das Attribut, liefert WebGL 0 = wie bis K2a
    float kkUeber = uKkBruecke.x * smoothstep( 0.0, 0.003, kkHub );
    transformed += kkRichtung * kkHub + kkN * max( max( kkSitz - kkHub * max( dot( kkN, kkRichtung ), 0.0 ), kkUeber ), 0.001 );
}
`;

    /** Text hinter `#include <name>` einfügen; null, wenn es die Stelle nicht gibt (andere Three-Fassung) — der Rufer meldet es. */
    static nach(quelle, name, text) {
        const marke = `#include <${name}>`;
        return quelle.includes(marke) ? quelle.replace(marke, () => `${marke}\n${text}`) : null;
    }

    /**
     * Den Shader patchen (`onBeforeCompile`): Uniforms des Stücks (`u`). → Liste der fehlenden Stellen (leer = alles eingesetzt).
     */
    static patchen(shader, u) {
        Object.assign(shader.uniforms, EigenkleidGLSL.VORGABEN(), u);
        const fehlt = [];
        const v = [['common', EigenkleidGLSL.VERTEX_KOPF], ['morphnormal_vertex', EigenkleidGLSL.VERTEX_NORMALE], ['morphtarget_vertex', EigenkleidGLSL.VERTEX]];
        for (const [name, text] of v) {
            const neu = EigenkleidGLSL.nach(shader.vertexShader, name, text);
            if (neu === null) fehlt.push(name); else shader.vertexShader = neu;
        }
        for (const [name, text] of EigenkleidschnittGLSL.STELLEN) {
            const neu = EigenkleidGLSL.nach(shader.fragmentShader, name, text);
            if (neu === null) fehlt.push(name); else shader.fragmentShader = neu;
        }
        return fehlt;
    }
}
