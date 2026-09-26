import { Protokoll } from './protokoll.js';

/**
 * Genesis9aufbau — die Figur in zwei Zügen: Käfig sofort, volle Stufe nach.
 *
 * WARUM (Edgar, 18.09.2026: „mach das laden asynchron - erst mit geringer
 * auflösung, dann asynchron mit höherer. ich möchte sofort das modell
 * sehen"): Ein Genesis-9-Körper auf Stufe 2 ist eine Antwort von 65 MB
 * (410.202 Punkte, Hautgewichte, fünf Anhänge), jedes Kleidungsstück noch
 * einmal 10–37 MB — bis alles da ist, vergeht bei Strg+Alt+H über eine
 * Minute, und solange stand die Szene leer.
 *
 * Jetzt fragt `progressiv` erst den KÄFIG (`?stufen=0`: 25.182 Punkte, ein
 * Viertel bis Sechzehntel der Bytes, der Server rechnet keine Unterteilung)
 * für Körper UND Kleidung — die Figur steht nach dem ersten Zug — und holt
 * dann im Hintergrund dieselbe Stellung in der Stufe des Browsers nach
 * (`inst.fein`, ein Promise für Proben). Der Server nimmt die Stufe aus der
 * Anfrage vor dem Keks (`core/dienste/netzstufenwahl.Netzstufenwahl`).
 *
 * Ein Reglerzug dazwischen erhöht `inst._lauf`; eine Antwort, die zu einem
 * älteren Lauf gehört, wird verworfen (`Genesis9Modell.koerperAufbauen`,
 * `anziehen`) — sonst überholte der Käfig die feine Stellung.
 */
export class Genesis9aufbau {

    /** Die Stufe des ersten Zugs: Daz' Käfig. */
    static GROB = 0;

    /** Käfig jetzt, volle Stufe im Hintergrund; liefert die Figur nach dem ersten Zug. */
    static async progressiv(inst) {
        await Genesis9aufbau.alles(inst, Genesis9aufbau.GROB);
        inst.fein = Genesis9aufbau.alles(inst, null).catch(fehler => {
            Protokoll.warnung('Genesis 9', `Feine Stufe nicht geladen: ${fehler.message}`);
            return inst;
        });
        return inst;
    }

    /**
     * Körper und jedes getragene Stück — auf `stufen` (null = Stufe des Browsers),
     * GLEICHZEITIG angefragt (18.09.2026 nachts): der Server rechnet Anfragen
     * nebeneinander (gemessen 3,6 s nacheinander gegen 2,4 s Wand), und ein Stück,
     * das vor dem Körper ankommt, bindet `_kleiderBinden` an das frische Skelett.
     *
     * EIN STÜCK DARF DIE FIGUR NICHT KOSTEN (26.09.2026, Edgar: „Modell laden
     * funktioniert nicht"): Ursula1 trug ein längst verschwundenes MakeHuman-
     * Stück (`mb_t_shirt`, 404 „Unbekanntes Stück") — ohne Fang riss das per
     * `Promise.all` den KÖRPER mit, die Figur blieb ganz aus der Szene. Nur der
     * Körper bleibt fatal; ein Stück, das scheitert, wird gemeldet und fehlt.
     */
    static async alles(inst, stufen) {
        const koerper = inst.koerperAufbauen(stufen);   // zählt `_lauf` hoch, bevor die Stücke ihn lesen
        const stuecke = inst.getragen().map(             // ohne Kaskade: alle kommen ohnehin
            kennung => inst.anziehen(kennung, inst.kleidung[kennung], stufen, false).catch(fehler => {
                Protokoll.warnung('Genesis 9', `${kennung} nicht geladen: ${fehler.message}`);
            }));
        await Promise.all([koerper, ...stuecke]);
        return inst;
    }

    /**
     * Strg+Alt+H ohne Neustart (18.09.2026 abends): jede Genesis-9-Figur holt
     * dieselbe Stellung in der neuen Stufe (der Server liest den Keks); die
     * Texturen liegen im Vorrat. Andere Figurarten bleiben stehen, wie sie
     * sind — ihre Stufe gilt beim nächsten Laden (Edgar, 18.09. nachts: „das
     * muss in 1-2 s gehen"; die HumanBody-Figur auf Stufe 3 sind 1,1 Mio.
     * Punkte und 17 s Browseraufbau). Liefert false nur ohne Genesis-Figur —
     * dann lädt die Seite neu wie bisher.
     */
    static async umschalten(figuren) {
        const alle = [...figuren].filter(inst => inst?.quelle === 'genesis9');
        const andere = [...figuren].length - alle.length;
        if (!alle.length) return false;
        if (andere) Protokoll.info('Genesis 9', `${andere} andere Figur(en) bleiben auf ihrer Stufe bis zum nächsten Laden`);
        await Promise.all(alle.map(inst => {
            inst.fein = Genesis9aufbau.alles(inst, null).catch(fehler => {
                Protokoll.warnung('Genesis 9', `Stufe nicht umgebaut: ${fehler.message}`);
                return inst;
            });
            return inst.fein;
        }));
        return true;
    }

    /** Die Adresse mit `?stufen=` — oder unverändert. */
    static adresse(url, stufen) {
        return stufen === null || stufen === undefined ? url : `${url}?stufen=${stufen}`;
    }
}
