# -*- coding: utf-8 -*-
"""Mesh to 3D, 12.10.2026: Maßterm (Segmentlängen der SAM-Gelenke), Tiefe der Gelenke im Netz, Versatz der SAM-Gelenkpunkte auf Genesis.

Anlass (Auftrag „Edgar", `2026.10.12.07.45.13`): das Netz ist 2,00 m hoch (Import-Setzung), die Figur in Ruhe 1,825 m. Die Anpassung ließ `ProportionHeight` bei 0,015 und `LegsLength` bei 0,005 und glich die 18 cm
mit Anheben (`tg` y +0,184 m) und 66–68° Fußdrehung aus; die Gelenke blieben 12–19 cm von den SAM-Punkten. Dazu lagen die SAM-Hüften wegen des Medians der Tiefe 8–12 cm vor dem Körper.
Kunstdaten; der Maßterm braucht torch (nur python10) und wird sonst übersprungen. Sabotage-Gegenprobe (12.10.2026, `ProjektTemp/_wegwerf/mesh3d/sabotage_tiefe.py`): `Engine2d3dKleiderposeabbildung.TIEFE` auf 'median' → `test_vorgabe_ist_die_mitte` rot; die Rechnung der Mitte auf den Median zurückgebogen (`np.percentile` liefert den Median) → `test_tiefe_mitte_statt_median` rot.
"""

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

TOOLS = Path(__file__).resolve().parents[4]
HAT_TORCH = importlib.util.find_spec('torch') is not None


class TiefeTest(unittest.TestCase):
    """Die Tiefe eines Gelenks im Strahl ist die Mitte der Dicke, nicht der Median."""

    def _abbildung(self):
        from core.dienste.engine2d3dkleiderposeabbildung import Engine2d3dKleiderposeabbildung as A

        z = np.random.default_rng(1)
        # Rumpf als zwei Schichten: vorn (z +0,10) mehr Punkte als hinten (z −0,10) — der Median liegt dann auf der Vorderseite.
        vorn = np.c_[z.uniform(-0.1, 0.1, 900), z.uniform(0.0, 1.0, 900), np.full(900, 0.10)]
        hinten = np.c_[z.uniform(-0.1, 0.1, 500), z.uniform(0.0, 1.0, 500), np.full(500, -0.10)]
        punkte = np.concatenate([vorn, hinten])
        scan = SimpleNamespace(punkte=punkte, abtasten=lambda n: (punkte, None))
        a = A.__new__(A)
        a.scan, a.variante, a.kasten, a.sx, a.sy, a.u0, a.v0 = scan, '(x,-y)', (0, 0, 1, 1), 1.0, 1.0, 0.0, 0.0
        a._baum = a._punkte = None
        return a

    def _tiefe(self, art):
        a = self._abbildung()
        a.TIEFE = art
        roh, treffer, _ = a.landmarken(np.array([[0.0, -0.5]]), ['huefte'], {23: 'huefte'})
        self.assertEqual(treffer[23], 9.0)
        return float(roh[23][2])

    def test_tiefe_mitte_statt_median(self):
        self.assertAlmostEqual(self._tiefe('mitte'), 0.0, places=6)

    def test_der_median_liegt_auf_einer_schicht(self):
        """Die Gegenprobe: die alte Wahl landet auf der Vorderseite (so waren die Hüften 11 cm vor dem Körper)."""
        self.assertGreater(self._tiefe('median'), 0.09)

    def test_vorgabe_ist_die_kette(self):
        """Seit 17.10.2026 die Kette (`Engine2d3dKleiderposetiefe`); Rumpf und Gesicht rechnet sie weiter mit der Mitte."""
        from core.dienste.engine2d3dkleiderposeabbildung import Engine2d3dKleiderposeabbildung as A

        self.assertEqual(A.TIEFE, 'kette')

    def test_kette_ohne_sam_ist_die_mitte(self):
        """Ohne `k3` (kein SAM, oder ein alter Aufrufer) rechnet die Kette wie die Mitte."""
        self.assertAlmostEqual(self._tiefe('kette'), 0.0, places=6)


class SamTabelleTest(unittest.TestCase):
    NUMMERN = (11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28)

    def test_tabelle_baut_und_beschreibt_sich(self):
        from Genesis9.netzlandmarkensam import G9netzlandmarkensam as T

        m, f = np.full((12, 3), 0.01), np.full((12, 3), 0.01)
        f[6] = [0.02, -0.01, 0.0]
        t = T.bauen({'masculine': m, 'feminine': f})
        self.assertEqual([int(n) for n in t.daten['nummer']], list(self.NUMMERN))
        brief = t.steckbrief()
        self.assertEqual(brief['gelenke'], list(self.NUMMERN))
        self.assertGreater(brief['unterschied_basen_cm'], 1.0)

    def _daten(self, tabelle, auftrag, optionen):
        from meshfigur_daten import Meshfigurdaten

        d = Meshfigurdaten.__new__(Meshfigurdaten)
        d.auftrag, d.optionen, d.SAM_TABELLE = auftrag, optionen, tabelle
        roh = {'lm_gelenk_nummer': np.array(self.NUMMERN, np.int32), 'lm_gelenk_versatz': np.full((12, 3), 0.5, np.float32)}
        return d, d._sam_versatz(roh)

    def test_mit_pose_gilt_die_sam_tabelle_je_grundfigur(self):
        with tempfile.TemporaryDirectory(dir=str(TOOLS / 'ProjektTemp')) as ordner:
            pfad = os.path.join(ordner, 'sam.npz')
            m, f = np.full((12, 3), 0.01, np.float32), np.full((12, 3), 0.02, np.float32)
            f[8] = np.nan                                                        # SAM fand dieses Gelenk bei der Frau nicht: der MediaPipe-Wert bleibt
            np.savez(pfad, nummer=np.array(self.NUMMERN), versatz_masculine=m, versatz_feminine=f)
            d, aus = self._daten(pfad, {'landmarken_hand': 'x.npz'}, {'basis': 'masculine'})
            self.assertEqual(d.versatz_quelle, 'sam')
            np.testing.assert_allclose(aus['lm_gelenk_versatz'], m)
            d, aus = self._daten(pfad, {'landmarken_hand': 'x.npz'}, {'basis': 'feminine'})
            np.testing.assert_allclose(aus['lm_gelenk_versatz'][0], f[0])
            np.testing.assert_allclose(aus['lm_gelenk_versatz'][8], [0.5, 0.5, 0.5])

    def test_ohne_pose_bleibt_mediapipe(self):
        d, aus = self._daten(str(TOOLS / 'gibt_es_nicht.npz'), {}, {})
        self.assertEqual(d.versatz_quelle, 'mediapipe')
        self.assertTrue((aus['lm_gelenk_versatz'] == 0.5).all())

    def test_fehlende_tabelle_wird_gesagt(self):
        d, aus = self._daten(str(TOOLS / 'gibt_es_nicht.npz'), {'landmarken_hand': 'x.npz'}, {})
        self.assertIn('SAM-Tabelle fehlt', d.versatz_quelle)
        self.assertTrue((aus['lm_gelenk_versatz'] == 0.5).all())


