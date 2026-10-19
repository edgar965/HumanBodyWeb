/**
 * Schnellanzeige — Genesis-Figuren in der groben Netzstufe und Leinwände mit Pixeldichte 1 (19.10.2026).
 *
 * Edgar: „für die Mesh3d AI Seite brauche ich eine schnelle Anzeige … so dass ich ggf. geringere Auflösung habe“ — „diese schnelle Anzeige kann in den allgemeinen
 * Code hinein, also auch für Charakter, per default aber nur für Mesh3d AI gesetzt“.
 *
 *   Netz       die Figuren bleiben auf Daz' Käfig (`grob`, 27.087 statt 104.480 Browserpunkte, eine Anfrage je Stück, kein Nachholen der feinen Stufe — `Genesis9haeppchen.zug`);
 *              verschweißte Stücke (Scham) bringen ihr Loch auch für diese Stufe mit (`G9stuecklochstufen`, `Stueckloch.fassung`)
 *   Leinwand   Pixeldichte 1 statt bis zu 2 (bei Bildschirmskalierung 1,5–2 ein Viertel bis die Hälfte der Pixel)
 *
 * Eingeschaltet wird sie von der SEITE, nicht im Code: `<meta name="schnellanzeige" content="an">` im Kopf der Vorlage (heute nur `mesh3dai.html`). Jede andere Seite — auch die
 * Charakter-Seite — bleibt bei der Vorgabe (fein, Pixeldichte des Bildschirms) und kann sie mit derselben Zeile einschalten. Strg+Alt+H schaltet die Netzstufe wie überall weiter
 * (grob → fein → ultrafein, `Netzstufenschalter`); die Pixeldichte bleibt beim Seitenaufruf.
 */
export class Schnellanzeige {
    static META = 'schnellanzeige';
    /** Höchste Pixeldichte ohne Schnellanzeige (wie bisher in den Bühnen). */
    static PIXELDICHTE_HOECHSTENS = 2;

    /** Ob die Seite die schnelle Anzeige verlangt — gelesen beim Laden des Moduls (Module laufen nach dem Kopf der Seite). */
    static an = typeof document !== 'undefined' && document.querySelector?.(`meta[name="${Schnellanzeige.META}"]`)?.content === 'an';

    /** Die Netzstufe, mit der eine Figur beim Laden ankommt, wenn nichts anderes gewählt ist (`Netzstufenstand.wahl`). */
    static stufe() {
        return Schnellanzeige.an ? 'grob' : 'fein';
    }

    /** Die Pixeldichte einer Leinwand: 1 mit Schnellanzeige, sonst die des Bildschirms bis `hoechstens`. */
    static pixeldichte(hoechstens = Schnellanzeige.PIXELDICHTE_HOECHSTENS) {
        if (Schnellanzeige.an) return 1;
        return Math.min((typeof window !== 'undefined' && window.devicePixelRatio) || 1, hoechstens);
    }
}
