import { Netzstufe } from './netzstufe.js';

/**
 * Netzstufenstand — in welcher Auflösung stehen die Figuren der Szene gerade, und welche hat der Nutzer gewählt?
 *
 * Edgar, 09.10.2026: „mach zwei Stufen für Ctrl-Alt-H, einmal grobe Stufe (beim ersten Laden), dann fein, dann ultrafein. Die
 * Stufe soll immer rechts unten angezeigt werden … Nach dem Laden lade die mittlere Stufe nach und nach, und ändere die
 * Anzeige, wenn fertig."
 *
 *   grob       der Käfig (`?stufen=0`, 25.182 Punkte) — so steht die Figur nach dem ersten Zug da
 *   fein       die Einstellung des Browsers (2 Unterteilungen, `Einstellungen → Modell`) — kommt danach stückweise
 *   ultrafein  die Filmstufe (Keks `netzstufen=3`, dazu die 8K-Detailnormalen) — die bisherige Wirkung von Strg+Alt+H
 *
 * Die GEWÄHLTE Stufe (`wahl`) gilt für alle Anfragen (`Genesis9aufbau.adresse`); die ANGEZEIGTE steht je Figur und ist die
 * letzte fertig gebaute. Die Anzeige rechts unten (`Netzstufenschalter`) hört auf das Ereignis `EREIGNIS`.
 */
export class Netzstufenstand {

    static EREIGNIS = 'netzstufe-stand';
    static STUFEN = ['grob', 'fein', 'ultrafein'];

    /** Was gewählt ist. Beim Laden: die Einstellung — oder die Filmstufe, wenn das Neuladen von Strg+Alt+H kommt. */
    static wahl = typeof document !== 'undefined' && Netzstufe.gewaehlt() === Netzstufe.HOCH ? 'ultrafein' : 'fein';

    /** Figur-Kennung → `{stufe, laedt, fertig, gesamt}`. */
    static _figuren = new Map();

    /**
     * Eine Figur meldet ihren Stand.
     * @param stufe die letzte FERTIGE Stufe (grob | fein | ultrafein)
     * @param laedt ob gerade eine höhere nachgeholt wird; `fertig`/`gesamt` zählen Körper plus Stücke
     */
    static melden(inst, stufe, laedt = false, fertig = 0, gesamt = 0) {
        if (!inst?.id) return;
        Netzstufenstand._figuren.set(inst.id, { stufe, laedt, fertig, gesamt });
        Netzstufenstand._senden();
    }

    static vergessen(inst) {
        if (inst?.id && Netzstufenstand._figuren.delete(inst.id)) Netzstufenstand._senden();
    }

    /** Die letzte fertige Stufe dieser Figur — oder null. */
    static stufeVon(inst) {
        return Netzstufenstand._figuren.get(inst?.id)?.stufe || null;
    }

    /** Alle Figuren zusammen: die NIEDRIGSTE fertige Stufe, ob eine lädt, die Zähler summiert. */
    static zusammen() {
        const alle = [...Netzstufenstand._figuren.values()];
        if (!alle.length) return { stufe: Netzstufenstand.wahl, laedt: false, fertig: 0, gesamt: 0 };
        const rang = stufe => Netzstufenstand.STUFEN.indexOf(stufe);
        return {
            stufe: alle.reduce((tief, e) => (rang(e.stufe) < rang(tief) ? e.stufe : tief), alle[0].stufe),
            laedt: alle.some(e => e.laedt),
            fertig: alle.reduce((s, e) => s + (e.laedt ? e.fertig : 0), 0),
            gesamt: alle.reduce((s, e) => s + (e.laedt ? e.gesamt : 0), 0),
        };
    }

    /** Die nächste Stufe im Kreis: grob → fein → ultrafein → grob. */
    static naechste(stufe) {
        const i = Netzstufenstand.STUFEN.indexOf(stufe);
        return Netzstufenstand.STUFEN[(i + 1) % Netzstufenstand.STUFEN.length];
    }

    static _senden() {
        if (typeof document === 'undefined' || !document.dispatchEvent) return;
        document.dispatchEvent(new CustomEvent(Netzstufenstand.EREIGNIS, { detail: Netzstufenstand.zusammen() }));
    }
}
