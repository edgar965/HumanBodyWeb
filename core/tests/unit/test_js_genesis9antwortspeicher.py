# -*- coding: utf-8 -*-
"""`Genesis9antwortspeicher`: jede Figur hält ihre Netzantworten JE STUFE im RAM (12.10.2026), geprüft in Node.

Edgar: „jede Figur soll auch ihre zweite Fassung (fein) und ultrafein im RAM halten." Bis dahin holte jeder Stufenwechsel (Strg+Alt+H) Körper und Stücke noch einmal vom Server.
Gemessen im Chrome (cute girl Daz, fünf Stücke): nach dem Laden liegen Körper und Stücke in `grob` UND `fein` im Speicher (rund 24 MB); `grob` und `fein` kommen danach in 81 bzw. 62 ms
ohne jede Anfrage (vom Server, dort schon im Speicher: 247 ms); ein Reglerzug ersetzt die Einträge, der Speicher wächst nicht. `Serverabruf.netzSenden` ist eine Attrappe.

1. `stufe`: eine ausdrückliche Stufe der Adresse (`?stufen=0`) gilt vor der gewählten (`fein`, `ultrafein`); `ohneStufen` schneidet sie ab.
2. `kopie`: Objekte und Listen sind unabhängig, die Zahlenfelder bleiben dieselben (niemand schreibt in sie).
3. `ablegen`/`suchen`: mehrere Stufen eines Teils liegen nebeneinander, die abgelegte Antwort ist eine Kopie (spätere Änderungen am Original ändern sie nicht), eine andere Stellung
   ersetzt den ganzen Eintrag samt seinen Stufen, ein Stück, das nicht mehr getragen wird, geht beim nächsten Ablegen mit weg.
4. `kleid`: ohne Eintrag eine Anfrage (`neu`), nach `ablegen` keine und eine eigene Kopie; eine andere Stufe (Wahl oder Adresse) oder ein anderer Rumpf fragt neu, die zuerst abgelegte Stufe
   bleibt daneben liegen.
5. `groessen`: jeder Antwortpuffer einmal gezählt, auch wenn mehrere Felder auf ihm liegen.
6. `einstellen` (Einstellungen → Charakter → „Netzantworten", 12.10.2026): nur `server` schaltet das Halten ab — dann findet `suchen` nichts, `ablegen` legt nichts ab und gibt Altbestand frei, `kleid`
   fragt jedes Mal den Server; alles andere (auch keine Angabe) heißt RAM.
7. Verdrahtung am Quelltext: `Genesis9kleidung.anziehen` holt über den Speicher und legt VOR dem Bau der Netze ab (der Bau verändert die Objekte der Antwort); die Szene reicht
   `ui_prefs.netzantworten` beim Laden an `einstellen` (`Starteinstellungen`).

Sabotage-Gegenprobe (nicht gefahren): in `ablegen` `kopie(daten)` durch `daten` ersetzen → Fall 3 rot; die Prüfung `eintrag.stellung !== stellung` streichen → Fall 3 rot; in `stufe` die Adresse
nicht lesen → Fall 1/4 rot; die Aufräumschleife in `ablegen` streichen → Fall 3 rot; in `suchen` die Zeile `if (!…halten) return null;` streichen → Fall 6 rot; `wahl !== 'server'` durch
`wahl === 'ram'` ersetzen → Fall 6 rot (keine Angabe hielte nichts).
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9antwortspeicher.js')
GEMEINSAM = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'gemeinsam'

SKRIPT = """
const { Genesis9antwortspeicher: S } = await import(MODUL);
const { Serverabruf } = await import(new URL('./serverabruf.js', MODUL).href);
const { Netzstufenstand } = await import(new URL('./netzstufenstand.js', MODUL).href);
const antwort = (name = 'a') => ({ name, punkte: new Float32Array([1, 2, 3]), skelett: { knochen: [{ n: 'hip', pos: [0, 1, 0] }] }, gruppen: [{ name: 'Torso', index_ab: 0 }] });

// 1. Stufe
Netzstufenstand.wahl = 'fein';
pruefe('gewählt: fein', S.stufe('/x/netz/'), 'fein');
pruefe('ausdrücklich: Käfig', S.stufe('/x/netz/?stufen=0'), 'S0');
Netzstufenstand.wahl = 'ultrafein';
pruefe('gewählt: ultrafein', S.stufe('/x/netz/'), 'ultrafein');
pruefe('ausdrücklich gilt vor der Wahl', S.stufe('/x/netz/?stufen=0'), 'S0');
Netzstufenstand.wahl = 'fein';
pruefe('ohneStufen', [S.ohneStufen('/x/netz/?stufen=0'), S.ohneStufen('/x/netz/')], ['/x/netz/', '/x/netz/']);

