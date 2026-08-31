import { Musterzustand } from './muster_zustand.js';
import {
    _peHitControlPoint, _peHitEdge, _peHitVertex, peRender,
} from './muster_zeichnen.js';
import { fn } from '../gemeinsam/registrierung.js';

/**
 * Musterzeichenflaeche — die Maus auf der 2D-Fläche des Muster-Editors.
 *
 * WARUM EIGENE DATEI (31.08.2026): `_peInitCanvas()` in
 * `pattern_editor.js` war EINE Funktion mit 103 Zeilen, die sechs
 * Ereignisse bediente — Klicken, Ziehen, Loslassen, Verlassen,
 * Doppelklick und Rad. Die Datei stand mit 314 Zeilen über der Faustregel
 * (`dateigroesse`), die Funktion über der von `jsfunktionen`.
 *
 * KEIN RINGIMPORT: Die Bedienung braucht drei Rückrufe aus
 * `pattern_editor.js` (Teileliste, Nahtliste, Modusknöpfe). Sie direkt zu
 * importieren gäbe `pattern_editor → muster_maus → pattern_editor` — einen
 * Zyklus, und `abhaengigkeiten` steht bei 0. Stattdessen kommen sie über
 * das Namensregister `fn`, das genau dafür da ist: `pattern_editor.js`
 * trägt sie beim Start ein, hier werden sie zur Laufzeit geholt.
 *
 * DIE ZUSTÄNDE liegen alle in `Musterzustand`; diese Klasse hält keinen
 * eigenen. Sie ist der Ereignisteil, nicht der Datenteil.
 */
export class Musterzeichenflaeche {

    /** Wie nah am ersten Punkt ein Klick das Teil schliesst (Bildpunkte). */
    static SCHLUSSNAEHE = 10;

    /** Grenzen der Vergrösserung — darunter/darüber ist nichts mehr zu sehen. */
    static ZOOM_MIN = 0.5;
    static ZOOM_MAX = 20;

    /** Wieviel ein Radschritt vergrössert. */
    static ZOOM_SCHRITT = 1.15;

    /** Wie weit ein Kontrollpunkt beim ersten Setzen von der Kante absteht. */
    static WOELBUNG = 5;

