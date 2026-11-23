/**
 * Meshgenesiszeichenflaeche — EIN WebGL-Kontext für alle Felder der Seiten „Mesh-Genesis“ (19.10.2026).
 *
 * Bis hierher hatte jedes Feld (`Meshgenesisansicht`) seinen eigenen `WebGLRenderer` — auf der Jobseite 16 Kontexte, so viele, wie Chrome je Seite zulässt. Jeder Kontext lädt jedes
 * Bild selbst hoch: die Genesis-Figuren in Ziel und Ergebnis teilen sich die Texturen (`Genesis9texturen`), auf der Grafikkarte lagen sie trotzdem einmal je Feld. Gemessen 19.10.2026
 * (Damira0, Ansicht „Textur“, zwei Genesis-Felder im Bild, 22 Bilder neu hochgeladen): 2,5–3,8 s Hauptfaden für EIN Neuzeichnen beider Felder.
 *
 * Jetzt zeichnet ein Renderer abseits der Seite in den Ausschnitt unten links seiner Leinwand (so groß wie das Feld) und kopiert das Bild in die 2D-Leinwand des Felds
 * (`drawImage` gleich nach dem Zeichnen, noch im selben Takt — der Zeichenpuffer ist dann noch gültig, `preserveDrawingBuffer` braucht es nicht). Ein Bild geht damit einmal auf die
 * Grafikkarte, egal in wie vielen Feldern es steht; Geometrien und Materialien, die die Felder teilen (`Meshgenesisgemeinsam`), ebenso.
 */
import * as THREE from 'three';
import { Schnellanzeige } from '../gemeinsam/schnellanzeige.js';
import { Texturweg } from '../gemeinsam/texturweg.js';

export class Meshgenesiszeichenflaeche {
    static _renderer = null;
    static _groesse = new THREE.Vector2();

    static renderer() {
        if (!Meshgenesiszeichenflaeche._renderer) {
            const r = new THREE.WebGLRenderer({ antialias: true });
            r.setPixelRatio(Schnellanzeige.pixeldichte());           // 1 auf diesen Seiten (`<meta name="schnellanzeige">`)
            r.setScissorTest(true);                                   // Löschen nur im Ausschnitt des Felds
            Texturweg.anmelden(r);                                    // Weg B lädt über diesen Renderer hoch, Weg C prüft hier S3TC (Einstellungen → Mesh-Genesis)
            // Keine Logs je Programm beim ersten Gebrauch (23.11.2026, Edgar: „löse das“): `getProgramInfoLog`/`getShaderInfoLog` fragen den GPU-Prozess synchron und warten hinter
            // allen Uploads dort — Bilder von 109–138 ms nach fertig gemeldeten Programmen, mit der Prüfung Zeichnen 145 ms gegen 45 ms ohne (iphone_mit_lidar, je ein Lauf). Fehler
            // meldet `_pruefen`, sobald `vorbereiten` ein Programm fertig sieht.
            r.debug.checkShaderErrors = false;
            Meshgenesiszeichenflaeche._renderer = r;
        }
        return Meshgenesiszeichenflaeche._renderer;
    }

    /**
     * Shader bauen lassen, ohne zu zeichnen (22.11.2026, Ladezeit /foto-genesis/test/zauberer_kleidungsregeln_kopie_48/: das erste Bild des Ergebnisfelds hielt den Hauptfaden 0,6–1,1 s,
     * im Profil davon `onFirstUse`/`getProgramInfoLog` 300–470 ms — three wartet beim ersten Gebrauch, bis der Treiber das Programm gebunden hat). `malen` läuft einmal mit einem
     * `render`, das nur `compile` ruft — derselbe Zustand wie beim Zeichnen (Tone-Mapping von `Studiolicht`, Lichter) —, dann wird gewartet, bis jedes Programm fertig ist
     * (`KHR_parallel_shader_compile`, wie `WebGLRenderer.compileAsync`). Das Ersatzmaterial (`overrideMaterial`) übergeht `compile`; es baut beim Zeichnen wie bisher.
     * 23.11.2026 (Edgar: „löse das“ — lange Bilder beim Laden): nur `objekte` (`zuBauen`), je Durchgang nur die, die er zeichnet (Ebenen der Kamera) — vorher die ganze Szene in jedem
     * Durchgang, auch Unsichtbares und Netze anderer Ebenen (jedes mit dem Tone-Mapping des falschen Durchgangs: Programme, die nie zeichnen). Ein Durchgang mit Ersatzmaterial baut nichts.
     * `frist` (performance.now()): länger wird nicht gewartet — ein Feld, dessen Materialien sich dauernd ändern, zeichnete sonst gar nicht (`zuBauen`).
     * Gebaut wird in Häppchen von `JE_AUFGABE` Netzen je Aufgabe (beim ersten Bild der Testfigur 41 Programme, 46–59 ms in einem Stück); bei neuen Netzen gehen danach ihre Felder auf die
     * Karte, eines je Aufgabe (`_hochladen`) — sonst im ersten Zeichnen alle zusammen (das Haar mit 2,1 Mio. Punkten: ~96 MB, Bild von 155–171 ms).
     * @returns {Promise|null} null ohne `KHR_parallel_shader_compile`, wenn alles schon fertig ist oder die Frist vorbei (dann wird gleich gezeichnet)
     */
    static vorbereiten(malen, objekte, frist = Infinity) {
        const r = Meshgenesiszeichenflaeche.renderer(), Z = Meshgenesiszeichenflaeche;
        if (!r.extensions.get('KHR_parallel_shader_compile')) return null;
        const reste = [...objekte], offen = new Set(), hoch = objekte.neu ? Z._hochzuladen(objekte) : [];
        const bauen = () => Z._bauen(r, malen, reste.splice(0, Z.JE_AUFGABE), offen);
        const fertige = () => {
            for (const m of offen) {
                const p = r.properties.get(m).currentProgram;
                if (p?.isReady() !== false) { Z._pruefen(r, p); offen.delete(m); }
            }
        };
        bauen();
        fertige();
        if (!reste.length && !hoch.length && (!offen.size || performance.now() >= frist)) return null;
        return (async () => {
            while (reste.length) { await Texturweg.naechsteAufgabe(); bauen(); }
            for (const a of hoch) { await Texturweg.naechsteAufgabe(); Z._hochladen(r, a); }
            for (fertige(); offen.size && performance.now() < frist; fertige()) await new Promise(weiter => setTimeout(weiter, 10));
        })();
    }

