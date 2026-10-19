# -*- coding: utf-8 -*-
"""`Stueckloch` — das Loch, das ein verschweißtes Ersatzstück (Scham aus einer .blend) in die Haut schneidet, in Node mit dem echten Modul.

Edgar, 09.10.2026, mit Bild: „bei der Scham gibt es immer noch die Probleme an den Rändern. Schau nach, wie Genesis das mit der Nase und
dem Mund macht, und mach es genau so." Bei Genesis ist ein Rand eine Kante: Daz' Geograft verschweißt seine Randpunkte mit einem Loch im
Körper. Der Bau legt das Loch fest (`Blendimportschamloch`), das Stück bringt die Dreiecknummern der Haut mit (`userData.hautLoch`).

1. `von`: das Loch gilt nur für eine Haut mit derselben Zahl Dreiecke (`von`); eine andere Stufe, ein Stück ohne Loch und ein leeres Loch
   geben null (die Haut rechnet dann wie vorher, `hautverdeckung.js`).
2. `maske`: die Vereinigung der Löcher aller passenden Stücke als eine Dreiecksmaske; ein Stück mit fremder Zahl zählt nicht; ohne
   passendes Stück null. Die Ringe und die Verschiebung der Ringpunkte gehen mit.
3. `verschieben`: addiert die Verschiebung auf das `einzug`-Feld (nie ersetzt — ein Saumband unter anderem Stoff behält seinen Einzug);
   ein Punkt außerhalb des Feldes wird übersprungen, ohne Verschiebung 0.
4. `vereinen`: null zählt als leer; die erste Maske bleibt unverändert.
5. entfallen (19.10.2026): `nurWeg`/`verschweisst` (MakeHuman-Stücke) wurden am 18.10.2026 abends zurückgenommen (`genesis9-garderobe.md`,
   „WIEDER AUS") — der Fall stand seitdem rot gegen Methoden, die es nicht mehr gibt.
7. `zwischen` (19.10.2026, ultrafein mit einem Stück ohne Unterteilung, `G9stuecklochultrafein._ring`): der Kantenpunkt der Haut rückt auf die
   Mitte seiner zwei Ecken, wie diese samt Verschiebung liegen (`kantenmitten`); ohne Punkte der Haut keine Kantenmitten. Sabotage: in
   `kantenmitten` die Verschiebung der Ecken weglassen (`lage` nur `haut[…]`) macht Fall 7 rot. Geschrieben, nicht gelaufen.

6. `weitere` (19.10.2026, grobe Stufe, `Genesis9/stuecklochstufen.py`): die Fassung, deren `von` zur Haut passt, liefert Dreiecke, Ring
   (mit `punkte2`/`t`) und Verschiebung; die feine Haut nimmt weiter das eigene Loch. Sabotage: in `fassung` nur `[loch]` statt
   `[loch, ...weitere]` macht Fall 6 rot. Geschrieben, nicht gelaufen.

Sabotage-Gegenprobe (nicht gelaufen — Tests laufen nur auf Ansage): in `von` `loch.von !== anzahl` zu `false` macht Fall 1 rot;
in `maske` `weg[nummern[i]] = 1` zu `= nummern[i] % 2` macht Fall 2 rot; in `verschieben` `+=` zu `=` macht Fall 3 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stueckloch.js')

SKRIPT = """
const { Stueckloch } = await import(MODUL);
const netz = (von, dreiecke, extra = {}) => ({ name: 'scham', userData: { hautLoch: { von, dreiecke, ...extra } } });
const rund = (x) => Math.round(x * 1e6) / 1e6;

// --- 1. von -------------------------------------------------------------------------------------------
pruefe('passt', Array.from(Stueckloch.von(netz(10, [1, 3]), 10)), [1, 3]);
pruefe('andere Haut', Stueckloch.von(netz(10, [1, 3]), 12), null);
pruefe('ohne Loch', Stueckloch.von({ userData: {} }, 10), null);
pruefe('leeres Loch', Stueckloch.von(netz(10, []), 10), null);
pruefe('kein Netz', Stueckloch.von(null, 10), null);

// --- 2. maske -----------------------------------------------------------------------------------------
const ring = { lage: [[0, 0, 0], [1, 0, 0], [0, 1, 0]], punkte: [1, 2, 3], d: [[0, 0, 0], [0, 0, 0], [0, 0, 0]] };
const mit = netz(10, [1, 3], { ring, verschiebung: { punkte: [2, 5], d: [[0.001, 0, 0], [0, 0.002, 0]] } });
const m = Stueckloch.maske([['a', mit], ['b', netz(10, [3, 4])], ['c', netz(99, [0])]], 10);
pruefe('Vereinigung', Array.from(m.weg), [0, 1, 0, 1, 1, 0, 0, 0, 0, 0]);
pruefe('nur passende Stücke', m.schluessel, ['a', 'b']);
pruefe('ein Ring', m.ringe.length, 1);
pruefe('Ring: Punkte', Array.from(m.ringe[0].ring.punkte), [1, 2, 3]);
pruefe('Ring: Lage flach', Array.from(m.ringe[0].ring.lage), [0, 0, 0, 1, 0, 0, 0, 1, 0]);
pruefe('Verschiebung: Punkte', Array.from(m.verschiebung.punkte), [2, 5]);
pruefe('keines passt', Stueckloch.maske([['c', netz(99, [0])]], 10), null);
pruefe('ohne Stücke', Stueckloch.maske([], 10), null);
pruefe('ohne Verschiebung', Stueckloch.maske([['b', netz(10, [3, 4])]], 10).verschiebung, null);

