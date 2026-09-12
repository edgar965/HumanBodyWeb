import { Startbericht } from './startbericht.js';

/**
 * Wo die Zeit beim Seitenaufbau hingeht — gemessen, nicht geraten.
 *
 * BEFUND (Edgar, 10.09.2026): „die Ladezeit http://127.0.0.1:8081/humanbody/
 * scene/ ist bei mehr als 15 Sekunden, alleine mehr als 10 s bis das UI ohne
 * Modell aufgebaut wird."
 *
 * WARUM ES DAFÜR EIN WERKZEUG BRAUCHT
 * ===================================
 * Von außen war die Ursache nicht zu finden. Gemessen wurde: Der Server
 * liefert die Seite in 26 ms, das HTML ist nur 159 KB mit 1.698 Tags, und
 * kein Endpunkt braucht länger als 145 ms. Nichts davon erklärt zehn
 * Sekunden — die Zeit entsteht im Browser, verteilt über Dutzende
 * Abschnitte, und keiner davon war benannt.
 *
 * WAS SIE MISST
 * =============
 * `performance.now()` um einen Abschnitt. Gibt der Abschnitt ein Promise
 * zurück, wird zusätzlich seine volle Dauer nachgetragen — ohne das misst
 * man bei einer `async`-Funktion nur den Weg bis zum ersten `await`. Genau
 * das ist am 10.09.2026 passiert: Acht Panel-Aufbauten standen mit „1 ms"
 * im Bericht, obwohl einer davon 21.334 DOM-Elemente baute.
 *
 * Dazu ein `longtask`-Beobachter: Er zählt jede Aufgabe über 50 ms, also die
 * Zeit, in der die Seite auf nichts reagiert. „Wann ist das UI fertig?" ist
 * keine Frage nach der Summe der Abschnitte — sie laufen parallel —, sondern
 * danach, wann der Hauptfaden wieder frei ist.
 *
 * Berichtet wird über `Startbericht`; dort steht auch, warum das Ergebnis in
 * den `localStorage` geht.
 */
export class Startmessung {

    /** Abstand zweier Nachfragen, ob die Seite zur Ruhe gekommen ist. */
    static TAKT_MS = 200;

    /** @type {{name: string, ms: number, wartend?: boolean}[]} */
    static _abschnitte = [];

    /** Aufgaben über 50 ms, vom Beobachter unten eingesammelt. */
    static _blockaden = [];

    /**
     * Einen Abschnitt messen: `Startmessung.um('Name', () => …)`.
     *
     * Gibt zurück, was die Funktion zurückgibt — so lässt sich ein Aufruf
     * einwickeln, ohne den Ablauf zu ändern. Wirft die Funktion, wird die
     * Zeit trotzdem vermerkt und der Fehler weitergereicht: Ein Abschnitt,
     * der abbricht, ist erst recht interessant.
     */
    static um(name, aufruf) {
        const start = performance.now();
        let ergebnis;
        try {
            ergebnis = aufruf();
            return ergebnis;
        } finally {
            Startmessung._abschnitte.push(
                { name, ms: performance.now() - start });
            // EIN PROMISE IST NICHT FERTIG, NUR WEIL DER AUFRUF ZURUECKKAM
            // (10.09.2026): Sieben der 26 Aufbauten sind `async`. Sie
            // standen alle mit „1 ms" im Bericht — gemessen war nur der Weg
            // bis zum ersten `await`. Der teure Teil (`loadAnimationUI`
            // baut 21.334 Elemente) lief danach und tauchte nirgends auf.
            // Das ist die Fehlerklasse aus `keine-unbelegten-zahlen.md`:
            // eine Zahl, die etwas anderes misst, als ihr Name sagt.
            if (ergebnis && typeof ergebnis.then === 'function') {
                ergebnis.then(
                    () => Startmessung._nachtragen(name, start),
                    () => Startmessung._nachtragen(name, start));
            }
        }
    }

