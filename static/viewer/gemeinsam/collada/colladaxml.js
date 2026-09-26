/**
 * Kleinstwerkzeuge für den Collada-Schreiber — von allen Teilen gebraucht.
 */

export function xmlEsc(text) {
    return String(text)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/** Zahlenfolge -> ein String, sechs Nachkommastellen, `-0` als `0`. */
export function zahlen(werte) {
    return Array.from(werte, n => (n === 0 ? 0 : n).toFixed(6)).join(' ');
}

/** Ein Name als Collada-`sid`/`id`-taugliches ASCII — Leerzeichen etc. raus. */
export function reinerName(name, ersatz) {
    const sauber = String(name || '').trim().replace(/[^\w-]/g, '_');
    return sauber || ersatz;
}

/**
 * `THREE.Matrix4` -> Collada-Reihenfolge (ZEILENweise). Three hält
 * `.elements` SPALTENweise (`e[0..3]` = erste Spalte) — Collades `<matrix>`
 * und die Bind-Matrizen im Skin-Controller sind Zeile für Zeile.
 */
export function zeilenMajor(mat4) {
    if (!mat4) return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
    const e = mat4.elements;
    return [
        e[0], e[4], e[8], e[12],
        e[1], e[5], e[9], e[13],
        e[2], e[6], e[10], e[14],
        e[3], e[7], e[11], e[15],
    ];
}