// --- 3. verschieben -----------------------------------------------------------------------------------
const w = new Float32Array(3 * 8);
w[3 * 5 + 1] = 0.5;                                                 // schon ein Einzug da
pruefe('zwei Punkte verschoben', Stueckloch.verschieben(w, m.verschiebung), 2);
pruefe('x von Punkt 2', rund(w[6]), 0.001);
pruefe('y von Punkt 5 addiert', rund(w[3 * 5 + 1]), 0.502);
Stueckloch.verschieben(w, m.verschiebung);
pruefe('zweimal addiert', rund(w[6]), 0.002);
pruefe('ohne Verschiebung', Stueckloch.verschieben(w, null), 0);
pruefe('Punkt außerhalb', Stueckloch.verschieben(new Float32Array(6), m.verschiebung), 0);

// --- 4. vereinen --------------------------------------------------------------------------------------
const a = Uint8Array.from([1, 0, 0]), b = Uint8Array.from([0, 0, 1]);
pruefe('beide', Array.from(Stueckloch.vereinen(a, b)), [1, 0, 1]);
pruefe('a unverändert', Array.from(a), [1, 0, 0]);
pruefe('nur a', Stueckloch.vereinen(a, null) === a, true);
pruefe('nur b', Stueckloch.vereinen(null, b) === b, true);
pruefe('keine', Stueckloch.vereinen(null, null), null);

// --- 5. (entfallen: `nurWeg`/`verschweisst` gibt es seit der Rücknahme am 18.10.2026 abends nicht mehr, `genesis9-garderobe.md`) ------

// --- 7. zwischen: ultrafein mit einem Stück, das nicht unterteilt wird (19.10.2026, `Stueckloch.kantenmitten`) ---------------------
// Haut: Punkt 0 und 2 sind Ecken, Punkt 1 der Kantenpunkt dazwischen (2 mm über der Geraden); Ecke 2 hat eine Verschiebung von 1 mm in x.
const haut = Float32Array.from([0, 0, 0,  0.01, 0.002, 0,  0.02, 0, 0]);
const ultra = netz(10, [0], { weitere: [{ von: 6, dreiecke: [5], ring: { lage: [[0, 0, 0], [0.02, 0, 0]], punkte: [0, 2], d: [[0, 0, 0], [0.001, 0, 0]], zwischen: [[1, 0, 2]] },
                                         verschiebung: { punkte: [2], d: [[0.001, 0, 0]] } }] });
const mu = Stueckloch.maske([['a', ultra]], 6, haut);
pruefe('zwischen: Kantenpunkt verschoben', Array.from(mu.verschiebung.punkte), [2, 1]);
pruefe('zwischen: auf die Mitte der verschobenen Ecken', Array.from(mu.verschiebung.d.slice(3)).map(rund), [0.0005, -0.002, 0]);
pruefe('zwischen: ohne Haut keine Kantenmitten', Array.from(Stueckloch.maske([['a', ultra]], 6).verschiebung.punkte), [2]);

// --- 6. weitere: dasselbe Loch für die grobe Stufe (19.10.2026, `G9stuecklochstufen`) ------------------------------------
const grobRing = { lage: ring.lage, punkte: [4, 5, 6], punkte2: [5, 5, 7], t: [0.5, 0, 0.5], d: [[0, 0, 0], [0, 0, 0], [0, 0, 0]] };
const zwei = netz(10, [1, 3], { ring, verschiebung: { punkte: [2], d: [[0.001, 0, 0]] }, weitere: [{ von: 4, dreiecke: [0, 2], ring: grobRing }] });
pruefe('grob: Fassung passt', Array.from(Stueckloch.von(zwei, 4)), [0, 2]);
pruefe('fein: weiter das eigene Loch', Array.from(Stueckloch.von(zwei, 10)), [1, 3]);
pruefe('keine Fassung passt', Stueckloch.von(zwei, 7), null);
const mg = Stueckloch.maske([['a', zwei]], 4);
pruefe('grob: Maske', Array.from(mg.weg), [1, 0, 1, 0]);
pruefe('grob: Ring der Fassung', Array.from(mg.ringe[0].ring.punkte), [4, 5, 6]);
pruefe('grob: zweiter Punkt', Array.from(mg.ringe[0].ring.punkte2), [5, 5, 7]);
pruefe('grob: Anteil', Array.from(mg.ringe[0].ring.t), [0.5, 0, 0.5]);
pruefe('grob: keine Verschiebung der feinen Haut', mg.verschiebung, null);
pruefe('fein: Ring ohne punkte2', Stueckloch.maske([['a', zwei]], 10).ringe[0].ring.punkte2, undefined);
console.log(JSON.stringify({ ok: true }));
"""


class StuecklochTest(SimpleTestCase):
    databases = set()

    def test_das_loch_gilt_nur_fuer_die_passende_haut_und_vereint_die_stuecke(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
