# -*- coding: utf-8 -*-
u"""`Genesis9felder.passform` / `passformAnfrage` (20.09.2026, „T-Shirt bei
Animation kaputt"): die Stückregler `passform:laenge`/`passform:weite` werden
zur Anfrage `&laenge=&weite=` — und zum Schlüssel, unter dem `Genesis9gelenke`
die Felder eines Stücks merkt; ohne Passform bleibt beides leer, damit ein
Stück ohne Regler dieselbe Adresse wie vor dem Umbau hat.

Sabotage-Gegenprobe: `passform` liefert auch bei 0/0 ein Objekt → Fall
„ohne" rot (die Anfrage bekäme `&laenge=0&weite=0`, ein zweiter Schlüssel für
denselben Stand).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9felder.js')

SKRIPT = """
const { Genesis9felder } = await import(MODUL);
pruefe('ohne Regler', Genesis9felder.passform(undefined), null);
pruefe('beide 0', Genesis9felder.passform({ 'passform:laenge': 0, 'passform:weite': '0' }), null);
pruefe('Unsinn ist 0', Genesis9felder.passform({ 'passform:laenge': 'x' }), null);
pruefe('Laenge', Genesis9felder.passform({ 'passform:laenge': -14.5 }), { laenge: -14.5, weite: 0 });
pruefe('beide, als Text', Genesis9felder.passform({ 'passform:laenge': '-14.5', 'passform:weite': '-2.7', 'Loosen': 1 }),
       { laenge: -14.5, weite: -2.7 });
pruefe('Anfrage ohne', Genesis9felder.passformAnfrage(null), '');
pruefe('Anfrage mit', Genesis9felder.passformAnfrage({ laenge: -14.5, weite: -2.7 }), '&laenge=-14.5&weite=-2.7');
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9felderPassformTest(SimpleTestCase):
    databases = set()

    def test_passform_aus_reglern_und_anfrage(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'ok': True})