// 2. kopie
const a = antwort(), b = S.kopie(a);
b.skelett.knochen[0].pos.push(9); b.skelett.knochen.push({ n: 'neu' }); b.gruppen[0].name = 'Arms';
pruefe('Objekte unabhängig', [a.skelett.knochen.length, a.skelett.knochen[0].pos.length, a.gruppen[0].name], [1, 3, 'Torso']);
pruefe('Zahlenfelder geteilt', b.punkte === a.punkte, true);
pruefe('Einfaches bleibt', [S.kopie(null), S.kopie(3), S.kopie('x')], [null, 3, 'x']);

// 3. ablegen / suchen
const inst = { kleidung: { hemd: {}, hose: {} } };
const orig = antwort('fein');
S.ablegen(inst, 'koerper', 'st1', 'fein', orig, 'm1');
S.ablegen(inst, 'koerper', 'st1', 'S0', antwort('grob'), 'm1');
S.ablegen(inst, 'koerper', 'st1', 'ultrafein', antwort('ultra'), 'm2');
pruefe('drei Stufen nebeneinander', ['fein', 'S0', 'ultrafein'].map(st => S.suchen(inst, 'koerper', 'st1', st).daten.name), ['fein', 'grob', 'ultra']);
pruefe('Material gemerkt', S.suchen(inst, 'koerper', 'st1', 'ultrafein').material, 'm2');
orig.skelett.knochen.push({ n: 'spaeter' }); orig.gruppen[0].name = 'verändert';
pruefe('abgelegt ist eine Kopie', [S.suchen(inst, 'koerper', 'st1', 'fein').daten.skelett.knochen.length, S.suchen(inst, 'koerper', 'st1', 'fein').daten.gruppen[0].name], [1, 'Torso']);
pruefe('andere Stufe: nichts', S.suchen(inst, 'koerper', 'st1', 'S5'), null);
pruefe('andere Stellung: nichts', S.suchen(inst, 'koerper', 'st2', 'fein'), null);
pruefe('anderes Teil: nichts', S.suchen(inst, 'kleid:hemd', 'st1', 'fein'), null);
pruefe('ohne Speicher: nichts', S.suchen({}, 'koerper', 'st1', 'fein'), null);
S.ablegen(inst, 'koerper', 'st2', 'fein', antwort('neu'), 'm1');
pruefe('neue Stellung ersetzt den Eintrag samt Stufen', [S.suchen(inst, 'koerper', 'st1', 'fein'), S.suchen(inst, 'koerper', 'st1', 'S0'), S.suchen(inst, 'koerper', 'st2', 'fein').daten.name], [null, null, 'neu']);
S.ablegen(inst, 'kleid:hemd', 's', 'fein', antwort('h'));
S.ablegen(inst, 'kleid:hose', 's', 'fein', antwort('o'));
delete inst.kleidung.hose;
S.ablegen(inst, 'kleid:hemd', 's', 'S0', antwort('h0'));
pruefe('ausgezogenes Stück weg, getragenes bleibt', [S.suchen(inst, 'kleid:hose', 's', 'fein'), S.suchen(inst, 'kleid:hemd', 's', 'fein').daten.name, S.suchen(inst, 'kleid:hemd', 's', 'S0').daten.name], [null, 'h', 'h0']);

// 4. kleid
const anfragen = [];
Serverabruf.netzSenden = async (adresse, rumpf) => { anfragen.push(adresse); return antwort('server'); };
const fig = { kleidung: { hemd: {} } };
const ADR = '/api/character/genesis9-figur/garderobe/hemd/netz/';
let r = await S.kleid(fig, 'hemd', ADR, { regler: { a: 1 } });
pruefe('leer: eine Anfrage', [anfragen, r.neu, r.teil, r.stufe, r.daten.name], [[ADR], true, 'kleid:hemd', 'fein', 'server']);
S.ablegen(fig, r.teil, r.stellung, r.stufe, r.daten);
anfragen.length = 0;
r = await S.kleid(fig, 'hemd', ADR, { regler: { a: 1 } });
pruefe('abgelegt: keine Anfrage', [anfragen, r.neu, r.daten.name], [[], false, 'server']);
r.daten.skelett.knochen.push({ n: 'x' });
pruefe('Treffer ist eine Kopie', (await S.kleid(fig, 'hemd', ADR, { regler: { a: 1 } })).daten.skelett.knochen.length, 1);
r = await S.kleid(fig, 'hemd', ADR, { regler: { a: 2 } });
pruefe('anderer Rumpf: Anfrage', [anfragen, r.neu], [[ADR], true]);
anfragen.length = 0;
r = await S.kleid(fig, 'hemd', ADR + '?stufen=0', { regler: { a: 1 } });
pruefe('andere Stufe (Adresse): Anfrage mit ihrer Adresse', [anfragen, r.stufe, r.neu], [[ADR + '?stufen=0'], 'S0', true]);
S.ablegen(fig, r.teil, r.stellung, r.stufe, r.daten);
anfragen.length = 0;
Netzstufenstand.wahl = 'ultrafein';
r = await S.kleid(fig, 'hemd', ADR, { regler: { a: 1 } });
pruefe('andere Stufe (Wahl): Anfrage', [anfragen, r.stufe, r.neu], [[ADR], 'ultrafein', true]);
S.ablegen(fig, r.teil, r.stellung, r.stufe, r.daten);
anfragen.length = 0;
Netzstufenstand.wahl = 'fein';
const zurueck = await S.kleid(fig, 'hemd', ADR + '?stufen=0', { regler: { a: 1 } });
const fein = await S.kleid(fig, 'hemd', ADR, { regler: { a: 1 } });
pruefe('zurück auf eine gehaltene Stufe: keine Anfrage', [anfragen, zurueck.neu, fein.neu], [[], false, false]);

