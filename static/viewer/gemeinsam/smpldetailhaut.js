import { Brauenhaut } from './brauenhaut.js';
import { Detailfarben } from './detailfarben.js';
import { Shaderpatch } from './shaderpatch.js';

/**
 * Smpldetailhaut — Augen, Brauen, Lippen und Nägel im Hautshader einer SMPL-X-Figur.
 *
 * WARUM (Edgar, 25.09.2026: „mach auch Augen/Augenbrauen/Mund/Nägel"): Das
 * HumanBody-Netz führt diese Teile als eigene Materialgruppen, SMPL-X hat
 * EIN Netz mit einer Fototextur. Wo die Teile liegen, sagt eine Maske im
 * UV-Raum (`/api/character/smpl-figur/details/<g>/maske/`, `SMPL/xdetails.py`:
 * R Lippen, G Fingernägel, B Fußnägel, A Augen als Winkel zur Blickrichtung).
 *
 * - Lippen und Nägel: das FOTO wird umgefärbt — Farbe ÷ HumanBody-Vorgabe
 *   (`Detailfarben.VORGABE`) als Faktor. Die Vorgabe lässt das Foto also
 *   unverändert; dieselben Felder und Farbwähler wie bei HumanBody.
 * - Augen: das Fotoauge des Augapfels, Iris und Sklera getrennt über den
 *   Winkel zur Blickrichtung (Maske A), wie Lippen und Nägel umgefärbt.
 * - Brauen: die Karte von `Brauendecal` auf dem SMPL-X-Brauenbogen
 *   (`quelle=smplx`), gemischt wie in `Brauenhaut`; die Fotobrauen sind aus
 *   der Textur retuschiert, damit die Regler greifen.
 * Ein Reglerwechsel setzt nur Uniforms (ein Eingriff je Material, `Shaderpatch`).
 */
export class Smpldetailhaut {

    static SCHLUESSEL = 'smpldetails';
    static MASKE = '/api/character/smpl-figur/details/';

    static _masken = new Map();
    static _fenster = new Map();

    /** Details auf das Körpermaterial legen oder nachziehen. */
    static async anwenden(netz, details, geschlecht) {
        const material = netz?.material;
        if (!material || !details) return false;
        const g = geschlecht === 'male' ? 'male' : 'female';
        const [maske, fenster] = await Promise.all([Smpldetailhaut.maske(g), Smpldetailhaut.fenster(g)]);
        const karte = fenster
            ? await Brauenhaut.karte(`${Brauenhaut.adresse(details, g, fenster.fassung)}&quelle=smplx`)
            : null;
        const werte = Smpldetailhaut.werte(details);
        const alt = Shaderpatch.eingriff(material, Smpldetailhaut.SCHLUESSEL);
        const uniforms = alt?.uniforms || Smpldetailhaut._uniforms();
        uniforms.detailMaske.value = maske;
        uniforms.brauenKarte.value = karte;
        uniforms.brauenAn.value = karte && fenster ? 1 : 0;
        if (fenster) uniforms.brauenFenster.value = fenster.fenster.slice();
        for (const [name, wert] of Object.entries(werte)) uniforms[name].value = wert;
        if (!alt) {
            const eingriff = shader => Smpldetailhaut.patchen(shader, uniforms);
            eingriff.uniforms = uniforms;
            Shaderpatch.anhaengen(material, Smpldetailhaut.SCHLUESSEL, eingriff);
            material.needsUpdate = true;
        }
        return true;
    }

    static _uniforms() {
        return {
            detailMaske: { value: null }, brauenKarte: { value: null },
            brauenFenster: { value: [0, 0, 1, 1] }, brauenAn: { value: 0 },
            lippenFaktor: { value: [1, 1, 1] }, fingerFaktor: { value: [1, 1, 1] },
            fussFaktor: { value: [1, 1, 1] }, irisFarbe: { value: [1, 1, 1] }, irisMisch: { value: 0 },
            skleraFaktor: { value: [1, 1, 1] }, lippenGlanz: { value: 0.6 },
        };
    }

    /** sRGB-Hex → lineares RGB. */
    static linear(hex) {
        const n = parseInt(String(hex).slice(1), 16);
        return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((c) => {
            const s = c / 255;
            return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
        });
    }

    /** Farbe ÷ Vorgabe je Kanal (linear) — 1 heißt: Foto bleibt. */
    static faktor(details, feld) {
        const soll = Smpldetailhaut.linear(Detailfarben.istFarbe(details[feld])
            ? details[feld] : Detailfarben.VORGABE[feld]);
        const basis = Smpldetailhaut.linear(Detailfarben.VORGABE[feld]);
        return soll.map((s, i) => Math.min(4, s / Math.max(basis[i], 1e-3)));
    }