@unittest.skipUnless(HAT_TORCH, 'torch fehlt (Maßterm läuft im Runner, python10)')
class MasstermTest(unittest.TestCase):
    NUMMERN = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

    def _skelett(self):
        """Gelenkpunkte einer stehenden Figur (m, Mitte x = 0): Schultern, Ellbogen, Handgelenke, Hüften, Knie, Knöchel."""
        x = {11: 0.2, 12: -0.2, 13: 0.3, 14: -0.3, 15: 0.35, 16: -0.35, 23: 0.09, 24: -0.09, 25: 0.1, 26: -0.1, 27: 0.1, 28: -0.1}
        y = {11: 1.5, 12: 1.5, 13: 1.2, 14: 1.2, 15: 0.95, 16: 0.95, 23: 0.95, 24: 0.95, 25: 0.5, 26: 0.5, 27: 0.08, 28: 0.08}
        return np.array([[x[n], y[n], 0.0] for n in self.NUMMERN], np.float32)

    def _term(self, schalter=None):
        import torch
        from meshfigur_massterm import Meshfigurmassterm as M

        ziel = torch.as_tensor(self._skelett())
        landmarken = SimpleNamespace(gelenk_nummer=np.array(self.NUMMERN), gelenk_gewicht=torch.ones(12), gelenk_ziel=ziel)
        namen = ['body_bs_ProportionHeight', 'body_bs_ProportionLegsLength', 'body_bs_BodyHeavy', 'head_bs_ProportionNeckLength']
        modell = SimpleNamespace(geraet=torch.device('cpu'), namen=namen, faktor=torch.ones(4), grosse=None)
        alt = os.environ.get(M.SCHALTER)
        if schalter is not None:
            os.environ[M.SCHALTER] = schalter
        try:
            return M(landmarken, modell), modell, ziel
        finally:
            if schalter is not None:
                if alt is None:
                    os.environ.pop(M.SCHALTER, None)
                else:
                    os.environ[M.SCHALTER] = alt

    def test_verlust_null_bei_gleichen_laengen_und_wachsend_bei_zu_kurzen(self):
        term, _, ziel = self._term()
        self.assertAlmostEqual(float(term.verlust(ziel)), 0.0, places=6)
        # Eine um 10 % kleinere Figur (um den Boden skaliert) — dieselbe Lage der Füße, kürzere Beine: das ist der Fall des Edgar-Laufs.
        klein = ziel * 0.9
        grosz = float(term.verlust(klein))
        self.assertGreater(grosz, 0.5)
        # Anheben ändert keine Länge.
        angehoben = ziel + torch_tensor([0.0, 0.16, 0.0])
        self.assertAlmostEqual(float(term.verlust(angehoben)), 0.0, places=6)

    def test_nur_die_groessenregler_sind_frei_und_entlastet(self):
        term, modell, _ = self._term()
        self.assertEqual(modell.grosse.tolist(), [True, True, False, False])
        self.assertEqual([round(float(x), 2) for x in modell.faktor], [0.1, 0.1, 1.0, 1.0])

    def test_hueftbreite_ist_kein_ziel(self):
        """Die SAM-Hüftpunkte sind Gelenkmitten; die Breite stand im Edgar-Lauf 62 mm daneben."""
        term, _, _ = self._term()
        self.assertEqual(term.matrix.shape[0], 10)            # acht Glieder, Schulterbreite, Rumpf

    def test_gewicht_faellt_mit_den_stufen_und_gesicht_hat_keins(self):
        term, _, _ = self._term()
        g = [term.gewicht_der(s) for s in ('haltung', 'groesse', 'koerpertyp', 'bereiche')]
        self.assertEqual(g, sorted(g, reverse=True))
        self.assertGreater(g[0], g[-1])
        self.assertEqual(term.gewicht_der('schaedel'), 0.0)

    def test_schalter_aus_gibt_keinen_term(self):
        term, modell, _ = self._term('0')
        self.assertFalse(term.aktiv)
        self.assertEqual(term.gewicht_der('haltung'), 0.0)
        self.assertIsNone(modell.grosse)


def torch_tensor(werte):
    import torch

    return torch.as_tensor(np.array(werte, np.float32))


if __name__ == '__main__':
    unittest.main()
