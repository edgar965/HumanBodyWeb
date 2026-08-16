/**
 * Musterzustand — was der Schnittmuster-Editor gerade bearbeitet.
 *
 * WARUM eine Klasse (Umbau 16.08.2026): pattern_editor.js hatte 392 Zeilen und
 * dreizehn lose Modulvariablen — das gewaehlte Muster, die aktive Flaeche, der
 * Bearbeitungsmodus, Auswahl, Verschiebung, Zoom, Ziehzustand. Beim Aufteilen
 * bleibt sonst die Haelfte davon auf der falschen Seite, und aus einem anderen
 * Modul laesst sich eine importierte Bindung ohnehin nicht beschreiben.
 */

export class Musterzustand {
    /** {panels: {}, stitches: []} — das bearbeitete Schnittmuster. */
    static pePattern = { panels: {}, stitches: [] };
    static peActivePanel = null;
    /** 'select' | 'add' | 'stitch' | … */
    static peMode = 'select';
    static peSelectedVertex = null;
    static peSelectedEdge = null;
    static peStitchFirst = null;
    /** Verschiebung der Ansicht in Bildpunkten. */
    static pePan = { x: 144, y: 200 };
    static peZoom = 2.0;
    static peDragging = null;
    static pePanning = false;
    static pePanStart = null;
    static peLastMouse = { x: 0, y: 0 };
}
