import { Serverabruf } from './serverabruf.js';
import { Netzstufenstand } from './netzstufenstand.js';
import { Genesis9vorrat } from './genesis9vorrat.js';

/**
 * Genesis9antwortspeicher — die Netzantworten einer Figur JE STUFE im Arbeitsspeicher halten (12.10.2026).
 *
 * Edgar: „jede Figur soll auch ihre zweite Fassung (fein) und ultrafein im RAM halten." Bis dahin holte jeder Stufenwechsel (Strg+Alt+H: grob → fein → ultrafein →
 * grob) den Körper und jedes Stück noch einmal vom Server — auch beim Rückweg auf eine Stufe, die schon dagewesen war. Jetzt bleibt jede Antwort, die gebaut wurde, unter
 * ihrer Stufe liegen: `grob` (Käfig, `?stufen=0`), `fein` und `ultrafein` (die Stufe steht in der Wahl des Nutzers und im Keks, nicht in der Adresse).
 *
 * WER WAS HÄLT: `koerper` (Körper, Skelett, Anhänge in EINER Antwort) und `kleid:<Kennung>` (je Daz-Stück). Der Eintrag eines Teils gilt für EINE Stellung — alles,
 * was Gestalt und Lage bestimmt (Regler, Pose, Ausdruck, Griffe, Kleidung, Lagen …). Ändert sie sich (Reglerzug), ersetzt die neue Antwort den ganzen Eintrag: die anderen
 * Stufen gehörten zur alten Stellung. So bleibt der Speicher bei drei Stufen je Teil, nicht bei einer Antwort je Reglerzug.
 *
 * NICHT VORAB GELADEN: gehalten wird, was geladen wurde. Die Filmstufe rechnet erst, wenn jemand sie wählt (`G9antworten.VORAUSRECHNEN`, Edgar 30.09.2026).
 *
 * EINSTELLBAR (Edgar, 12.10.2026: „mach das einstellbar im RAM, einstellbar unter Einstellungen - Charakter. Default: RAM"): `ui_prefs.netzantworten` (`ram` | `server`,
 * Vorgabe `ram`), von `Starteinstellungen` beim Laden an `einstellen` gereicht. Bei `server` liegt nichts im Speicher: `suchen` findet nie etwas, `ablegen` gibt frei, was
 * schon dalag (die ersten Antworten kommen vor den Einstellungen), und jeder Wechsel fragt den Server wie vor dem 12.10.2026.
 *
 * Die Antworten sind Sichten auf den Antwortpuffer des Servers (`Netzpaket`); jeder Verbraucher kopiert die Zahlenfelder (`kodierung.js`). Die Objekte darum
 * (Skelett, Gruppen, `hautLoch` …) gehören der Figur, die sie nach dem Bau verändern darf — deshalb liegt eine tiefe Kopie im Speicher (`kopie`: die Zahlenfelder bleiben
 * geteilt) und jeder Treffer gibt wieder eine heraus.
 */
export class Genesis9antwortspeicher {

    /** Ob gehalten wird (Einstellung „Netzantworten", Vorgabe RAM); die Figuren aller Seiten ohne Einstellung halten. */
    static halten = true;

    /** Die Wahl aus `ui_prefs.netzantworten`: nur `server` schaltet das Halten ab, alles andere (auch nichts) heißt RAM. */
    static einstellen(wahl) {
        Genesis9antwortspeicher.halten = wahl !== 'server';
    }

    /** Die Stufe einer Anfrage: eine ausdrückliche in der Adresse (`?stufen=0` → `S0`), sonst die gewählte (`fein`, `ultrafein`). */
    static stufe(adresse) {
        const treffer = /[?&]stufen=(\d+)/.exec(adresse);
        return treffer ? `S${treffer[1]}` : Netzstufenstand.wahl;
    }

    /** Die Adresse ohne `?stufen=` — die Stellung gilt für alle Stufen. */
    static ohneStufen(adresse) {
        return adresse.replace(/[?&]stufen=\d+/, '');
    }

