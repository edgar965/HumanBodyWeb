/**
 * Auswahl — was in der Bühne gerade ausgewählt ist.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026). Dort waren es zwei
 * Closure-Variablen, `selectedCharacter` und `selectedLightIcon`, die an
 * fuenfzehn Stellen gesetzt und gelesen wurden — unter anderem im
 * Klick-Zuhoerer, beim Laden einer Szene, beim Laden eines Modells, in der
 * Render-Schleife und beim Aufspielen einer Animation.
 *
 * Solange alles in einer Funktion stand, ging das. Sobald Teile in Module
 * wandern, braucht es einen gemeinsamen Ort — sonst haelt jedes Modul seine
 * eigene Kopie und die Auswahl laeuft auseinander. Genau deshalb eine Klasse
 * und keine zwei Variablen: Die Regel "Figur ODER Licht, nie beides" steht
 * jetzt an einer Stelle statt an fuenfzehn.
 */
export class Auswahl {

    constructor(transformControls) {
        this.steuerung = transformControls;
        this.figur = null;
        this.lichtsymbol = null;
        this.kleidung = null;
    }

    /** Figur waehlen (und Licht/Kleidung abwaehlen). */
    figurWaehlen(figur) {
        this.figur = figur;
        this.lichtsymbol = null;
        this.kleidung = null;
        this.steuerung?.attach(figur);
        return figur;
    }

    lichtWaehlen(symbol) {
        this.lichtsymbol = symbol;
        this.figur = null;
        this.kleidung = null;
        this.steuerung?.attach(symbol);
        return symbol;
    }

    kleidungWaehlen(netz) {
        this.kleidung = netz;
        this.figur = null;
        this.lichtsymbol = null;
        this.steuerung?.attach(netz);
        return netz;
    }

    /**
     * Figur waehlen, ohne die Transform-Steuerung anzufassen — fuer das
     * automatische Auswaehlen nach dem Laden. Vorher stand dafuer dreimal
     * `selectedCharacter = charGroup;  // Auto-select loaded character`.
     */
    figurVormerken(figur) {
        this.figur = figur;
        return figur;
    }

    leeren() {
        this.figur = null;
        this.lichtsymbol = null;
        this.kleidung = null;
        this.steuerung?.detach();
    }

    /** Das gewaehlte Licht, falls eines gewaehlt ist. */
    licht() {
        return this.lichtsymbol?.userData?.light || null;
    }
}
