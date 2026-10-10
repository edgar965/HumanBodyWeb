/**
 * Combosortierung — jede Auswahlliste (`<select>`) der Seite steht alphabetisch (10.10.2026).
 *
 * Edgar: „bei allen Combo boxen möchte ich die Einträge alphabetisch sortiert haben, checke ALLE Combo Boxen, alle Tabs, alle Listen".
 * Es gibt rund 150 `<select>` in den Vorlagen und viele, die das JS zur Laufzeit füllt (Haut, Augen, Brauen, Schminke, Modelle …) —
 * einzeln hätte jede neue Liste ihre eigene Sortierung gebraucht und eine vergessene wäre unsortiert geblieben. Darum EINE Stelle:
 * beim Laden sortiert sie alle vorhandenen Listen, danach jede, die neu entsteht oder neue Einträge bekommt (`MutationObserver`).
 *
 * Regeln:
 *  - Reihenfolge ohne Groß-/Kleinschreibung, deutsch, Zahlen als Zahlen („Stufe 2" vor „Stufe 10", „512 px" vor „2048 px").
 *  - Die ersten Einträge, die „nichts" oder „Vorgabe" bedeuten (Wert leer, „—", „Keine …", „Original …", „Standard", „Alle", „Automatisch …",
 *    „Vorgabe …"), bleiben vorn und in ihrer Reihenfolge; sortiert wird, was danach kommt. Weiter hinten stehende Einträge dieser Art
 *    zählen als gewöhnliche Namen.
 *  - Eine Liste mit `<optgroup>`: die Gruppen nach Beschriftung, die Einträge je Gruppe; Einträge ohne Gruppe stehen davor.
 *  - Die Auswahl bleibt, wo sie war (auch bei Mehrfachauswahl); es wird kein `change` ausgelöst.
 *  - **Ausnahme: Stufenfolgen** — Auflösungen, „Niedrig/Mittel/Hoch", Einheiten, deren Reihenfolge der Sinn ist. Sie tragen
 *    `data-reihenfolge="fest"` (am `<select>` oder an einem Elternelement) und bleiben, wie der Bau sie legt.
 */
export class Combosortierung {

    static KOLLATOR = new Intl.Collator('de', { numeric: true, sensitivity: 'base' });
    /** Anfang einer Beschriftung, die „nichts" oder „die Vorgabe" meint und deshalb vorn bleibt. */
    static NEUTRAL = /^\s*(—|–|-{1,2}|\.{3}|…|\(|keine?[nrms]?\b|ohne\b|none\b|bitte\b|alle\b|standard\b|vorgabe\b|original\b|auto(matisch)?\b)/i;
    static FEST = '[data-reihenfolge="fest"]';

    static _beobachter = null;
    static _offen = new Set();

    /** Einmal je Seite aufrufen: vorhandene Listen sortieren und neue/ergänzte beobachten. */
    static einrichten(wurzel = document) {
        if (Combosortierung._beobachter) return;
        const sortierenAlle = () => wurzel.querySelectorAll('select').forEach(s => Combosortierung.sortieren(s));
        sortierenAlle();
        Combosortierung._beobachter = new MutationObserver(Combosortierung._geaendert);
        Combosortierung._beobachter.observe(wurzel.documentElement || wurzel, { childList: true, subtree: true });
        if (wurzel.readyState === 'loading') wurzel.addEventListener('DOMContentLoaded', sortierenAlle, { once: true });
    }

    static _geaendert(aenderungen) {
        for (const a of aenderungen) {
            const ziel = a.target.nodeType === 1 ? a.target.closest?.('select') : null;
            if (ziel) Combosortierung._offen.add(ziel);
            for (const n of a.addedNodes) {
                if (n.nodeType !== 1) continue;
                if (n.tagName === 'SELECT') Combosortierung._offen.add(n);
                else if (n.querySelectorAll) n.querySelectorAll('select').forEach(s => Combosortierung._offen.add(s));
            }
        }
        if (Combosortierung._offen.size) queueMicrotask(Combosortierung._abarbeiten);
    }

    static _abarbeiten() {
        const liste = [...Combosortierung._offen];
        Combosortierung._offen.clear();
        for (const s of liste) if (s.isConnected) Combosortierung.sortieren(s);
    }

    /** Ist diese Beschriftung/dieser Wert ein „nichts"- oder Vorgabe-Eintrag? */
    static neutral(option) {
        return option.value === '' || Combosortierung.NEUTRAL.test(option.textContent);
    }

    /** Sortierschlüssel einer Beschriftung: ein deutsches Datum „14.09.2026" steht als „2026-09-14", damit „Aufzeichnung 05.10.2026" hinter „… 14.09.2026" kommt. */
    static schluessel(text) {
        return text.trim().replace(/\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b/g,
            (_, tag, monat, jahr) => `${jahr}-${monat.padStart(2, '0')}-${tag.padStart(2, '0')}`);
    }

    /** Die Reihenfolge einer Liste von Einträgen: führende neutrale zuerst (unverändert), der Rest nach Beschriftung. */
    static reihenfolge(optionen) {
        let vorn = 0;
        while (vorn < optionen.length && Combosortierung.neutral(optionen[vorn])) vorn++;
        const k = Combosortierung.KOLLATOR;
        const s = Combosortierung.schluessel;
        const rest = optionen.slice(vorn).sort((a, b) => k.compare(s(a.textContent), s(b.textContent)));
        return [...optionen.slice(0, vorn), ...rest];
    }

    static sortieren(select) {
        if (select.closest(Combosortierung.FEST)) return false;
        const kinder = [...select.children];
        const direkt = kinder.filter(k => k.tagName === 'OPTION');
        const gruppen = kinder.filter(k => k.tagName === 'OPTGROUP');
        const k = Combosortierung.KOLLATOR;
        const neu = [
            ...Combosortierung.reihenfolge(direkt),
            ...gruppen.sort((a, b) => k.compare(a.label || '', b.label || '')),
        ];
        const gewaehlt = [...select.options].filter(o => o.selected);
        const bisher = kinder.filter(c => c.tagName === 'OPTION' || c.tagName === 'OPTGROUP');
        let geaendert = neu.some((n, i) => n !== bisher[i]);
        for (const g of gruppen) {
            const optionen = [...g.children].filter(c => c.tagName === 'OPTION');
            const sortiert = Combosortierung.reihenfolge(optionen);
            if (sortiert.some((o, i) => o !== optionen[i])) { g.append(...sortiert); geaendert = true; }
        }
        if (!geaendert) return false;
        select.append(...neu);
        for (const o of gewaehlt) o.selected = true;
        return true;
    }
}