// 5. groessen
const puffer = new ArrayBuffer(64);
const gross = { vertices: new Float32Array(puffer, 0, 4), faces: new Uint32Array(puffer, 16, 4), inner: { uv: new Float32Array(puffer, 32, 2) }, liste: [new Uint8Array(new ArrayBuffer(10))] };
const g = { kleidung: {} };
S.ablegen(g, 'koerper', 's', 'fein', gross);
pruefe('jeder Puffer einmal', S.groessen(g), { koerper: { fein: 74 } });
pruefe('ohne Speicher', S.groessen({}), {});

// 6. einstellen: `server` hält nichts
S.einstellen('server');
pruefe('Halten aus', S.halten, false);
const h = { kleidung: {} };
S.ablegen(h, 'koerper', 's', 'fein', antwort('x'), 'm');
pruefe('aus: nichts abgelegt', [S.suchen(h, 'koerper', 's', 'fein'), h._antworten], [null, null]);
S.einstellen('ram');
S.ablegen(h, 'koerper', 's', 'fein', antwort('x'), 'm');
pruefe('RAM hält wieder', S.suchen(h, 'koerper', 's', 'fein').daten.name, 'x');
S.einstellen('server');
pruefe('aus: Gehaltenes wird nicht mehr gefunden', S.suchen(h, 'koerper', 's', 'fein'), null);
S.ablegen(h, 'koerper', 's', 'fein', antwort('y'), 'm');
pruefe('aus: das nächste Ablegen gibt den Altbestand frei', h._antworten, null);
anfragen.length = 0;
await S.kleid(fig, 'hemd', ADR, { regler: { a: 1 } });
const zweite = await S.kleid(fig, 'hemd', ADR, { regler: { a: 1 } });
pruefe('aus: jedes Mal eine Anfrage, obwohl die Figur Einträge hat', [anfragen.length, zweite.neu], [2, true]);
for (const wahl of [undefined, null, '', 'ram', 'unsinn']) { S.einstellen(wahl); pruefe(`Wahl ${wahl}: hält`, S.halten, true); }
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9antwortspeicherTest(SimpleTestCase):

    def test_jede_figur_haelt_ihre_antworten_je_stufe(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_die_kleidung_holt_ueber_den_speicher_und_legt_vor_dem_bau_ab(self):
        quelle = (GEMEINSAM / 'genesis9kleidung.js').read_text(encoding='utf-8')
        self.assertIn("import { Genesis9antwortspeicher } from './genesis9antwortspeicher.js';", quelle)
        rumpf = quelle.split('static async anziehen(', 1)[1].split('\n    }\n', 1)[0]
        self.assertIn('await Genesis9antwortspeicher.kleid(inst, kennung,', rumpf)
        self.assertNotIn('Serverabruf.netzSenden', rumpf, 'der Abruf des Stücks läuft über den Speicher')
        ablegen = 'Genesis9antwortspeicher.ablegen(inst, antwort.teil, antwort.stellung, antwort.stufe, daten)'
        self.assertIn(ablegen, rumpf)
        # Abgelegt wird erst, wenn gebaut wird (nach den Prüfungen auf Überholt/Ausgezogen) und VOR dem Bau der Netze.
        self.assertLess(rumpf.index('if (lauf !== inst._lauf || !inst.kleidung[kennung]) return 0;'), rumpf.index(ablegen))
        self.assertLess(rumpf.index('inst._stueckWeg(kennung);'), rumpf.index(ablegen))
        self.assertLess(rumpf.index(ablegen), rumpf.index('Genesis9netz.bauen('))

    def test_die_szene_reicht_die_einstellung_an_den_speicher(self):
        quelle = (GEMEINSAM.parent / 'charakter' / 'starteinstellungen.js').read_text(encoding='utf-8')
        self.assertIn("import { Genesis9antwortspeicher } from '../gemeinsam/genesis9antwortspeicher.js';", quelle)
        self.assertIn('Genesis9antwortspeicher.einstellen(eigene.netzantworten);', quelle)
