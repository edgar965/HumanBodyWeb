# -*- coding: utf-8 -*-
"""`Combosortierung`: jede Auswahlliste steht alphabetisch (Edgar, 10.10.2026: „bei allen Combo boxen möchte ich die Einträge
alphabetisch sortiert haben, checke ALLE Combo Boxen, alle Tabs, alle Listen"), geprüft in Node an einer DOM-Attrappe.

1. Gewöhnliche Liste: ohne Groß-/Kleinschreibung, deutsch; Zahlen als Zahlen („Stufe 2" vor „Stufe 10").
2. Führende „nichts"-/Vorgabe-Einträge (Wert leer, „—", „Original …", „Vorgabe …") bleiben vorn; sortiert wird der Rest. Ein
   Eintrag wie „Keine" MITTEN in der Liste ist ein gewöhnlicher Name.
3. Die Auswahl bleibt, auch wenn ihr Eintrag wandert.
4. `data-reihenfolge="fest"` (am Feld oder an einem Elternelement) lässt die Liste, wie sie ist — Stufenfolgen wie „Niedrig/Mittel/Hoch".
5. `<optgroup>`: Gruppen nach Beschriftung, Einträge je Gruppe, Einträge ohne Gruppe davor.
6. Eine schon sortierte Liste wird nicht angefasst (Rückgabe `false`) — sonst fände der Beobachter in seinen eigenen Änderungen
   eine Endlosschleife.

Sabotage-Gegenprobe: `sensitivity: 'base'` und `numeric: true` aus dem Kollator nehmen → Fall 1 rot; die Schleife über die führenden neutralen Einträge
(`while (vorn < …)`) streichen → Fall 2 rot; `for (const o of gewaehlt) o.selected = true` streichen → Fall 3 rot; die Zeile mit `FEST` streichen →
Fall 4 rot; den Vergleich `neu.some(…)` weglassen und immer anhängen → Fall 6 rot.

Nicht getestet (kein DOM in Node): der `MutationObserver` in `einrichten` — im Chrome an den echten Seiten prüfen.
Nicht gelaufen — läuft nur auf Ansage.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'combosortierung.js')

SKRIPT = """
class Opt {
    constructor(text, wert = text, gewaehlt = false) { this.tagName = 'OPTION'; this.textContent = text; this.value = wert; this.selected = gewaehlt; }
}
class Gruppe {
    constructor(label, kinder) { this.tagName = 'OPTGROUP'; this.label = label; this.children = kinder; }
    append(...k) { this.children = k; }
}
class Sel {
    constructor(kinder, fest = false) { this.tagName = 'SELECT'; this.children = kinder; this.fest = fest; this.aenderungen = 0; }
    closest(muster) { return this.fest && muster === '[data-reihenfolge="fest"]' ? this : null; }
    get options() { return this.children.flatMap(k => k.tagName === 'OPTGROUP' ? k.children : [k]); }
    append(...k) {
        // Wie der Browser beim Umhängen: die Auswahl fällt weg, ohne Auswahl gilt der erste Eintrag.
        for (const o of this.options) o.selected = false;
        this.children = k;
        if (this.options.length) this.options[0].selected = true;
        this.aenderungen += 1;
    }
}
const { Combosortierung: C } = await import(MODUL);
const text = s => s.options.map(o => o.textContent);

