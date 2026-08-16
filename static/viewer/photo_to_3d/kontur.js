/**
 * Umrisse weich zeichnen — geschlossene Kurve durch die Mittelpunkte der
 * Strecken, mit den gegebenen Punkten als Stützstellen.
 *
 * Umbau 16.08.2026: Es gab zwei Fassungen, `drawSmoothContour` und
 * `drawSmoothContourTransformed`, Zeile für Zeile gleich bis auf die
 * Umrechnung der Punkte. Jetzt eine Fassung; die einfache Form ist die mit der
 * Umrechnung "nichts ändern".
 */

/** Kurve durch die Punkte in den Pfad des Stifts legen. */
export function drawSmoothContourTransformed(stift, punkte, umrechnen) {
    if (punkte.length < 3) return;
    const p = umrechnen ? punkte.map(([x, y]) => umrechnen(x, y)) : punkte;
    const n = p.length;
    stift.beginPath();
    // Start ist die Mitte zwischen letztem und erstem Punkt — so schließt die
    // Kurve ohne Ecke.
    stift.moveTo((p[n - 1][0] + p[0][0]) / 2, (p[n - 1][1] + p[0][1]) / 2);
    for (let i = 0; i < n; i++) {
        const naechster = (i + 1) % n;
        stift.quadraticCurveTo(p[i][0], p[i][1],
                               (p[i][0] + p[naechster][0]) / 2,
                               (p[i][1] + p[naechster][1]) / 2);
    }
    stift.closePath();
}

export function drawSmoothContour(stift, punkte) {
    drawSmoothContourTransformed(stift, punkte, null);
}
