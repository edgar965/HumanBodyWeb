/**
 * Zeiten — die Wartezeiten der Oberfläche an einer Stelle.
 *
 * Umbau 16.08.2026: In 31 `setTimeout`/`setInterval`-Aufrufen stand die Zeit als
 * nackte Zahl im Code. Zwei Dinge fielen dabei auf:
 *
 *  * Dieselbe Sache hatte verschiedene Werte: Der WebSocket der Viewer-Seite
 *    verbindet nach 2000 ms neu, der der Ergebnisseite nach 3000 ms — ohne
 *    Grund, es ist dieselbe Lage.
 *  * Sechsmal dasselbe "Knopf zeigt kurz Gespeichert, dann wieder normal" mit
 *    1500 ms, jedes Mal neu geschrieben (siehe `Knopfmeldung`).
 *
 * Wer eine Zeit ändern will, findet sie hier — und sieht, welche anderen
 * dieselbe Bedeutung haben.
 */
export class Zeiten {

    /** Ein Knopf zeigt kurz eine Bestätigung, dann wieder seine Beschriftung. */
    static BESTAETIGUNG_MS = 1500;

    /** Nach dem Aufbau der Figur wird ein Bildschirmfoto gesichert. */
    static FOTO_MS = 500;

    /** Abgerissene WebSocket-Verbindung erneut versuchen. */
    static VERBINDEN_MS = 2000;

    /** Ein neu gewählter Eintrag wird in den sichtbaren Bereich gerollt. */
    static ROLLEN_MS = 50;

    /** Kleidung und Haare erst nachladen, wenn der Körper steht. */
    static NACHLADEN_MS = 800;

    /** Kurze Pause in Warteschleifen, die auf ein Netz oder Modell warten. */
    static WARTESCHRITT_MS = 200;

    /** Pause, bevor ein Bild aufgenommen oder ein Schritt weitergeht. */
    static BILDPAUSE_MS = 500;

    /** Eine Sekunde — Wartezeit, bis der Server eine Datei geschrieben hat. */
    static SEKUNDE_MS = 1000;

    /** Ein erzeugter Download-Verweis wird danach wieder freigegeben. */
    static DOWNLOAD_MS = 2000;

    /** Fortschritt eines Serverlaufs abfragen. */
    static FORTSCHRITT_MS = 500;

    /** Sammelzeit, bevor eine Liste neu gebaut wird. */
    static SAMMELN_MS = 100;

    /** Kurz warten, bis eine Einstellung im DOM angekommen ist. */
    static NACHZIEHEN_MS = 200;
}