    /** Die Uniform-Werte aus den Details (ohne Three.js, Node-prüfbar). */
    static werte(details) {
        const glanz = Number(details.lippen_glanz);
        return {
            lippenFaktor: Smpldetailhaut.faktor(details, 'lippen'),
            fingerFaktor: Smpldetailhaut.faktor(details, 'naegel_hand'),
            fussFaktor: Smpldetailhaut.faktor(details, 'naegel_fuss'),
            // Die Iris wird UMGEFÄRBT (Farbe × Fotohelligkeit): ein Faktor dreht
            // Braun nicht nach Blau (25.09.2026 gemessen: #3a78c8 blieb braun).
            irisFarbe: Smpldetailhaut.linear(Detailfarben.istFarbe(details.iris)
                ? details.iris : Detailfarben.VORGABE.iris),
            irisMisch: Detailfarben.istFarbe(details.iris)
                && details.iris.toLowerCase() !== Detailfarben.VORGABE.iris ? 1 : 0,
            skleraFaktor: Smpldetailhaut.faktor(details, 'sklera'),
            lippenGlanz: Number.isFinite(glanz) ? glanz : Detailfarben.VORGABE.lippen_glanz,
        };
    }

    /** Die Maske je Geschlecht, einmal geladen; Daten, kein sRGB. */
    static async maske(geschlecht) {
        if (!Smpldetailhaut._masken.has(geschlecht)) {
            Smpldetailhaut._masken.set(geschlecht, (async () => {
                const THREE = await import('three');
                const textur = await new THREE.TextureLoader()
                    .loadAsync(`${Smpldetailhaut.MASKE}${geschlecht}/maske/`);
                textur.colorSpace = THREE.NoColorSpace;
                textur.anisotropy = 8;
                return textur;
            })());
        }
        return Smpldetailhaut._masken.get(geschlecht);
    }

    /** Das Brauenfenster der SMPL-X-UV (eigener Vorrat — `Brauenhaut.fenster`
     *  hält das HumanBody-Fenster unter demselben Geschlecht). */
    static async fenster(geschlecht) {
        if (!Smpldetailhaut._fenster.has(geschlecht)) {
            Smpldetailhaut._fenster.set(geschlecht, fetch(
                `${Brauenhaut.ADRESSE}fenster/?geschlecht=${geschlecht}&quelle=smplx`)
                .then((a) => (a.ok ? a.json() : null)).catch(() => null));
        }
        return Smpldetailhaut._fenster.get(geschlecht);
    }

    /** Der Eingriff: Maske lesen, Foto umfärben, Augen zeichnen, Braue mischen, Glanz. */
    static patchen(shader, uniforms) {
        for (const name of Object.keys(uniforms)) shader.uniforms[name] = uniforms[name];
        shader.vertexShader = 'varying vec2 vDetailUv;\n'
            + shader.vertexShader.replace('#include <begin_vertex>',
                                          '#include <begin_vertex>\n\tvDetailUv = uv;');
        const kopf = 'varying vec2 vDetailUv;\nuniform sampler2D detailMaske;\n'
            + 'uniform sampler2D brauenKarte;\nuniform vec4 brauenFenster;\nuniform float brauenAn;\n'
            + 'uniform vec3 lippenFaktor;\nuniform vec3 fingerFaktor;\nuniform vec3 fussFaktor;\n'
            + 'uniform vec3 irisFarbe;\nuniform float irisMisch;\nuniform vec3 skleraFaktor;\nuniform float lippenGlanz;\n';
        shader.fragmentShader = kopf + shader.fragmentShader
            .replace('#include <color_fragment>', `#include <color_fragment>
	vec4 dm = texture2D(detailMaske, vDetailUv);
	vec3 foto = diffuseColor.rgb;
	diffuseColor.rgb = mix(diffuseColor.rgb, min(foto * lippenFaktor, vec3(1.0)), dm.r);
	diffuseColor.rgb = mix(diffuseColor.rgb, min(foto * fingerFaktor, vec3(1.0)), dm.g);
	diffuseColor.rgb = mix(diffuseColor.rgb, min(foto * fussFaktor, vec3(1.0)), dm.b);
	float augeAn = step(0.02, dm.a);
	if (augeAn > 0.5) {
		float w = (1.0 - dm.a) / 0.75 * 180.0;
		float iris = 1.0 - smoothstep(27.0, 30.0, w);
		float hell = dot(foto, vec3(0.2126, 0.7152, 0.0722));
		vec3 umgefaerbt = irisFarbe * hell / max(dot(irisFarbe, vec3(0.2126, 0.7152, 0.0722)), 1e-3);
		vec3 irisTon = mix(foto, min(umgefaerbt, vec3(1.0)), irisMisch);
		diffuseColor.rgb = mix(min(foto * skleraFaktor, vec3(1.0)), irisTon, iris);
	}
	if (brauenAn > 0.5) {
		vec2 bUv = (vDetailUv - brauenFenster.xy) / (brauenFenster.zw - brauenFenster.xy);
		if (all(greaterThanEqual(bUv, vec2(0.0))) && all(lessThanEqual(bUv, vec2(1.0)))) {
			vec4 braue = texture2D(brauenKarte, bUv);
			diffuseColor.rgb = mix(diffuseColor.rgb, braue.rgb, braue.a);
		}
	}`)
            .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
	roughnessFactor = mix(roughnessFactor, 1.0 - lippenGlanz, dm.r);
	roughnessFactor = mix(roughnessFactor, 0.3, max(dm.g, dm.b));
	roughnessFactor = mix(roughnessFactor, 0.06, augeAn);`);
        return shader;
    }
}
