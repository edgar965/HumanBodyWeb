# -*- coding: utf-8 -*-
"""Skriptdienst von Mesh3D-AI und die Morphsumme auf der Karte (24.10.2026, Edgar: „mach“ auf „Neubau der Figur bleibt ein eigener Prozess“ und „G9formung hat noch keinen Weg auf der Karte“).

    1  `Modellwahl` liest `MESH3DAI_MODELL` bei jedem Zugriff, stellt `Mesh3dairig` um und leert dessen Zwischenspeicher nur bei einem Wechsel
    2  `Skriptdienst._haken` findet `_skriptdienst_zuruecksetzen` über das Modul-__dict__, ohne ein Modul-__getattr__ zu rufen
    3  `Skriptdienst._module_zuruecksetzen`: ohne Stand → Haken ohne Argument (frischer Prozess), mit Ständen → je Modul sein Stand
    3b Pfade, die frühere Aufträge hinzugefügt haben, stehen hinter der Basis (der Kopf-Schritt fand nach dem Figurbau im selben Dienst `MediapipeTorch` nicht)
    4  `G9rechenkarte.stand`/`zuruecksetzen`: zurück auf den Stand, ohne Stand aus
    5  `G9morphsummekarte` = die Schleife über `G9morphsumme.addieren`, bitweise (Kunstablage, gemischte Werte, Nummern außerhalb, ein Morph mit np.float64) — nur mit Karte, unter der Sperre
Die Bitgleichheit an echten Stellungen misst `ProjektTemp/_wegwerf/formung_gpu/summe_gegenprobe.py` (44 von 44), den Neubau im Dienst `ProjektTemp/_wegwerf/dienst/probe/neubau_probe.py`.
Sabotage-Gegenprobe (von Hand): in `Modellwahl.einstellen` `_speicher.clear()` streichen → Fall 1 rot; in `Skriptdienst._haken` `getattr(m, name, None)` statt `__dict__` → Fall 2 rot;
in `G9morphsummekarte.summe` die zweite stabile Sortierung (`rang`) weglassen → Fall 5 rot; `t.float64` statt `w.float()` im Produkt → Fall 5 rot.
"""
import os
import sys
import types
import unittest
from unittest import mock

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))

from core.dienste.mesh3dairig import Mesh3dairig  # noqa: E402
from Genesis9.morphsumme import G9morphsumme  # noqa: E402
from Genesis9.rechenkarte import G9rechenkarte  # noqa: E402
from mesh3dai_modellwahl import Modellwahl  # noqa: E402
from mesh3dai_skriptdienst import Skriptdienst  # noqa: E402


