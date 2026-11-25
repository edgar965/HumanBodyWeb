import * as THREE from 'three';
import { Programmhalter } from './programmhalter.js';
import { Sanduhr } from './sanduhr.js';

/**
 * Programmvorbau — die Shader-Programme einer Figur bauen lassen, BEVOR sie ins Bild kommt (24.11.2026).
 *
 * Edgar, 24.11.2026: „EdgarNeu laden im Charakter dauert ewig, das muss in 2 s laden“. Gemessen im Charakter (JS-Profil beim Laden von EdgarNeu): das erste Bild mit der Figur hielt den
 * Hauptfaden 400–620 ms an, darin `onFirstUse` mit `getProgramInfoLog`/`getShaderInfoLog` 130–200 ms je Stufe — three wartet beim ersten Gebrauch synchron, bis der Treiber das Programm
 * gebunden hat, und in der Warteschlange des GPU-Prozesses stehen gerade die Bilder der Figur. Foto-/Mesh-Genesis lösen das seit 22.11.2026 mit `Meshgenesiszeichenflaeche.vorbereiten`;
 * hier steht, was jede Seite mit eigener Szene braucht:
 *
 *   anmelden(renderer)    keine Logs je Programm beim ersten Gebrauch (`checkShaderErrors` aus) — Fehler meldet `pruefen`, sobald ein Programm fertig ist
 *   bauen(…)              `renderer.compile` für ein Objekt, das noch nicht in der Szene hängt, und warten, bis jedes Programm fertig ist (`KHR_parallel_shader_compile`)
 *   wartet(…)             je Bild: hat sich ein Material geändert (Bilder kamen an), wird sein neues Programm angestoßen; war es schon zu sehen, zeichnet es bis dahin mit dem alten weiter
 *                         (`Programmhalter`, 25.11.2026), ein nie gezeichnetes Netz lässt das Bild so lange aus — sonst wartete three darin
 *   nachpruefen(renderer) einmal je Sekunde: die Programme, die niemand vorgebaut hat
 */
export class Programmvorbau {

    /** Länger wartet niemand auf die Programme — dann wird gezeichnet und three wartet selbst. */
    static FRIST_MS = 1500;
    static _geprueft = new WeakSet();
    static _ziel = null;

    static anmelden(renderer) {
        renderer.debug.checkShaderErrors = false;
        return renderer;
    }

    /**
     * Die Programme der Netze unter `objekt` bauen lassen, mit den Lichtern von `szene`. Das Versprechen löst sich, wenn alle fertig sind (oder nach `FRIST_MS`, oder sofort ohne
     * `KHR_parallel_shader_compile`). Scheitert der Vorbau, baut three beim Zeichnen wie bisher.
     * @param zielGedacht ob die Szene in ein Renderziel gezeichnet wird (Composer der Auswahl-Aura): dann ohne Tonwert und linear — andere Programme als direkt auf die Leinwand
     */
    static async bauen(renderer, objekt, kamera, szene, zielGedacht = false) {
        if (!renderer?.extensions?.get('KHR_parallel_shader_compile')) return;
        const offen = Programmvorbau._anstossen(renderer, objekt, kamera, szene, zielGedacht);
        for (const m of offen) Programmvorbau._gebaut.set(m, m.version);
        objekt.traverse(o => { if (o.material) Programmvorbau._gesehen.add(o); });
        const frist = performance.now() + Programmvorbau.FRIST_MS;
        for (;;) {
            for (const material of offen) {
                const programm = renderer.properties.get(material).currentProgram;
                if (programm?.isReady() !== false) { Programmvorbau.pruefen(renderer, programm); offen.delete(material); }
            }
            if (!offen.size || performance.now() >= frist) return;
            await new Promise(weiter => setTimeout(weiter, 8));
        }
    }

    /** So lange lässt `wartet` für ein nie gezeichnetes Netz höchstens Bilder aus; danach wird gezeichnet, was da ist. Bis 25.11.2026 300 ms: die Haut mit Hautebenen brauchte kalt 6,4 s,
     *  und three hielt die ganze Seite an (jetzt 2,3 s, `Genesis9hautrauschenGLSL`). Das letzte Bild bleibt stehen, die Seite bedienbar. */
    static WARTEN_MS = 8000;
    /** Ab hier zeigt die Sanduhr, dass ein Programm noch übersetzt wird. */
    static UHR_MS = 400;
    static _offen = new Set();
    static _seit = null;
    static _uhrSeit = null;
    static _uhr = false;
    static _gesehen = new WeakSet();
    /** Material → seine Fassung, als `wartet` es zuletzt bauen ließ. */
    static _gebaut = new WeakMap();

