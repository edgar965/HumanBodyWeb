import { Protokoll } from './protokoll.js';
import { Figuraufbaustand } from './figuraufbaustand.js';

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

    /** So lange wartet der feine Zug höchstens auf die GarmentCode-Stücke. */
    static GC_FRIST_MS = 20000;

    /**
     * Käfig jetzt, volle Stufe im Hintergrund; liefert die Figur nach dem ersten Zug.
     *
     * Trägt die Figur GarmentCode-Stücke (`inst.gcBereit`, im Konstruktor aus den
     * gespeicherten Daten gesetzt), wartet der feine Zug auf sie: Sie hängen erst NACH
     * `bauen()`, und ein Daz-Stück, das vor ihnen geholt wird, kennt sie in seiner
     * Lagenrechnung nicht — es müsste hinterher ein zweites Mal kommen
     * (`Genesis9lagen.nachGcBau`). Mit dem Warten holt der feine Zug jedes Stück genau
     * EINMAL und gleich richtig gelegt (Edgar, 30.09.2026: „die Kleideranfragen zuerst,
     * und dann den Aufbau des Modells nur einmal mit ALLEN Kleidern auf einmal"). Der
     * Käfig steht davon unberührt sofort — die Figur ist genauso schnell zu sehen.
     *
     * Die Frist ist das Sicherheitsnetz: Scheitert die Wiederherstellung so, dass niemand
     * freigibt, bliebe die Figur sonst für immer auf der groben Stufe.
     */
    static async progressiv(inst) {
        await Genesis9aufbau.alles(inst, Genesis9aufbau.GROB);
        inst.fein = Genesis9aufbau._gcAbwarten(inst)
            .then(() => Genesis9aufbau._nachzug(inst, 'Feine Stufe nicht geladen'));
        return inst;
    }

    /** Das Versprechen auf die GarmentCode-Stücke — mit Frist, und ohne je zu scheitern. */
    static _gcAbwarten(inst) {
        if (!inst?.gcBereit) return Promise.resolve();
        return Promise.race([
            Promise.resolve(inst.gcBereit).catch(() => {}),
            new Promise(loesen => setTimeout(loesen, Genesis9aufbau.GC_FRIST_MS)),
        ]);
    }

    /**
     * Der Nachzug auf die volle Stufe, im Aufbaustand vermerkt — solange er
     * läuft, zeigt die Szene das grobe Netz, und ein Export daraus wäre
     * stillschweigend ein Sechzehntel der Figur (`Figuraufbaustand`).
     */
    static _nachzug(inst, meldung) {
        Figuraufbaustand.beginnen(inst);
        return Genesis9aufbau.alles(inst, null)
            .catch(fehler => {
                Protokoll.warnung('Genesis 9', `${meldung}: ${fehler.message}`);
                return inst;
            })
            .finally(() => Figuraufbaustand.beenden(inst));
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
            inst.fein = Genesis9aufbau._nachzug(inst, 'Stufe nicht umgebaut');
            return inst.fein;
        }));
        return true;
    }

    /** Die Adresse mit `?stufen=` — oder unverändert. */
    static adresse(url, stufen) {
        return stufen === null || stufen === undefined ? url : `${url}?stufen=${stufen}`;
    }
}
