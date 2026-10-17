# -*- coding: utf-8 -*-
"""`Mhmorphplan`: welche MakeHuman-Regler zu Genesis-Morphs werden (17.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM: Aus MakeHumans Katalog (269 Regler plus 22 Koerperformen) wird die Auftragsliste fuer `Mhmorpheaufgenesis`. Ein Regler, der hier fehlt oder zwei Kennungen bekommt (die
Datei `<kennung>.npz` wuerde ueberschrieben), faellt nirgends auf. Geprueft gegen die echten MakeHuman-Daten (uebersprungen, wenn sie fehlen):

1. Alle Kennungen sind eindeutig und dateisicher (`G9mhmorphe.kennung` aendert sie nicht).
2. Zwoelf Makros von Hand, kein Geschlecht (Genesis hat BaseFeminine/BaseMasculine); Alter in DREI Morphs (Baby, Kind, Alt).
3. Jeder Detailregler des Katalogs (ohne Makros) kommt vor; zweiseitige Regler laufen −1…1 mit `minus`, einseitige 0…1 ohne.
4. Die Koerperformen sind einseitige `ziel`-Auftraege.
5. Jeder Auftrag liegt in einem Bereich der Familie, Reihenfolge `reihe` lueckenlos aufsteigend.
"""
import unittest

from django.test import SimpleTestCase
from Genesis9.mhmorphe import G9mhmorphe

from core.dienste.mhmorphplan import Mhmorphplan

try:
    from MakeHuman.modifikatoren import Mhmodifikatoren
    DA = Mhmodifikatoren.vorhanden()
except ImportError:
    DA = False


@unittest.skipUnless(DA, 'MakeHuman-Daten nicht da')
class MhmorphplanTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = Mhmorphplan.auftraege()

    def test_1_kennungen_eindeutig_und_dateisicher(self):
        kennungen = [a['kennung'] for a in self.plan]
        self.assertEqual(len(kennungen), len(set(kennungen)))
        for k in kennungen:
            self.assertEqual(G9mhmorphe.kennung(k), k)

    def test_2_zwoelf_makros_ohne_geschlecht_und_alter_in_drei_morphs(self):
        makros = [a for a in self.plan if a['bereich'] == 'mh_makro']
        self.assertEqual(len(makros), 12)
        kennungen = {a['kennung'] for a in makros}
        self.assertTrue({'macro_Alter_Baby', 'macro_Alter_Kind', 'macro_Alter_Alt'} <= kennungen)
        self.assertFalse([k for k in kennungen if 'eschlecht' in k or 'ender' in k])
        kind = [a for a in makros if a['kennung'] == 'macro_Alter_Kind'][0]
        self.assertEqual(kind['plus'], {'makro': {'age': 0.1875}})
        self.assertIsNone(kind['minus'])
        self.assertEqual(kind['min'], 0.0)

    def test_3_jeder_detailregler_kommt_vor_mit_den_richtigen_seiten(self):
        katalog = Mhmodifikatoren.holen().regler
        details = {k.replace('/', '_').replace('|', '_'): r for k, r in katalog.items() if not r.makro}
        vorhanden = {a['kennung']: a for a in self.plan}
        self.assertEqual([k for k in details if k not in vorhanden], [])
        for kennung, regler in details.items():
            auftrag = vorhanden[kennung]
            self.assertEqual(bool(auftrag['minus']), bool(regler.links), kennung)
            self.assertEqual(auftrag['min'], -1.0 if regler.links else 0.0, kennung)

    def test_4_koerperformen_sind_einseitige_zielauftraege(self):
        formen = [a for a in self.plan if a['bereich'] == 'mh_formen']
        self.assertEqual(len(formen), 22)
        for a in formen:
            self.assertIn('ziel', a['plus'])
            self.assertIsNone(a['minus'])

    def test_5_bereiche_der_familie_und_reihenfolge_lueckenlos(self):
        for a in self.plan:
            self.assertIn(a['bereich'], G9mhmorphe.BEREICHE)
        self.assertEqual([a['reihe'] for a in self.plan], list(range(len(self.plan))))