// 1. gewöhnlich, Zahlen als Zahlen
let s = new Sel(['Zebra', 'apfel', 'Banane', 'Cherry'].map(t => new Opt(t)));
C.sortieren(s);
pruefe('Groß/Klein egal', text(s), ['apfel', 'Banane', 'Cherry', 'Zebra']);
s = new Sel(['Stufe 10', 'Stufe 2', 'Stufe 1'].map(t => new Opt(t)));
C.sortieren(s);
pruefe('Zahlen als Zahlen', text(s), ['Stufe 1', 'Stufe 2', 'Stufe 10']);
s = new Sel(['2048 px', '512 px', '1024 px'].map(t => new Opt(t)));
C.sortieren(s);
pruefe('Auflösungen aufsteigend', text(s), ['512 px', '1024 px', '2048 px']);
s = new Sel(['Aufzeichnung 05.10.2026', 'Aufzeichnung 20.09.2026', 'Aufzeichnung 14.09.2026 10:00'].map(t => new Opt(t)));
C.sortieren(s);
pruefe('Datum nach Jahr, Monat, Tag', text(s), ['Aufzeichnung 14.09.2026 10:00', 'Aufzeichnung 20.09.2026', 'Aufzeichnung 05.10.2026']);

// 2. führende neutrale Einträge bleiben vorn
s = new Sel([new Opt('—', ''), new Opt('Zebra'), new Opt('Alpha')]);
C.sortieren(s);
pruefe('leerer Wert vorn', text(s), ['—', 'Alpha', 'Zebra']);
s = new Sel([new Opt('Original Augen vom Modell', 'orig'), new Opt('Zeta', 'z'), new Opt('Beta', 'b')]);
C.sortieren(s);
pruefe('Original vorn', text(s), ['Original Augen vom Modell', 'Beta', 'Zeta']);
s = new Sel([new Opt('Vorgabe (Brown)', ''), new Opt('Keine', 'k'), new Opt('Blond', 'b')]);
C.sortieren(s);
pruefe('mehrere neutrale vorn, Reihenfolge bleibt', text(s), ['Vorgabe (Brown)', 'Keine', 'Blond']);
s = new Sel([new Opt('Alpha'), new Opt('Keine'), new Opt('Beta')]);
C.sortieren(s);
pruefe('Keine mitten in der Liste ist ein Name', text(s), ['Alpha', 'Beta', 'Keine']);

// 3. die Auswahl bleibt
const gewaehlt = new Opt('b', 'b', true);
s = new Sel([gewaehlt, new Opt('c'), new Opt('a')]);
C.sortieren(s);
pruefe('Reihenfolge', text(s), ['a', 'b', 'c']);
pruefe('Auswahl bleibt', gewaehlt.selected, true);

// 4. feste Reihenfolge
s = new Sel(['Niedrig', 'Mittel', 'Hoch'].map(t => new Opt(t)), true);
pruefe('fest: Rückgabe', C.sortieren(s), false);
pruefe('fest: Reihenfolge bleibt', text(s), ['Niedrig', 'Mittel', 'Hoch']);

// 5. Gruppen
s = new Sel([new Gruppe('Z-Gruppe', [new Opt('y'), new Opt('x')]), new Opt('ohne Gruppe'), new Gruppe('A-Gruppe', [new Opt('m'), new Opt('k')])]);
C.sortieren(s);
pruefe('Einträge ohne Gruppe davor, Gruppen sortiert', s.children.map(k => k.tagName === 'OPTGROUP' ? k.label : k.textContent), ['ohne Gruppe', 'A-Gruppe', 'Z-Gruppe']);
pruefe('Einträge je Gruppe sortiert', s.children.filter(k => k.tagName === 'OPTGROUP').map(g => g.children.map(o => o.textContent)), [['k', 'm'], ['x', 'y']]);

// 6. schon sortiert: nicht anfassen
s = new Sel(['a', 'b', 'c'].map(t => new Opt(t)));
pruefe('sortiert: Rückgabe', C.sortieren(s), false);
pruefe('sortiert: nichts angefasst', s.aenderungen, 0);
s = new Sel(['b', 'a'].map(t => new Opt(t)));
pruefe('unsortiert: Rückgabe', C.sortieren(s), true);
console.log(JSON.stringify({ ok: true }));
"""


class CombosortierungTest(SimpleTestCase):
    databases = set()

    def test_alle_auswahllisten_stehen_alphabetisch_stufenfolgen_bleiben(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