    /** Tiefe Kopie der Objekte und Listen; Zahlenfelder (TypedArrays) bleiben dieselben — niemand schreibt in sie. */
    static kopie(wert) {
        if (Array.isArray(wert)) return wert.map(w => Genesis9antwortspeicher.kopie(w));
        if (wert && typeof wert === 'object' && !ArrayBuffer.isView(wert)) {
            return Object.fromEntries(Object.entries(wert).map(([name, w]) => [name, Genesis9antwortspeicher.kopie(w)]));
        }
        return wert;
    }

    /** Der Eintrag für Teil, Stellung und Stufe — `{daten, material}` — oder null. Die Daten sind der Speicher selbst: wer sie baut, nimmt `kopie`. */
    static suchen(inst, teil, stellung, stufe) {
        if (!Genesis9antwortspeicher.halten) return null;
        const eintrag = inst?._antworten?.get(teil);
        return eintrag && eintrag.stellung === stellung ? eintrag.stufen.get(stufe) || null : null;
    }

    /**
     * Eine Antwort ablegen, die gebaut wird. Eine andere Stellung als die des Eintrags ersetzt ihn ganz. Stücke, die nicht mehr getragen werden, gehen hier mit weg.
     * @param material  was die Materialien bestimmt (nur Körper, `Genesis9materialabruf.material`) — oder null
     */
    static ablegen(inst, teil, stellung, stufe, daten, material = null) {
        if (!Genesis9antwortspeicher.halten) { inst._antworten = null; return; }
        const ablage = inst._antworten ??= new Map();
        for (const name of [...ablage.keys()]) {
            if (name.startsWith('kleid:') && !inst.kleidung?.[name.slice('kleid:'.length)]) ablage.delete(name);
        }
        let eintrag = ablage.get(teil);
        if (!eintrag || eintrag.stellung !== stellung) {
            eintrag = { stellung, stufen: new Map() };
            ablage.set(teil, eintrag);
        }
        eintrag.stufen.set(stufe, { daten: Genesis9antwortspeicher.kopie(daten), material });
    }

    /**
     * Die Antwort für ein Daz-Stück: aus dem Speicher, sonst vom Server.
     * @returns {Promise<{daten: object, teil: string, stellung: string, stufe: string, neu: boolean}>} `neu`: vom Server, also noch abzulegen (`ablegen`)
     */
    static async kleid(inst, kennung, adresse, nutzlast) {
        const teil = `kleid:${kennung}`;
        const stellung = JSON.stringify([Genesis9antwortspeicher.ohneStufen(adresse), nutzlast]);
        const stufe = Genesis9antwortspeicher.stufe(adresse);
        const treffer = Genesis9antwortspeicher.suchen(inst, teil, stellung, stufe);
        if (treffer) return { daten: Genesis9antwortspeicher.kopie(treffer.daten), teil, stellung, stufe, neu: false };
        return { daten: await Serverabruf.netzSenden(adresse, nutzlast, Genesis9vorrat.kopf(inst, teil, adresse, nutzlast)), teil, stellung, stufe, neu: true };   // Anzeige → dauerhaft (`Genesis9vorrat`)
    }

    /** Was im Speicher liegt, in Bytes: `{teil: {stufe: Bytes}}` — jeder Antwortpuffer einmal gezählt (die Felder einer Antwort teilen ihn). Für Proben. */
    static groessen(inst) {
        const aus = {};
        for (const [teil, eintrag] of inst?._antworten || []) {
            aus[teil] = {};
            for (const [stufe, { daten }] of eintrag.stufen) {
                const puffer = new Set();
                Genesis9antwortspeicher._puffer(daten, puffer);
                aus[teil][stufe] = [...puffer].reduce((summe, p) => summe + p.byteLength, 0);
            }
        }
        return aus;
    }

    static _puffer(wert, puffer) {
        if (ArrayBuffer.isView(wert)) puffer.add(wert.buffer);
        else if (Array.isArray(wert)) wert.forEach(w => Genesis9antwortspeicher._puffer(w, puffer));
        else if (wert && typeof wert === 'object') Object.values(wert).forEach(w => Genesis9antwortspeicher._puffer(w, puffer));
    }
}
