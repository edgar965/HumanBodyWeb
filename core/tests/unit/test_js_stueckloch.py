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
console.log(JSON.stringify({ ok: true }));
"""


class StuecklochTest(SimpleTestCase):
    databases = set()

    def test_das_loch_gilt_nur_fuer_die_passende_haut_und_vereint_die_stuecke(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
