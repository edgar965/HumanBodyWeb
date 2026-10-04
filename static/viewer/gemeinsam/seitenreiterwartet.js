/**
 * Seitenreiterwartet — die Sanduhr eines Reiterwechsels (03.10.2026).
 *
 * Edgar: „Es soll eine Sanduhr kommen, falls der Klick länger braucht." Ein Reiter schaltet die Felder sofort um; was danach kommt
 * (Zustand nachfragen, Tabelle der Runden aufbauen, die Seite lädt noch ihre Bausteine) kann dauern, und ohne Zeichen sieht ein
 * Klick, der arbeitet, aus wie ein Klick, der nichts tut.
 *
 * Verbindung zur Seite nur über zwei Ereignisse auf der Leiste, kein Import in beide Richtungen: `reiterwechsel` meldet der
 * Reiter (`Seitenreiter.zeigen`), `reiterfertig` meldet die Seite, wenn das Feld steht. Dazwischen steht die Sanduhr — erst nach
 * `VERZOEGERUNG_MS`, damit ein schneller Wechsel nicht flackert, und höchstens `HOECHSTENS_MS`, damit ein Ende, das nie gemeldet
 * wird, sie nicht ewig stehen lässt. Gezeigt wird sie als Klasse am Dokument (Zeiger „wartet" überall, Symbol im gewählten Reiter,
 * `css/mesh.css`).
 */
export class Seitenreiterwartet {

    static KLASSE = 'seitenreiter-wartet';
    static VERZOEGERUNG_MS = 150;
    static HOECHSTENS_MS = 20000;

    constructor(leiste) {
        this.leiste = leiste;
        this._anzeige = null;
        this._sicherung = null;
        leiste.addEventListener('reiterwechsel', () => this.beginnen());
        leiste.addEventListener('reiterfertig', () => this.beenden());
    }

    beginnen() {
        this.beenden();
        this._anzeige = setTimeout(
            () => document.documentElement.classList.add(Seitenreiterwartet.KLASSE), Seitenreiterwartet.VERZOEGERUNG_MS);
        this._sicherung = setTimeout(() => this.beenden(), Seitenreiterwartet.HOECHSTENS_MS);
    }

    beenden() {
        clearTimeout(this._anzeige);
        clearTimeout(this._sicherung);
        document.documentElement.classList.remove(Seitenreiterwartet.KLASSE);
    }
}
