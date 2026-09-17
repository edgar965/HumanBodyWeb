import { Shaderpatch } from './shaderpatch.js';

/**
 * Lippenhaut — die Lippenfarbe läuft am Rand glatt in die Haut aus.
 *
 * WARUM (Edgar, 13.09.2026, Bild aus der Szene: „die Lippen sind fehlerhaft"):
 * Die Lippen sind eine eigene Materialgruppe (`Lippengruppe`) — ein Dreieck
 * ist ganz Lippe oder ganz Haut. Auf 2–3 mm großen Dreiecken wird der Rand
 * damit zum Zickzack, und wo die Maske über die Lippen hinauslief, standen
 * die Zacken mitten auf der Wange.
 *
 * Der Server schickt seit heute zu den Lippenpunkten einen SAUM: je Punkt
 * nahe am Rand den Vorzeichenabstand in Millimetern (innen positiv,
 * `core/dienste/lippenlinse.py`). Der steht hier als Attribut `lippe` am
 * Netz; der Shader der HAUT mischt daraus je Bildpunkt die Lippenfarbe ein
 * (`smoothstep` über ±SAUM_MM um den Nullpunkt). Weil der Abstand über ein
 * Dreieck linear läuft, liegt der Nullpunkt als gerade Strecke QUER durch
 * das Dreieck — der Rand folgt der Linse, nicht den Kanten.
 *
 * Mit Saum wird die Lippengruppe NICHT mehr abgespalten (`Lippenbau`): Ein
 * Dreieck mit drei knapp positiven Ecken stünde sonst als roter Zacken über
 * den weichen Rand hinaus. Das Lippenmaterial an Index LIPPEN bleibt als
 * Wertehalter — dort setzt `Detailfarben` Farbe und Glanz, `nachziehen`
 * holt sie in die Uniforms des Hautshaders (`Detailfarben.faerben` ruft es).
 * Die Uniforms hängen am Eingriff selbst (`Shaderpatch.eingriff`), damit sie
 * auch am Klon des Materials gefunden werden (Weichgewebe klont alle).
 *
 * Ohne `import * as THREE`: die Farbe kommt als Klon von `material.color`,
 * das Attribut über die Klasse von `attributes.position` — so läuft das
 * Modul in Node mit Attrappen (`test_js_lippenhaut.py`). Der Eingriff geht
 * über `Shaderpatch`, damit er sich mit Weichgewebe und Hautverdeckung am
 * selben Material verträgt.
 */
export class Lippenhaut {

    static SCHLUESSEL = 'lippen';
    static ATTRIBUT = 'lippe';
    /** Halbe Breite des Übergangs in mm — ein knapper Millimeter, sonst wirkt der Rand verwaschen. */
    static SAUM_MM = 0.7;
    /** Materialgruppen: Haut (mit Censor) bekommt den Shader, die Lippen liefern die Werte. */
    static HAUT = [0, 1];
    static LIPPEN = 11;
    /** Abstand für Punkte, die der Saum nicht nennt: Lippenpunkte innen, alle anderen außen (mm). */
    static INNEN = 10;
    static AUSSEN = -10;

    /**
     * Attribut anlegen und den Hautshader patchen.
     * @param netz    Körpernetz mit Materialliste (Lippenmaterial an Index LIPPEN)
     * @param lippen  `{punkte, saum: {punkte, abstand}}` der Netzantwort
     * @returns Zahl der Punkte mit Saumabstand (0 = nichts getan)
     */
    static anlegen(netz, lippen) {
        const geo = netz?.geometry;
        const saum = lippen?.saum;
        const lippe = netz?.material?.[Lippenhaut.LIPPEN];
        if (!geo?.attributes?.position || !saum?.punkte?.length || !lippe?.color?.clone) return 0;
        const werte = Lippenhaut.abstaende(geo.attributes.position.count, lippen.punkte, saum);
        const Attribut = geo.attributes.position.constructor;
        geo.setAttribute(Lippenhaut.ATTRIBUT, new Attribut(werte, 1));
        const uniforms = { lippenFarbe: { value: lippe.color.clone() },
                           lippenRauheit: { value: lippe.roughness } };
        const eingriff = shader => Lippenhaut.patchen(shader, uniforms);
        eingriff.uniforms = uniforms;
        for (const g of Lippenhaut.HAUT) {
            if (netz.material[g]) Shaderpatch.anhaengen(netz.material[g], Lippenhaut.SCHLUESSEL, eingriff);
        }
        return saum.punkte.length;
    }

    /** Das Abstandsfeld: Vorgabe außen, Lippenpunkte innen, der Saum mit seinen Werten. */
    static abstaende(anzahl, punkte, saum) {
        const werte = new Float32Array(anzahl).fill(Lippenhaut.AUSSEN);
        for (const i of punkte || []) werte[i] = Lippenhaut.INNEN;
        for (let k = 0; k < saum.punkte.length; k++) werte[saum.punkte[k]] = saum.abstand[k];
        return werte;
    }

    /** Der Eingriff in den Shader: Attribut durchreichen, Farbe und Rauheit mischen. */
    static patchen(shader, uniforms) {
        shader.uniforms.lippenFarbe = uniforms.lippenFarbe;
        shader.uniforms.lippenRauheit = uniforms.lippenRauheit;
        shader.vertexShader = `attribute float ${Lippenhaut.ATTRIBUT};\nvarying float vLippe;\n`
            + shader.vertexShader.replace('#include <begin_vertex>',
                                          `#include <begin_vertex>\n\tvLippe = ${Lippenhaut.ATTRIBUT};`);
        const saum = Lippenhaut.SAUM_MM.toFixed(2);
        shader.fragmentShader = 'varying float vLippe;\nuniform vec3 lippenFarbe;\nuniform float lippenRauheit;\n'
            + shader.fragmentShader
                .replace('#include <color_fragment>',
                         '#include <color_fragment>\n\tfloat lippenAnteil = smoothstep('
                         + `-${saum}, ${saum}, vLippe);\n`
                         + '\tdiffuseColor.rgb = mix(diffuseColor.rgb, lippenFarbe, lippenAnteil);')
                .replace('#include <roughnessmap_fragment>',
                         '#include <roughnessmap_fragment>\n'
                         + '\troughnessFactor = mix(roughnessFactor, lippenRauheit, lippenAnteil);');
        return shader;
    }

    /** Farbe und Glanz des Lippenmaterials in die Uniforms der Haut holen. */
    static nachziehen(materialien) {
        const lippe = materialien?.[Lippenhaut.LIPPEN];
        if (!lippe?.color) return 0;
        let gesetzt = 0;
        for (const g of Lippenhaut.HAUT) {
            const uniforms = Shaderpatch.eingriff(materialien[g], Lippenhaut.SCHLUESSEL)?.uniforms;
            if (!uniforms) continue;
            uniforms.lippenFarbe.value.copy(lippe.color);
            uniforms.lippenRauheit.value = lippe.roughness;
            gesetzt += 1;
        }
        return gesetzt;
    }

    /** Trägt die Haut dieses Netzes den Eingriff? */
    static aktiv(netz) {
        return Lippenhaut.HAUT.some(g => netz?.material?.[g]
            && Shaderpatch.hat(netz.material[g], Lippenhaut.SCHLUESSEL));
    }
}