class DienstModellTest(unittest.TestCase):
    def setUp(self):
        self.rig = (Mesh3dairig.MODELL, Mesh3dairig.MODELL_DATEI, dict(Mesh3dairig._speicher))
        self.karte = G9rechenkarte.stand()

    def tearDown(self):
        Mesh3dairig.MODELL, Mesh3dairig.MODELL_DATEI = self.rig[:2]
        Mesh3dairig._speicher.clear()
        Mesh3dairig._speicher.update(self.rig[2])
        G9rechenkarte.zuruecksetzen(self.karte)

    def test_1_modell_je_zugriff(self):
        with mock.patch.dict(os.environ, {'MESH3DAI_MODELL': '_probe_a_gibt_es_nicht'}):
            self.assertEqual(Modellwahl.werte()['MODELL'], '_probe_a_gibt_es_nicht')
            Modellwahl.einstellen()
            self.assertEqual((Mesh3dairig.MODELL, Mesh3dairig.MODELL_DATEI), ('_probe_a_gibt_es_nicht', None))
            Mesh3dairig._speicher['probe'] = 1
            Modellwahl.einstellen()                      # gleiches Modell: Zwischenspeicher bleibt
            self.assertIn('probe', Mesh3dairig._speicher)
        with mock.patch.dict(os.environ, {'MESH3DAI_MODELL': '_probe_b_gibt_es_nicht'}):
            w = Modellwahl.einstellen()
            self.assertEqual(w['DATEN'].name, '_probe_b_gibt_es_nicht')
            self.assertEqual(Mesh3dairig.MODELL, '_probe_b_gibt_es_nicht')
            self.assertNotIn('probe', Mesh3dairig._speicher)

    def test_2_haken_ohne_modul_getattr(self):
        m = types.ModuleType('_probe_dienst_haken')
        m._skriptdienst_zuruecksetzen = lambda stand=None: None

        def nie(name):
            raise AssertionError('Modul-__getattr__ gerufen: %s' % name)

        anderes = types.ModuleType('_probe_dienst_ohne_haken')
        anderes.__getattr__ = nie
        with mock.patch.dict(sys.modules, {m.__name__: m, anderes.__name__: anderes}):
            namen = [n for n, _f in Skriptdienst._haken('_skriptdienst_zuruecksetzen')]
        self.assertIn(m.__name__, namen)
        self.assertNotIn(anderes.__name__, namen)

    def test_3_zuruecksetzen_mit_und_ohne_stand(self):
        aufrufe = []
        haken = [('a', lambda stand=None: aufrufe.append(('a', stand))), ('b', lambda stand=None: aufrufe.append(('b', stand)))]
        with mock.patch.object(Skriptdienst, '_haken', return_value=haken):
            Skriptdienst._module_zuruecksetzen()
            Skriptdienst._module_zuruecksetzen({'a': 'X'})
        self.assertEqual(aufrufe, [('a', None), ('b', None), ('a', 'X'), ('b', None)])

    def test_3b_pfade_frueherer_auftraege_hinten(self):
        d = Skriptdienst.__new__(Skriptdienst)
        d.basis, d.pfade = {'path': ['/basis']}, []
        alt = list(sys.path)
        try:
            sys.path[:] = ['/skript', '/vom_import', '/basis']
            d._pfade_merken()
            sys.path[:] = ['/skript', '/basis', '/neu']
            d._pfade_merken()
        finally:
            sys.path[:] = alt
        self.assertEqual(d.pfade, ['/skript', '/vom_import', '/neu'])
        self.assertEqual(d.basis['path'] + d.pfade, ['/basis', '/skript', '/vom_import', '/neu'])     # so setzt `_zuruecksetzen` sys.path

    def test_4_rechenkarte_stand(self):
        G9rechenkarte.aktiv, G9rechenkarte.grund = True, 'probe'
        stand = G9rechenkarte.stand()
        G9rechenkarte.zuruecksetzen()
        self.assertEqual(G9rechenkarte.stand(), (False, 'aus (Vorgabe)'))
        G9rechenkarte.zuruecksetzen(stand)
        self.assertEqual(G9rechenkarte.stand(), (True, 'probe'))

    def test_5_morphsumme_auf_der_karte_bitgleich(self):
        try:
            import torch
        except ImportError:
            self.skipTest('kein torch')
        if not torch.cuda.is_available():
            self.skipTest('keine CUDA')
        from Genesis9.morphsummekarte import G9morphsummekarte
        from mesh3dai_gpusperre import Gpusperre
        rng = np.random.default_rng(7)
        n = 400
        basis = rng.standard_normal((n, 3))
        basis[::7, 0] = -0.0
        ab, bis, punkt, delta = {}, {}, [], []
        for k in range(30):
            nr = np.sort(rng.choice(n + 20, size=int(rng.integers(5, 120)), replace=False)).astype(np.int32)   # auch Nummern ≥ n
            ab['m%d' % k], bis['m%d' % k] = sum(map(len, punkt)), sum(map(len, punkt)) + len(nr)
            punkt.append(nr)
            delta.append(rng.standard_normal((len(nr), 3)).astype(np.float32) * 0.01)
        ablage = types.SimpleNamespace(ab=ab, bis=bis, punkt=np.concatenate(punkt), delta=np.concatenate(delta))
        daz = [('m%d' % k, float(rng.standard_normal())) for k in range(30)] + [('fehlt', 0.5), ('m3', 0.0)]
        eigene = [(np.arange(0, n, 3, dtype=np.int32), rng.standard_normal((len(range(0, n, 3)), 3)).astype(np.float32), 1.0),
                  (np.arange(5, n, 11, dtype=np.int32), rng.standard_normal((len(range(5, n, 11)), 3)).astype(np.float32), np.float64(0.3))]
        cpu = basis.copy()
        for name, wert in daz:
            if name in ab:
                G9morphsumme.addieren(cpu, ablage.punkt[ab[name]:bis[name]], ablage.delta[ab[name]:bis[name]], wert)
        for nr, d, wert in eigene:
            G9morphsumme.addieren(cpu, nr, d, wert)
        G9rechenkarte.aktiv = True
        with Gpusperre('test_morphsummekarte', bedarf=1):
            gpu = G9morphsummekarte(G9rechenkarte.an()).summe(basis, ablage, daz, eigene)
            G9morphsummekarte._ablage = None
        self.assertTrue(np.array_equal(cpu.view(np.uint64), gpu.view(np.uint64)))


if __name__ == '__main__':
    unittest.main()
