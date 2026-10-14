/**
 * Mesh3dnetztasten — Strg+Z und Strg+Y im Netzwerkzeug der Jobseite Mesh-3D (14.10.2026, Edgar: „ich brauche auch einen Undo-Button für Löschen, bzw. Strg+Z und Strg+Y für Löschen“).
 *
 * Zurücknehmen und Wiederholen kann die Auswahl (`Mesh3dnetzwahl.zurueck/wiederholen`) schon für jeden Schritt, auch für „Entfernen“; bis dahin hörte aber nur die Leinwand auf Strg+Z (nur mit Fokus dort), und ein
 * Wiederholen gab es nicht. Hier steht, welche Taste was bedeutet und wo sie gilt:
 *   Strg+Z (Mac: Cmd+Z)              zurück
 *   Strg+Y, Strg+Umschalt+Z          wiederholen
 * `seite` gilt auf der ganzen Seite, solange die Leiste sichtbar ist — nicht in Eingabefeldern (dort gehören die Tasten dem Feld).
 */
export class Mesh3dnetztasten {
    /** @returns {boolean} `true`, wenn die Taste dazu gehörte (und ausgeführt wurde) */
    static rueckgaengig(e, wahl) {
        if (!wahl || !(e.ctrlKey || e.metaKey) || e.altKey) return false;
        const taste = (e.key || '').toLowerCase();
        if (taste === 'y' || (taste === 'z' && e.shiftKey)) wahl.wiederholen();
        else if (taste === 'z') wahl.zurueck();
        else return false;
        return true;
    }

    /** Die Taste irgendwo auf der Seite: nur wenn die Leiste da ist, niemand sie schon bearbeitet hat und das Ziel kein Eingabefeld ist. */
    static seite(e, wahl, feld) {
        if (!wahl || !feld || feld.hidden || e.defaultPrevented) return false;
        const ziel = e.target;
        if (ziel && (ziel.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(ziel.tagName))) return false;
        return Mesh3dnetztasten.rueckgaengig(e, wahl);
    }
}
