import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Studiostart — Theatre.js hochfahren und seine Oberfläche zurechtrücken.
 *
 * Herausgelöst aus `main.js` (788 Zeilen). Drei Eingriffe, jeder mit Grund:
 *
 * 1. **Alten Zustand verwerfen.** Theatre.js zieht `localStorage` dem
 *    mitgelieferten `state.json` VOR. Steht dort ein alter Stand ohne eigene
 *    Schlüsselbilder (z. B. mit der früheren Sequenzlänge 300), gewinnt er —
 *    und die Zeitleiste ist falsch. Enthält er Schlüsselbilder, ist es Arbeit
 *    des Nutzers und bleibt.
 * 2. **`position: fixed` auf die Studio-Wurzel.** Sonst stehen die
 *    Kontextmenüs an der falschen Stelle.
 * 3. **Zeiger-Ereignisse nur dort durchlassen, wo Theatre.js sie braucht.**
 *    Die Wurzel liegt über der ganzen Seite; ohne `pointer-events: none` wäre
 *    die Bühne darunter tot. Zeitleiste, Werkzeugleiste und Menüs bekommen sie
 *    einzeln zurück.
 *
 * Der Stil geht in den Shadow-DOM des Studios — von außen ist er nicht
 * erreichbar, deshalb steht er hier als Zeichenkette und nicht in einer
 * Stildatei.
 */
export class Studiostart {

    static SPEICHERSCHLUESSEL = 'theatre-0.4.persistent';
    static EIGENE_MARKE = '"keyframes":[{';
    static WURZEL = 'theatrejs-studio-root';
    /** Theatre.js baut sein Wurzelelement in einem `setTimeout`. */
    static AUFBAU_MS = 100;

    /**
     * Was das Studio-Wurzelelement IMMER braucht — mit `important` gesetzt,
     * weil Theatre.js seine eigenen Inline-Stile schreibt.
     */
    static RAHMEN = { 'z-index': '900', position: 'fixed',
                      'pointer-events': 'none' };

    /**
     * Der Kasten, in dem das Studio sitzt — OHNE `important`.
     *
     * BEFUND 24.08.2026: Hier standen `top:0; left:0; width:100vw;
     * height:100vh` MIT `important` — und haben damit die Regel der Vorlage
     * ausgehebelt. `templates/theatre.html` setzt naemlich
     *
     *     #theatrejs-studio-root { top:40px; right:320px; bottom:160px;
     *                              left:220px; z-index:900 !important; }
     *
     * damit das Studio zwischen Seitenleiste, Menuezeile, rechtem Feld und
     * Abspielleiste liegt. Ein Inline-Stil mit `important` schlaegt jede
     * Stilregel — also lag das Studio ueber der ganzen Seite, und seine
     * Werkzeugleiste (`GlobalToolbar`, `pointer-events: auto`) sass oben links
     * ueber der djangoBase-Leiste. Der Knopf zum Ein- und Ausklappen der
     * Seitenleiste war dort nicht mehr erreichbar.
     *
     * Jetzt ohne `important`: Eine Stilregel MIT `important` gewinnt gegen
     * einen Inline-Stil OHNE — die Vorlage entscheidet also wieder, und diese
     * Werte sind nur der Rueckfall fuer Seiten ohne eigene Regel.
     */
    static KASTEN = { inset: '0' };
    // `inset` und NICHT `width`/`height`: Die Vorlage spannt den Kasten ueber
    // `top/right/bottom/left` auf. Stuenden hier zusaetzlich Breite und Hoehe,
    // waere die Angabe ueberbestimmt — CSS wirft dann `right` bzw. `bottom`
    // weg, und das rechte Feld waere wieder verdeckt.

    static SCHATTENSTIL = `
                    :host { font-size: 13px !important; }
                    svg { transform: scale(1.3); }
                    [data-testid] { min-height: 28px; }

                    /* Re-enable pointer events only on the Sequence Editor (bottom timeline) */
                    [data-testid="SequenceEditor"],
                    [data-testid="GlobalToolbar"] {
                        pointer-events: auto !important;
                    }

                    /* Outline panel: shift right to clear sidebar */
                    div[class] > div[class]:nth-child(3) {
                        left: 220px !important;
                        pointer-events: auto !important;
                    }
                    /* Detail panel (properties): shift left to clear right panel */
                    div[class] > div[class]:nth-child(4) {
                        pointer-events: auto !important;
                    }

                    /* Context menus + popovers must be clickable */
                    [data-radix-popper-content-wrapper],
                    [data-radix-menu-content],
                    [role="menu"],
                    [role="dialog"] {
                        pointer-events: auto !important;
                        z-index: 99999 !important;
                    }
                `;

    /** Alten Studiozustand verwerfen, wenn er keine eigenen Schlüssel enthält. */
    static altenZustandVerwerfen() {
        try {
            const stand = localStorage.getItem(Studiostart.SPEICHERSCHLUESSEL);
            if (!stand || stand.includes(Studiostart.EIGENE_MARKE)) return;
            localStorage.removeItem(Studiostart.SPEICHERSCHLUESSEL);
            Protokoll.debug('Theatre Studio',
                            'Cleared stale localStorage (no user keyframes)');
        } catch (fehler) {
            Protokoll.debug('Theatre Studio', 'Alter Studiozustand nicht lesbar',
                            fehler);
        }
    }

    /**
     * Studio hochfahren. MUSS auf Modulebene laufen — nach `DOMContentLoaded`
     * ist es zu spät, Theatre.js hat sich dann schon eingerichtet.
     */
    static hochfahren(studio) {
        Studiostart.altenZustandVerwerfen();
        studio.initialize().then(() => {
            Protokoll.debug('Theatre Studio', 'initialized successfully');
            studio.ui.restore();   // es merkt sich „versteckt" im localStorage
            setTimeout(() => Studiostart._zurechtruecken(),
                       Studiostart.AUFBAU_MS);
        }).catch(fehler => {
            Protokoll.fehler('Theatre Studio', 'initialize() FAILED', fehler);
        });
        window.studio = studio;
        return studio;
    }

    static _zurechtruecken() {
        const wurzel = document.getElementById(Studiostart.WURZEL);
        if (!wurzel) return;
        for (const [name, wert] of Object.entries(Studiostart.RAHMEN)) {
            wurzel.style.setProperty(name, wert, 'important');
        }
        for (const [name, wert] of Object.entries(Studiostart.KASTEN)) {
            wurzel.style.setProperty(name, wert);      // ohne `important`
        }
        if (wurzel.shadowRoot) {
            const stil = document.createElement('style');
            stil.textContent = Studiostart.SCHATTENSTIL;
            wurzel.shadowRoot.prepend(stil);
        }
        Protokoll.debug('Theatre Studio',
                        'UI visible, position:fixed, context menu fix active');
    }
}
