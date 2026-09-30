import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Letztewahl — was die Szene zuletzt geladen hat: Figur und Animation.
 *
 * WARUM (Edgar, 30.09.2026): „entferne das Standardmodell und die Standard Animation.
 * Auf der Seite /Charakter/ soll immer nur der letzte geladene Modell und die letzte
 * Animation geladen werden". Bis dahin standen beide als Einstellung in
 * `/settings/charakter/` (`default_model_scene`, `default_anim_scene`) — eine Vorgabe,
 * die man von Hand pflegen muss und die deshalb nie beschrieb, woran gerade gearbeitet
 * wurde: Wer abends Ursula1 lud, bekam am nächsten Morgen wieder `femaleWithClothes`.
 *
 * WARUM `localStorage` UND NICHT `sessionStorage`: Die Sitzungsablage (`session.js`)
 * hält den GANZEN Szenenstand, aber nur für diesen einen Tab und nur bis er zugeht —
 * genau der Fall „Browser neu auf, Szene leer" war gemeint. Hier steht bewusst wenig:
 * ein Name je Figurart und eine Adresse. Einen ganzen Szenenstand dauerhaft zu halten
 * wäre etwas anderes (und gehörte dann gespeichert, nicht gemerkt).
 *
 * Was NICHT hierher gehört: Figuren, die nur zum Vergleich dazugeladen wurden. Gemerkt
 * wird die ZULETZT geladene — mehr zu raten wäre eine Szene, die niemand gespeichert hat.
 */
export class Letztewahl {

    static SCHLUESSEL = 'hb_szene_letzte_wahl';

    /** Solange nie etwas geladen wurde — dieselbe Figur wie vor dem 30.09.2026. */
    static VORGABE = { name: 'femaleWithClothes', quelle: 'modell', bereich: 'gespeichert' };

    static _lesen() {
        try {
            const roh = JSON.parse(localStorage.getItem(Letztewahl.SCHLUESSEL));
            return (roh && typeof roh === 'object') ? roh : {};
        } catch (fehler) {
            return {};                     // privates Fenster, gesperrte Seitendaten
        }
    }

    static _schreiben(stand) {
        try {
            localStorage.setItem(Letztewahl.SCHLUESSEL, JSON.stringify(stand));
        } catch (fehler) {
            Protokoll.debug('Letztewahl', 'nicht gemerkt', fehler);
        }
    }

    // ------------------------------------------------------------------ Figur

    /** `{name, quelle, bereich}` der zuletzt geladenen Figur — sonst die Vorgabe. */
    static figur() {
        const f = Letztewahl._lesen().figur;
        if (!f || !f.name) return { ...Letztewahl.VORGABE };
        return {
            name: String(f.name),
            quelle: String(f.quelle || Letztewahl.VORGABE.quelle),
            bereich: f.bereich === 'standard' ? 'standard' : 'gespeichert',
        };
    }

    /** Nach dem Laden einer Figur — `quelle` wie in `Charakterdialog.LADER`. */
    static figurGemerkt(name, quelle, bereich) {
        if (!name) return;
        Letztewahl._schreiben({
            ...Letztewahl._lesen(),
            figur: {
                name: String(name),
                quelle: String(quelle || Letztewahl.VORGABE.quelle),
                bereich: bereich === 'standard' ? 'standard' : 'gespeichert',
            },
        });
    }

    // -------------------------------------------------------------- Animation

    /** Die Adresse der zuletzt geladenen Animation — leer, wenn nie eine lief. */
    static animation() {
        const a = Letztewahl._lesen().animation;
        return typeof a === 'string' ? a : '';
    }

    static animationGemerkt(url) {
        if (!url) return;
        Letztewahl._schreiben({ ...Letztewahl._lesen(), animation: String(url) });
    }

    /** Eine Animation, die es nicht mehr gibt, darf beim nächsten Start nicht stören. */
    static animationVergessen(url) {
        const stand = Letztewahl._lesen();
        if (!url || stand.animation !== String(url)) return;
        delete stand.animation;
        Letztewahl._schreiben(stand);
    }
}
