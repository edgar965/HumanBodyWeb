import { Netzstufe } from './netzstufe.js';
import { Schnellanzeige } from './schnellanzeige.js';

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

    /** Was gewählt ist. Beim Laden: die Einstellung (`grob` auf Seiten mit `Schnellanzeige`) — oder die Filmstufe, wenn das Neuladen von Strg+Alt+H kommt. */
    static wahl = typeof document !== 'undefined' && Netzstufe.gewaehlt() === Netzstufe.HOCH ? 'ultrafein' : Schnellanzeige.stufe();

    /** Figur-Kennung → `{stufe, laedt, fertig, gesamt}`. */
    static _figuren = new Map();
    /** Figur-Kennung → was an ihr noch nicht gezeichnet ist (`Zeichenstand`, 19.10.2026), Texte. */
    static _offen = new Map();
    /** Entsorgte Figuren (`vergessen`): `Zeichenstand` hört auf, sie zu beobachten. */
    static _entsorgt = new WeakSet();

    /**
     * Die Seite lädt noch, bevor sich eine Figur anmeldet (19.10.2026): zwischen Seitenaufbau und erster Figur stand rund 0,8 s „Netz: grob" ohne Sanduhr — als wäre
     * alles da. Bis `seiteFertig` (die Seite hat ihre Figuren angestoßen, `Szenenaufbau.startsequenz`, `Mesh3daiseite`) oder spätestens `SEITE_MS` heißt es „lädt noch: Seite".
     */
    static SEITE_MS = 15000;
    static _seite = typeof document !== 'undefined';
    static _seiteUhr = Netzstufenstand._seite ? Netzstufenstand._uhr(() => Netzstufenstand.seiteFertig(0), Netzstufenstand.SEITE_MS) : null;

    /** Die Seite hat ihre Figuren angestoßen; meldet sich in `nachMs` keine an, steht die blanke Stufe da (ohne Figur gibt es nichts zu warten). */
    static seiteFertig(nachMs = 1500) {
        clearTimeout(Netzstufenstand._seiteUhr);
        const aus = () => { Netzstufenstand._seite = false; Netzstufenstand._senden(); };
        if (nachMs > 0) Netzstufenstand._seiteUhr = Netzstufenstand._uhr(aus, nachMs); else aus();
    }

    /** Ein Zeitgeber, der in Node den Prozess nicht offen hält (Tests). */
    static _uhr(tun, ms) {
        const uhr = setTimeout(tun, ms);
        uhr?.unref?.();
        return uhr;
    }

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

    /** Was an der Figur noch fehlt (`Zeichenstand`): leere Liste = alles gezeichnet. Gesendet wird nur, wenn sich etwas ändert. */
    static offen(inst, liste) {
        if (!inst?.id || Netzstufenstand._entsorgt.has(inst)) return;
        if ((Netzstufenstand._offen.get(inst.id) || []).join('|') === liste.join('|')) return;
        if (liste.length) Netzstufenstand._offen.set(inst.id, [...liste]); else Netzstufenstand._offen.delete(inst.id);
        Netzstufenstand._senden();
    }

    static vergessen(inst) {
        if (!inst?.id) return;
        Netzstufenstand._entsorgt.add(inst);
        const stufe = Netzstufenstand._figuren.delete(inst.id), offen = Netzstufenstand._offen.delete(inst.id);
        if (stufe || offen) Netzstufenstand._senden();
    }

    static entsorgt(inst) {
        return Boolean(inst) && Netzstufenstand._entsorgt.has(inst);
    }

    /** Die letzte fertige Stufe dieser Figur — oder null. */
    static stufeVon(inst) {
        return Netzstufenstand._figuren.get(inst?.id)?.stufe || null;
    }

    /** Alle Figuren zusammen: die NIEDRIGSTE fertige Stufe, ob eine lädt, die Zähler summiert, was noch fehlt (`offen`, gleiche Texte gezählt). */
    static zusammen() {
        const alle = [...Netzstufenstand._figuren.values()];
        const offen = Netzstufenstand._offenListe();
        if (!alle.length) return { stufe: Netzstufenstand.wahl, laedt: false, fertig: 0, gesamt: 0, offen: Netzstufenstand._seite && !offen.length ? ['Seite'] : offen };
        const rang = stufe => Netzstufenstand.STUFEN.indexOf(stufe);
        return {
            stufe: alle.reduce((tief, e) => (rang(e.stufe) < rang(tief) ? e.stufe : tief), alle[0].stufe),
            laedt: alle.some(e => e.laedt),
            fertig: alle.reduce((s, e) => s + (e.laedt ? e.fertig : 0), 0),
            gesamt: alle.reduce((s, e) => s + (e.laedt ? e.gesamt : 0), 0),
            offen,
        };
    }

    /** Die offenen Teile aller Figuren; derselbe Text an zwei Figuren (Ziel und Ergebnis) steht einmal, mit „×2". */
    static _offenListe() {
        const zahl = new Map();
        for (const liste of Netzstufenstand._offen.values()) for (const text of liste) zahl.set(text, (zahl.get(text) || 0) + 1);
        return [...zahl].map(([text, n]) => (n > 1 ? `${text} ×${n}` : text));
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
