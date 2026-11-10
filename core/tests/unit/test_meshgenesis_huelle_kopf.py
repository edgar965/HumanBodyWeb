"""Kopf unter Helm: `Meshgenesismeshhuelle` hält ihn an MIA, wenn das Ziel dort kaum Haut hat (roboter, 07.11.2026). Ohne Datenbank, ohne Karte."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'meshgenesis'))
from Genesis9.koerperteile import G9koerperteile  # noqa: E402
from Genesis9.meshipnet import G9meshipnet  # noqa: E402
from Genesis9.meshziel import G9meshziel  # noqa: E402
from Genesis9.meshkopf import G9meshkopf  # noqa: E402
from meshgenesis_meshhuelle import Meshgenesismeshhuelle  # noqa: E402
from meshgenesis_meshkopf import Meshgenesismeshkopf  # noqa: E402


class KopfUnterStoffTest(unittest.TestCase):
    databases = []

    @staticmethod
    def ziel(kopf_haut, kopf_stoff):
        n = kopf_haut + kopf_stoff
        klasse = torch.full((n,), G9meshziel.HAUT + 1)
        klasse[:kopf_haut] = G9meshziel.HAUT
        return SimpleNamespace(teil=torch.full((n,), G9koerperteile.NUMMER['kopf']), klasse=klasse)

    def stoff(self, kopf_haut, kopf_stoff):
        return Meshgenesismeshhuelle(None).stoff(self.ziel(kopf_haut, kopf_stoff))

    def test_helm_mit_kragenresten_haelt_den_kopf(self):
        self.assertTrue(self.stoff(57, 3000)['kopf'])

    def test_langes_haar_ueber_dem_gesicht_zaehlt_nicht_als_stoff(self):
        self.assertFalse(self.stoff(G9meshipnet.KOPF_MIN_HAUT, 5000)['kopf'])

    def test_teile_ohne_punkte_fehlen(self):
        self.assertEqual(list(self.stoff(10, 10)), ['kopf'])

    def test_gelenke(self):
        self.assertEqual(Meshgenesismeshhuelle.gelenk('kopf'), 'head')
        self.assertEqual(Meshgenesismeshhuelle.gelenk('r_unterarm'), 'r_hand')

    def test_kopfschritt_entscheidet_mit_derselben_zahl_wie_die_huelle(self):
        """zdmit: Das Ziel hat Kopfhaut, nur liegt der Kopf der Figur daneben. Die Schwelle darf den Kopfschritt nicht abschalten."""
        for haut, stoff in ((Meshgenesismeshkopf.MIN_HAUT, 5000), (2000, 3000)):
            ziel = self.ziel(haut, stoff)
            self.assertFalse(Meshgenesismeshhuelle(None).stoff(ziel)['kopf'])
            self.assertEqual(Meshgenesismeshkopf.mindesthaut(ziel), (G9meshkopf.MIN_HAUT, haut))

    def test_kopfschritt_bleibt_aus_unter_dem_helm(self):
        ziel = self.ziel(57, 3000)
        self.assertTrue(Meshgenesismeshhuelle(None).stoff(ziel)['kopf'])
        self.assertEqual(Meshgenesismeshkopf.mindesthaut(ziel), (Meshgenesismeshkopf.MIN_HAUT, 57))

    def test_ohne_teile_bleibt_die_schwelle(self):
        self.assertEqual(Meshgenesismeshkopf.mindesthaut(SimpleNamespace(teil=None, klasse=None)), (Meshgenesismeshkopf.MIN_HAUT, None))


if __name__ == '__main__':
    unittest.main()
