# -*- coding: utf-8 -*-
"""`Kleidunggewebe` — Hautgewichte für Stoff, der nicht am Körper anliegt, über das Gewebe (14.10.2026).

Edgar: „ballerina riggt den Rock an die Hände, daher ist die Animation falsch.“ Gemessen am Neulauf der Spiralballerina: 1.549 von 3.667 Rockpunkten trugen über 0,3 Gewicht auf Arm-Knochen (die breite Mischung der Käfig-Nachbarn reicht bei 8–10 cm
Abstand bis zu den Händen), mit der Regel 17. Die Fälle hier bauen ein Tuch (Gitter) mit Randbedingungen aus Kunstgewichten:

    anliegende Punkte behalten ihre Gewichte (bitgleich), die Summe je Punkt ist 1, die vier Knochen sind absteigend sortiert
    ein Tuch, das beidseitig an Knochen 0 anliegt, aber in der Mitte (weit weg) Arm-Gewichte trägt, bekommt dort Knochen 0 — der Arm hat keinen Einfluss
    zwischen zwei verschiedenen Ankern (Knochen 0 links, Knochen 2 rechts) mischen die Gewichte stetig (in der Mitte je etwa ½, nirgends ein Sprung)
    ein Teil ohne einen Punkt nahe am Körper bekommt Ersatzanker (seine dem Körper nächsten Punkte), die Rechnung bleibt lösbar
    mehr freie Punkte als `MAX_FREI` werden nicht gerechnet, die Gewichte bleiben, der Grund steht im Befund
    ohne freie Punkte (alles anliegend) ändert sich nichts

Sabotage: in `Kleidunggewebe.berechnen` die Zeilen `ind[anker_nr] = index[anker_nr]` und `gew[anker_nr] = gewicht[anker_nr]` streichen → der Fall der anliegenden Punkte wird rot; die Gleichung durch `x_frei = rand @ x_anker` (ohne Lösen) ersetzen → der Fall der stetigen Mischung wird rot.
Probegelaufen (ohne Testlauf) an den echten Gewichten der Ballerina: `ProjektTemp/_wegwerf/mesh3d/gewebe_anker_reihe.py`.
"""

import numpy as np
from django.test import SimpleTestCase

from Kleidung.kleidunggewebe import Kleidunggewebe

N = 5                                                           # Knochen 0 Becken, 1 Arm, 2 Bein, 3 Brust, 4 Kopf


def tuch(nx=21, ny=3, breite=1.0):
    """Ein Gitter in der x-y-Ebene (x 0…breite), Dreiecke je Zelle; `(punkte, dreiecke, x)`."""
    xs, ys = np.linspace(0, breite, nx), np.linspace(0, 0.1, ny)
    p = np.array([[x, y, 0.0] for y in ys for x in xs])
    d = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            d += [[a, a + 1, a + nx], [a + 1, a + nx + 1, a + nx]]
    return p, np.array(d), p[:, 0]


def gewichte(m, tabelle):
    """`tabelle`: `{Knochen: Gewicht}` für alle Punkte (index (M, 4), gewicht (M, 4))."""
    index, gewicht = np.zeros((m, 4), dtype=np.int64), np.zeros((m, 4))
    for k, (b, w) in enumerate(tabelle.items()):
        index[:, k], gewicht[:, k] = b, w
    return index, gewicht


def dichte(index, gewicht):
    aus = np.zeros((len(index), N))
    np.add.at(aus, (np.repeat(np.arange(len(index)), index.shape[1]), index.ravel()), gewicht.ravel())
    return aus


