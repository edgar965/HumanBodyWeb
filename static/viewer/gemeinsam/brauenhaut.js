import { Shaderpatch } from './shaderpatch.js';

/**
 * Brauenhaut — die gezeichnete Augenbraue im Hautshader.
 *
 * Edgar, 16.09.2026 (Konzept A, `Docu/konzepte/2026-09-16_augenbrauen.md`):
 * die Braue liegt in der Haut, nicht davor — aber nicht in der 2048²-Albedo
 * (90 × 12 px), sondern als eigene Karte NUR für das Brauenfenster, die der
 * Server aus den Reglern zeichnet (`core/dienste/brauendecal.py`, 0,2 s,
 * `/api/character/brauen/bild/?…`). Der Shader der HAUT mischt sie je
 * Bildpunkt über Albedo oder Hautfarbe, wo die UV im Fenster liegt
 * (`/api/character/brauen/fenster/`, einmal je Geschlecht). Die Braue folgt
 * den Morphs, weil sie an den UVs hängt — der Anker der alten Objekt-Brauen
 * (`augenbrauenbau.js`) entfällt.
 *
 * Ein Reglerwechsel tauscht nur die Karte in den Uniforms — kein neuer
 * Shader (der Eingriff hängt einmal am Material, `Shaderpatch`). Ohne
 * `import * as THREE` (Node-Test `test_js_brauenhaut.py`); `three` kommt
 * beim Laden der Karte per `import('three')`, wie in `Hauttextur`.
 */
export class Brauenhaut {

    static SCHLUESSEL = 'brauen';
    static ADRESSE = '/api/character/brauen/';
    /** Materialgruppen der Haut (mit Censor) — wie `Hauttextur.HAUT`. */
    static HAUT = [0, 1];
    /** Detailfelder → Abfrageparameter; mm-Felder stehen in Metern in `details`. */
    /** @type {Object<string, [string, number]>} */
    static FELDER = {
        brauen: ['farbe', 1], brauen_staerke: ['haar_laenge', 1], brauen_dicke: ['dicke', 1],
        brauen_dichte: ['dichte', 1], brauen_bogen_laenge: ['laenge', 1],
        brauen_deckkraft: ['deckkraft', 1], brauen_lage: ['lage', 1000],
        brauen_hoehe_innen: ['hoehe_innen', 1000], brauen_hoehe_aussen: ['hoehe_aussen', 1000],
        brauen_woelbung: ['woelbung', 1000],
    };

    static _fenster = new Map();
    static _karten = new Map();
    static _lader = null;

    /** Das Geschlecht der Karte aus der Körperart (`Male_…` → male). */
    static geschlecht(bodyType) {
        return String(bodyType || '').toLowerCase().startsWith('male') ? 'male' : 'female';
    }

    /** Die Abfrage aus den Details — gerundet, damit gleiche Regler dieselbe Adresse geben. */
    static abfrage(details, geschlecht, fassung = 1) {
        const teile = [`geschlecht=${geschlecht}`, `f=${fassung}`];
        for (const [feld, [name, faktor]] of Object.entries(Brauenhaut.FELDER)) {
            const wert = details?.[feld];
            if (wert === undefined || wert === null || wert === '') continue;
            const text = typeof wert === 'number'
                ? String(Math.round(wert * faktor * 100) / 100) : String(wert);
            teile.push(`${name}=${encodeURIComponent(text)}`);
        }
        return teile.join('&');
    }

    static adresse(details, geschlecht, fassung = 1) {
        return `${Brauenhaut.ADRESSE}bild/?${Brauenhaut.abfrage(details, geschlecht, fassung)}`;
    }

