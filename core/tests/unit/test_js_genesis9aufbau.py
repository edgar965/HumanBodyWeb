# -*- coding: utf-8 -*-
u"""`Genesis9aufbau` (18.09.2026 nachts): Körper und Stücke gleichzeitig,
Strg+Alt+H im Stand auch neben anderen Figurarten.

In Node mit einer Figur-Attrappe, deren `koerperAufbauen`/`anziehen` erst auf
ein Signal hin zurückkehren:

1. `alles` startet den Körper UND alle Stücke, bevor der Körper fertig ist
   (gleichzeitig, nicht nacheinander); `_lauf` zählt vor den Stücken hoch.
2. `umschalten` mit nur Genesis-Figuren: jede holt die Stufe des Browsers
   (`stufen` null), liefert true.
3. Gemischt (HumanBody + Genesis): true, NUR die Genesis-Figur wird umgebaut,
   die andere bleibt unangetastet.
4. Ohne Genesis-Figur: false (die Seite lädt neu wie bisher).

Sabotage-Gegenprobe: `alles` wieder nacheinander (`await` je Stück) → Fall 1 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9aufbau.js')

SKRIPT = """
const { Genesis9aufbau } = await import(MODUL);

const figur = (quelle, stuecke) => {
    const f = { quelle, _lauf: 0, kleidung: Object.fromEntries(stuecke.map(k => [k, {}])),
                gestartet: [], fertig: [], signale: [] };
    f.getragen = () => Object.keys(f.kleidung);
    const warten = (name) => new Promise(r => f.signale.push([name, r]));
    f.koerperAufbauen = async (stufen) => { f._lauf += 1; f.gestartet.push(['koerper', stufen, f._lauf]);
                                            await warten('koerper'); f.fertig.push('koerper'); return f; };
    f.anziehen = async (kennung, werte, stufen) => { f.gestartet.push([kennung, stufen, f._lauf]);
                                                     await warten(kennung); f.fertig.push(kennung); return 1; };
    f.frei = () => { f.signale.splice(0).forEach(([, r]) => r()); };
    return f;
};

// 1. gleichzeitig
const u = figur('genesis9', ['kleid', 'haar']);
const lauf = Genesis9aufbau.alles(u, 2);
await new Promise(r => setTimeout(r, 0));
pruefe('alle gestartet, bevor der koerper fertig ist',
       u.gestartet.map(g => g[0]), ['koerper', 'kleid', 'haar']);
pruefe('stufe durchgereicht', u.gestartet.map(g => g[1]), [2, 2, 2]);
pruefe('lauf vor den stuecken erhoeht', u.gestartet.map(g => g[2]), [1, 1, 1]);
pruefe('noch nichts fertig', u.fertig, []);
u.frei();
pruefe('alles liefert die figur', await lauf, u);
pruefe('alles fertig', u.fertig.sort(), ['haar', 'kleid', 'koerper']);

// 2. nur Genesis
const a = figur('genesis9', ['kleid']), b = figur('genesis9', []);
const um = Genesis9aufbau.umschalten([a, b]);
await new Promise(r => setTimeout(r, 0));
pruefe('beide gestartet', [a.gestartet.length, b.gestartet.length], [2, 1]);
pruefe('stufe des browsers', a.gestartet.map(g => g[1]), [null, null]);
a.frei(); b.frei();
pruefe('umgeschaltet', await um, true);
pruefe('fein gesetzt', [a.fein instanceof Promise, b.fein instanceof Promise], [true, true]);

// 3. gemischt
const h = figur('modell', []), g = figur('genesis9', ['haar']);
const gemischt = Genesis9aufbau.umschalten([h, g]);
await new Promise(r => setTimeout(r, 0));
g.frei();
pruefe('gemischt: kein neustart', await gemischt, true);
pruefe('genesis umgebaut', g.gestartet.map(x => x[0]), ['koerper', 'haar']);
pruefe('humanbody unangetastet', [h.gestartet.length, h.fein], [0, undefined]);

// 4. ohne Genesis
pruefe('ohne genesis: neustart', await Genesis9aufbau.umschalten([figur('modell', [])]), false);
pruefe('leer: neustart', await Genesis9aufbau.umschalten([]), false);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9aufbauTest(SimpleTestCase):

    def test_gleichzeitig_und_gemischt(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