    /**
     * Alle Maus-Ereignisse an die Zeichenfläche hängen.
     *
     * @param leinwand das `<canvas>`; fehlt es, passiert nichts
     */
    static binden(leinwand) {
        if (!leinwand) return;
        leinwand.addEventListener('mousedown',
            (e) => Musterzeichenflaeche._drueckt(e));
        leinwand.addEventListener('mousemove',
            (e) => Musterzeichenflaeche._bewegt(e));
        for (const name of ['mouseup', 'mouseleave']) {
            leinwand.addEventListener(name,
                () => Musterzeichenflaeche._laesstLos());
        }
        leinwand.addEventListener('dblclick',
            (e) => Musterzeichenflaeche._doppelklick(e));
        leinwand.addEventListener('wheel',
            (e) => Musterzeichenflaeche._rad(e), { passive: false });
        leinwand.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    // ------------------------------------------------------------- Drücken

    static _drueckt(e) {
        const cx = e.offsetX;
        const cy = e.offsetY;
        // Mittlere Taste oder Strg+links schiebt die Fläche.
        if (e.button === 1 || (e.button === 0 && e.ctrlKey)) {
            Musterzustand.pePanning = true;
            Musterzustand.pePanStart = {
                x: e.clientX, y: e.clientY,
                px: Musterzustand.pePan.x, py: Musterzustand.pePan.y,
            };
            e.preventDefault();
            return;
        }
        if (e.button !== 0) return;
        if (Musterzustand.peMode === 'select') {
            Musterzeichenflaeche._waehlt(cx, cy);
        } else if (Musterzustand.peMode === 'draw') {
            Musterzeichenflaeche._zeichnet(cx, cy);
        } else if (Musterzustand.peMode === 'stitch') {
            Musterzeichenflaeche._naeht(cx, cy);
        }
    }

    static _waehlt(cx, cy) {
        // Reihenfolge zählt: Der Kontrollpunkt liegt ÜBER der Kante, der
        // Eckpunkt über beidem. Wer zuerst die Kante prüft, bekommt einen
        // Eckpunkt nie zu fassen.
        const kontrollpunkt = _peHitControlPoint(cx, cy);
        if (kontrollpunkt) {
            Musterzustand.peDragging = { type: 'cp', panel: kontrollpunkt.panel,
                                         edgeIndex: kontrollpunkt.edgeIndex };
            return;
        }
        const ecke = _peHitVertex(cx, cy);
        if (ecke) {
            Musterzustand.peSelectedVertex = ecke;
            Musterzustand.peSelectedEdge = null;
            Musterzustand.peActivePanel = ecke.panel;
            Musterzustand.peDragging = { type: 'vertex', panel: ecke.panel,
                                         index: ecke.index };
            peRender();
            fn.peUpdatePanelList?.();
            return;
        }
        const kante = _peHitEdge(cx, cy);
        if (kante) {
            Musterzustand.peSelectedEdge = kante;
            Musterzustand.peSelectedVertex = null;
            Musterzustand.peActivePanel = kante.panel;
            peRender();
            fn.peUpdatePanelList?.();
            return;
        }
        Musterzustand.peSelectedVertex = null;
        Musterzustand.peSelectedEdge = null;
        peRender();
    }

    static _zeichnet(cx, cy) {
        const teil = Musterzustand.pePattern.panels[Musterzustand.peActivePanel];
        if (!Musterzustand.peActivePanel || !teil) return;
        const [wx, wy] = fn.peCanvasToWorld(cx, cy);
        // Ab drei Ecken schliesst ein Klick nahe der ersten das Teil.
        if (teil.vertices.length >= 3) {
            const [fx, fy] = fn.peWorldToCanvas(...teil.vertices[0]);
            if (Math.hypot(cx - fx, cy - fy)
                    < Musterzeichenflaeche.SCHLUSSNAEHE) {
                teil.edges.push({ endpoints: [teil.vertices.length - 1, 0],
                                  curvature: null });
                teil.closed = true;
                Musterzustand.peMode = 'select';
                fn.peSetModeButtons?.();
                peRender();
                fn.peUpdatePanelList?.();
                return;
            }
        }
        const platz = teil.vertices.length;
        teil.vertices.push([wx, wy]);
        if (platz > 0) {
            teil.edges.push({ endpoints: [platz - 1, platz], curvature: null });
        }
        peRender();
    }

    static _naeht(cx, cy) {
        const kante = _peHitEdge(cx, cy);
        if (!kante) return;
        if (!Musterzustand.peStitchFirst) {
            Musterzustand.peStitchFirst = kante;
            Musterzustand.peSelectedEdge = kante;
            Musterzustand.peActivePanel = kante.panel;
            peRender();
            return;
        }
        const erste = Musterzustand.peStitchFirst;
        // Eine Naht verbindet ZWEI Teile — zweimal dasselbe Teil ergibt keine.
        if (kante.panel !== erste.panel) {
            Musterzustand.pePattern.stitches.push({
                panelA: erste.panel, edgeA: erste.index,
                panelB: kante.panel, edgeB: kante.index,
            });
        }
        fn.peUpdateStitchList?.();
        Musterzustand.peStitchFirst = null;
        Musterzustand.peSelectedEdge = null;
        peRender();
    }

    // ------------------------------------------------------------- Bewegen

    static _bewegt(e) {
        const cx = e.offsetX;
        const cy = e.offsetY;
        Musterzustand.peLastMouse = { x: cx, y: cy };
        if (Musterzustand.pePanning && Musterzustand.pePanStart) {
            const anfang = Musterzustand.pePanStart;
            Musterzustand.pePan.x = anfang.px + (e.clientX - anfang.x);
            Musterzustand.pePan.y = anfang.py + (e.clientY - anfang.y);
            peRender();
            return;
        }
        if (Musterzustand.peDragging) {
            const [wx, wy] = fn.peCanvasToWorld(cx, cy);
            const zug = Musterzustand.peDragging;
            const teil = Musterzustand.pePattern.panels[zug.panel];
            if (zug.type === 'vertex') {
                teil.vertices[zug.index] = [wx, wy];
            } else if (zug.type === 'cp') {
                teil.edges[zug.edgeIndex].curvature = [wx, wy];
            }
            peRender();
        }
        Musterzeichenflaeche._anzeigen(cx, cy);
    }

    static _anzeigen(cx, cy) {
        const anzeige = document.getElementById('pe-status');
        if (!anzeige) return;
        const [wx, wy] = fn.peCanvasToWorld(cx, cy);
        const stufe = Math.round(Musterzustand.peZoom / 2 * 100);
        anzeige.textContent = `${wx.toFixed(1)}, ${wy.toFixed(1)} cm`
            + `    ${stufe}%`;
    }

    static _laesstLos() {
        Musterzustand.peDragging = null;
        Musterzustand.pePanning = false;
        Musterzustand.pePanStart = null;
    }

    // -------------------------------------------------- Doppelklick und Rad

    /** Doppelklick auf eine Kante: Wölbung an oder aus. */
    static _doppelklick(e) {
        if (Musterzustand.peMode !== 'select') return;
        const kante = _peHitEdge(e.offsetX, e.offsetY);
        if (!kante) return;
        const teil = Musterzustand.pePattern.panels[kante.panel];
        const rand = teil.edges[kante.index];
        if (rand.curvature) {
            rand.curvature = null;
        } else {
            rand.curvature = Musterzeichenflaeche._kontrollpunkt(teil, rand);
        }
        peRender();
    }

    /**
     * Der Kontrollpunkt einer neu gewölbten Kante: auf der Mitte, um
     * `WOELBUNG` senkrecht nach aussen versetzt.
     */
    static _kontrollpunkt(teil, rand) {
        const a = teil.vertices[rand.endpoints[0]];
        const b = teil.vertices[rand.endpoints[1]];
        const dx = b[0] - a[0];
        const dy = b[1] - a[1];
        // `|| 1` faengt die Kante der Laenge 0 ab — sonst NaN, und der
        // Kontrollpunkt verschwindet spurlos aus dem Bild.
        const laenge = Math.hypot(dx, dy) || 1;
        const versatz = Musterzeichenflaeche.WOELBUNG;
        return [(a[0] + b[0]) / 2 + (-dy / laenge) * versatz,
                (a[1] + b[1]) / 2 + (dx / laenge) * versatz];
    }

    /** Rad: vergrössern um den Mauszeiger herum, nicht um die Bildmitte. */
    static _rad(e) {
        e.preventDefault();
        const cx = e.offsetX;
        const cy = e.offsetY;
        const [wx, wy] = fn.peCanvasToWorld(cx, cy);
        const schritt = e.deltaY < 0
            ? Musterzeichenflaeche.ZOOM_SCHRITT
            : 1 / Musterzeichenflaeche.ZOOM_SCHRITT;
        Musterzustand.peZoom = Math.max(
            Musterzeichenflaeche.ZOOM_MIN,
            Math.min(Musterzeichenflaeche.ZOOM_MAX,
                     Musterzustand.peZoom * schritt));
        // Der Weltpunkt unter dem Zeiger bleibt unter dem Zeiger.
        Musterzustand.pePan.x = cx - wx * Musterzustand.peZoom;
        Musterzustand.pePan.y = cy + wy * Musterzustand.peZoom;
        peRender();
    }
}
