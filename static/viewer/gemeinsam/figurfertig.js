import { Netzstufenstand } from './netzstufenstand.js';

/**
 * Figurfertig — warten, bis eine Figur ganz dasteht: die gewählte Stufe gebaut und nichts mehr offen (`Zeichenstand`: Bilder, Hautmaske, Anatomie).
 *
 * Edgar, 24.11.2026: „EdgarNeu laden im Charakter dauert ewig, das muss in 2 s laden“. Gemessen im Charakter: mitten im Laden baute die Seite die Reglerliste (334–610 ms am Stück),
 * die Garderobe (4,3 MB Katalog lesen und eintragen, 130–540 ms) und fragte die Vorab-Anzeigen der Figur an (`Genesis9vorrat.fuellen`) — alles im selben Hauptfaden, der die Figur
 * gerade baut. Wer nicht zum Bild gehört, wartet jetzt hier, bis die Figur steht.
 */
export class Figurfertig {

    /** Länger wartet niemand: danach geht es ohne die fertige Figur weiter (ein Bild, das nie kommt, hielte sonst die Reglerliste auf). */
    static FRIST_MS = 6000;
    static TAKT_MS = 100;

    /** Löst sich, wenn die Figur steht — bei einer fertigen Figur gleich. Scheitert nie. `ausser`: worauf der Aufrufer nicht wartet (Texte von `Zeichenstand.offen`). */
    static async abwarten(inst, frist = Figurfertig.FRIST_MS, ausser = []) {
        if (!inst) return;
        const ende = performance.now() + frist, pause = ms => new Promise(weiter => setTimeout(weiter, ms));
        await Promise.race([Promise.resolve(inst.fein).catch(() => {}), pause(frist)]);
        while (performance.now() < ende && !Netzstufenstand.entsorgt(inst) && Netzstufenstand.offenAn(inst).some(t => !ausser.includes(t))) await pause(Figurfertig.TAKT_MS);
    }
}
