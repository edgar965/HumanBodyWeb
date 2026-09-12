/**
 * Was `Startmessung` gesammelt hat, lesbar machen und aufheben.
 *
 * Konsolenausgabe dauerhaft gewollt: Der Bericht ist die Antwort auf die Frage,
 * warum der Start so lange dauert, und muss auch ohne Debug-Schalter erscheinen.
 *
 * AUS `startmessung.js` HERAUSGELÖST (10.09.2026): Die Datei war auf 288
 * Zeilen gewachsen. Messen und Berichten sind auch zwei Aufgaben — die eine
 * läuft während des Seitenstarts und muss billig sein, die andere einmal
 * danach.
 *
 * WARUM DER BERICHT DEN TAB ÜBERLEBEN MUSS
 * ========================================
 * Ein ferngesteuerter Browser-Tab liegt immer im Hintergrund. Dort zeichnet
 * Chrome nicht: `first-contentful-paint` kommt nie, `longtask` wird nicht
 * gemeldet, Zeitgeber laufen gedrosselt. Am 10.09.2026 gemessen — derselbe
 * Seitenstart meldete im Hintergrund `erstesBild: null` und `blockiert: 0`,
 * im Vordergrund 712 ms und 559 ms. Wer im Hintergrund misst, misst also
 * genau das nicht, worum es geht.
 *
 * Deshalb legt der Bericht sich in den `localStorage`: Die Seite läuft im
 * Vordergrund, gelesen wird später — auch aus einem anderen Tab derselben
 * Herkunft. `Startbericht.reihe()` hält die letzten zwölf Läufe, weil ein
 * einzelner Wert nichts über die Streuung sagt (die lag beim Nachmessen
 * zwischen 3,9 und 6,5 Sekunden).
 */
export class Startbericht {

    /** Wo der letzte Bericht liegt. */
    static ABLAGE = 'humanbody_startmessung';

    /** Ab hier ist ein Abschnitt es wert, genannt zu werden. */
    static SCHWELLE_MS = 5;

    /**
     * Bericht in die Konsole schreiben und ablegen.
     *
     * Bewusst `console.info` und keine Protokoll-Klasse: Diese Zeile soll
     * auch dann erscheinen, wenn die Debug-Ausgabe abgeschaltet ist — sie
     * ist die Antwort auf „warum dauert das so lange?".
     *
     * @param abschnitte gemessene Abschnitte `{name, ms, wartend}`
     * @param blockaden lange Aufgaben `{ab, ms}`
     */
    static schreiben(abschnitte, blockaden) {
        const gesamt = Math.round(performance.now());
        const liste = abschnitte
            .filter(a => a.ms >= Startbericht.SCHWELLE_MS)
            .sort((a, b) => b.ms - a.ms);
        const summe = abschnitte.reduce((s, a) => s + a.ms, 0);
        const versteckt = document.visibilityState === 'hidden';
        console.info(
            `[Start] UI in ${gesamt} ms aufgebaut `
            + `(${abschnitte.length} Abschnitte, ${Math.round(summe)} ms gemessen)`
            + (versteckt
                ? ' — ACHTUNG: Tab lag im Hintergrund, er zeichnet dort nicht; '
                  + 'Wartezeiten, erstes Bild und Blockaden sind wertlos'
                : ''));
        for (const a of liste) {
            console.info(`[Start]   ${Math.round(a.ms).toString().padStart(6)} ms  `
                + `${a.name}${a.wartend ? '  (wartend)' : ''}`);
        }
        const blockiert = Math.round(blockaden.reduce((s, b) => s + b.ms, 0));
        console.info(`[Start] Hauptfaden ${blockiert} ms blockiert `
            + `(${blockaden.length} Aufgaben über 50 ms)`);

        const ergebnis = {
            gesamt, blockiert, versteckt,
            zeitpunkt: new Date().toISOString(),
            ...Startbericht.seitenzahlen(),
            abschnitte: liste.map(a => ({
                name: a.name, ms: Math.round(a.ms), wartend: !!a.wartend })),
            blockaden: blockaden.slice(0, 20),
        };
        Startbericht._ablegen(ergebnis);
        return ergebnis;
    }

    /**
     * Die Zahlen, die der Browser selbst führt.
     *
     * `erstesBild` (First Contentful Paint) beantwortet „das UI ist da" —
     * alles davor sieht der Nutzer als leere Seite. `module` zählt die
     * geladenen JS-Dateien: Am 10.09.2026 gemessen kostet JEDE Anfrage an
     * diesen Server 10–12 ms Grundaufwand, unabhängig vom Inhalt, und er
     * arbeitet sie nacheinander ab. 230 Module sind damit rund 2,8 Sekunden,
     * bevor die erste Zeile eigener Code läuft.
     */
    static seitenzahlen() {
        const bild = performance.getEntriesByType('paint')
            .find(e => e.name === 'first-contentful-paint');
        const module = performance.getEntriesByType('resource')
            .filter(e => e.name.endsWith('.js'));
        const navigation = performance.getEntriesByType('navigation')[0];
        return {
            erstesBild: bild ? Math.round(bild.startTime) : null,
            dom: document.querySelectorAll('*').length,
            module: module.length,
            moduleMs: module.length
                ? Math.round(Math.max(...module.map(e => e.responseEnd))
                             - Math.min(...module.map(e => e.startTime)))
                : 0,
            html: navigation ? Math.round(navigation.responseEnd) : null,
        };
    }

    static _ablegen(ergebnis) {
        try {
            localStorage.setItem(Startbericht.ABLAGE, JSON.stringify(ergebnis));
            const reihe = Startbericht.reihe();
            reihe.push({
                zeit: ergebnis.zeitpunkt, adresse: location.search,
                gesamt: ergebnis.gesamt, blockiert: ergebnis.blockiert,
                dom: ergebnis.dom, erstesBild: ergebnis.erstesBild,
                moduleMs: ergebnis.moduleMs,
            });
            localStorage.setItem(`${Startbericht.ABLAGE}_reihe`,
                                 JSON.stringify(reihe.slice(-12)));
        } catch (fehler) {
            // stumm gewollt: Ohne Ablage bleibt der Konsolenbericht — eine
            // Messung darf den Seitenstart nie zum Scheitern bringen.
        }
    }

    /** Der letzte Bericht — auch aus einem anderen Tab derselben Herkunft. */
    static letzte() {
        return Startbericht._lesen(Startbericht.ABLAGE, null);
    }

    /** Die letzten zwölf Läufe, ältester zuerst. */
    static reihe() {
        return Startbericht._lesen(`${Startbericht.ABLAGE}_reihe`, []);
    }

    static _lesen(schluessel, ersatz) {
        try {
            const roh = localStorage.getItem(schluessel);
            return roh ? JSON.parse(roh) : ersatz;
        } catch (fehler) {
            return ersatz;
        }
    }
}
