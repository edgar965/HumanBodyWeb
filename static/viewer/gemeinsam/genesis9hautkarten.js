import { Protokoll } from './protokoll.js';
import { Serverabruf } from './serverabruf.js';

/**
 * Genesis9hautkarten — die Karten der Hautebenen vom Server holen (17.10.2026): `zeichnung` (Muskel-/Fettnormalen) und `gebiet` (Sommersprossen, Altersflecken).
 *
 * Der Server baut sie beim ersten Abruf je Geschlecht im Hintergrund (`G9hautfaltenablage`, 60–80 s) und antwortet bis dahin mit `stand: baut`; hier wird alle
 * `PAUSE_MS` nachgefragt. Das Ergebnis (oder `null` bei einem Fehler) merkt sich die Klasse je Produkt und Geschlecht — ein zweiter Abruf kostet nichts.
 * Dieselbe Form wie `Genesis9hautfalten.bilder`, nur für zwei Produkte.
 */
export class Genesis9hautkarten {

    static ADRESSE = '/api/character/genesis9-figur/hautebenen/';
    static VERSUCHE = 60;
    static PAUSE_MS = 3000;
    /** `produkt/geschlecht` → Promise<{bilder: {kachel: Adresse}, kacheln: {kachel: {…}}}|null> */
    static _stand = new Map();

    static holen(produkt, geschlecht) {
        const schluessel = `${produkt}/${geschlecht}`;
        if (!Genesis9hautkarten._stand.has(schluessel)) {
            Genesis9hautkarten._stand.set(schluessel, Genesis9hautkarten._abwarten(produkt, geschlecht).catch(fehler => {
                Protokoll.warnung('Hautkarten', `${schluessel} nicht verfügbar: ${fehler.message}`);
                Genesis9hautkarten._stand.delete(schluessel);
                return null;
            }));
        }
        return Genesis9hautkarten._stand.get(schluessel);
    }

    static async _abwarten(produkt, geschlecht) {
        for (let i = 0; i < Genesis9hautkarten.VERSUCHE; i++) {
            const antwort = await Serverabruf.json(`${Genesis9hautkarten.ADRESSE}${produkt}/${geschlecht}/`);
            if (antwort.stand === 'fertig') return { bilder: antwort.bilder || {}, kacheln: antwort.kacheln || {} };
            if (antwort.stand === 'fehler') throw new Error(antwort.fehler || 'Bau fehlgeschlagen');
            await new Promise(weiter => setTimeout(weiter, Genesis9hautkarten.PAUSE_MS));
        }
        throw new Error('Bau dauert zu lange');
    }
}