    /**
     * Die Braue auf die Haut setzen oder nachziehen.
     * @param netz      Körpernetz mit Materialliste
     * @param details   `Koerperdetails`
     * @param bodyType  Körperart der Figur
     * @returns Promise<boolean> — true, wenn eine Karte gesetzt wurde
     */
    static async anwenden(netz, details, bodyType) {
        const materialien = Array.isArray(netz?.material) ? netz.material : null;
        if (!materialien || !details) return false;
        const geschlecht = Brauenhaut.geschlecht(bodyType);
        const fenster = await Brauenhaut.fenster(geschlecht);
        if (!fenster) return false;
        const karte = await Brauenhaut.karte(Brauenhaut.adresse(details, geschlecht, fenster.fassung));
        let gesetzt = 0;
        for (const g of Brauenhaut.HAUT) {
            const m = materialien[g];
            if (!m) continue;
            const alt = Shaderpatch.eingriff(m, Brauenhaut.SCHLUESSEL);
            if (alt?.uniforms) {
                alt.uniforms.brauenKarte.value = karte;
            } else {
                const uniforms = { brauenKarte: { value: karte },
                                   brauenFenster: { value: fenster.fenster.slice() } };
                const eingriff = shader => Brauenhaut.patchen(shader, uniforms);
                eingriff.uniforms = uniforms;
                Shaderpatch.anhaengen(m, Brauenhaut.SCHLUESSEL, eingriff);
            }
            gesetzt += 1;
        }
        return gesetzt > 0;
    }

    /** Fenster und Fassung je Geschlecht — einmal geholt. */
    static async fenster(geschlecht) {
        if (!Brauenhaut._fenster.has(geschlecht)) {
            Brauenhaut._fenster.set(geschlecht, (async () => {
                const antwort = await fetch(`${Brauenhaut.ADRESSE}fenster/?geschlecht=${geschlecht}`);
                if (!antwort.ok) return null;
                return antwort.json();
            })());
        }
        return Brauenhaut._fenster.get(geschlecht);
    }

    /** Eine Karte laden — einmal je Adresse; Farben in sRGB. */
    static async karte(adresse) {
        if (Brauenhaut._karten.has(adresse)) return Brauenhaut._karten.get(adresse);
        const THREE = await import('three');
        Brauenhaut._lader ??= new THREE.TextureLoader();
        const versprechen = Brauenhaut._lader.loadAsync(adresse).then(textur => {
            textur.colorSpace = THREE.SRGBColorSpace;
            textur.anisotropy = 8;
            return textur;
        });
        Brauenhaut._karten.set(adresse, versprechen);
        return versprechen;
    }

    /** Der Eingriff: UV durchreichen, im Fenster die Karte über die Farbe mischen. */
    static patchen(shader, uniforms) {
        shader.uniforms.brauenKarte = uniforms.brauenKarte;
        shader.uniforms.brauenFenster = uniforms.brauenFenster;
        shader.vertexShader = 'varying vec2 vBrauenUv;\n'
            + shader.vertexShader.replace('#include <begin_vertex>',
                                          '#include <begin_vertex>\n\tvBrauenUv = uv;');
        shader.fragmentShader = 'varying vec2 vBrauenUv;\nuniform sampler2D brauenKarte;\n'
            + 'uniform vec4 brauenFenster;\n'
            + shader.fragmentShader.replace('#include <color_fragment>',
                '#include <color_fragment>\n'
                + '\tvec2 brauenUv = (vBrauenUv - brauenFenster.xy)'
                + ' / (brauenFenster.zw - brauenFenster.xy);\n'
                + '\tif (all(greaterThanEqual(brauenUv, vec2(0.0)))'
                + ' && all(lessThanEqual(brauenUv, vec2(1.0)))) {\n'
                + '\t\tvec4 braue = texture2D(brauenKarte, brauenUv);\n'
                + '\t\tdiffuseColor.rgb = mix(diffuseColor.rgb, braue.rgb, braue.a);\n'
                + '\t}');
        return shader;
    }

    /** Trägt die Haut dieses Netzes die Braue? */
    static aktiv(netz) {
        return Brauenhaut.HAUT.some(g => netz?.material?.[g]
            && Shaderpatch.hat(netz.material[g], Brauenhaut.SCHLUESSEL));
    }
}
