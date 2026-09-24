/**
 * Bildtakt — wie viele Bilder der Abspielkopf in diesem Zeitschritt weitergeht.
 *
 * WARUM (Edgar, 13.09.2026: „die Play-Geschwindigkeit stimmt nicht, die
 * Normalgeschwindigkeit ist viel zu schnell, bei 0,5 ist es viel zu langsam"):
 * Die Schleife rundete JEDEN Schritt einzeln — `Math.round(dt · fps · Tempo)`.
 * Bei 60 Hz und 30 Bildern je Sekunde sind das 0,5 Bilder je Schritt: JavaScript
 * rundet 0,5 AUF, also ein Bild je Schritt = 60 Bilder je Sekunde, doppeltes
 * Tempo. Bei Tempo 0,5 sind es 0,25 → 0, der Kopf steht. Bei 144 Hz stand er
 * auch bei Tempo 1 (0,21 → 0). Das Tempo hing also am Monitor.
 *
 * Der Bruchteil wird jetzt mitgeführt: Was in diesem Schritt kein ganzes Bild
 * ergibt, bleibt als Rest für den nächsten. Über eine Sekunde kommen so genau
 * fps · Tempo Bilder zusammen, gleich bei welcher Bildwiederholrate. Ohne
 * Importe — der Test rechnet in Node (`test_js_bildtakt`).
 */
export class Bildtakt {
    /** Gleitkomma-Rest, der nicht als fehlendes Bild zählen soll. */
    static TOLERANZ = 1e-9;

    /** Angesammelter Bruchteil eines Bildes (0 ≤ rest < 1). */
    rest = 0;

    /**
     * Ganze Bilder für diesen Schritt; der Bruchteil bleibt in `rest`.
     * @param {number} dt    Sekunden seit dem letzten Schritt
     * @param {number} fps   Bilder je Sekunde des Projekts
     * @param {number} tempo Abspieltempo (1 = normal)
     */
    bilder(dt, fps, tempo) {
        this.rest += dt * fps * tempo;
        // 144 × (30/144) ist in Gleitkomma 29,999…; die Toleranz macht daraus 30.
        const ganz = Math.floor(this.rest + Bildtakt.TOLERANZ);
        this.rest = Math.max(0, this.rest - ganz);
        return ganz;
    }

    /** Nach einem Sprung oder Stopp fängt der Bruchteil bei 0 an. */
    zuruecksetzen() {
        this.rest = 0;
    }
}
