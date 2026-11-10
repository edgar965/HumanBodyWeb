"""`Modulraum`: zwei Pakete gleichen Namens im selben Prozess, wie PSHuman und Django im Skriptdienst. Kunstpakete, ohne Karte."""
import importlib
import shutil
import sys
import types
import unittest
import uuid
from pathlib import Path

from django.conf import settings

sys.path.insert(0, str(Path(settings.TOOLS_ROOT) / 'meshgenesis'))
from meshgenesis_modulraum import Modulraum  # noqa: E402


class ModulraumTest(unittest.TestCase):
    def setUp(self):
        self.name = 'kunst_' + uuid.uuid4().hex[:8]
        self.t = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / self.name
        self.addCleanup(shutil.rmtree, self.t, ignore_errors=True)
        self.aussen, self.wurzel = self.t / 'aussen', self.t / 'wurzel'
        self.fremd = self.wurzel / 'fremd'
        for p in (self.aussen / self.name, self.fremd / self.name):
            p.mkdir(parents=True)
        (self.aussen / self.name / '__init__.py').write_text('WER = "aussen"\n', encoding='utf-8')
        (self.fremd / self.name / '__init__.py').write_text('import sys\nWER = "raum"\nsys.modulraum_zaehler = getattr(sys, "modulraum_zaehler", 0) + 1\n', encoding='utf-8')
        (self.fremd / 'spaet_raum.py').write_text('WER = "spaet"\n', encoding='utf-8')
        sys.path.insert(0, str(self.aussen))
        self.addCleanup(lambda: (sys.path.remove(str(self.aussen)), sys.modules.pop(self.name, None)))
        sys.modulraum_zaehler = 0
        self.raum = Modulraum(self.wurzel, [self.fremd])
        importlib.import_module(self.name)

    def _auftrag(self, spaet=False):
        with self.raum:
            if str(self.fremd) not in sys.path:
                sys.path.insert(0, str(self.fremd))
            self.assertEqual(importlib.import_module(self.name).WER, 'raum')
            sys.modules.setdefault('attrappe_raum', types.ModuleType('attrappe_raum'))
            if spaet:
                self.assertEqual(importlib.import_module('spaet_raum').WER, 'spaet')

    def test_aussen_bleibt_nach_dem_auftrag(self):
        pfad = list(sys.path)
        self._auftrag()
        self.assertEqual(sys.modules[self.name].WER, 'aussen')
        self.assertNotIn('attrappe_raum', sys.modules)
        self.assertEqual(sys.path, pfad)

    def test_zweiter_auftrag_importiert_nicht_neu(self):
        self._auftrag()
        self._auftrag()
        self.assertEqual(sys.modulraum_zaehler, 1)

    def test_suchpfad_des_raums_bleibt_fuer_spaetere_importe(self):
        self._auftrag()
        self._auftrag(spaet=True)
        self.assertNotIn('spaet_raum', sys.modules)

    def test_paket_ohne_init_bleibt_im_raum(self):
        """PSHumans `core` hat keine `__init__.py`, also keine Datei; außen liegt Djangos `core`."""
        with self.raum:
            sys.modules[self.name] = types.ModuleType(self.name)        # wie ein Paket ohne Datei
        self.assertEqual(sys.modules[self.name].WER, 'aussen')
        self.assertIn(self.name, self.raum.drin)

    def _paket_ohne_init_gegen_aussen(self):
        """Wie PSHumans `core` (ohne `__init__.py`) gegen Djangos `core` (mit) im Suchpfad. → Name, Raum."""
        ns = self.name + '_ns'
        (self.aussen / ns).mkdir()
        (self.aussen / ns / '__init__.py').write_text('', encoding='utf-8')
        (self.fremd / ns).mkdir()
        (self.fremd / ns / 'teil.py').write_text('WER = "raum"\n', encoding='utf-8')
        importlib.invalidate_caches()
        self.addCleanup(sys.modules.pop, ns, None)
        return ns, Modulraum(self.wurzel, [self.fremd])

    def _teil_aus_dem_raum(self, ns, raum):
        with raum:
            sys.path.insert(0, str(self.fremd))
            self.assertEqual(importlib.import_module(ns + '.teil').WER, 'raum')
        self.assertNotIn(ns + '.teil', sys.modules)

    def test_paket_ohne_init_gewinnt_gegen_geladenes_paket_aussen(self):
        """Reihenfolge Mesh-Genesis, dann PSHuman im selben Dienst: „No module named 'core.opt'“ (`Zauberer_Performancen`, 07.11.2026)."""
        ns, raum = self._paket_ohne_init_gegen_aussen()
        importlib.import_module(ns)
        self._teil_aus_dem_raum(ns, raum)
        self.assertIn(str(self.aussen), sys.modules[ns].__file__)

    def test_paket_ohne_init_gewinnt_auch_gegen_ungeladenes_paket_im_suchpfad(self):
        ns, raum = self._paket_ohne_init_gegen_aussen()
        self._teil_aus_dem_raum(ns, raum)
        self.assertNotIn(ns, sys.modules)

    def test_pfad_mit_schraegstrich_gehoert_in_den_raum(self):
        raum, modul = self.raum, types.ModuleType('schraeg')
        modul.__file__ = str(self.fremd / 'x.py').replace('\\', '/')
        raum._vorher = set()
        self.assertTrue(raum._gehoert('schraeg', modul))

    def test_fehler_im_auftrag_stellt_die_aussenwelt_her(self):
        pfad = list(sys.path)
        with self.assertRaises(ValueError), self.raum:
            raise ValueError('Fehler im Auftrag')
        self.assertEqual(sys.modules[self.name].WER, 'aussen')
        self.assertEqual(sys.path, pfad)
