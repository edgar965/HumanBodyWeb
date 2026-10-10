/**
 * Normalenarbeiter — die Normalen der Gelenkkorrekturen in einem Web Worker (09.10.2026).
 *
 * Der Hauptfaden stand für `Genesis9normalen.nachziehen` an einer tanzenden Genesis-9-Figur 25–70 ms je Bild
 * (`normalenrechnung.js`). Hier läuft dieselbe Rechnung neben dem Zeichnen; der Hauptfaden schickt je Bild die Punktlage und die
 * berührten Punkte und schreibt das Ergebnis ins Normalen-Attribut (`normalenarbeit.js`).
 *
 * Nachrichten (Hauptfaden → Worker):
 *   netz    {netz, index, gruppe, ruhePos, anzahlGruppen}   einmal je Geometrie; der Worker rechnet die Ruhe-Dreiecksnormalen
 *   rechnen {netz, folge, stempel, pos, ruheNormalen, punkte, anzahl}
 *           → fertig {netz, folge, stempel, punkte, normalen}   (die Puffer werden übertragen, nicht kopiert)
 *           → fehler {netz, folge, meldung}                      (der Hauptfaden rechnet dann selbst weiter)
 *   frei    {netz}                                           die Geometrie ist weg — Speicher freigeben
 *
 * Er liegt außerhalb des Szenenbündels (`/buendel/<fassung>/scene.js`): die Vorlage nennt seinen Pfad mit Fassung
 * (`<meta name="normalenarbeiter">`, `{% fassungspfad %}`) — dieselbe Lösung wie bei `hautarbeiter.js`.
 */
import { Normalenrechnung } from './normalenrechnung.js';

class Normalenarbeiter {

    /** netz-Kennung -> {index, gruppe, ruheDreiecke, summen} */
    static netze = new Map();

    static netz(d) {
        Normalenarbeiter.netze.set(d.netz, {
            index: d.index, gruppe: d.gruppe,
            ruheDreiecke: Normalenrechnung.ruheDreiecke(d.index, d.gruppe, d.ruhePos, d.anzahlGruppen),
            summen: new Float64Array(d.anzahlGruppen * 3),
        });
    }

    static rechnen(d) {
        const netz = Normalenarbeiter.netze.get(d.netz);
        if (!netz) throw new Error(`Netz ${d.netz} unbekannt`);
        const normalen = Normalenrechnung.rechnen(netz, d);
        self.postMessage({ typ: 'fertig', netz: d.netz, folge: d.folge, stempel: d.stempel, punkte: d.punkte, normalen },
                         [d.punkte.buffer, normalen.buffer]);
    }

    static nachricht(ereignis) {
        const d = ereignis.data;
        try {
            if (d?.typ === 'netz') Normalenarbeiter.netz(d);
            else if (d?.typ === 'rechnen') Normalenarbeiter.rechnen(d);
            else if (d?.typ === 'frei') Normalenarbeiter.netze.delete(d.netz);
        } catch (fehler) {
            self.postMessage({ typ: 'fehler', netz: d?.netz, folge: d?.folge, meldung: fehler?.stack || String(fehler) });
        }
    }
}

self.onmessage = Normalenarbeiter.nachricht;
