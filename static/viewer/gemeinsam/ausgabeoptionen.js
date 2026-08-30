/**
 * Ausgabeoptionen — was bei einem Videoexport neben den Bilddaten mitgeht.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): Dieselben sechs Zuweisungen standen
 * in `bvh_studio/export1.js` und `scene/cloth_export.js`. Beide bauen eine
 * Nutzlast aus Netz- und Animationsdaten und hängen danach dieselben sechs
 * Felder an.
 *
 * DIE NAMEN SIND DRAHTFORMAT: `engine`, `quality`, `width`, `height`,
 * `output_dir`, `filename` liest der Server (`core/api/studio_video.py` und
 * die Kleider-Endpunkte). Ein Tippfehler in einem davon fällt nicht auf — der
 * Server nimmt für ein fehlendes Feld seine Vorgabe und rendert klaglos in
 * falscher Größe oder ins falsche Verzeichnis.
 *
 * LEERE ANGABEN BLEIBEN DRAUSSEN, und das ist der Punkt bei `output_dir` und
 * `filename`: Ein leerer String ist etwas anderes als „nicht gesetzt". Der
 * Server erzeugt bei fehlendem Feld einen Namen aus Zeitstempel und Auftrag;
 * mit einem leeren String schreibt er in eine Datei ohne Namen.
 */
export class Ausgabeoptionen {
    /**
     * Die Optionen an eine fertige Nutzlast hängen.
     *
     * @param {Object} nutzlast wird VERÄNDERT und zurückgegeben
     * @param {Object} wahl {engine, quality, width, height, outputDir, filename}
     * @returns {Object} dieselbe Nutzlast
     */
    static anhaengen(nutzlast, { engine, quality, width, height,
                                 outputDir, filename } = {}) {
        nutzlast.engine = engine;
        nutzlast.quality = quality;
        nutzlast.width = width;
        nutzlast.height = height;
        if (outputDir) nutzlast.output_dir = outputDir;
        if (filename) nutzlast.filename = filename;
        return nutzlast;
    }
}
