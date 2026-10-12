/**
 * Anatomiearbeiter — die Karten des Scham-Stücks in einem Web Worker rechnen (12.10.2026).
 *
 * Edgar: „das Backen der neuen Haut soll nur ein paar Sekunden dauern." Bild und Füllen (`Anatomierechnung`) standen 1,5–2 s auf dem Hauptfaden, in Häppchen
 * zwischen dem Zeichnen. Hier läuft dieselbe Rechnung daneben; der Hauptfaden liest die Fenster der Karten der Haut (Canvas, `Anatomiefenster`), schickt Zuordnung,
 * Dreiecke und Fenster und baut aus den Antworten die Texturen (`anatomiearbeit.js`).
 *
 * Nachrichten:
 *   rechnen  {id, zu: {anzahl, texel, btri, l2, l3, stri, belegt}, st: {pos, uv, normal, index}, ha: {pos, uv, normal, ecken},
 *             gruppe, fenster: [{farbe, normal, rauh}|null], breite, hoehe, uvKarte}
 *            → fertig {id, ergebnis: {farbe, normal, rauheit}}   (die Puffer werden übertragen, nicht kopiert)
 *            → fehler {id, meldung}                              (der Hauptfaden rechnet dann selbst weiter)
 *
 * Er liegt außerhalb des Szenenbündels (`/buendel/<fassung>/scene.js`): die Vorlage nennt seinen Pfad mit Fassung
 * (`<meta name="anatomiearbeiter">`, `{% fassungspfad %}`) — dieselbe Lösung wie bei `hautarbeiter.js`.
 */
import { Anatomierechnung } from './anatomierechnung.js';

class Anatomiearbeiter {

    static async rechnen(d) {
        const ergebnis = await Anatomierechnung.rechnen(d);
        self.postMessage({ typ: 'fertig', id: d.id, ergebnis }, Anatomiearbeiter.puffer(ergebnis));
    }

    /** Die Puffer des Ergebnisses, jeder genau einmal (eine doppelte Nennung wirft beim Übertragen). */
    static puffer(r) {
        return [...new Set([r.farbe, r.normal, r.rauheit].filter(Boolean).map((a) => a.buffer))];
    }

    /** Der Rückgabewert ist das Versprechen des Laufs (der Worker selbst braucht ihn nicht; die Prüfung wartet darauf). */
    static nachricht(ereignis) {
        const d = ereignis.data;
        if (d?.typ !== 'rechnen') return undefined;
        return Anatomiearbeiter.rechnen(d).catch((fehler) => {
            self.postMessage({ typ: 'fehler', id: d.id, meldung: fehler?.stack || String(fehler) });
        });
    }
}

self.onmessage = Anatomiearbeiter.nachricht;
