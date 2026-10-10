/**
 * Baumsortierung — Baumlisten und Listen der Seite stehen alphabetisch (10.10.2026).
 *
 * Edgar: „bei allen Combo boxen möchte ich die Einträge alphabetisch sortiert haben, checke ALLE Combo Boxen, alle Tabs, alle Listen" und, als
 * `Combosortierung` die Baumlisten und Tabellen noch ausnahm: „mach das auch". Die Listen entstehen an einem Dutzend Stellen (Animationen,
 * GarmentCode, MakeHuman, Kleider, Posen, die Garderobe der Genesis-Figuren, „Getragen", die Objektliste) — wie bei den Combo-Boxen EINE Klasse,
 * die beim Laden sortiert und danach jede Liste, die neu entsteht oder Einträge bekommt (`MutationObserver`).
 *
 * Gemeinsame Formen (`Kategoriekasten`, `kleider_liste.js`, `pose_apply.js`, `mhproxy_ordner.js`, Studio `bibliotheksbaum.js` mit `.lib-cat`): ein Kasten `.anim-category` / `.anim-folder` mit Kopf
 * und Körper, im Körper Einträge `.anim-item` (Studio: `.lib-item`) und weitere Kästen. Dazu die Garderobe der Genesis-Figuren (`details.g9-kategorie` mit Zeilen
 * `.slider-row`, deren „Einstellungen" hinter ihrer Zeile mitwandern) und zwei einfache Listen (`#prop-equipped-list`, `#character-list`).
 *
 * Regeln:
 *  - Reihenfolge wie `Combosortierung` (deutsch, ohne Groß-/Kleinschreibung, Zahlen als Zahlen, Datum als Jahr-Monat-Tag).
 *  - Kästen und Einträge werden je für sich sortiert und bleiben an den Plätzen ihrer Art; was nicht dazugehört (Kopf, Hinweiszeilen, die
 *    „Einstellungen" vor der ersten Zeile) bleibt, wo es steht.
 *  - In der Garderobe stehen Sammeleinträge („Kleidung – Generisch …") vorn; hinter einer Zeile bleibt, was zu ihr gehört, bis zur nächsten Zeile.
 *  - `data-reihenfolge="fest"` an der Liste oder einem Elternelement lässt sie, wie sie ist (wie bei den Combo-Boxen).
 *  - Eine schon sortierte Liste wird nicht angefasst (sonst fände der Beobachter in seinen eigenen Änderungen eine Endlosschleife).
 */
import { Combosortierung } from './combosortierung.js';

export class Baumsortierung {

    static FEST = '[data-reihenfolge="fest"]';
    static KASTEN = '.anim-category, .anim-folder, .lib-cat';
    /** Alles, was Einträge ordnet: Körper der Kästen und die Listen mit eigener Regel. */
    static BEHAELTER = '.anim-category-body, .anim-folder-body, .lib-cat-body, #prop-equipped-list, #character-list, #assets-genesis9-garderobe, details.g9-kategorie';
    /** Teile eines Kopfes, die nicht zur Beschriftung gehören (Pfeil, Zähler). */
    static KOPF_ZUSATZ = /chevron|count|zahl|gedaempft/;
    static NAMEN = '.kld-name, .garment-name, .kleidungsname, .stueckname';
    /** Sammeleinträge der Garderobe, die vor den einzelnen Stücken stehen bleiben. */
    static VORN = /\bGenerisch\b/i;

    static _beobachter = null;
    static _offen = new Set();

    /** Einmal je Seite aufrufen: vorhandene Listen sortieren und neue/ergänzte beobachten. */
    static einrichten(wurzel = document) {
        if (Baumsortierung._beobachter) return;
        Baumsortierung.alle(wurzel);
        Baumsortierung._beobachter = new MutationObserver(Baumsortierung._geaendert);
        Baumsortierung._beobachter.observe(wurzel.documentElement || wurzel, { childList: true, subtree: true });
        if (wurzel.readyState === 'loading') wurzel.addEventListener('DOMContentLoaded', () => Baumsortierung.alle(wurzel), { once: true });
    }

    static alle(wurzel = document) {
        const behaelter = new Set(wurzel.querySelectorAll(Baumsortierung.BEHAELTER));
        for (const kasten of wurzel.querySelectorAll(Baumsortierung.KASTEN)) if (kasten.parentElement) behaelter.add(kasten.parentElement);
        for (const b of behaelter) Baumsortierung.sortiere(b);
    }

    static _geaendert(aenderungen) {
        for (const a of aenderungen) {
            if (a.target.nodeType === 1 && a.target.matches(Baumsortierung.BEHAELTER)) Baumsortierung._offen.add(a.target);
            for (const n of a.addedNodes) if (n.nodeType === 1) Baumsortierung._vormerken(n);
        }
        if (Baumsortierung._offen.size) queueMicrotask(Baumsortierung._abarbeiten);
    }

    /** Ein neuer Knoten und alles darunter: Listen, deren Einträge schon beim Bau (abgehängt) kamen, sind erst jetzt zu sehen. */
    static _vormerken(knoten) {
        const T = Baumsortierung;
        if (knoten.matches(T.BEHAELTER)) T._offen.add(knoten);
        if (knoten.matches(T.KASTEN) && knoten.parentElement) T._offen.add(knoten.parentElement);
        knoten.querySelectorAll(T.BEHAELTER).forEach(b => T._offen.add(b));
        knoten.querySelectorAll(T.KASTEN).forEach(k => { if (k.parentElement) T._offen.add(k.parentElement); });
    }

    static _abarbeiten() {
        const liste = [...Baumsortierung._offen];
        Baumsortierung._offen.clear();
        for (const b of liste) Baumsortierung.sortiere(b);
    }

