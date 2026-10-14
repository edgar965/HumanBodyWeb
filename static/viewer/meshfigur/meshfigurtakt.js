/**
 * Meshfigurtakt — wann eine Bühne ein Bild zeichnet (12.10.2026).
 *
 * Edgar: „sobald ich klicke geht die GPU hoch auf 70 %“, dazu Klicks, die nie in der Seite ankamen. Die Bühnen (`Meshfigurbuehne`, `Mesh3dnetzbuehne`) zeichneten jedes Bild neu, solange der Reiter
 * sichtbar war, auch wenn sich nichts bewegte: zwei Leinwände mit je 3200 × 783 Pixeln, vierfach geglättet, eine Figur mit Haar und Kleidern und ein Netz mit 200.000 Flächen — gemessen
 * (`bilder_langsam` im client.log) 32–51 Bilder je Sekunde; eine Probe `nvidia-smi` bei offener Seite zeigte 36 % (Sichtbarkeit des Reiters in dem Moment unbekannt). Ein verdeckter Reiter zeichnet nicht
 * (Chrome hält `requestAnimationFrame` an), deshalb passt es zu Edgars Beobachtung, dass die Last stieg, wenn er ins Fenster klickte — belegt ist das nicht, es ist die naheliegende Erklärung.
 *
 * Jetzt zeichnet die Bühne mit voller Rate nur, solange jemand etwas tut — Eingabe irgendwo auf der Seite (Druck, Rad, Taste, Regler, bewegte Maus mit gedrückter Taste), die Kamera, die noch ausläuft
 * (`OrbitControls` meldet `change`), eine laufende Animation (die Animationsklasse ruft `wach()`), eine Größenänderung — und danach noch `WACH_MS`. Im Leerlauf kommt alle `LEERLAUF_MS` ein Bild: Was
 * unabhängig von Eingaben nachkommt (ein Netz, das fertig geladen ist, Haar, Kleider), erscheint damit höchstens 200 ms später, statt dass jemand daran denken muss, ein Bild anzufordern.
 * Nicht gemessen ist, wie weit die GPU-Last damit fällt (Edgars Seite muss neu geladen werden).
 */
export class Meshfigurtakt {
    /** Im Leerlauf ein Bild alle 200 ms (5 je Sekunde). */
    static LEERLAUF_MS = 200;
    /** So lange nach der letzten Eingabe läuft die volle Rate weiter (die Kamera läuft aus, ein Schalter lädt nach). */
    static WACH_MS = 3000;
    /** Beim Anlegen der Bühne: die ersten Bilder (Figur wird gebaut, Netz lädt) mit voller Rate. */
    static ANFANG_MS = 8000;

    constructor() {
        this._bis = performance.now() + Meshfigurtakt.ANFANG_MS;
        this._letztes = 0;
        const wach = () => this.wach();
        // Erfassungsphase: auch Ereignisse, deren Ziel `stopPropagation` ruft, wecken die Bühne.
        for (const art of ['pointerdown', 'wheel', 'keydown', 'input', 'change']) document.addEventListener(art, wach, { capture: true, passive: true });
        document.addEventListener('pointermove', ereignis => { if (ereignis.buttons) this.wach(); }, { capture: true, passive: true });
        document.addEventListener('visibilitychange', () => { if (!document.hidden) this.wach(); });
    }

    /** Die volle Rate für die nächsten `ms` (nie kürzer als eine schon laufende Frist). */
    wach(ms = Meshfigurtakt.WACH_MS) {
        this._bis = Math.max(this._bis, performance.now() + ms);
    }

    /** `true`, wenn JETZT ein Bild gezeichnet werden soll (und merkt sich den Zeitpunkt). */
    faellig() {
        const jetzt = performance.now();
        if (jetzt < this._bis || jetzt - this._letztes >= Meshfigurtakt.LEERLAUF_MS) {
            this._letztes = jetzt;
            return true;
        }
        return false;
    }
}
