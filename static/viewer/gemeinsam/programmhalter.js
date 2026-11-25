/**
 * Programmhalter — Shader-Programme überleben den Neubau einer Figur, und ein noch nicht fertiges lässt das alte weiterzeichnen (25.11.2026).
 *
 * Edgar, 25.11.2026: „Zweimal stand die Seite kurz nach einem Zug an „Wirkt älter / jünger“ 6,4 und 5,1 s, in einem einzelnen Bild der Zeichenschleife.“ Belegt (Chrome, Shader künstlich
 * „kalt“): die Haut bekam ein neues Programm (Falten, Altersflecken), `Programmvorbau.wartet` ließ 300 ms Bilder aus, danach wartete three IM Bild auf den Übersetzer
 * (`getProgramParameter(ACTIVE_UNIFORMS)`, 6,1 und 6,6 s).
 *
 *   zurueckhalten(…)  Ein Material, das schon gezeichnet wurde, bekommt sein neues Programm erst, wenn es fertig ist: bis dahin zeichnet es mit dem alten weiter. Die Uniforms bleiben die
 *                     neuen — three führt je Material EINEN Satz für alle seine Programme, der neue enthält, was das alte liest.
 *   behalten(…)       Jeder Reglerzug baut neue Materialien; three löscht die Programme der alten, sobald keines mehr sie benutzt, und übersetzt dieselben gleich noch einmal. Hier zählt
 *                     jedes Programm einmal mehr, höchstens `HOECHSTENS` — die am längsten unbenutzten gehen zuerst.
 */
export class Programmhalter {

    static HOECHSTENS = 160;
    /** Programm → wann zuletzt von einem Material benutzt. */
    static _behalten = new Map();
    /** Material → {e: seine Eigenschaften im Renderer, neu: Programm, fassung: Fassung des Materials} */
    static _zurueck = new Map();

    /** Was zu diesem Material gerade gezeichnet wird — vor `renderer.compile` merken; null, wenn es noch nie gezeichnet wurde. */
    static stand(renderer, material) {
        const e = renderer.properties.get(material);
        return e.currentProgram && e.__version !== undefined ? e.currentProgram : null;
    }

    /**
     * Nach `renderer.compile`: hat `material` ein NEUES, noch nicht fertiges Programm bekommen, zeichnet es mit `alt` (aus `stand`) weiter. Gibt true, wenn es so ist.
     */
    static zurueckhalten(renderer, material, alt) {
        const e = renderer.properties.get(material), neu = e.currentProgram;
        if (!alt?.program || neu === alt || neu?.isReady() !== false) return false;
        Programmhalter._zurueck.set(material, { e, neu, fassung: material.version });
        Programmhalter._setzen(e, alt, material.version);
        return true;
    }

    static _setzen(e, programm, fassung) {
        e.currentProgram = programm;
        e.uniformsList = null;
        e.__version = fassung;                       // sonst holte three das neue gleich selbst (und wartete darauf)
    }

    /** Je Bild: die fertigen einsetzen — `fertig(programm)` für jedes. */
    static einsetzen(fertig) {
        for (const [material, z] of Programmhalter._zurueck) {
            if (material.version !== z.fassung || !z.neu.program) { Programmhalter._zurueck.delete(material); continue; }      // inzwischen wieder geändert: `wartet` sieht es neu
            if (z.neu.isReady() === false) continue;
            Programmhalter._setzen(z.e, z.neu, z.fassung);
            Programmhalter._zurueck.delete(material);
            fertig(z.neu);
        }
    }

    /** Zahl der Materialien, die noch mit dem alten Programm zeichnen. */
    static wartend() {
        return Programmhalter._zurueck.size;
    }

    /** Die Programme des Renderers behalten (gelegentlich aufrufen, `Programmvorbau.nachpruefen`). */
    static behalten(renderer) {
        const jetzt = performance.now(), programme = renderer.info.programs || [];
        for (const p of programme) {
            const neu = !Programmhalter._behalten.has(p);
            if (neu) p.usedTimes += 1;
            if (neu || p.usedTimes > 1) Programmhalter._behalten.set(p, jetzt);
        }
        if (Programmhalter._behalten.size <= Programmhalter.HOECHSTENS) return;
        const frei = [...Programmhalter._behalten].filter(([p]) => p.usedTimes === 1).sort((a, b) => a[1] - b[1]);
        for (const [p] of frei.slice(0, Programmhalter._behalten.size - Programmhalter.HOECHSTENS)) {
            Programmhalter._behalten.delete(p);
            const i = programme.indexOf(p);
            if (i < 0) continue;
            programme[i] = programme[programme.length - 1];       // wie `WebGLPrograms.releaseProgram` (three r170)
            programme.pop();
            p.usedTimes = 0;
            p.destroy();
        }
    }
}