class NahTest(SimpleTestCase):
    """`Kleidunghautgewichte`: anliegender Stoff bekommt eine schmale Mischung, damit er sich wie die Haut bewegt (Strumpfhose am Hüftansatz, 14.10.2026).
    Gemessen an der Ballerina: Abstand zur Haut ändert sich im Tanz bei 0,75–0,95 m Höhe um p95 99 mm / max 240 mm (5-cm-Mischung), mit 1 cm um 2,9 mm / 20 mm."""

    databases = set()

    @staticmethod
    def _gewichte(p, d_stoff):
        """Ein Käfig entlang x (Knochen 0 links von 0,5, Knochen 1 rechts), ein Stoffpunkt bei x = 0,52 im Abstand `d_stoff` → die Gewichte des Punkts."""
        from types import SimpleNamespace

        from scipy.spatial import cKDTree

        from Kleidung.kleidunghautgewichte import Kleidunghautgewichte

        x = np.linspace(0, 1, 101)
        kaefig = np.stack([x, np.zeros_like(x), np.zeros_like(x)], axis=1)
        k_index = np.where(x[:, None] < 0.5, 0, 1) * np.ones((1, 4), dtype=np.int64)
        k_gewicht = np.zeros((len(x), 4))
        k_gewicht[:, 0] = 1.0
        stub = SimpleNamespace(baum=cKDTree(kaefig), NACHBARN=40, SIGMA=0.05, nachbarn={})
        ind, gew = Kleidunghautgewichte(stub).berechnen(np.array([[0.52, d_stoff, 0.0]]), k_index, k_gewicht, 6)
        aus = np.zeros(6)
        np.add.at(aus, ind[0], gew[0])
        return aus

    def test_die_mindestbreite_waechst_mit_dem_abstand(self):
        from Kleidung.kleidunghautgewichte import Kleidunghautgewichte as K

        b = K.mindestbreite(np.array([0.0, 0.02, 0.035, 0.05, 0.3]), 0.05)
        np.testing.assert_allclose(b, [0.01, 0.01, 0.03, 0.05, 0.05], atol=1e-12)

    def test_anliegender_stoff_nimmt_die_gewichte_der_haut_darunter(self):
        w = self._gewichte(None, 0.01)
        self.assertGreater(float(w[1]), 0.97, 'bei 1 cm Abstand zählt fast nur der Knochen der nächsten Haut: %s' % w)

    def test_anliegender_stoff_nimmt_die_nachbarschaft_der_ruhelage_nicht_die_der_haltung(self):
        """Der Käfig steht in der Haltung gespiegelt (Knochen 0 rechts): der nächste Käfigpunkt in der HALTUNG gehört zum falschen Knochen, in der Ruhelage zum richtigen — der Stoff folgt der Ruhelage."""
        from types import SimpleNamespace

        from scipy.spatial import cKDTree

        from Kleidung.kleidunghautgewichte import Kleidunghautgewichte

        x = np.linspace(0, 1, 101)
        ruhe = np.stack([x, np.zeros_like(x), np.zeros_like(x)], axis=1)
        posiert = ruhe.copy()
        posiert[:, 0] = 1.0 - x
        k_index = np.where(x[:, None] < 0.5, 0, 1) * np.ones((1, 4), dtype=np.int64)
        k_gewicht = np.zeros((len(x), 4))
        k_gewicht[:, 0] = 1.0
        stub = SimpleNamespace(baum=cKDTree(posiert), ruhe=ruhe, NACHBARN=40, SIGMA=0.05, nachbarn={})
        netz = np.array([[0.52, 0.01, 0.0]])                        # in der Haltung liegt der Käfig mit Knochen 0 bei x = 0,52
        aus = {}
        for name, argumente in (('mit_ruhe', {'ruhe': np.array([[0.52, 0.01, 0.0]])}), ('ohne_ruhe', {})):
            ind, gew = Kleidunghautgewichte(stub).berechnen(netz, k_index, k_gewicht, 6, **argumente)
            w = np.zeros(6)
            np.add.at(w, ind[0], gew[0])
            aus[name] = w
        self.assertGreater(float(aus['mit_ruhe'][1]), 0.95, 'Ruhelage: Knochen 1 liegt dort — %s' % aus['mit_ruhe'])
        self.assertGreater(float(aus['ohne_ruhe'][0]), 0.9, 'nur die Haltung: Knochen 0 — %s' % aus['ohne_ruhe'])

    def test_weit_abstehender_stoff_mischt_weiter_breit(self):
        w = self._gewichte(None, 0.30)
        self.assertGreater(float(w[0]), 0.2, 'bei 30 cm Abstand mischt σ = ½ · Abstand beide Knochen: %s' % w)
        self.assertGreater(float(w[1]), 0.2, str(w))


