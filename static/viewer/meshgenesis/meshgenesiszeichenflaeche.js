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
            Meshgenesiszeichenflaeche._renderer = r;
        }
        return Meshgenesiszeichenflaeche._renderer;
    }

    /**
     * Shader bauen lassen, ohne zu zeichnen (22.11.2026, Ladezeit /foto-genesis/test/zauberer_kleidungsregeln_kopie_48/: das erste Bild des Ergebnisfelds hielt den Hauptfaden 0,6–1,1 s,
     * im Profil davon `onFirstUse`/`getProgramInfoLog` 300–470 ms — three wartet beim ersten Gebrauch, bis der Treiber das Programm gebunden hat). `malen` läuft einmal mit einem
     * `render`, das nur `compile` ruft — derselbe Zustand wie beim Zeichnen (Tone-Mapping von `Studiolicht`, Lichter) —, dann wird gewartet, bis jedes Programm fertig ist
     * (`KHR_parallel_shader_compile`, wie `WebGLRenderer.compileAsync`). Das Ersatzmaterial (`overrideMaterial`) übergeht `compile`; es baut beim Zeichnen wie bisher.
     * @returns {Promise|null} null ohne `KHR_parallel_shader_compile` (dann wird wie bisher gleich gezeichnet)
     */
    static vorbereiten(malen) {
        const r = Meshgenesiszeichenflaeche.renderer();
        if (!r.extensions.get('KHR_parallel_shader_compile')) return null;
        const offen = new Set(), zeichnen = r.render;
        r.render = (szene, kamera) => { for (const m of r.compile(szene, kamera)) offen.add(m); };
        try {
            malen(r);
        } finally {
            r.render = zeichnen;
        }
        return new Promise(fertig => {
            const pruefen = () => {
                for (const m of offen) if (r.properties.get(m).currentProgram?.isReady() !== false) offen.delete(m);
                if (offen.size) setTimeout(pruefen, 10);
                else fertig();
            };
            pruefen();
        });
    }

    /**
     * Steht in `szene` ein sichtbares Netz, das dieses Feld noch nie gezeichnet hat (`gesehen`, WeakSet je Feld)? Nicht „Material ohne Programm“: die Materialien teilen sich die Felder
     * (`Meshgenesisgemeinsam`), ein `SkinnedMesh` braucht aber ein anderes Programm als ein `Mesh` mit demselben Material (gesehen 22.11.2026: so griff das Vorbauen nicht). Merkt sich
     * die Netze gleich mit. Nicht auch Materialien, die ihr Programm wechseln (versucht 23.11.2026 mit `material.version`): seit die Bilder je Aufgabe einzeln kommen (`Texturweg`),
     * ändert sich dauernd eines, und das Feld zeichnete 1,8 s lang gar nicht, weil es immer wieder auf das Vorbauen wartete.
     */
    static neueNetze(szene, gesehen) {
        let neu = false;
        szene.traverseVisible(o => {
            if (!o.material || gesehen.has(o)) return;
            gesehen.add(o);
            neu = true;
        });
        return neu;
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