    /**
     * Vor jedem Bild: Netze, die noch nie gezeichnet wurden oder deren Material sich geändert hat, bauen ihr Programm jetzt (`compile` wartet nicht) — true, solange das eines nie
     * gezeichneten Netzes noch übersetzt wird, dann lässt die Seite dieses Bild aus (das letzte bleibt stehen). Gemessen (EdgarNeu, 24.11.2026): als die Karten der Haut ankamen, wartete
     * three 296 ms in `getProgramParameter`. Länger als `WARTEN_MS` am Stück wird nie ausgelassen. Dasselbe tut `Meshgenesiszeichenflaeche` je Feld.
     */
    static wartet(renderer, szene, kamera, zielGedacht = false) {
        const P = Programmvorbau;
        if (!renderer.extensions.get('KHR_parallel_shader_compile')) return false;
        Programmhalter.einsetzen(programm => P.pruefen(renderer, programm));
        const neu = [], geaendert = m => m.version !== renderer.properties.get(m).__version && m.version !== P._gebaut.get(m);
        szene.traverseVisible(o => {
            if (!o.material) return;
            const erst = !P._gesehen.has(o);
            if (erst) P._gesehen.add(o);
            if (erst || (Array.isArray(o.material) ? o.material.some(geaendert) : geaendert(o.material))) neu.push(o);
        });
        for (const o of neu) {
            const vorher = new Map([o.material].flat().map(m => [m, Programmhalter.stand(renderer, m)]));
            for (const m of P._anstossen(renderer, o, kamera, szene, zielGedacht)) {
                P._gebaut.set(m, m.version);
                if (!Programmhalter.zurueckhalten(renderer, m, vorher.get(m))) P._offen.add(m);
            }
        }
        for (const m of P._offen) {
            const programm = renderer.properties.get(m).currentProgram;
            if (programm?.isReady() !== false) { P.pruefen(renderer, programm); P._offen.delete(m); }
        }
        P._anzeigen(P._offen.size > 0 || Programmhalter.wartend() > 0);
        if (!P._offen.size) { P._seit = null; return false; }
        P._seit ??= performance.now();
        if (performance.now() - P._seit < P.WARTEN_MS) return true;
        P._offen.clear();
        P._seit = null;
        return false;
    }

    /** Die Sanduhr, solange ein Programm länger als `UHR_MS` übersetzt wird (Edgar, 25.11.2026: „Mach eine Sanduhr wenn ein regler nicht durch ist“). */
    static _anzeigen(wartet) {
        const P = Programmvorbau;
        P._uhrSeit = wartet ? P._uhrSeit ?? performance.now() : null;
        const an = wartet && performance.now() - P._uhrSeit > P.UHR_MS;
        if (an === P._uhr) return;
        P._uhr = an;
        if (an) Sanduhr.an('Haut und Stoff werden vorbereitet …');
        else Sanduhr.aus();
    }

    /** `renderer.compile` mit dem Ziel, in das die Seite zeichnet — die Materialien (Set); leer, wenn es scheitert (dann baut three beim Zeichnen). */
    static _anstossen(renderer, objekt, kamera, szene, zielGedacht) {
        const vorher = renderer.getRenderTarget();
        try {
            if (zielGedacht) renderer.setRenderTarget(Programmvorbau._ziel ??= new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType, samples: 4 }));
            return renderer.compile(objekt, kamera, szene);
        } catch (fehler) {
            console.warn(`Programmvorbau: ${fehler.message} — die Programme entstehen beim Zeichnen`);
            return new Set();
        } finally {
            if (zielGedacht) renderer.setRenderTarget(vorher);
        }
    }

    /** Statt three's Prüfung (`checkShaderErrors` aus): ist das fertige Programm gebunden? Einmal je Programm; die Logs nur im Fehlerfall (three löscht die Shader beim ersten Gebrauch). */
    static pruefen(renderer, programm) {
        if (!programm?.program || Programmvorbau._geprueft.has(programm)) return;
        Programmvorbau._geprueft.add(programm);
        const gl = renderer.getContext();
        if (gl.getProgramParameter(programm.program, gl.LINK_STATUS) !== false) return;
        const log = shader => (shader && gl.isShader(shader) ? gl.getShaderInfoLog(shader) : '(Shader schon gelöscht)');
        console.error(`Programmvorbau: Shader „${programm.name}“ nicht gebunden — ${gl.getProgramInfoLog(programm.program)}\n`
            + `Vertex: ${log(programm.vertexShader)}\nFragment: ${log(programm.fragmentShader)}`);
    }

    /** Die fertigen Programme, die noch niemand geprüft hat — höchstens `JE_AUFRUF` je Aufruf (die Frage nach dem Bindestand geht an den GPU-Prozess). */
    static JE_AUFRUF = 4;

    static nachpruefen(renderer) {
        Programmhalter.behalten(renderer);
        let n = 0;
        for (const programm of renderer.info.programs || []) {
            if (Programmvorbau._geprueft.has(programm) || programm.isReady?.() === false) continue;
            Programmvorbau.pruefen(renderer, programm);
            if ((n += 1) >= Programmvorbau.JE_AUFRUF) return;
        }
    }
}
