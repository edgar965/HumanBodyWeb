/**
 * Shaderpatch — mehrere Eingriffe in den Shader EINES Materials, die sich
 * nicht gegenseitig überschreiben.
 *
 * WARUM (11.09.2026): Three.js kennt je Material genau ein
 * `onBeforeCompile` und einen `customProgramCacheKey`. Das Weichgewebe
 * hängt seinen Zuschlag daran (`transformed += zuschlag`), die
 * Hautverdeckung ihren Einzug (`transformed += einzug`) — wer als Zweiter
 * kommt, löscht den Ersten, ohne Fehler und ohne Meldung. Dazu kopiert
 * `Material.clone()` weder `onBeforeCompile` noch `customProgramCacheKey`,
 * und `userData` geht durch JSON (Funktionen fallen heraus): Ein Patch am
 * Körpermaterial wäre nach dem Klonen im Weichgewebe still verschwunden.
 *
 * Hier stehen die Eingriffe je Material in einem Register (`WeakMap`, das
 * Material selbst bleibt unangetastet); `onBeforeCompile` ruft alle der
 * Reihe nach, der Programmschlüssel nennt alle Namen — Three.js teilt
 * kompilierte Programme zwischen gleichartigen Materialien, und ohne
 * eigenen Schlüssel bekäme ein ungepatchtes Material dasselbe Programm.
 * `klonen` nimmt das Register mit.
 *
 * OHNE THREE.JS: `material` ist irgendein Objekt mit den beiden Feldern —
 * deshalb in Node prüfbar (`core/tests/unit/test_js_shaderpatch.py`).
 */
export class Shaderpatch {

    static _register = new WeakMap();

    /** Den Eingriff `fn(shader)` unter `schluessel` anhängen (ersetzt einen
     *  gleichnamigen); `needsUpdate` wird gesetzt, wenn das Material es kennt. */
    static anhaengen(material, schluessel, fn) {
        const eintraege = Shaderpatch._register.get(material) || new Map();
        eintraege.set(schluessel, fn);
        Shaderpatch._register.set(material, eintraege);
        Shaderpatch._binden(material, eintraege);
        return material;
    }

    /** Trägt das Material den Eingriff schon? */
    static hat(material, schluessel) {
        return Shaderpatch._register.get(material)?.has(schluessel) ?? false;
    }

    /** Die Namen der Eingriffe, sortiert. */
    static schluessel(material) {
        return Array.from(Shaderpatch._register.get(material)?.keys() ?? []).sort();
    }

    /** `material.clone()` — mit allen Eingriffen. */
    static klonen(material) {
        const neu = material.clone();
        const eintraege = Shaderpatch._register.get(material);
        if (eintraege) {
            const kopie = new Map(eintraege);
            Shaderpatch._register.set(neu, kopie);
            Shaderpatch._binden(neu, kopie);
        }
        return neu;
    }

    static _binden(material, eintraege) {
        material.onBeforeCompile = (shader, renderer) => {
            for (const fn of eintraege.values()) fn(shader, renderer);
        };
        material.customProgramCacheKey = () => Array.from(eintraege.keys()).sort().join('+');
        if ('needsUpdate' in material || material.isMaterial) material.needsUpdate = true;
    }

    /** Eine Zeile im Vertex-Shader hinter einem `#include` einfügen — der
     *  häufigste Eingriff. */
    static hinterInclude(shader, include, zeile) {
        const marke = `#include <${include}>`;
        if (!shader.vertexShader.includes(marke)) return false;
        shader.vertexShader = shader.vertexShader.replace(marke, `${marke}\n${zeile}`);
        return true;
    }
}
