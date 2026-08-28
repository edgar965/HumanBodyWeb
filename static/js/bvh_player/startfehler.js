/**
 * Startfehler — der rote Balken, wenn der Spieler gar nicht erst hochkommt.
 *
 * WARUM ALS MODUL (Befund `doppelcode`, 28.08.2026): Derselbe Block stand
 * wortgleich in `job_result.html` und `standalone_result.html` — inklusive
 * eines 200 Zeichen langen `style.cssText`, den `jsstilfassungen` daneben als
 * Inline-Stil meldete. Zwei Kopien einer Fehleranzeige sind die unangenehmste
 * Sorte: Sie laufen auseinander, und auffallen tut es erst in dem Moment, in
 * dem ohnehin schon etwas kaputt ist.
 *
 * DIE ANZEIGE MUSS OHNE DAS SEITEN-JS AUSKOMMEN: Sie erscheint ja gerade,
 * wenn ein Modul nicht geladen hat. Deshalb baut sie ihr Element selbst und
 * hängt nur an `document.body` — kein Aufbau, keine Registrierung.
 */
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';

export class Startfehler {
    /** Klasse aus `stilhelfer.css` — der Balken selbst. */
    static BALKEN = 'startfehler';
    /** Der Schließen-Knopf, ebenfalls aus `stilhelfer.css`. */
    static KNOPF = 'fehlerknopf';

    /**
     * Den Balken anzeigen und den Fehler protokollieren.
     * @param {string} woher Name des Bausteins, der nicht hochkam
     * @param {Error} fehler
     */
    static zeigen(woher, fehler) {
        Protokoll.fehler(woher, 'Start fehlgeschlagen:', fehler);
        const balken = document.createElement('div');
        balken.className = Startfehler.BALKEN;
        const text = document.createElement('span');
        text.textContent = 'JS Error: ' + (fehler?.message || fehler);
        const knopf = document.createElement('button');
        knopf.className = Startfehler.KNOPF;
        knopf.textContent = 'X';
        // Zuhörer statt `onclick`-Attribut: Ein `onclick` braucht einen
        // globalen Namen, und ES-Module legen keinen an.
        knopf.addEventListener('click', () => balken.remove());
        balken.append(text, knopf);
        document.body.appendChild(balken);
        return balken;
    }
}
