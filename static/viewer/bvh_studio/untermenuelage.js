/**
 * Untermenuelage — ein Untermenü so neben sein Elternteil legen, dass es ganz
 * im Fenster liegt.
 *
 * WARUM (Edgar, 13.09.2026: „kann nun das Kontextmenü nicht mehr bedienen -
 * beim Hinzufügen einer Animation klappt es zu"): Die Untermenüs standen
 * starr rechts neben ihrem Eintrag, fünf Pixel höher, bis 400 Pixel hoch.
 * Das Spurmenü einer leeren Spur ist 162 Pixel hoch und wird deshalb bis an
 * den unteren Fensterrand gerückt — sein Untermenü „Hinzufügen" ragte dann
 * bis 230 Pixel UNTER das Fenster, und die Animationsliste eines Ordners in
 * der unteren Hälfte lag ganz außerhalb. Gemessen bei 1548 × 804:
 * Ordnerliste 631–1031, Liste zu „Dance" 780–1180. Wer mit der Maus dorthin
 * wollte, verließ das Menü, und es klappte zu. Nach rechts dasselbe: drei
 * Ebenen brauchen rund 700 Pixel.
 *
 * Gelegt wird beim Überfahren des Elternteils (`mouseenter`): erst `offen`
 * (macht es sichtbar und damit messbar), dann messen und legen. Reicht der Platz
 * rechts nicht, kommt es links neben den Eintrag; reicht er unten nicht,
 * rutscht es hoch, und die Höhe bleibt unter der Fensterhöhe (die Liste
 * rollt dann in sich).
 *
 * KARENZZEIT (Edgar, 13.09.2026, zweiter Anlauf: „sobald ich zum Menü rechts
 * wechseln möchte um einzufügen, verschwindet das Kontext Menü"): Zwischen
 * dem Ordnereintrag und seiner Animationsliste liegt der Rollbalken der
 * Ordnerliste. Fährt die Maus darüber, verlässt sie den Eintrag, `:hover`
 * endet, die Liste ist weg, bevor die Maus sie erreicht. Deshalb hält die
 * Klasse `offen` ein Untermenü nach `mouseleave` noch `VERZOEGERUNG` ms —
 * ein Wiedereintritt (auch in die Liste selbst, sie ist ein Kind des
 * Eintrags) bricht das ab. Und ein Geschwister öffnet sich erst, wenn die Maus
 * `EINTRITT` ms auf ihm bleibt — wer schräg von „A_Results" zu dessen zweitem
 * Eintrag fährt, streift „Aist", ohne dass dessen Liste die alte verdrängt.
 *
 * `rechnen` ist reine Arithmetik ohne DOM — `test_js_untermenuelage.py`.
 */
export class Untermenuelage {

    /** Abstand zum Fensterrand. */
    static RAND = 10;
    /** Ein Untermenü sitzt fünf Pixel höher als sein Elternteil. */
    static VERSATZ_Y = 5;
    /** Höher als das wird ein Untermenü nie (wie die CSS-Regel). */
    static HOECHSTENS = 400;
    /** So lange bleibt ein Untermenü offen, nachdem die Maus den Eintrag verließ. */
    static VERZOEGERUNG = 350;
    /** So lange muss die Maus auf einem Geschwister bleiben, bis dessen Untermenü das offene ersetzt. */
    static EINTRITT = 150;

    /**
     * Das Untermenü `feld` bei jedem Überfahren von `elternteil` legen und
     * mit Karenzzeit offen halten. Setzt `ctx-submenu-fixed`, damit
     * `left`/`top` als Fensterkoordinaten gelten (CSS in `bvh_studio.html`).
     */
    static anbinden(elternteil, feld) {
        feld.classList.add('ctx-submenu-fixed');
        let schliesser = null;
        let oeffner = null;
        elternteil.addEventListener('mouseenter', () => {
            clearTimeout(schliesser);
            clearTimeout(oeffner);
            if (Untermenuelage._geschwister(elternteil, feld).length) {
                oeffner = setTimeout(() => Untermenuelage.oeffnen(elternteil, feld),
                                     Untermenuelage.EINTRITT);
            } else {
                Untermenuelage.oeffnen(elternteil, feld);
            }
        });
        elternteil.addEventListener('mouseleave', () => {
            clearTimeout(oeffner);
            clearTimeout(schliesser);
            schliesser = setTimeout(() => feld.classList.remove('offen'),
                                    Untermenuelage.VERZOEGERUNG);
        });
    }

    /** Öffnen, Geschwister zu. */
    static oeffnen(elternteil, feld) {
        Untermenuelage._geschwister(elternteil, feld).forEach(anderes => anderes.classList.remove('offen'));
        feld.classList.add('offen');
        Untermenuelage.legen(elternteil, feld);
    }

    /** Offene Untermenüs, die nicht `feld` sind und `elternteil` nicht enthalten (Vorfahren bleiben). */
    static _geschwister(elternteil, feld) {
        return [...document.querySelectorAll('.ctx-submenu.offen')]
            .filter(anderes => anderes !== feld && !anderes.contains(elternteil));
    }

    /** Alle Untermenüs unter `wurzel` zu — beim Öffnen eines Kontextmenüs. */
    static alleSchliessen(wurzel) {
        wurzel?.querySelectorAll('.ctx-submenu.offen').forEach(feld => feld.classList.remove('offen'));
    }

    /** Alle Untermenüs unter `wurzel` (Einträge `.has-submenu` mit `.ctx-submenu`). */
    static alleAnbinden(wurzel) {
        if (!wurzel) return;
        wurzel.querySelectorAll('.ctx-item.has-submenu').forEach(eintrag => {
            const feld = eintrag.querySelector(':scope > .ctx-submenu');
            if (feld) Untermenuelage.anbinden(eintrag, feld);
        });
    }

    static legen(elternteil, feld, fenster = window) {
        const grenze = Untermenuelage.hoechstens(fenster.innerHeight);
        feld.style.maxHeight = grenze + 'px';
        const lage = Untermenuelage.rechnen(elternteil.getBoundingClientRect(),
                                            feld.offsetWidth, feld.offsetHeight,
                                            fenster.innerWidth, fenster.innerHeight);
        feld.style.left = lage.left + 'px';
        feld.style.top = lage.top + 'px';
    }

    /** Wie hoch ein Untermenü in diesem Fenster höchstens wird. */
    static hoechstens(fensterHoehe) {
        return Math.max(60, Math.min(Untermenuelage.HOECHSTENS,
                                     fensterHoehe - 2 * Untermenuelage.RAND));
    }

    /**
     * Fensterkoordinaten für ein Untermenü der Größe `breite` × `hoehe` neben
     * dem Elternteil `rahmen` (`{left, right, top}`), im Fenster
     * `fensterBreite` × `fensterHoehe`.
     */
    static rechnen(rahmen, breite, hoehe, fensterBreite, fensterHoehe) {
        const rand = Untermenuelage.RAND;
        const hoch = Math.min(hoehe, Untermenuelage.hoechstens(fensterHoehe));
        let left = rahmen.right;
        if (left + breite > fensterBreite - rand) {
            left = Math.max(rand, rahmen.left - breite);
        }
        let top = rahmen.top - Untermenuelage.VERSATZ_Y;
        if (top + hoch > fensterHoehe - rand) {
            top = Math.max(rand, fensterHoehe - rand - hoch);
        }
        return { left, top };
    }
}
