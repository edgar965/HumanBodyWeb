# -*- coding: utf-8 -*-
"""Das Herrenhaar auf einem Kunstkopf (05.10.2026): Kappe und Strähnengruppen aus einer Kugel als Kopf und einer Kugelhülle als Hülle des Fotohaars — LongRunner, weil allein der Bau der rund 20.000 Strähnen über der
1-s-Schwelle liegt. Keine Datenbank; die Bilder der Kappe liegen in einem Ordner unter `ProjektTemp/` und werden danach gelöscht.

Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `Herrenhaar._bis_zur_linie` `drin` auf immer True setzen → Fall 3 rot (Strähnen reichen über die Haarlinie); in `Herrenhaar._strahlen` das `np.minimum(radius, … huelle …)` streichen → Fall 2 rot.
"""

import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.haarklemme import Haarklemme
from core.dienste.herrenhaar import Herrenhaar

MITTE = np.array([0.0, 1.6, 0.0])
RADIUS, HUELLE = 0.10, 0.115


def _kopf(radius=RADIUS, n_az=48, n_el=24):
    """Eine Kugel um MITTE ohne Pole als Kopf: (Punkte, Dreiecke, Haut)."""
    el = np.radians(np.linspace(-80.0, 80.0, n_el))
    az = np.radians(np.linspace(0.0, 360.0, n_az, endpoint=False))
    punkte = np.array([[radius * np.cos(e) * np.sin(a), radius * np.sin(e), radius * np.cos(e) * np.cos(a)] for e in el for a in az]) + MITTE
    dreiecke = []
    for i in range(n_el - 1):
        for j in range(n_az):
            a, b, c, e = i * n_az + j, i * n_az + (j + 1) % n_az, (i + 1) * n_az + j, (i + 1) * n_az + (j + 1) % n_az
            dreiecke += [[a, b, c], [b, e, c]]
    haut = {'knochen': ['head'], 'index': np.zeros(len(punkte) * 4, dtype=np.int64), 'gewicht': np.tile([1.0, 0.0, 0.0, 0.0], len(punkte))}
    return punkte, np.array(dreiecke, dtype=np.int64), haut


def _karte(huelle=HUELLE):
    """Hülle des Fotohaars rundum — nur das Gesicht (Azimut bis 60° von vorn, unter 42° Höhe) hat kein Netzhaar."""
    karte = np.full((36, 72), huelle)
    el = ((np.arange(36) + 0.5) * 5.0 - 90.0)[:, None]
    az = (np.arange(72) + 0.5) * 5.0
    karte[(np.minimum(az, 360.0 - az)[None, :] <= 60.0) & (el < 42.0)] = np.nan
    return karte


def _bauen(ordner, klemme):
    punkte, dreiecke, haut = _kopf()
    ablage = SimpleNamespace(arbeit=lambda name='': ordner / name)
    with mock.patch.object(Haarklemme, 'fuer', return_value=klemme):
        return Herrenhaar(ablage, {'punkte': punkte, 'dreiecke': dreiecke, 'haut': haut}).teile([0.4, 0.4, 0.4])


class DasHerrenhaarAufDemKunstkopf(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ordner = Path(tempfile.mkdtemp(prefix='herrenhaar_', dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')))
        cls.teile = _bauen(cls.ordner, Haarklemme(_karte(), MITTE))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.ordner, ignore_errors=True)
        super().tearDownClass()

    def straehnen(self):
        return [t for t in self.teile if t['sorte'].startswith(Herrenhaar.SORTE + '_')]

    def test_1_die_kappe_liegt_darunter_und_die_straehnen_kommen_in_gruppen_mit_haut_je_punkt(self):
        self.assertIsNotNone(self.teile)
        self.assertEqual(self.teile[0]['sorte'], 'haarkappe')
        gruppen = self.straehnen()
        self.assertTrue(1 <= len(gruppen) <= len(Herrenhaar.GRUPPEN))
        k = Herrenhaar.PUNKTE
        for t in gruppen:
            self.assertEqual(t['art'], 'haar')
            self.assertEqual(len(t['dreiecke']) % (6 * (k - 1)), 0)                                      # sechs Dreiecke je Segment einer dreiseitigen Röhre
            self.assertEqual(len(t['punkte']) % (3 * k), 0)
            self.assertEqual(len(t['punkte']) // (3 * k), len(t['dreiecke']) // (6 * (k - 1)))             # gleich viele Strähnen nach Punkten und nach Dreiecken
            self.assertEqual(len(t['haut']['index']), len(t['punkte']))                                   # Haut und Gewichte je Punkt (für den Tanz)
            self.assertLess(int(np.asarray(t['dreiecke']).max()), len(t['punkte']))

    def test_2_die_straehnen_liegen_ueber_der_haut_und_nicht_ueber_der_huelle_des_fotohaars(self):
        for t in self.straehnen():
            r = np.linalg.norm(np.asarray(t['punkte']) - MITTE, axis=1)
            self.assertGreater(float(r.min()), RADIUS - 0.002)                                            # nirgends in der Haut (Röhrenradius < 1 mm)
            self.assertLess(float(r.max()), HUELLE + Herrenhaar.UEBER_HUELLE_M + 0.002)                   # höchstens `UEBER_HUELLE_M` über der Hülle

    def test_3_gesicht_und_nacken_bleiben_frei(self):
        for t in self.straehnen():
            v = np.asarray(t['punkte']) - MITTE
            el = np.degrees(np.arcsin(v[:, 1] / np.linalg.norm(v, axis=1)))
            von_vorn = np.abs(np.degrees(np.arctan2(v[:, 0], v[:, 2])))
            self.assertGreater(float(el[von_vorn < 40.0].min()), 30.0)                                    # Gesicht und Stirn: das Netz hat dort kein Haar (Grenze bei 42°)
            self.assertGreater(float(el.min()), -44.0)                                                    # Nacken: das Haar endet bei −38° (die Linie ist um bis zu 2,5° unregelmäßig, `Herrenhaar.LINIE_GRAD`)

    def test_4_die_gruppen_sind_von_dunkel_nach_hell_getoent_die_kappe_ist_dunkler_als_ihr_mittel(self):
        hell = [float(np.mean(t['farbe'])) for t in self.straehnen()]
        self.assertEqual(hell, sorted(hell))
        kappe = self.teile[0]
        self.assertTrue(kappe['textur'][0]['albedo'])                                                      # die Kappe trägt ihre Farbe im Bild
        self.assertLess(Herrenhaar.KAPPE_ANTEIL, 1.0)

    def test_5_zweimal_gebaut_gibt_dasselbe_haar(self):
        nochmal = _bauen(self.ordner, Haarklemme(_karte(), MITTE))
        self.assertEqual([len(t['dreiecke']) for t in nochmal], [len(t['dreiecke']) for t in self.teile])   # feste Saat (`Herrenhaar.SAMEN`)
        np.testing.assert_array_equal(np.asarray(nochmal[1]['punkte']), np.asarray(self.teile[1]['punkte']))

    def test_6_ohne_huelle_des_fotohaars_kein_haar(self):
        self.assertIsNone(_bauen(self.ordner, None))
