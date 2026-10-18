import { Shaderpatch } from './shaderpatch.js';

/**
 * Genesis9ergrauen — graue Haare und Brauen (17.10.2026, Edgar: „Hautebenen … graue Haare"; Tabelle 5 in `genesis9-alter.md`).
 *
 * `anteil` (0…1) ist der Anteil der STRÄHNEN, die grau-weiß sind: jede Strähne hat eine feste Zufallszahl (aus ihrer Nummer, nie aus dem Lauf — dieselbe Einstellung
 * zeigt dieselben Strähnen, sonst flackerte das Haar bei jedem Reglerzug); sie ist grau, wenn ihre Zahl unter dem Anteil liegt. Echtes Ergrauen beginnt an der Wurzel:
 * Strähnen knapp über der Schwelle sind nur im Wurzelbereich grau.
 *
 * ZWEI WEGE, je nachdem, wie das Haar gezeichnet wird:
 * - STRÄHNEN (`Genesis9strang`: Linien mit Punktfarben, `material.vertexColors`): die Punktfarben werden aus den gemerkten Originalen neu gerechnet. Die Strähnen sind die
 *   Zusammenhangskomponenten der Segmente (`[a, b, b]`); der Rang eines Punkts entlang der Strähne ist seine Reihenfolge nach Punktnummer (Wurzel zuerst — so schreibt
 *   `Genesis9/strang.py` sie; nicht an einer Frisur mit anderer Reihenfolge geprüft).
 * - KARTEN (Haarkarten mit Textur oder Alphakarte): ein Shaderzusatz mischt die Farbe zu Grau; eine Zufallszahl je Zelle der Kartenkoordinate (70 × 70 je UV) entscheidet,
 *   welche Stellen grau sind — die Karten haben keine Strähnennummer, also Flecken statt ganzer Strähnen. Ganz ohne Kartenkoordinate wird die Farbe um `anteil · 0,7` zu Grau gemischt.
 *
 * Grau ist `luma · 0,3 + 0,5` (linear): dunkles Haar wird Silber, helles bleibt hell. Gesetzt, nach Augenmaß.
 */
export class Genesis9ergrauen {

    /** Breite der Wurzelzone über der Schwelle (Zufallszahl) und Anteil der Strähnenlänge, bis zu dem sie grau ist. */
    static WURZELZONE = 0.2;
    static WURZELLAENGE = 0.5;

    /** Haare (Stücke der Art `haar`) und Brauen der Figur. */
    static netze(inst) {
        const haar = Object.values(inst?.clothMeshes || {}).filter(n => n?.userData?.art === 'haar');
        return inst?.anhangNetze?.brauen ? [...haar, inst.anhangNetze.brauen] : haar;
    }

    static anwenden(inst, anteil) {
        for (const netz of Genesis9ergrauen.netze(inst)) Genesis9ergrauen._netz(netz, anteil);
    }

    static _netz(netz, anteil) {
        const material = [].concat(netz.material).filter(Boolean);
        const farben = netz.geometry?.attributes?.color;
        if (farben && material.some(m => m.vertexColors)) Genesis9ergrauen._straehnen(netz.geometry, farben, anteil);
        for (const m of material) if (!m.vertexColors) Genesis9ergrauen._karte(m, anteil);
    }

    /** Eine feste Zufallszahl 0…1 zu einer Nummer. */
    static zufall(n) {
        const x = Math.sin(n * 12.9898 + 78.233) * 43758.5453;
        return x - Math.floor(x);
    }

    // ----------------------------------------------------------- Strähnen

    static _straehnen(geo, farben, anteil) {
        const daten = geo.userData;
        if (anteil <= 0 && !daten.ergrauenOriginal) return;           // nie grau gewesen: nichts zu tun, nichts zu merken
        if (!daten.ergrauenOriginal) {
            daten.ergrauenOriginal = Float32Array.from(farben.array);
            daten.ergrauenStrang = Genesis9ergrauen.strangnummern(geo);
        }
        if (daten.ergrauenAnteil === anteil) return;
        daten.ergrauenAnteil = anteil;
        const { id, rang } = daten.ergrauenStrang;
        const orig = daten.ergrauenOriginal;
        const aus = farben.array;
        const zone = Genesis9ergrauen.WURZELZONE;
        for (let p = 0; p < id.length; p++) {
            const r = Genesis9ergrauen.zufall(id[p]);
            let g = 0;
            if (r < anteil) g = 1;
            else if (anteil > 0 && r < anteil + zone && rang[p] < ((anteil + zone - r) / zone) * Genesis9ergrauen.WURZELLAENGE) g = 1;
            const luma = 0.2126 * orig[p * 3] + 0.7152 * orig[p * 3 + 1] + 0.0722 * orig[p * 3 + 2];
            const grau = luma * 0.3 + 0.5;
            for (let k = 0; k < 3; k++) aus[p * 3 + k] = orig[p * 3 + k] + (grau - orig[p * 3 + k]) * g;
        }
        farben.needsUpdate = true;
    }

    /** `{id (Strähne je Punkt), rang (0 Wurzel … 1 Spitze je Punkt)}` aus den Segmenten `[a, b, b]`. */
    static strangnummern(geo) {
        const n = geo.attributes.position.count;
        const index = geo.index.array;
        const eltern = new Int32Array(n).map((_, i) => i);
        const wurzel = i => { while (eltern[i] !== i) { eltern[i] = eltern[eltern[i]]; i = eltern[i]; } return i; };
        for (let t = 0; t + 1 < index.length; t += 3) {
            const a = wurzel(index[t]);
            const b = wurzel(index[t + 1]);
            if (a !== b) eltern[Math.max(a, b)] = Math.min(a, b);
        }
        const id = new Uint32Array(n);
        const anzahl = new Uint32Array(n);
        for (let p = 0; p < n; p++) { id[p] = wurzel(p); anzahl[id[p]]++; }
        const lauf = new Uint32Array(n);
        const rang = new Float32Array(n);
        for (let p = 0; p < n; p++) {
            const s = id[p];
            rang[p] = anzahl[s] > 1 ? lauf[s]++ / (anzahl[s] - 1) : 0;
        }
        return { id, rang };
    }

    // -------------------------------------------------------------- Karten

    static _karte(material, anteil) {
        const z = material.userData.ergrauen ??= { uErgrauen: { value: 0 } };
        z.uErgrauen.value = anteil;
        if (anteil <= 0 || Shaderpatch.hat(material, 'ergrauen')) return;
        const eingriff = (shader) => {
            shader.uniforms.uErgrauen = z.uErgrauen;
            shader.fragmentShader = shader.fragmentShader
                .replace('#include <common>', '#include <common>\nuniform float uErgrauen;')
                .replace('#include <map_fragment>', `#include <map_fragment>
{
    float egG = uErgrauen * 0.7;
#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
    #ifdef USE_MAP
    vec2 egUv = vMapUv;
    #else
    vec2 egUv = vAlphaMapUv;
    #endif
    float egZ = fract( sin( dot( floor( egUv * 70.0 ), vec2( 12.9898, 78.233 ) ) ) * 43758.5453 );
    egG = smoothstep( egZ, egZ + 0.04, uErgrauen );
#endif
    float egL = dot( diffuseColor.rgb, vec3( 0.2126, 0.7152, 0.0722 ) );
    diffuseColor.rgb = mix( diffuseColor.rgb, vec3( egL * 0.3 + 0.5 ), egG );
}`);
        };
        Shaderpatch.anhaengen(material, 'ergrauen', eingriff);
    }
}