class GewebeTest(SimpleTestCase):
    databases = set()

    def _abstand(self, x, rand=0.01, mitte=0.2):
        """Anliegend (1 cm) an den beiden Rändern des Tuchs, in der Mitte weit weg (20 cm)."""
        return np.where((x < 0.06) | (x > 0.94), rand, mitte)

    def test_der_arm_im_rand_hat_keinen_einfluss_auf_ein_tuch_das_am_becken_haengt(self):
        p, d, x = tuch()
        index, gewicht = gewichte(len(p), {0: 1.0})
        arm = (x > 0.4) & (x < 0.6)                                   # die Mitte trägt Arm-Gewichte (breite Mischung), obwohl sie weit weg hängt
        index[arm], gewicht[arm] = [1, 0, 0, 0], [0.8, 0.2, 0, 0]
        ind, gew = Kleidunggewebe(anker_m=0.06).berechnen(p, d, index, gewicht, self._abstand(x), N)
        arm_nachher = dichte(ind, gew)[:, 1]
        self.assertGreater(float(dichte(index, gewicht)[arm, 1].min()), 0.7, 'Ausgang: Arm-Gewicht in der Mitte')
        self.assertLess(float(arm_nachher.max()), 1e-9, 'nachher kein Arm-Gewicht mehr')
        np.testing.assert_allclose(dichte(ind, gew)[:, 0], 1.0, atol=1e-9)

    def test_anliegende_punkte_behalten_ihre_gewichte_summe_eins_absteigend(self):
        p, d, x = tuch()
        index, gewicht = gewichte(len(p), {0: 0.6, 3: 0.4})
        anliegend = self._abstand(x) < 0.05
        index[~anliegend], gewicht[~anliegend] = [1, 2, 0, 0], [0.5, 0.5, 0, 0]
        ind, gew = Kleidunggewebe(anker_m=0.06).berechnen(p, d, index, gewicht, self._abstand(x), N)
        np.testing.assert_array_equal(ind[anliegend], index[anliegend])
        np.testing.assert_array_equal(gew[anliegend], gewicht[anliegend])
        np.testing.assert_allclose(gew.sum(axis=1), 1.0, atol=1e-9)
        self.assertTrue((np.diff(gew, axis=1) <= 1e-12).all(), 'je Punkt absteigend sortiert')

    def test_zwischen_zwei_ankern_mischen_die_gewichte_stetig(self):
        p, d, x = tuch(nx=41)
        index, gewicht = gewichte(len(p), {0: 1.0})
        links, rechts = x < 0.06, x > 0.94
        index[rechts] = 2
        ind, gew = Kleidunggewebe(anker_m=0.06).berechnen(p, d, index, gewicht, self._abstand(x), N)
        dicht = dichte(ind, gew)
        mitte = np.abs(x - 0.5) < 0.026
        self.assertTrue(((dicht[mitte, 0] > 0.4) & (dicht[mitte, 0] < 0.6)).all(), 'in der Mitte etwa je ein Halbes: %s' % dicht[mitte, 0])
        reihe = dicht[np.argsort(x), 0][::3]
        self.assertLess(float(np.abs(np.diff(reihe)).max()), 0.15, 'kein Sprung entlang des Tuchs')
        self.assertGreater(float(dicht[links, 0].min()), 0.99)

    def test_ein_teil_ohne_anliegenden_punkt_bekommt_ersatzanker(self):
        p, d, x = tuch()
        index, gewicht = gewichte(len(p), {0: 1.0})
        abstand = np.full(len(p), 0.3)
        abstand[x < 0.03] = 0.25                                       # die dem Körper nächsten Punkte, aber alle weit weg
        regel = Kleidunggewebe(anker_m=0.06)
        ind, gew = regel.berechnen(p, d, index, gewicht, abstand, N)
        self.assertEqual(regel.befund['ersatz_teile'], 1)
        self.assertGreaterEqual(regel.befund['anker'], 3)
        np.testing.assert_allclose(dichte(ind, gew)[:, 0], 1.0, atol=1e-9)

    def test_zu_viele_freie_punkte_werden_nicht_gerechnet(self):
        p, d, x = tuch()
        index, gewicht = gewichte(len(p), {0: 1.0})
        arm = (x > 0.4) & (x < 0.6)
        index[arm], gewicht[arm] = [1, 0, 0, 0], [1.0, 0, 0, 0]
        regel = Kleidunggewebe(anker_m=0.06)
        regel.MAX_FREI = 5
        ind, gew = regel.berechnen(p, d, index, gewicht, self._abstand(x), N)
        np.testing.assert_array_equal(ind, index)
        np.testing.assert_array_equal(gew, gewicht)
        self.assertIn('zu viele freie Punkte', regel.befund['uebersprungen'])

    def test_ohne_freie_punkte_aendert_sich_nichts(self):
        p, d, _ = tuch()
        index, gewicht = gewichte(len(p), {0: 0.7, 2: 0.3})
        regel = Kleidunggewebe(anker_m=0.06)
        ind, gew = regel.berechnen(p, d, index, gewicht, np.full(len(p), 0.01), N)
        np.testing.assert_array_equal(ind, index)
        np.testing.assert_array_equal(gew, gewicht)
        self.assertEqual(regel.befund['frei'], 0)
