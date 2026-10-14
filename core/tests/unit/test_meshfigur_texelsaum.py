# -*- coding: utf-8 -*-
"""Mesh to 3D: der Schatten am Rand von Armband und Uhr in der Armkachel (14.10.2026, Edgar4: dunkelbraune Splitter am Handgelenk).

    SaumTest    `Meshfigurtexelsaum.schatten` an einer Kunstkachel: ein Schatten neben einer Fremdfläche geht, ein dunkles Härchen daneben und ein dunkler Fleck weit weg bleiben, `PX` 0 schaltet ab
    GrundTest   `Meshfigurtexelsaum.grund`: die Füllung nimmt den Grund der Haut, nicht das Mittel mit dem eingebackenen Schatten (die dunklen Scherben der Füllung am Handrücken)
    DrahtTest   Quelltext: die Texelprüfung ruft die Regel nur für die Armkachel

Sabotage (`ProjektTemp/_wegwerf/mesh3d/texelsaum_sabotage.py`, beide rot): `FLECK_PX` 0 → das Härchen wird mitgenommen (`test_ein_haerchen_bleibt`); in `schatten` `& nah` aus der Bedingung streichen → `test_ein_dunkler_fleck_weit_weg_bleibt`.
Gemessen (Edgar4, Kachel 1004, `ProjektTemp/_wegwerf/mesh3d/schatten_alle.py`): 17.292 von 1.911.870 Hauttexel (0,9 %); die anderen Kacheln 0. Im Bild (`hand_schatten_f3.png`): der dunkle Streifen und die Splitter am Handgelenk sind weg.
"""

from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.meshfigurtexelpruefung import Meshfigurtexelpruefung
from core.dienste.meshfigurtexelsaum import Meshfigurtexelsaum

WEB = Path(settings.BASE_DIR)
S = 128
HAUT = np.array([200.0, 140.0, 110.0])


class SaumTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.vorher = (Meshfigurtexelsaum.PX, Meshfigurtexelsaum.FAKTOR, Meshfigurtexelsaum.GROESSE_PX, Meshfigurtexelsaum.FLECK_PX)
        Meshfigurtexelsaum.PX, Meshfigurtexelsaum.FAKTOR, Meshfigurtexelsaum.GROESSE_PX, Meshfigurtexelsaum.FLECK_PX = 12, 0.85, 1, 2
        self.addCleanup(self._zurueck)
        bild = np.tile(HAUT, (S, S, 1))
        self.fremd_bild = np.zeros((S, S), dtype=bool)
        self.fremd_bild[40:60, 10:30] = True                       # das Armband
        bild[self.fremd_bild] = (40.0, 60.0, 140.0)
        self.schatten = np.zeros((S, S), dtype=bool)
        self.schatten[40:60, 30:38] = True                         # 8 Pixel dahinter: der eingebackene Schatten
        self.haerchen = np.zeros((S, S), dtype=bool)
        self.haerchen[36, 5:40] = True                             # ein Pixel hoch, vier Pixel über dem Band
        self.fern = np.zeros((S, S), dtype=bool)
        self.fern[100:110, 100:110] = True                         # weit weg vom Band
        for maske, faktor in ((self.schatten, 0.7), (self.haerchen, 0.6), (self.fern, 0.7)):
            bild[maske] = HAUT * faktor
        self.bild = bild
        self.drin = np.nonzero(np.ones((S, S), dtype=bool))
        self.farbe = bild[self.drin]
        self.hell = self.farbe @ np.array([0.299, 0.587, 0.114])
        self.fremd = self.fremd_bild[self.drin]
        self.gut = ~self.fremd

    def _zurueck(self):
        Meshfigurtexelsaum.PX, Meshfigurtexelsaum.FAKTOR, Meshfigurtexelsaum.GROESSE_PX, Meshfigurtexelsaum.FLECK_PX = self.vorher

    def _schatten(self):
        saum = Meshfigurtexelsaum(S, Meshfigurtexelpruefung.glatt)
        aus = saum.schatten(self.drin, self.fremd, self.hell, self.farbe, self.gut)
        bild = np.zeros((S, S), dtype=bool)
        bild[self.drin] = aus
        return bild

    def test_der_schatten_neben_dem_band_geht(self):
        bild = self._schatten()
        self.assertGreater(bild[self.schatten].mean(), 0.95, 'der Schatten wird verworfen')
        self.assertFalse(bild[self.fremd_bild].any(), 'das Band selbst ist keine gute Haut und steht nicht in der Antwort')

    def test_ein_haerchen_bleibt(self):
        bild = self._schatten()
        self.assertLess(bild[self.haerchen].mean(), 0.1, 'ein Pixel breit: kein Fleck')

    def test_ein_dunkler_fleck_weit_weg_bleibt(self):
        self.assertFalse(self._schatten()[self.fern].any(), 'außerhalb von PX gilt die Regel nicht')

    def test_px_null_schaltet_ab(self):
        Meshfigurtexelsaum.PX = 0
        self.assertFalse(self._schatten().any())

    def test_ohne_fremdflaeche_gibt_es_nichts(self):
        self.fremd = np.zeros_like(self.fremd)
        self.assertFalse(self._schatten().any())


class GrundTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        bild = np.tile(HAUT, (S, S, 1))
        dunkel = np.zeros((S, S), dtype=bool)
        dunkel[50:78, 40:54] = True                                 # ein eingebackener Schatten direkt neben dem Loch
        bild[dunkel] = HAUT * 0.72
        loch = np.zeros((S, S), dtype=bool)
        loch[56:72, 54:70] = True                                   # nie getroffen: wird gefüllt
        self.drin = np.nonzero(np.ones((S, S), dtype=bool))
        self.farbe = bild[self.drin]
        self.gut = ~loch[self.drin]
        self.loch = loch[self.drin]
        saum = Meshfigurtexelsaum(S, Meshfigurtexelpruefung.glatt)
        self.saum = saum
        # die Füllung wie in der Texelprüfung: Mittel der guten Nachbarn, fein, wo genug da ist
        voll = np.zeros((S, S, 3))
        voll[self.drin] = self.farbe
        maske = np.zeros((S, S), dtype=bool)
        maske[self.drin] = self.gut
        self.mittel = saum._feld(voll, maske)[self.drin]
        self.hell = np.array([0.299, 0.587, 0.114])

    def test_der_schatten_neben_dem_loch_dunkelt_die_fuellung_nicht_mehr(self):
        fuellung = self.mittel.copy()
        geaendert = self.saum.grund(self.drin, self.gut, self.farbe, fuellung, self.loch)
        self.assertEqual(geaendert, int(self.loch.sum()), 'nur die zu füllenden Texel')
        np.testing.assert_array_equal(fuellung[self.gut], self.mittel[self.gut], 'gute Texel behalten ihre Farbe')
        vorher, nachher = (self.mittel[self.loch] @ self.hell).mean(), (fuellung[self.loch] @ self.hell).mean()
        self.assertLess(vorher, HAUT @ self.hell - 3.0, 'das Mittel der Nachbarn ist dunkler als die Haut (Ausgangslage der Probe)')
        self.assertGreater(nachher, vorher + 3.0, 'der Grund der Haut ist heller als das Mittel mit dem Schatten')
        self.assertGreater(nachher, HAUT @ self.hell - 4.0, 'und liegt nahe an der Haut daneben')

    def test_ohne_grund_bleibt_alles_wie_es_war(self):
        Meshfigurtexelsaum.FUELL_GRUND = False
        self.addCleanup(setattr, Meshfigurtexelsaum, 'FUELL_GRUND', True)
        fuellung = self.mittel.copy()
        self.assertEqual(self.saum.grund(self.drin, self.gut, self.farbe, fuellung), 0)
        np.testing.assert_array_equal(fuellung, self.mittel)


class DrahtTest(SimpleTestCase):
    databases = set()

    def test_die_texelpruefung_ruft_die_regel_nur_fuer_die_armkachel(self):
        text = WEB.joinpath('core', 'dienste', 'meshfigurtexelpruefung.py').read_text(encoding='utf-8')
        self.assertIn('saum=kachel == Meshfigurtexelsaum.KACHEL', text)
        self.assertIn('Meshfigurtexelsaum(self.abtastung.seite, self.glatt).schatten(', text)
        self.assertIn('Meshfigurtexelsaum(self.abtastung.seite, self.glatt).grund(drin, gut, farbe, fuellung, ziel) if saum else 0', text)
        self.assertEqual(Meshfigurtexelsaum.KACHEL, 1004, 'UDIM 1004 = Arme und Hände von Genesis 9')
