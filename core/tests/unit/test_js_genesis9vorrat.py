# -*- coding: utf-8 -*-
u"""`Genesis9vorrat` — welche Netzanfragen der Server dauerhaft ablegt (19.10.2026, Kopf `X-G9-Vorrat`, `core/dienste/g9modellvorrat.py`).

1. Während eines Ladevorgangs (`laden`) trägt jede Anfrage den Kopf und gilt als Anzeige; danach nur Anfragen mit derselben Stellung (Adresse ohne Stufe
   + Rumpf): ein Stufenwechsel ja, ein Reglerzug nein.
2. Einstellung „aus": kein Kopf, nichts gemerkt.
3. `festhalten` (nach „Modell speichern"): die letzten Anfragen je Teil werden die Anzeige; ausgezogene Stücke fallen weg; der Körper nimmt den Rumpf von jetzt
   (`koerperNutzlast`).
4. `laden` zählt verschachtelt und gibt auch nach einem Fehler frei.

Sabotage (nicht gelaufen): in `kopf` die Stellung ohne `?stufen` vergleichen weglassen (ganze Adresse) → Fall 1 rot (der Stufenwechsel trüge keinen Kopf);
`finally` in `laden` streichen → Fall 4 rot. Geschrieben, nicht gelaufen.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9vorrat.js')

SKRIPT = """
globalThis.window = globalThis.window || { addEventListener() {}, removeEventListener() {} };
globalThis.document = globalThis.document || { addEventListener() {}, removeEventListener() {}, dispatchEvent() { return true; }, cookie: '' };
const { Genesis9vorrat: V } = await import(MODUL);
const inst = { id: 'f', kleidung: { hemd: {} } };
const K = { 'X-G9-Vorrat': '1' };

// 1. Laden markiert, danach nur dieselbe Stellung
const r1 = await V.laden(inst, async () => [V.kopf(inst, 'koerper', '/n/basis/netz/?stufen=0', { regler: {} }), V.kopf(inst, 'kleid:hemd', '/g/hemd/netz/?stufen=0', { a: 1 })]);
pruefe('laden: beide markiert', r1, [K, K]);
pruefe('Stufenwechsel: markiert', V.kopf(inst, 'koerper', '/n/basis/netz/', { regler: {} }), K);
pruefe('Reglerzug: nicht markiert', V.kopf(inst, 'koerper', '/n/basis/netz/', { regler: { x: 1 } }), {});
pruefe('zurück auf die Stellung: markiert', V.kopf(inst, 'koerper', '/n/basis/netz/?stufen=3', { regler: {} }), K);

// 2. aus
V.einstellen('aus');
pruefe('aus: kein Kopf', V.kopf(inst, 'koerper', '/n/basis/netz/', { regler: {} }), {});
V.einstellen(undefined);
pruefe('unbekannt: Vorgabe ultrafein', V.wahl, 'ultrafein');

// 3. festhalten
V.kopf(inst, 'koerper', '/n/basis/netz/', { regler: { x: 1 } });
V.kopf(inst, 'kleid:alt', '/g/alt/netz/', { b: 1 });
V.koerperNutzlast = () => ({ regler: { x: 2 } });
V.festhalten(inst);
pruefe('festhalten: Teile', [...inst._vorratAnzeige.keys()].sort(), ['kleid:hemd', 'koerper']);
pruefe('festhalten: Körper mit dem Rumpf von jetzt', V.kopf(inst, 'koerper', '/n/basis/netz/?stufen=0', { regler: { x: 2 } }), K);

// 4. laden zählt und gibt nach einem Fehler frei
await V.laden(inst, async () => { await V.laden(inst, async () => {}); pruefe('verschachtelt', inst._vorratLaedt, 1); });
try { await V.laden(inst, async () => { throw new Error('x'); }); } catch (e) { /* gewollt */ }
pruefe('nach Fehler frei', inst._vorratLaedt, 0);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9vorratTest(SimpleTestCase):
    databases = set()

    def test_anzeigen_tragen_den_kopf(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