    static JE_AUFGABE = 6;
    static _geprueft = new WeakSet();

    /** Statt three's Prüfung (`checkShaderErrors` aus): ist das fertige Programm gebunden? Die Logs nur im Fehlerfall — die Shader sind dann noch da (three löscht sie beim ersten Gebrauch). */
    static _pruefen(r, programm) {
        if (!programm?.program || Meshgenesiszeichenflaeche._geprueft.has(programm)) return;
        Meshgenesiszeichenflaeche._geprueft.add(programm);
        const gl = r.getContext();
        if (gl.getProgramParameter(programm.program, gl.LINK_STATUS) !== false) return;
        console.error(`Meshgenesiszeichenflaeche: Shader „${programm.name}“ nicht gebunden — ${gl.getProgramInfoLog(programm.program)}\n`
            + `Vertex: ${gl.getShaderInfoLog(programm.vertexShader)}\nFragment: ${gl.getShaderInfoLog(programm.fragmentShader)}`);
    }

    /** `teil` bauen: `malen` mit einem `render`, das nur `compile` ruft, je Durchgang nur die Netze seiner Ebenen; die Materialien kommen in `offen`. */
    static _bauen(r, malen, teil, offen) {
        const zeichnen = r.render;
        r.render = (szene, kamera) => {
            if (szene.overrideMaterial) return;
            for (const o of teil) if (o.layers.test(kamera.layers)) for (const m of r.compile(o, kamera, szene)) offen.add(m);
        };
        try {
            malen(r);
        } finally {
            r.render = zeichnen;
        }
        // `compile` erhöht bei durchsichtigen zweiseitigen Materialien die Fassung (es baut Vorder- und Rückseite) — gemerkt wird die Fassung danach, sonst gälte es als geändert
        for (const m of offen) Meshgenesiszeichenflaeche._gebaut.set(m, m.version);
    }

    /** Attribut → Fassung, mit der `_hochladen` es auf die Karte gab. */
    static _hochgeladen = new WeakMap();

    /** Die Felder (ohne Index) der Netze, die noch nicht oben sind. */
    static _hochzuladen(objekte) {
        const aus = new Set();
        for (const o of objekte) for (const a of Object.values(o.geometry?.attributes ?? {})) if (Meshgenesiszeichenflaeche._hochgeladen.get(a) !== a.version) aus.add(a);
        return [...aus];
    }

    /**
     * Ein Feld auf die Karte, ohne zu zeichnen: three lädt jedes Attribut einmal hoch, wenn ein Netz damit ins Bild kommt (`WebGLObjects.update`, je Attributobjekt gemerkt) — hier ein
     * Hilfsnetz mit unsichtbarem Material (kein Programm, kein Zeichnen) und diesem Feld als Lage; das echte Netz findet es danach oben. Den Index lädt three erst beim Zeichnen
     * (`WebGLBindingStates`, ein Indexpuffer darf in WebGL kein anderes Ziel gehabt haben) — er bleibt dort.
     */
    static _hochladen(r, attribut) {
        const h = Meshgenesiszeichenflaeche._helfer ??= Meshgenesiszeichenflaeche._helferBauen();
        h.geo.setAttribute('position', attribut);
        const loeschen = r.autoClear;
        r.autoClear = false;
        try {
            r.render(h.szene, h.kamera);
        } finally {
            r.autoClear = loeschen;
            h.geo.deleteAttribute('position');          // das Hilfsnetz hält das Feld nicht fest
        }
        Meshgenesiszeichenflaeche._hochgeladen.set(attribut, attribut.version);
    }

