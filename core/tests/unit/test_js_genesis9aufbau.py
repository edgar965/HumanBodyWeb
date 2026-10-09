# -*- coding: utf-8 -*-
u"""`Genesis9aufbau` (18.09.2026 nachts; 09.10.2026 drei Stufen): Körper und Stücke gleichzeitig im Käfig, die gewählte
Stufe stückweise, Strg+Alt+H im Stand auch neben anderen Figurarten.

In Node mit einer Figur-Attrappe, deren `koerperAufbauen`/`anziehen` erst auf ein Signal hin zurückkehren:

1. `alles` startet den Körper UND alle Stücke, bevor der Körper fertig ist (gleichzeitig, nicht nacheinander); `_lauf`
   zählt vor den Stücken hoch.
2. `stufeSetzen(…, 'fein')` mit nur Genesis-Figuren: Stück für Stück (nacheinander, `Genesis9haeppchen`), der Körper ZULETZT
   (seine Haut-Maske rechnet danach einmal), jede in der Stufe des Browsers (`stufen` null), liefert true.
3. Gemischt (HumanBody + Genesis): true, NUR die Genesis-Figur wird umgebaut, die andere bleibt unangetastet.
4. Ohne Genesis-Figur: false (die Seite lädt neu wie bisher).
5. `grob`: alles im Käfig (`stufen` 0), der Export bleibt gesperrt (`_grobHalt`); ohne Angabe holt `adresse` bei gewähltem
   „grob" ebenfalls `?stufen=0`.
6. Ruhe: Mit `ruhe` ruft der Bau `vorBau`, bevor er baut; ohne nicht.

Sabotage-Gegenprobe: `alles` wieder nacheinander (`await` je Stück) → Fall 1 rot; `Genesis9haeppchen._lauf` startet alle Stücke
zugleich → Fall 2 rot; `adresse` ohne die Regel für „grob" → Fall 5 rot.

Gelaufen am 09.10.2026 (Gesamtlauf auf Ansage): grün.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9aufbau.js')

SKRIPT = """
const { Genesis9aufbau } = await import(MODUL);
const { Netzstufenstand } = await import(MODUL.replace('genesis9aufbau.js', 'netzstufenstand.js'));
const tick = () => new Promise(r => setTimeout(r, 0));

let zaehler = 0;
const figur = (quelle, stuecke) => {
    const f = { id: 'f' + (zaehler += 1), quelle, _lauf: 0, kleidung: Object.fromEntries(stuecke.map(k => [k, {}])),
                gestartet: [], fertig: [], signale: [], vorBau: [] };
    f.getragen = () => Object.keys(f.kleidung);
    const warten = (name) => new Promise(r => f.signale.push([name, r]));
    f.koerperAufbauen = async (stufen, frisch, vorBau) => { f._lauf += 1; f.gestartet.push(['koerper', stufen, f._lauf]);
                                                             f.vorBau.push(!!vorBau);
                                                             await warten('koerper'); f.fertig.push('koerper'); return f; };
    f.anziehen = async (kennung, werte, stufen, kaskade, vorBau) => { f.gestartet.push([kennung, stufen, f._lauf]);
                                                                      f.vorBau.push(!!vorBau);
                                                                      await warten(kennung); f.fertig.push(kennung); return 1; };
    f.frei = () => { f.signale.splice(0).forEach(([, r]) => r()); };
    return f;
};
const freigeben = async (...figuren) => { for (let i = 0; i < 8; i += 1) { figuren.forEach(f => f.frei()); await tick(); } };

// 1. gleichzeitig
const u = figur('genesis9', ['kleid', 'haar']);
const lauf = Genesis9aufbau.alles(u, 2);
await tick();
pruefe('alle gestartet, bevor der koerper fertig ist',
       u.gestartet.map(g => g[0]), ['koerper', 'kleid', 'haar']);
pruefe('stufe durchgereicht', u.gestartet.map(g => g[1]), [2, 2, 2]);
pruefe('lauf vor den stuecken erhoeht', u.gestartet.map(g => g[2]), [1, 1, 1]);
pruefe('noch nichts fertig', u.fertig, []);
u.frei();
pruefe('alles liefert die figur', await lauf, u);
pruefe('alles fertig', u.fertig.sort(), ['haar', 'kleid', 'koerper']);

// 2. nur Genesis: die gewaehlte Stufe stueckweise
Netzstufenstand.wahl = 'fein';
const a = figur('genesis9', ['kleid']), b = figur('genesis9', []);
const um = Genesis9aufbau.stufeSetzen([a, b], 'fein');
await tick();
pruefe('zuerst nur das stueck (der koerper ZULETZT)', [a.gestartet.map(g => g[0]), b.gestartet.map(g => g[0])], [['kleid'], ['koerper']]);
await freigeben(a, b);
pruefe('umgeschaltet', await um, true);
pruefe('koerper erst nach dem stueck', a.gestartet.map(g => g[0]), ['kleid', 'koerper']);
pruefe('stufe des browsers', a.gestartet.map(g => g[1]), [null, null]);
pruefe('fein gesetzt', [a.fein instanceof Promise, b.fein instanceof Promise], [true, true]);
pruefe('stand fein', Netzstufenstand.zusammen(), { stufe: 'fein', laedt: false, fertig: 0, gesamt: 0 });

// 3. gemischt
const h = figur('modell', []), g = figur('genesis9', ['haar']);
const gemischt = Genesis9aufbau.stufeSetzen([h, g], 'fein');
await freigeben(g);
pruefe('gemischt: kein neustart', await gemischt, true);
pruefe('genesis umgebaut', g.gestartet.map(x => x[0]), ['haar', 'koerper']);
pruefe('humanbody unangetastet', [h.gestartet.length, h.fein], [0, undefined]);

// 4. ohne Genesis
pruefe('ohne genesis: neustart', await Genesis9aufbau.stufeSetzen([figur('modell', [])], 'fein'), false);
pruefe('leer: neustart', await Genesis9aufbau.stufeSetzen([], 'fein'), false);

// 5. grob
const k = figur('genesis9', ['hemd']);
Netzstufenstand.wahl = 'grob';
const grob = Genesis9aufbau.stufeSetzen([k], 'grob');
await tick();
pruefe('grob: alles im kaefig', k.gestartet.map(x => [x[0], x[1]]), [['koerper', 0], ['hemd', 0]]);
k.frei();
pruefe('grob: erledigt', await grob, true);
pruefe('grob: export gesperrt', k._grobHalt, true);
pruefe('grob: adresse ohne angabe', Genesis9aufbau.adresse('/x/', null), '/x/?stufen=0');
Netzstufenstand.wahl = 'fein';
pruefe('fein: adresse ohne angabe', Genesis9aufbau.adresse('/x/', null), '/x/');
pruefe('explizit gilt', Genesis9aufbau.adresse('/x/', 2), '/x/?stufen=2');

// 6. ruhe
const { Genesis9haeppchen } = await import(MODUL.replace('genesis9aufbau.js', 'genesis9haeppchen.js'));
const r = figur('genesis9', ['rock']), s = figur('genesis9', ['rock']);
const mit = Genesis9haeppchen.zug(r, true), ohne = Genesis9haeppchen.zug(s, false);
await freigeben(r, s);
await mit; await ohne;
pruefe('mit ruhe: vorBau gesetzt', r.vorBau, [true, true]);
pruefe('ohne ruhe: kein vorBau', s.vorBau, [false, false]);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9aufbauTest(SimpleTestCase):

    def test_gleichzeitig_stueckweise_und_gemischt(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
