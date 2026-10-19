/**
 * Mesh3daizeichenflaeche — EIN WebGL-Kontext für alle Felder der Seiten „Mesh3D-AI“ (19.10.2026).
 *
 * Bis hierher hatte jedes Feld (`Mesh3daiansicht`) seinen eigenen `WebGLRenderer` — auf der Jobseite 16 Kontexte, so viele, wie Chrome je Seite zulässt. Jeder Kontext lädt jedes
 * Bild selbst hoch: die Genesis-Figuren in Ziel und Ergebnis teilen sich die Texturen (`Genesis9texturen`), auf der Grafikkarte lagen sie trotzdem einmal je Feld. Gemessen 19.10.2026
 * (Damira0, Ansicht „Textur“, zwei Genesis-Felder im Bild, 22 Bilder neu hochgeladen): 2,5–3,8 s Hauptfaden für EIN Neuzeichnen beider Felder.
 *
 * Jetzt zeichnet ein Renderer abseits der Seite in den Ausschnitt unten links seiner Leinwand (so groß wie das Feld) und kopiert das Bild in die 2D-Leinwand des Felds
 * (`drawImage` gleich nach dem Zeichnen, noch im selben Takt — der Zeichenpuffer ist dann noch gültig, `preserveDrawingBuffer` braucht es nicht). Ein Bild geht damit einmal auf die
 * Grafikkarte, egal in wie vielen Feldern es steht; Geometrien und Materialien, die die Felder teilen (`Mesh3daigemeinsam`), ebenso.
 */
import * as THREE from 'three';
import { Schnellanzeige } from '../gemeinsam/schnellanzeige.js';
import { Texturweg } from '../gemeinsam/texturweg.js';

export class Mesh3daizeichenflaeche {
    static _renderer = null;
    static _groesse = new THREE.Vector2();

    static renderer() {
        if (!Mesh3daizeichenflaeche._renderer) {
            const r = new THREE.WebGLRenderer({ antialias: true });
            r.setPixelRatio(Schnellanzeige.pixeldichte());           // 1 auf diesen Seiten (`<meta name="schnellanzeige">`)
            r.setScissorTest(true);                                   // Löschen nur im Ausschnitt des Felds
            Texturweg.anmelden(r);                                    // Weg B lädt über diesen Renderer hoch, Weg C prüft hier S3TC (Einstellungen → Mesh3D-AI)
            Mesh3daizeichenflaeche._renderer = r;
        }
        return Mesh3daizeichenflaeche._renderer;
    }

    /**
     * Ein Bild für ein Feld.
     * @param {HTMLCanvasElement} leinwand die 2D-Leinwand des Felds @param {number} breite @param {number} hoehe Größe des Felds in CSS-Pixeln
     * @param {number} grund Farbe des Grunds @param {(r: THREE.WebGLRenderer) => void} malen zeichnet die Durchgänge des Felds (Ausschnitt und Grund sind gesetzt)
     */
    static zeichnen(leinwand, breite, hoehe, grund, malen) {
        const r = Mesh3daizeichenflaeche.renderer(), jetzt = r.getSize(Mesh3daizeichenflaeche._groesse);
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
