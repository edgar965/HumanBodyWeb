# -*- coding: utf-8 -*-
"""Gebackene Haut: Saum um die Fehlstellen schließen und die Form aus der Normalenkarte nehmen (Edgar, 08.10.2026).

Edgar: „die scham ist völlig anders als in Blender, überprüfe, Textur und form kaputt — vor allem in der hohen Auflösung". Gesehen
an Kachel 1002 (8K): dünne dunkle Konturen um die Inseln der Scham (der Rand zwischen Bild und Fehlstelle ist nicht rein schwarz und
fiel durch die Schwelle von 6) und großflächig gekippte Normalen, wo die Figur vom Original abweicht (die Karte trug die FORM).

1. `Blendimportrand.saum` nennt genau die Pixel neben einer Fehlstelle, ohne die Fehlstelle selbst.
2. `schliessen` setzt die Saumpixel auf das Mittel der gültigen Pixel daneben, lässt die Fehlstelle und die Eingabe unberührt, und
   ohne Fehlstelle bleibt alles, wie es ist.
3. `feindetail` entfernt ein großflächiges Neigungsfeld fast ganz, behält ein feines Muster fast ganz, hält Fehlstellen flach und
   verändert die Eingabe nicht.

Sabotage-Gegenprobe: in `saum` `& ~leer` streichen → Fall 1 rot; in `schliessen` `kern` nicht um `saum` kleiner machen → Fall 2 rot;
in `feindetail` die Subtraktion `tx - tief(tx)` durch `tx` ersetzen → Fall 4 rot.

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportnormalen import Blendimportnormalen
from core.dienste.blendimportrand import Blendimportrand


def kodiert(tx, ty):
    """Neigung (tan der Kippung in x/y) → Tangentenraum-Karte als uint8 (H, W, 3)."""
    laenge = np.sqrt(tx * tx + ty * ty + 1.0)
    return np.clip(np.rint((np.stack([tx / laenge, ty / laenge, 1.0 / laenge], axis=-1) + 1.0) * 127.5), 0, 255).astype(np.uint8)


def neigung(karte):
    z = np.maximum(karte[..., 2].astype(np.float32) / 127.5 - 1.0, 0.05)
    return (karte[..., 0] / 127.5 - 1.0) / z, (karte[..., 1] / 127.5 - 1.0) / z


class RandTest(SimpleTestCase):
    databases = set()

    def _bild(self):
        farbe = np.zeros((40, 40, 3), dtype=np.uint8)
        farbe[:] = (200, 150, 120)
        leer = np.zeros((40, 40), dtype=bool)
        leer[15:25, 15:25] = True
        farbe[leer] = 0
        # Der Saum: dunkle Mischpixel um die Fehlstelle (nicht rein schwarz, sonst wären sie selbst Fehlstelle).
        saum = Blendimportrand.saum(leer)
        farbe[saum] = (40, 30, 25)
        return farbe, leer

    def test_1_saum_sind_die_pixel_neben_der_fehlstelle(self):
        _farbe, leer = self._bild()
        saum = Blendimportrand.saum(leer, 2)
        self.assertFalse((saum & leer).any(), 'die Fehlstelle selbst gehört nicht dazu')
        # Erwartet: alle Pixel mit Manhattan-Abstand 1 oder 2 zum Block (binary_dilation mit Kreuz, 2 Durchgänge).
        zeile, spalte = np.mgrid[0:40, 0:40]
        dx = np.maximum(np.maximum(15 - spalte, spalte - 24), 0)
        dy = np.maximum(np.maximum(15 - zeile, zeile - 24), 0)
        erwartet = ((dx + dy) >= 1) & ((dx + dy) <= 2)
        self.assertTrue(np.array_equal(saum, erwartet), 'genau die Pixel im Abstand 1–2')
        self.assertTrue(saum[14, 20] and saum[13, 20] and not saum[12, 20], 'zwei Pixel breit')
        self.assertFalse(Blendimportrand.saum(np.zeros((8, 8), dtype=bool)).any())

    def test_2_schliessen_mittelt_den_saum_aus_den_gueltigen_pixeln(self):
        farbe, leer = self._bild()
        vorher = farbe.copy()
        neu, saum = Blendimportrand.schliessen(farbe, leer)
        self.assertTrue(np.array_equal(farbe, vorher), 'die Eingabe bleibt unverändert')
        self.assertTrue(np.array_equal(neu[leer], farbe[leer]), 'die Fehlstelle füllt die Kachel von „Mesh to 3D", nicht dieser Saum')
        mittel = neu[saum].astype(float).mean(axis=0)
        self.assertLess(abs(mittel - np.array([200, 150, 120])).max(), 4.0, 'Saum = Farbe der gültigen Pixel daneben')
        ohne, leer_saum = Blendimportrand.schliessen(farbe, np.zeros((40, 40), dtype=bool))
        self.assertFalse(leer_saum.any())
        self.assertTrue(np.array_equal(ohne, farbe))


class FeindetailTest(SimpleTestCase):
    databases = set()

    def _gitter(self):
        y, x = np.mgrid[0:64, 0:64].astype(np.float32)
        return x, y

    def test_3_ein_grossflaechiges_neigungsfeld_faellt_weg(self):
        x, y = self._gitter()
        karte = kodiert(0.5 * (x / 63.0 - 0.5) * 2.0, 0.4 * (y / 63.0 - 0.5) * 2.0)    # eine Beule über die ganze Kachel
        vorher = np.abs(np.stack(neigung(karte))).mean()
        nachher = np.abs(np.stack(neigung(Blendimportnormalen.feindetail(karte, None, 8.0)))).mean()
        self.assertLess(nachher, 0.2 * vorher, 'das Großflächige ist bis auf einen Rest weg')

    def test_4_ein_feines_muster_bleibt(self):
        x, y = self._gitter()
        karte = kodiert(0.2 * np.where((x + y) % 4 < 2, 1.0, -1.0), 0.0 * x)         # Schachbrett aus 2-Pixel-Feldern
        vorher = np.abs(neigung(karte)[0]).mean()
        nachher = np.abs(neigung(Blendimportnormalen.feindetail(karte, None, 8.0))[0]).mean()
        self.assertGreater(nachher, 0.7 * vorher, 'Poren und Stoppeln bleiben')

    def test_5_fehlstellen_bleiben_flach_und_die_eingabe_unveraendert(self):
        x, y = self._gitter()
        karte = kodiert(0.3 * np.sin(x / 5.0), 0.3 * np.cos(y / 5.0))
        leer = np.zeros((64, 64), dtype=bool)
        leer[10:30, 10:30] = True
        vorher = karte.copy()
        neu = Blendimportnormalen.feindetail(karte, leer, 8.0)
        self.assertTrue(np.array_equal(karte, vorher))
        self.assertTrue((neu[leer] == np.array(Blendimportnormalen.FLACH)).all(), 'Fehlstellen: flache Normale')
        self.assertEqual(neu.shape, karte.shape)
        self.assertEqual(neu.dtype, karte.dtype)