    static _helferBauen() {
        const geo = new THREE.BufferGeometry();
        geo.boundingSphere = new THREE.Sphere();          // sonst rechnet three sie zum Sortieren über das Feld
        const netz = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ visible: false }));
        netz.frustumCulled = false;
        const szene = new THREE.Scene();
        szene.add(netz);
        return { geo, szene, kamera: new THREE.PerspectiveCamera() };
    }

    /** So lange darf ein Feld höchstens auf Programme geänderter Materialien warten (neue Netze warten, bis sie fertig sind). */
    static FRIST_MS = 300;

    /** Material → seine Fassung (`version`), als `vorbereiten` es zuletzt gebaut hat. */
    static _gebaut = new WeakMap();

    /**
     * Die sichtbaren Netze in `szene`, deren Programm vor dem Zeichnen gebaut werden soll (Set): die, die dieses Feld noch nie gezeichnet hat (`gesehen`, WeakSet je Feld, merkt sie
     * gleich mit) — nicht „Material ohne Programm“: die Materialien teilen sich die Felder (`Meshgenesisgemeinsam`), ein `SkinnedMesh` braucht aber ein anderes Programm als ein `Mesh`
     * mit demselben Material (gesehen 22.11.2026: so griff das Vorbauen nicht) —, dazu die, deren Material sich seit dem letzten Zeichnen geändert hat (Fassung ≠ der des Renderers und
     * ≠ der zuletzt gebauten). 23.11.2026 (Edgar: „löse das“): kommen Normal-, Rauheits- oder Glanzkarte nach, braucht das Material ein neues Programm, und three wartete beim Zeichnen
     * darauf (`onFirstUse`/`getProgramInfoLog`, Bilder von 64–208 ms an iphone_mit_lidar). Der erste Versuch mit `material.version` allein (23.11.2026 mittags) wartete bei JEDER
     * Änderung, auch wenn das Programm blieb — das Feld zeichnete 1,8 s nicht; jetzt wartet `vorbereiten` nur, solange ein Programm wirklich noch übersetzt wird, und bei geänderten
     * Materialien höchstens `FRIST_MS` (ohne Frist stand das Feld beim Laden 2,5 s, weil die Bilder der Figur einzeln kamen; seitdem setzt `Genesis9texturzaehler` sie je Material gemeinsam ein).
     */
    static zuBauen(szene, gesehen) {
        const r = Meshgenesiszeichenflaeche.renderer(), aus = new Set(), gebaut = Meshgenesiszeichenflaeche._gebaut;
        const geaendert = m => m.version !== r.properties.get(m).__version && m.version !== gebaut.get(m);
        aus.neu = false;          // ein neues Netz dabei: dann ohne Frist warten (`vorbereiten`)
        szene.traverseVisible(o => {
            if (!o.material) return;
            const neu = !gesehen.has(o);
            if (neu) gesehen.add(o);
            aus.neu ||= neu;
            if (neu || (Array.isArray(o.material) ? o.material.some(geaendert) : geaendert(o.material))) aus.add(o);
        });
        return aus;
    }

    /**
     * Ein Bild für ein Feld.
     * @param {HTMLCanvasElement} leinwand die 2D-Leinwand des Felds @param {number} breite @param {number} hoehe Größe des Felds in CSS-Pixeln
     * @param {number} grund Farbe des Grunds @param {(r: THREE.WebGLRenderer) => void} malen zeichnet die Durchgänge des Felds (Ausschnitt und Grund sind gesetzt)
     */
    static zeichnen(leinwand, breite, hoehe, grund, malen) {
        const r = Meshgenesiszeichenflaeche.renderer(), jetzt = r.getSize(Meshgenesiszeichenflaeche._groesse);
        if (jetzt.x < breite || jetzt.y < hoehe) r.setSize(Math.max(jetzt.x, breite), Math.max(jetzt.y, hoehe), false);
        r.setViewport(0, 0, breite, hoehe);
        r.setScissor(0, 0, breite, hoehe);
        r.setClearColor(grund, 1);
        malen(r);
        const quelle = r.domElement, dichte = r.getPixelRatio();
        const b = Math.floor(breite * dichte), h = Math.floor(hoehe * dichte);
        if (leinwand.width !== b || leinwand.height !== h) Object.assign(leinwand, { width: b, height: h });
        // WebGL zählt von unten, die 2D-Leinwand von oben: der Ausschnitt liegt unten in der Quelle.
        leinwand.getContext('2d', { alpha: false }).drawImage(quelle, 0, quelle.height - h, b, h, 0, 0, b, h);
    }
}