    // ---------------------------------------------------------------- Beschriftungen

    static text(element) {
        return (element?.textContent || '').trim().replace(/\s+/g, ' ');
    }

    /**
     * Der Name eines Kastens: Kopf ohne Pfeil und Zähler. Der Pfeil ist ein Element (`.cat-chevron`, `.chevron`), der Zähler ein Element (`.cat-count`)
     * oder Text hinter dem Namen („accessories (27)" in Kleider und MakeHuman); der Pfeil wechselt beim Aufklappen (▶ → ▼) und darf nicht mitzählen
     * — im Chrome sortierte sich das geöffnete „dresses" sonst hinter alle geschlossenen.
     */
    static kopfname(kasten) {
        const T = Baumsortierung;
        const kopf = kasten.querySelector(':scope > .anim-category-header, :scope > .anim-folder-header, :scope > .lib-cat-header');
        if (!kopf) return T.text(kasten.firstElementChild);
        const teile = [...kopf.childNodes]
            .filter(n => n.nodeType === 3 || !T.KOPF_ZUSATZ.test(String(n.className)))
            .map(n => n.textContent);
        return teile.join(' ').trim().replace(/\s+/g, ' ').replace(/\s*\(\d+\)$/, '');
    }

    /** Der Name einer Kategorie der Garderobe: nur der Text der Überschrift, ohne den Zähler „(98)". */
    static kategoriename(kategorie) {
        const kopf = kategorie.querySelector(':scope > summary');
        const eigen = [...(kopf?.childNodes || [])].filter(n => n.nodeType === 3).map(n => n.textContent).join('');
        return (eigen || Baumsortierung.text(kopf)).trim().replace(/\s+/g, ' ');
    }

    static eintragsname(eintrag) {
        const T = Baumsortierung;
        const name = eintrag.querySelector(T.NAMEN);
        return name ? T.text(name) : (eintrag.dataset?.name || T.text(eintrag.querySelector('span')) || T.text(eintrag));
    }

    // ---------------------------------------------------------------- Ordnen

    /** Die Läufe eines Behälters: was darin in welcher Reihenfolge steht (`eintrag`: Selektor der direkten Kinder, `name`: Beschriftung). */
    static laeufe(behaelter) {
        const T = Baumsortierung;
        const im = id => behaelter.id === id;
        if (im('prop-equipped-list')) return [{ eintrag: ':scope > li', name: e => T.text(e.querySelector('.equipped-item-name')) }];
        if (im('character-list')) return [{ eintrag: ':scope > li', name: e => T.text(e.querySelector('.character-item-name')) }];
        if (im('assets-genesis9-garderobe')) return [{ eintrag: ':scope > details.g9-kategorie', name: T.kategoriename }];
        if (behaelter.matches('details.g9-kategorie')) {
            return [{ eintrag: ':scope > .slider-row', filter: e => !!e.querySelector('.stueckname'), name: e => T.text(e.querySelector('.stueckname')),
                      anhaengen: true, vorn: n => T.VORN.test(n) }];
        }
        return [{ eintrag: ':scope > .anim-category, :scope > .anim-folder, :scope > .lib-cat', name: T.kopfname },
                { eintrag: ':scope > .anim-item, :scope > .lib-item', name: T.eintragsname }];
    }

    /**
     * Die neue Reihenfolge der Kinder — oder `null`, wenn sie schon stimmt.
     * `anhaengen`: Was hinter einem Eintrag steht und selbst keiner ist, wandert mit ihm bis zum nächsten Eintrag. Sonst bleibt jedes
     * Nicht-Eintrag an seinem Platz und die Einträge verteilen sich auf ihre Plätze. `vorn(name)`: solche Einträge stehen zuerst, in ihrer Reihenfolge.
     */
    static ordnen(kinder, eintraege, name, { anhaengen = false, vorn = null } = {}) {
        const menge = new Set(eintraege);
        const schluessel = e => Combosortierung.schluessel(name(e));
        const vergleich = (a, b) => Combosortierung.KOLLATOR.compare(schluessel(a), schluessel(b));
        const fest = vorn ? eintraege.filter(e => vorn(name(e))) : [];
        const festMenge = new Set(fest);
        const geordnet = [...fest, ...eintraege.filter(e => !festMenge.has(e)).sort(vergleich)];
        let neu;
        if (anhaengen) {
            const erste = kinder.findIndex(k => menge.has(k));
            if (erste < 0) return null;
            const gruppen = new Map();
            let aktuell = null;
            for (const k of kinder.slice(erste)) {
                if (menge.has(k)) { aktuell = [k]; gruppen.set(k, aktuell); } else aktuell.push(k);
            }
            neu = [...kinder.slice(0, erste), ...geordnet.flatMap(e => gruppen.get(e))];
        } else {
            let i = 0;
            neu = kinder.map(k => (menge.has(k) ? geordnet[i++] : k));
        }
        return neu.some((k, i) => k !== kinder[i]) ? neu : null;
    }

    /** Einen Behälter ordnen; `true`, wenn sich etwas bewegt hat. */
    static sortiere(behaelter) {
        if (!behaelter.isConnected || behaelter.closest(Baumsortierung.FEST)) return false;
        let geaendert = false;
        for (const lauf of Baumsortierung.laeufe(behaelter)) {
            const eintraege = [...behaelter.querySelectorAll(lauf.eintrag)].filter(lauf.filter || (() => true));
            const neu = Baumsortierung.ordnen([...behaelter.children], eintraege, lauf.name, lauf);
            if (neu) { behaelter.append(...neu); geaendert = true; }
        }
        return geaendert;
    }
}