    /** Die volle Dauer eines `async`-Abschnitts, wenn sein Promise fällt. */
    static _nachtragen(name, start) {
        Startmessung._abschnitte.push({
            name: `${name} (bis fertig)`,
            ms: performance.now() - start,
            wartend: true,
        });
    }

    /** Dasselbe für einen Abschnitt, auf den hier gewartet wird. */
    static async umAsync(name, aufruf) {
        const start = performance.now();
        try {
            return await aufruf();
        } finally {
            Startmessung._abschnitte.push(
                { name, ms: performance.now() - start, wartend: true });
        }
    }

    /** Einen fertig gemessenen Abschnitt von außen eintragen. */
    static eintragen(name, ms, wartend = false) {
        Startmessung._abschnitte.push({ name, ms, wartend });
    }

    /** Den Bericht jetzt schreiben. */
    static bericht() {
        return Startbericht.schreiben(Startmessung._abschnitte,
                                      Startmessung._blockaden);
    }

    /**
     * Berichten, sobald der Aufbau zur Ruhe gekommen ist.
     *
     * `starten()` ist zurück, lange bevor die Seite fertig ist: Die
     * `async`-Aufbauten laufen dann noch. Ein Bericht an dieser Stelle
     * meldete eine Zeit, die der Nutzer nie erlebt hat.
     *
     * RUHE HEISST: kein neuer Abschnitt UND keine neue lange Aufgabe. Erst
     * nur auf die Aufgaben zu sehen war falsch (10.09.2026) — ein Tab im
     * Hintergrund liefert gar keine `longtask`-Einträge, dort galt die Seite
     * sofort als fertig und der Bericht meldete drei Sekunden, wo die Arbeit
     * noch lief. Eine Messung, die im Hintergrund etwas anderes misst als im
     * Vordergrund, ist schlimmer als keine (`~/.claude/rules/zeit-messen.md`).
     */
    static berichtWennRuhig(ruheMs = 800, hoechstensMs = 30000) {
        const start = performance.now();
        let stand = Startmessung._stand();
        let seit = performance.now();
        const pruefen = () => {
            if (Startmessung._stand() !== stand) {
                stand = Startmessung._stand();
                seit = performance.now();
            }
            if (performance.now() - seit >= ruheMs
                || performance.now() - start >= hoechstensMs) {
                Startmessung.bericht();
                return;
            }
            setTimeout(pruefen, Startmessung.TAKT_MS);
        };
        setTimeout(pruefen, Startmessung.TAKT_MS);
    }

    static _stand() {
        return Startmessung._blockaden.length + Startmessung._abschnitte.length;
    }

    /**
     * Lange Aufgaben mitzählen.
     *
     * Muss beim MODULLADEN starten, nicht beim Aufbau: Was zwischen dem
     * ersten Skript und dem ersten Abschnitt blockiert, gehört genauso zur
     * wahrgenommenen Ladezeit.
     */
    static _blockadenBeobachten() {
        if (typeof PerformanceObserver === 'undefined') return;
        if (!PerformanceObserver.supportedEntryTypes?.includes('longtask')) return;
        try {
            new PerformanceObserver(liste => {
                for (const eintrag of liste.getEntries()) {
                    Startmessung._blockaden.push({
                        ab: Math.round(eintrag.startTime),
                        ms: Math.round(eintrag.duration),
                    });
                }
            }).observe({ type: 'longtask', buffered: true });
        } catch (fehler) {
            // stumm gewollt: Der Beobachter ist Diagnose, keine Funktion.
        }
    }
}

Startmessung._blockadenBeobachten();

// Von der Konsole aus abrufbar, ohne Import — der Nutzer soll die Zahlen
// ansehen können, ohne ein Modul zu kennen: `startmessung.letzte()` zeigt den
// letzten Lauf, `startmessung.reihe()` die letzten zwölf.
Startmessung.letzte = Startbericht.letzte;
Startmessung.reihe = Startbericht.reihe;
window.startmessung = Startmessung;
