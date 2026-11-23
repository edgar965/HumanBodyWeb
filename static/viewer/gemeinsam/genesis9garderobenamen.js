import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';

/**
 * Genesis9garderobenamen — die Anzeigenamen getragener Stücke ohne den ganzen Garderobe-Katalog (23.11.2026).
 *
 * WARUM (Edgar: „alle offene punkte weiter“): `Genesis9kleidung.beschildern` holte für das Hover-Schild eines Stücks den
 * ganzen Katalog (4,36 MB, am Server 0,46–0,82 s) — auf der Foto-Genesis-Seite nur für „Daz Anatomie Mann“. Hier fragt
 * EINE Anfrage je Takt die Namen aller wartenden Kennungen ab (`G9garderobenamenapi`, dieselben Namen wie im Katalog).
 * Was der Server dort nicht kennt (Sammeleinträge „… – Generisch“, ausgeblendete Stücke) oder bei einem Fehler: `null`
 * — dann nimmt `anzeigename` den Katalog wie bisher.
 */
export class Genesis9garderobenamen {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/namen/';

    /** Kennung → Name, nur was der Server geliefert hat. */
    static _namen = new Map();

    /** Die Sammlung des laufenden Takts: `{kennungen, versprechen}`. */
    static _offen = null;

    /** Kennung → Versprechen der Anfrage, die sie schon trägt (eine zweite Frage während der Antwort schickt keine zweite Anfrage). */
    static _laufend = new Map();

    /** Der Name aus der leichten Liste — oder null (dort unbekannt, Fehler). */
    static async name(kennung) {
        const N = Genesis9garderobenamen;
        if (N._namen.has(kennung)) return N._namen.get(kennung);
        if (!N._laufend.has(kennung)) {
            const lauf = N._offen ??= N._sammeln();
            lauf.kennungen.add(kennung);
            N._laufend.set(kennung, lauf.versprechen);
        }
        await N._laufend.get(kennung);
        return N._namen.get(kennung) ?? null;
    }

    /** Der Name, wenn er schon da ist — sonst null. Wartet nie. */
    static gemerkt(kennung) {
        return Genesis9garderobenamen._namen.get(kennung) ?? null;
    }

    /** Nach Umbenennen oder Löschen (`Genesis9kleidung.vergessen`): neu fragen. */
    static vergessen() {
        Genesis9garderobenamen._namen.clear();
    }

    static _sammeln() {
        const kennungen = new Set();
        const versprechen = new Promise(weiter => setTimeout(weiter, 0)).then(async () => {
            Genesis9garderobenamen._offen = null;
            const suche = new URLSearchParams([...kennungen].map(k => ['k', k]));
            try {
                const daten = await Serverabruf.json(`${Genesis9garderobenamen.ADRESSE}?${suche}`);
                for (const [k, name] of Object.entries(daten?.namen || {})) Genesis9garderobenamen._namen.set(k, name || k);
            } catch (fehler) {
                Protokoll.info('Genesis 9', `Namen der Stücke nicht geholt (${fehler.message}) — die Schilder nehmen den Katalog`);
            } finally {
                for (const k of kennungen) Genesis9garderobenamen._laufend.delete(k);
            }
        });
        return { kennungen, versprechen };
    }
}
