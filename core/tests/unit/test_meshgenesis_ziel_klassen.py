# -*- coding: utf-8 -*-
"""Ziel der Einpassung (07.11.2026, Edgar zum Zauberer: „genesis einpassung mehr als miserabel“): lange Kleidung nie anliegend (`Meshgenesismeshanliegend`), „ungesehen“ nur ohne Blick der
Erkennung und Teile aus dem Rig-Käfig auf dem Weg „rig“ (`Meshgenesismeshziel`), die Prüfungen dazu (`Meshgenesismeshklassen`), Hautabstand ohne Hautpunkt (`G9meshipnet._s2m`) und wann die Textur
aus allen Fotos rechnet (`Alletextur.gilt`). Kunstdaten auf der CPU."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
import torch

sys.path.insert(0, r'A:\3DTools\meshgenesis')
sys.path.insert(0, r'A:\3DTools\pshuman_port14')
sys.path.insert(0, r'A:\3DTools')

from ._pruefablage import Pruefablage  # noqa: E402
from Genesis9.koerperteile import G9koerperteile  # noqa: E402
from Genesis9.meshziel import G9meshziel  # noqa: E402
from meshgenesis_kostuemarten import Kostuemarten  # noqa: E402
from meshgenesis_meshanliegend import Meshgenesismeshanliegend  # noqa: E402
from meshgenesis_meshklassen import Meshgenesismeshklassen  # noqa: E402
from meshgenesis_meshziel import Meshgenesismeshziel  # noqa: E402
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402


class Kunstziel:
    """Haut oben (y 1,70) und an den Füßen (y 0), darunter eine Art mit Rand ohne Stufe (y 1,68), Rumpf (y 1,0) und auf Wunsch ein langer Teil (y 0,2)."""

    @staticmethod
    def bau(art='oberteil', lang=False):
        x = lambda n: torch.linspace(0.0, 1.0, n, dtype=torch.float64)  # noqa: E731
        reihe = lambda n, y: torch.stack([x(n), torch.full((n,), y, dtype=torch.float64), torch.zeros(n, dtype=torch.float64)], 1)  # noqa: E731
        haut = torch.cat([reihe(200, 1.70), reihe(20, 0.0)])
        stoff = torch.cat([reihe(300, 1.68), reihe(1000, 1.0)] + ([reihe(1000, 0.2)] if lang else []))
        punkte = torch.cat([haut, stoff])
        klasse = torch.cat([torch.full((len(haut),), G9meshziel.HAUT), torch.full((len(stoff),), G9meshziel.KLEID)])
        nummer = torch.cat([torch.full((len(haut),), Kostuemarten.nummer('haut')), torch.full((len(stoff),), Kostuemarten.nummer(art))])
        return punkte, klasse, nummer

    @staticmethod
    def klassen(punkte, klasse, nummer):
        n = torch.tensor([[0.0, 0.0, 1.0]], dtype=torch.float64).expand(len(punkte), 3)
        with mock.patch.object(G9meshziel, 'normalen', return_value=n):
            return Meshgenesismeshanliegend.klassen(punkte, torch.zeros((1, 3), dtype=torch.long), klasse, nummer, None)


class AnliegendTest(unittest.TestCase):
    databases = []

    def test_kurzes_oberteil_ohne_stufe_ist_anliegend(self):
        neu, b = Kunstziel.klassen(*Kunstziel.bau())
        self.assertTrue(b['oberteil']['anliegend'])
        self.assertEqual(b['oberteil']['tief'], 0.0)
        self.assertEqual(int((neu == G9meshziel.HAUT).sum()), 220 + 1300)

    def test_robe_unter_dem_schritt_bleibt_kleidung(self):
        neu, b = Kunstziel.klassen(*Kunstziel.bau(lang=True))
        self.assertFalse(b['oberteil']['anliegend'])
        self.assertTrue(b['oberteil']['nie'])
        self.assertGreaterEqual(b['oberteil']['tief'], Meshgenesismeshanliegend.TIEF_ANTEIL)
        self.assertEqual(int((neu == G9meshziel.HAUT).sum()), 220)

    def test_hose_darf_unter_den_schritt(self):
        _neu, b = Kunstziel.klassen(*Kunstziel.bau('hose', lang=True))
        self.assertTrue(b['hose']['anliegend'])


class KlassenpruefungTest(unittest.TestCase):
    databases = []

    @staticmethod
    def ziel(klasse_roh, klasse, gesehen, kostuem, art, y):
        t = lambda w, d=torch.float32: torch.tensor(w, dtype=d)  # noqa: E731
        n = len(y)
        punkte = torch.stack([torch.zeros(n), t(y), torch.zeros(n)], 1)
        return {'klasse_roh': t(klasse_roh, torch.long), 'klasse': t(klasse, torch.long), 'art': t([Kostuemarten.nummer(a) for a in art], torch.long), 'punkte': punkte,
                'erkennung': {'kostuem': t(kostuem), 'haar': torch.zeros(n), 'kostuem_einig': torch.zeros(n), 'gesehen': t(gesehen)}, 'zahlen': {'klassen_quelle': 'erkennung'}}

    def test_gesehen_aber_ungesehen_ist_rot(self):
        u, k = G9meshziel.UNBEKANNT, G9meshziel.KLEID
        z = self.ziel([u, u, k, k], [u, u, k, k], [1.0, 0.2, 1.0, 1.0], [1.0] * 4, ['oberteil'] * 4, [1.0, 1.1, 1.2, 1.3])
        m = Meshgenesismeshklassen.messen(z)
        self.assertTrue(m['ungesehen']['rot'])
        self.assertEqual(m['ungesehen']['ungesehen'], 2)
        self.assertTrue(any('ungesehen' in r for r in m['rot']))

    def test_ungesehen_ohne_blick_ist_gruen(self):
        u, k = G9meshziel.UNBEKANNT, G9meshziel.KLEID
        m = Meshgenesismeshklassen.messen(self.ziel([u, k, k, k], [u, k, k, k], [0.0, 1.0, 1.0, 1.0], [1.0] * 4, ['oberteil'] * 4, [1.0, 1.1, 1.2, 1.3]))
        self.assertFalse(m['ungesehen']['rot'])

    def test_robe_als_haut_unter_dem_schritt_ist_rot_hose_nicht(self):
        h, k = G9meshziel.HAUT, G9meshziel.KLEID
        y = [0.0, 0.1, 0.2, 1.8]
        robe = self.ziel([k] * 4, [h, h, h, h], [1.0] * 4, [1.0] * 4, ['oberteil'] * 4, y)
        self.assertTrue(Meshgenesismeshklassen.messen(robe)['lang_als_haut']['rot'])
        hose = self.ziel([k] * 4, [h, h, h, h], [1.0] * 4, [1.0] * 4, ['hose'] * 4, y)
        self.assertFalse(Meshgenesismeshklassen.messen(hose)['lang_als_haut']['rot'])
        robe_kleid = self.ziel([k] * 4, [k, k, k, k], [1.0] * 4, [1.0] * 4, ['oberteil'] * 4, y)
        self.assertFalse(Meshgenesismeshklassen.messen(robe_kleid)['lang_als_haut']['rot'])


class TeileRigTest(unittest.TestCase):
    databases = []
    RAHMEN = {'heading': 0.0, 'zentrum': [0.0, 0.0], 'boden': 0.0, 'massstab': 1.0, 'ruhehoehe': 0.0}

    @staticmethod
    def zielrechner():
        z = Meshgenesismeshziel.__new__(Meshgenesismeshziel)
        z.g, z.log = 'cpu', lambda *_a: None
        return z

    def _kette(self, ordner):
        kopf, fuss = G9koerperteile.NUMMER['kopf'], G9koerperteile.NUMMER['l_fuss']
        Npztorch.speichern(Path(ordner) / 'figur.npz', kaefig_posiert=np.array([[0.0, 1.7, 0.0], [0.0, 0.1, 0.0]]), teil=np.array([kopf, fuss]), m=np.eye(4), rahmen=np.array('M'), faktor=np.array(1.0), zu_glb=np.eye(4))
        return Path(ordner)

    def test_weg_rig_nimmt_den_kaefig(self):
        with Pruefablage.ordner() as o:
            kette = self._kette(o)
            punkte = torch.tensor([[0.0, 1.6, 0.0], [0.0, 0.2, 0.0]], dtype=torch.float64)
            teil = self.zielrechner()._teile(kette, torch.zeros(2, dtype=torch.long), 2, punkte, 'rig', self.RAHMEN, 0.0)
        self.assertEqual(teil.tolist(), [G9koerperteile.NUMMER['kopf'], G9koerperteile.NUMMER['l_fuss']])

    def test_plausible_mia_teile_bleiben_auch_auf_weg_rig(self):
        n = G9koerperteile.NUMMER
        teil = torch.tensor([n['kopf'], n['becken'], n['l_fuss'], n['r_fuss']])
        punkte = torch.tensor([[0.0, 1.7, 0.0], [0.0, 1.0, 0.0], [0.1, 0.1, 0.0], [-0.1, 0.1, 0.0]], dtype=torch.float64)
        self.assertTrue(Meshgenesismeshziel.plausibel(teil, punkte))
        self.assertFalse(Meshgenesismeshziel.plausibel(teil, punkte.flip(0)))          # Kopf an den Füßen (Zauberer, MIA)
        self.assertFalse(Meshgenesismeshziel.plausibel(teil[:3], punkte[:3]))          # ein Fuß fehlt
        with Pruefablage.ordner() as o, mock.patch.object(Meshgenesismeshziel, '_teile_mia', return_value=teil):
            aus = self.zielrechner()._teile(self._kette(o), torch.zeros(4, dtype=torch.long), 4, punkte, 'rig', self.RAHMEN, 0.0)
        self.assertEqual(aus.tolist(), teil.tolist())

    def test_miagelenke_unplausibel_auf_weg_rig_nimmt_die_ansichten(self):
        from meshgenesis_fotogelenke import Meshgenesisfotogelenke
        from meshgenesis_miagelenke import Miagelenke
        namen = ['mixamorig:Head', 'mixamorig:Hips', 'mixamorig:LeftFoot', 'mixamorig:RightFoot']
        oben = np.array([[0.0, 1.7, 0.0], [0.0, 1.0, 0.0], [0.1, 0.1, 0.0], [-0.1, 0.1, 0.0]])
        self.assertTrue(Miagelenke.plausibel(namen, oben))
        self.assertFalse(Miagelenke.plausibel(namen, oben[::-1]))
        sicht = (['Head', 'Hips', 'LeftFoot', 'RightFoot'], oben)
        with Pruefablage.ordner() as o:
            kette = Path(o) / 'vorstufe' / '0001'
            (kette / 'mia').mkdir(parents=True)
            Npztorch.speichern(kette / 'mia' / 'mia.npz', namen=np.array(namen), gelenke=oben[::-1])
            (kette / 'kette.json').write_text('{"weg": "rig"}', encoding='utf-8')
            with mock.patch.object(Meshgenesisfotogelenke, 'ansichten', return_value=sicht) as ansichten:
                m = Miagelenke(kette)
            self.assertEqual(ansichten.call_args[0][0], Path(o))
            self.assertEqual((m.da, m.bezug, m.namen), (True, 'den Gelenken der sechs Ansichten', sicht[0]))
            with mock.patch.object(Meshgenesisfotogelenke, 'ansichten', return_value=None):
                self.assertFalse(Miagelenke(kette).da)
            (kette / 'kette.json').write_text('{"weg": "mia"}', encoding='utf-8')
            self.assertEqual(Miagelenke(kette).bezug, 'MIA')

    def test_weg_mia_nimmt_den_kaefig_nicht(self):
        with Pruefablage.ordner() as o:
            kette = self._kette(o)
            punkte = torch.tensor([[0.0, 1.6, 0.0], [0.0, 0.2, 0.0]], dtype=torch.float64)
            teil = self.zielrechner()._teile(kette, torch.zeros(2, dtype=torch.long), 2, punkte, 'mia', self.RAHMEN, 0.0)
        self.assertIsNone(teil)         # ohne mia.npz kein Teil


class S2mOhneHautTest(unittest.TestCase):
    databases = []

    @staticmethod
    def netz(haut):
        from Genesis9.meshipnet import G9meshipnet
        n = G9meshipnet.__new__(G9meshipnet)
        n.scan_haut_p = haut
        n.fl_smpl = SimpleNamespace(abstaende=lambda p, v: (p ** 2).sum(1))
        return n

    def test_ohne_hautpunkt_null_statt_nan(self):
        w = self.netz(torch.zeros((0, 3)))._s2m(torch.zeros((5, 3)))
        self.assertEqual(float(w), 0.0)

    def test_mit_hautpunkten_das_mittel(self):
        w = self.netz(torch.tensor([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0]]))._s2m(torch.zeros((5, 3)))
        self.assertAlmostEqual(float(w), 2.5)


class AlletexturGiltTest(unittest.TestCase):
    databases = []

    def test_wann_die_textur_aus_allen_fotos_rechnet(self):
        from alletextur import Alletextur
        fotos = [{'winkel': 0}, {'winkel': 90}]
        self.assertTrue(Alletextur.gilt({'fotos': fotos}))
        self.assertFalse(Alletextur.gilt({'fotos': [{'winkel': 0}]}))
        self.assertFalse(Alletextur.gilt({'fotos': [{'winkel': 0}, {'winkel': None}]}))
        self.assertFalse(Alletextur.gilt({'fotos': fotos, 'pshuman': {'up2you': True}}))
        self.assertFalse(Alletextur.gilt({'fotos': fotos, 'pshuman': {'textur_alle_fotos': False}}))
        self.assertTrue(Alletextur.gilt({'fotos': fotos, 'pshuman': {'textur_alle_fotos': True}}))
        self.assertTrue(Alletextur.gilt({'fotos': fotos, 'pshuman': {'textur_alle_fotos': None}}))


if __name__ == '__main__':
    unittest.main()
