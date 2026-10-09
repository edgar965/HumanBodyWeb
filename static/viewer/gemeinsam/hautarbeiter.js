/**
 * Hautarbeiter — die Haut-Maske in einem Web Worker (09.10.2026).
 *
 * Der Hauptfaden stand für `Hautverdeckung.anwenden` am feinen Körper 2,8 s, belastet 11–14 s, auf der Filmstufe bis 19 s
 * (`hautrechnung.js`). Hier läuft dieselbe Rechnung neben dem Zeichnen; der Hauptfaden schickt Punkte und Stücke, bekommt Maske,
 * Einzug und Index-Wegweiser zurück und schreibt sie ins Netz (`hautarbeit.js`).
 *
 * Nachrichten:
 *   rechnen  {id, pos (n·3), index, stoffe: [{schluessel, punkte, dreiecke, tiefe, starr, nahe, ersatz}]}
 *            → fertig {id, ergebnis}   (`Hautrechnung.rechnen`; die Puffer werden übertragen, nicht kopiert)
 *            → fehler {id, meldung}    (der Hauptfaden rechnet dann selbst weiter)
 *
 * Er liegt außerhalb des Szenenbündels (`/buendel/<fassung>/scene.js`): die Vorlage nennt seinen Pfad mit Fassung
 * (`<meta name="hautarbeiter">`, `{% fassungspfad %}`) — dieselbe Lösung wie beim Stoffschwung (`stoffarbeiter.js`).
 */
import { Hautrechnung } from './hautrechnung.js';

class Hautarbeiter {

    static rechnen(d) {
        const ergebnis = Hautrechnung.rechnen(d.pos, d.index, d.stoffe);
        self.postMessage({ typ: 'fertig', id: d.id, ergebnis }, Hautarbeiter.puffer(ergebnis));
    }

    /** Die Puffer des Ergebnisses, jeder genau einmal (eine doppelte Nennung wirft beim Übertragen). */
    static puffer(r) {
        const alle = [r.maske, r.ersatz, r.hoehe, r.rand, r.normalen, r.einzug.werte, r.einzug.weg, ...r.randabstaende];
        return [...new Set(alle.filter(Boolean).map((a) => a.buffer))];
    }

    static nachricht(ereignis) {
        const d = ereignis.data;
        if (d?.typ !== 'rechnen') return;
        try {
            Hautarbeiter.rechnen(d);
        } catch (fehler) {
            self.postMessage({ typ: 'fehler', id: d.id, meldung: fehler?.stack || String(fehler) });
        }
    }
}

self.onmessage = Hautarbeiter.nachricht;
