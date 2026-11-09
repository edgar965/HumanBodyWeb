"""Fotoaufrichtung: Schieflage aus Kopf und Hüfte, Vierteldrehungen, Zuschnitt — mit Attrappe, ohne Karte."""
import sys
import unittest
from pathlib import Path

import numpy as np
from django.conf import settings
from PIL import Image

sys.path.insert(0, str(Path(settings.TOOLS_ROOT) / 'pshuman_port14'))
from fotoaufrichtung import Fotoaufrichtung  # noqa: E402


class Wert:
    def __init__(self, a):
        self.a = a

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self.a


class Punkte:
    """Liest Kopf (rot) und Hüfte (grün) aus dem Bild; `werte` je Aufruf, Vorgabe sicher."""
    NAMEN = sorted(set(Fotoaufrichtung.KOPF + Fotoaufrichtung.HUEFTE + Fotoaufrichtung.KOERPER))

    def __init__(self, werte=None):
        self.werte = list(werte or [])
        self.aufrufe = 0

    @classmethod
    def index(cls, name):
        return cls.NAMEN.index(name)

    @staticmethod
    def _ort(rgb, kanal):
        ys, xs = np.nonzero(rgb[..., kanal] > 200)
        return np.array([xs.mean(), ys.mean()])

    def punkte(self, rgb, _kasten):
        self.aufrufe += 1
        xy = np.zeros((len(self.NAMEN), 2))
        for name in self.NAMEN:
            xy[self.index(name)] = self._ort(rgb, 0 if name in Fotoaufrichtung.KOPF else 1)
        wert = np.full(len(self.NAMEN), self.werte.pop(0) if self.werte else 0.9)
        return Wert(xy), Wert(wert)


def bild(kopf, huefte, seite=200):
    rgb = np.zeros((seite, seite, 3), np.uint8)
    for (x, y), kanal in ((kopf, 0), (huefte, 1)):
        rgb[y - 3:y + 4, x - 3:x + 4, kanal] = 255
    return rgb


class Lage(unittest.TestCase):
    def setUp(self):
        self.maske = np.ones((200, 200), bool)

    def test_aufrecht_braucht_einen_durchgang_und_kein_drehen(self):
        vp = Punkte()
        e = Fotoaufrichtung.lage(vp, bild((100, 40), (100, 120)), self.maske)
        self.assertEqual(vp.aufrufe, 1)
        self.assertAlmostEqual(e['grad'], 0, places=3)

    def test_schraeg_unter_der_grenze_zaehlt_als_aufrecht(self):
        vp = Punkte()
        e = Fotoaufrichtung.lage(vp, bild((130, 40), (100, 120)), self.maske)
        self.assertEqual(vp.aufrufe, 1)
        self.assertLess(abs(e['grad']), Fotoaufrichtung.GRENZE_GRAD)

    def test_liegend_kopf_links_gibt_minus_90_in_jeder_ansicht(self):
        for k in range(4):
            vp = Punkte([0.6, 0.6, 0.6, 0.6])
            vp.werte[k] = 0.9
            e = Fotoaufrichtung.lage(vp, bild((40, 100), (120, 100)), self.maske)
            self.assertEqual(vp.aufrufe, 4)
            self.assertEqual(e['viertel'], k)
            self.assertAlmostEqual(e['grad'], -90, places=3)

    def test_kopfueber_gibt_180(self):
        e = Fotoaufrichtung.lage(Punkte(), bild((100, 160), (100, 80)), self.maske)
        self.assertAlmostEqual(abs(e['grad']), 180, places=3)

    def test_ohne_sichere_lage_kein_winkel(self):
        vp = Punkte([0.4, 0.4, 0.4, 0.4])
        self.assertIsNone(Fotoaufrichtung.lage(vp, bild((40, 100), (120, 100)), self.maske)['grad'])


class Drehen(unittest.TestCase):
    def test_dreht_gegen_den_uhrzeigersinn_und_schneidet_auf_die_maske(self):
        foto = Image.new('RGB', (300, 200), 'black')
        m = np.zeros((200, 300), np.uint8)
        m[90:110, 80:220] = 255
        neu, neu_maske = Fotoaufrichtung.drehen(foto, Image.fromarray(m), 90)
        rand = Fotoaufrichtung.RAND_PX
        self.assertEqual(neu.size, neu_maske.size)
        self.assertAlmostEqual(neu.width, 20 + 2 * rand, delta=2)
        self.assertAlmostEqual(neu.height, 140 + 2 * rand, delta=2)

    def test_rand_bleibt_im_bild(self):
        m = np.full((50, 80), 255, np.uint8)
        neu, _ = Fotoaufrichtung.drehen(Image.new('RGB', (80, 50)), Image.fromarray(m), 0)
        self.assertEqual(neu.size, (80, 50))
