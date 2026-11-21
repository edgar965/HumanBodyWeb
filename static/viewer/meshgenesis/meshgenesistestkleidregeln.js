/**
 * Meshgenesistestkleidregeln — der Satz „gebaut mit: …“ in der Kleiderliste der Testseite (21.11.2026, Edgar: „wo ist jetzt deine neue Kleider Auswahl im UI?“, Konzept
 * `2026-11-21_bibliothek-anpassen-konzept.md`, Abschnitt 11). Der Server (`Kleidregelnstand`) hängt an die Einträge z, e, f den Schlüssel `regeln_text` {kurz, titel}: die Regeln, die die Stufe
 * „Kleidungsregeln“ am Stück angewandt hat, und der Stand je Regel als Hinweis (Maus über der Zeile). Ohne `regeln_text` bleibt die Zeile, wie sie ist.
 */
export class Meshgenesistestkleidregeln {
    /** Setzt Text und Hinweis einer Zeile der Liste: `text` = Satz des Wegs, `eintrag` = `st[weg]`. */
    static setzen(zeile, text, eintrag) {
        const r = eintrag?.regeln_text;
        zeile.textContent = r?.kurz ? `${text} · ${r.kurz}` : text;
        if (r?.titel) zeile.title = r.titel;
    }
}
