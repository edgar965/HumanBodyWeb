/**
 * Stueckhautpatch — das Stück nimmt an seinem Rand die Farbe der Haut an (09.10.2026): Attribute und Eingriff in den Shader.
 *
 * Die Rechnung (Farbe der Haut je Punkt, Maß der Überblendung) steht in `stueckhautrechnung.js`. Hier: die Attribute `hautfarbe` (vec3,
 * linear) und `hautmisch` (float) am Netz des Stücks und der Eingriff (`Shaderpatch`, damit er neben Einzug, Durchlicht und Detail besteht):
 * hinter `map_fragment` wird die Farbe des Stücks mit der Hautfarbe gemischt, `diffuseColor.rgb = mix(diffuseColor.rgb, vHautFarbe,
 * vHautMisch)`. Das Maß ist am Rand 1 und klingt aus — eine Überblendung der Farbe an der Naht, kein Faktor auf die Karte des Stücks:
 * am Ring ist es die Farbe der Haut, nicht „ungefähr", und weiter innen die eigene Karte des Stücks mit all ihren Einzelheiten.
 * Die Farbe läuft als Attribut (Mittel der nächsten Hautpunkte), nicht als zweite Karte mit UV: die UV der Haut springt an einer Naht
 * der Karte, und dort zeigte sie auf eine fremde Stelle.
 */
import * as THREE from 'three';
import { Shaderpatch } from './shaderpatch.js';

export class Stueckhautpatch {

    static SCHLUESSEL = 'stueckhaut';

    /** Attribute am Netz setzen (oder überschreiben) und die Materialien des Stücks patchen. */
    static eintragen(netz, farbe, misch) {
        const geo = netz.geometry;
        Stueckhautpatch._attribut(geo, 'hautfarbe', farbe, 3);
        Stueckhautpatch._attribut(geo, 'hautmisch', misch, 1);
        const liste = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const mat of liste) {
            if (!mat || Shaderpatch.hat(mat, Stueckhautpatch.SCHLUESSEL)) continue;
            Shaderpatch.anhaengen(mat, Stueckhautpatch.SCHLUESSEL, Stueckhautpatch.eingriff);
        }
    }

    /** Den Eingriff wieder abnehmen (kein verschweißtes Stück mehr): Attribute weg, Shader ohne. */
    static aufheben(netz) {
        netz.geometry.deleteAttribute('hautfarbe');
        netz.geometry.deleteAttribute('hautmisch');
        const liste = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const mat of liste) if (mat) Shaderpatch.entfernen(mat, Stueckhautpatch.SCHLUESSEL);
    }

    static eingriff(shader) {
        Shaderpatch.hinterInclude(shader, 'common', 'attribute vec3 hautfarbe;\nattribute float hautmisch;\nvarying vec3 vHautFarbe;\nvarying float vHautMisch;');
        Shaderpatch.hinterInclude(shader, 'begin_vertex', 'vHautFarbe = hautfarbe;\nvHautMisch = hautmisch;');
        shader.fragmentShader = shader.fragmentShader
            .replace('#include <common>', '#include <common>\nvarying vec3 vHautFarbe;\nvarying float vHautMisch;')
            .replace('#include <map_fragment>',
                     '#include <map_fragment>\n#ifdef USE_MAP\n    diffuseColor.rgb = mix( diffuseColor.rgb, vHautFarbe, vHautMisch );\n#endif');
    }

    static _attribut(geo, name, werte, anzahl) {
        const alt = geo.getAttribute(name);
        if (alt && alt.array.length === werte.length) { alt.array.set(werte); alt.needsUpdate = true; return; }
        geo.setAttribute(name, new THREE.BufferAttribute(Float32Array.from(werte), anzahl));
    }
}
