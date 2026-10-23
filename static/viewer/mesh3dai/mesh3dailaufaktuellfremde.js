/**
 * Mesh3dailaufaktuellfremde — die Liste „Weitere Programme auf der GPU“ im Reiter „Lauf Aktuell“, ruhig gehalten (22.10.2026, Edgar: „die anzeige flackert, weil sich die Anzahl der Einträge
 * in dieser Tabelle ändert … etwas ruhiger, sodass sich nicht bei einem weiteren Eintrag das ganze UI flackert“).
 * Der Server meldet nur Programme über der Schwelle (200 MB oder 1 %, `Mesh3dailaufprozesse._fremde`); dwm, Code, System pendeln um 1 % und kamen und gingen bei jeder Abfrage —
 * die Karte am Ende der Seite änderte ihre Höhe, und wer unten stand, sah die ganze Seite springen. Darum:
 *   * ein Programm bleibt `HALTEN_S` nach seiner letzten Meldung stehen, blass und mit „unter der Schwelle“;
 *   * die Reihenfolge ist die des ersten Auftauchens (nicht nach Last — die tauschte die Zeilen);
 *   * die Karte steht immer, auch leer.
 * Der Zustand lebt so lange wie die Seite (statisch), ein Neuladen fängt leer an.
 */
export class Mesh3dailaufaktuellfremde {
    static HALTEN_S = 60;
    /** pid → {name, pid, gpu_mb, gpu_prozent, zuletzt, erst} */
    static gesehen = new Map();
    static zaehler = 0;

    /** → Einträge in fester Reihenfolge, je mit `aktiv` (jetzt über der Schwelle gemeldet). */
    static liste(fremde, jetzt) {
        for (const f of fremde || []) {
            const alt = this.gesehen.get(f.pid);
            this.gesehen.set(f.pid, { ...f, zuletzt: jetzt, erst: alt ? alt.erst : this.zaehler++ });
        }
        for (const [pid, f] of this.gesehen) {
            if (jetzt - f.zuletzt > this.HALTEN_S) this.gesehen.delete(pid);
        }
        return [...this.gesehen.values()].sort((a, b) => a.erst - b.erst).map((f) => ({ ...f, aktiv: f.zuletzt === jetzt }));
    }
}
