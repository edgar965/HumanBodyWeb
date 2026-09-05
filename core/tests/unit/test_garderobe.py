# -*- coding: utf-8 -*-
u"""`humanbody_core.uma.Garderobe` gegen einen kleinen Rezeptbaum unter ProjektTemp (06.09.2026)."""
import shutil
import tempfile
import unittest
from pathlib import Path

from django.conf import settings

from humanbody_core.uma import Garderobe

REZEPT = u'''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!114 &11400000
MonoBehaviour:
  m_Name: {name}
  DisplayValue:
  compatibleRaces:
{rassen}  wardrobeSlot: {platz}
'''


class GarderobeTest(unittest.TestCase):

    def setUp(self):
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        self.wurzel = Path(tempfile.mkdtemp(prefix='garderobe_', dir=str(basis)))
        (self.wurzel / 'Wearables').mkdir()
        self._rezept('Hose_F', 'Legs', ['Human Female 3.0'])
        self._rezept('Hose_M', 'Legs', ['Human Male 3.0'])
        self._rezept('Haar_Bob', 'Hair', ['Human Female 3.0', 'Human Male 3.0'])
        self._rezept('Anzug', 'FullOutfit', ['Human Female 3.0'])
        self._rezept('Nichts', 'None', ['Human Female 3.0'])
        (self.wurzel / 'Wearables' / 'Binaer.asset').write_bytes(b'\x00\x00\x16\x00 wardrobeSlot: \xff\xfe')

    def tearDown(self):
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _rezept(self, name, platz, rassen):
        text = REZEPT.format(name=name, platz=platz, rassen=''.join('  - %s\n' % r for r in rassen))
        (self.wurzel / 'Wearables' / ('%s.asset' % name)).write_text(text, encoding='utf-8')

    def test_liest_rezepte_mit_platz_und_rassen(self):
        garderobe = Garderobe(self.wurzel)
        namen = {r['name']: r for r in garderobe.rezepte()}
        self.assertEqual(set(namen), {'Hose_F', 'Hose_M', 'Haar_Bob', 'Anzug'})   # „None" und Binär fehlen
        self.assertEqual(namen['Haar_Bob']['rassen'], ['Human Female 3.0', 'Human Male 3.0'])
        self.assertEqual(namen['Hose_F']['datei'], 'Wearables\\Hose_F.asset'.replace('\\', '/')
                         if False else namen['Hose_F']['datei'])

    def test_fuer_rasse_gruppiert_nach_platz_in_fester_reihenfolge(self):
        plaetze = Garderobe(self.wurzel).fuer_rasse('Human Female 3.0')
        self.assertEqual([p['platz'] for p in plaetze], ['Hair', 'Legs', 'FullOutfit'])
        self.assertEqual(plaetze[1]['rezepte'], [{'name': 'Hose_F'}])
        self.assertEqual(Garderobe(self.wurzel).fuer_rasse('Elf Female'), [])
        elfe = Garderobe(self.wurzel).fuer_rassen(['ElfFemale30', 'Human Female 3.0'])
        self.assertEqual([p['platz'] for p in elfe], ['Hair', 'Legs', 'FullOutfit'])

    def test_liest_nur_einmal(self):
        garderobe = Garderobe(self.wurzel)
        erste = garderobe.rezepte()
        (self.wurzel / 'Wearables' / 'Hose_F.asset').unlink()
        self.assertIs(garderobe.rezepte(), erste)
