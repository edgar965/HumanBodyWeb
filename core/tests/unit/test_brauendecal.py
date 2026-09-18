# -*- coding: utf-8 -*-
"""Die gezeichnete Augenbraue: Retusche, Bogen, Zeichner, Endpunkte.

WARUM (Edgar, 16.09.2026: „doppelte Augenbrauen" → Konzept A: „meinetwegen
kann ich die auch aus der Textur nehmen, aber dann sollen die auch anpassbar
sein!"): Die Braue ist eine Zeichnung im Brauenfenster der Haut. Hier ohne
die echten Texturen (Kunstbilder, Kunstbogen), unter einer Sekunde:

1. `Brauenretusche.maske` findet den dunklen Bogen, der die Brauenpunkte
   berührt — nicht den dunklen Fleck weiter weg (Augenwinkel); `fuellen`
   ersetzt ihn durch die Umgebung.
2. `Brauenbogen.mittellinie` liefert je Spalte die Mitte, geglättet.
3. `Brauendecal`: die Regler werden geklemmt, die Kennung folgt den Reglern,
   das Bild ist deterministisch, beide Brauen liegen im Fenster, mehr Dichte
   heißt mehr gedeckte Pixel, die Farbe kommt an, Höhe verschiebt den Bogen.
4. Endpunkte: `fenster/` liefert Fenster und Vorgaben, `bild/` ein PNG mit
   Cache-Header — beides mit Kunstbogen, ohne Texturdateien.

Sabotage-Gegenprobe: in `Brauendecal.haare` `regler['dichte']` durch 1
ersetzen → Fall 3 rot (Dichte 2 deckt nicht mehr Pixel).
"""

import io
from unittest import mock

import numpy as np
from django.test import Client, SimpleTestCase
from PIL import Image

from core.dienste.brauenbogen import Brauenbogen
from core.dienste.brauendecal import Brauendecal
from core.dienste.brauenretusche import Brauenretusche
from core.tests.unit._pruefablage import Pruefablage


class BrauenretuscheTest(SimpleTestCase):
    def test_maske_findet_den_bogen_am_kern_nicht_den_fleck_daneben(self):
        bild = np.full((200, 300, 3), 200, dtype=np.uint8)
        bild[100:106, 80:180] = 40  # der gemalte Bogen
        bild[150:156, 100:120] = 40  # Fleck weiter weg
        uvs = np.array([[u / 299, 1 - 103 / 199] for u in range(90, 170, 10)])
        zone = Brauenretusche.zone(uvs, bild.shape[:2])
        kern = Brauenretusche.kern(uvs, bild.shape[:2], Brauenretusche.KERN_PX)
        maske = Brauenretusche.maske(bild, zone, kern)
        self.assertTrue(maske[103, 130])
        self.assertFalse(maske[153, 110], 'der Fleck berührt die Brauenpunkte nicht')
        fertig = Brauenretusche.fuellen(bild, maske)
        self.assertGreater(int(fertig[103, 130].min()), 180, 'Bogen durch Haut ersetzt')
        self.assertEqual(int(fertig[153, 110, 0]), 40, 'Fleck bleibt')


class BrauenbogenTest(SimpleTestCase):
    def test_mittellinie_je_spalte_geglaettet(self):
        komponente = np.zeros((50, 40), dtype=bool)
        for x in range(10, 30):
            komponente[20 + (x % 2) : 26 + (x % 2), x] = True
        linie = Brauenbogen.mittellinie(komponente)
        self.assertEqual(linie.shape, (20, 2))
        self.assertEqual(list(linie[:, 0]), list(range(10, 30)))
        self.assertLess(float(np.abs(np.diff(linie[4:-4, 1])).max()), 0.2, 'geglättet')


class BrauendecalTest(SimpleTestCase):
    def setUp(self):
        ablage = Pruefablage.ordner('brauen_')
        self.ordner = ablage.__enter__()
        self.addCleanup(ablage.__exit__, None, None, None)
        self.laden = mock.patch.object(Brauenbogen, 'laden', return_value=BrauendecalTest.kunstbogen())
        self.laden.start()
        self.addCleanup(self.laden.stop)
        self.ordnerpatch = mock.patch.object(Brauendecal, 'ORDNER', Brauenbogen.ORDNER.__class__(self.ordner))
        self.ordnerpatch.start()
        self.addCleanup(self.ordnerpatch.stop)
        # Ein Viertel der Breite reicht dem Test und hält das Modul unter 1 s.
        self.breite = mock.patch.object(Brauendecal, 'BREITE', 512)
        self.breite.start()
        self.addCleanup(self.breite.stop)

    def test_regler_geklemmt_und_kennung_folgt(self):
        r = Brauendecal.regler({'dichte': '9', 'lage': -99, 'farbe': '#ABCDEF', 'quatsch': 1})
        self.assertEqual((r['dichte'], r['lage'], r['farbe']), (3.0, -20.0, '#abcdef'))
        self.assertEqual(Brauendecal.regler({'farbe': 'rot'})['farbe'], '#3a2a1e')
        self.assertNotEqual(
            Brauendecal.kennung('female', r), Brauendecal.kennung('female', Brauendecal.regler({}))
        )
        self.assertNotEqual(Brauendecal.kennung('female', r), Brauendecal.kennung('male', r))

    def _alpha(self, **regler):
        bild = Image.open(Brauendecal.bild('female', Brauendecal.regler(regler)))
        return np.asarray(bild)[..., 3], bild

    def test_beide_brauen_im_fenster_dichte_farbe_hoehe(self):
        alpha, bild = self._alpha()
        self.assertEqual(bild.size[0], Brauendecal.BREITE)
        links = int(alpha[:, : bild.size[0] // 2].sum())
        rechts = int(alpha[:, bild.size[0] // 2 :].sum())
        self.assertGreater(links, 0)
        self.assertGreater(rechts, 0)
        self.assertLess(abs(links - rechts) / links, 0.35, 'beide Seiten ähnlich')
        dicht, _ = self._alpha(dichte=2.0)
        # Gemessen bei 512 px: 1,55-fache Deckung (Pixelsumme), 1,18-fach Fläche.
        self.assertGreater(int(dicht.sum()), int(alpha.sum()) * 1.3)
        rot = np.asarray(self._alpha(farbe='#ff0000')[1])
        gedeckt = rot[..., 3] > 200
        self.assertGreater(int(rot[gedeckt, 0].mean()), 200)
        self.assertLess(int(rot[gedeckt, 1].mean()), 60)
        hoch, _ = self._alpha(lage=10.0)
        self.assertLess(
            np.nonzero(hoch)[0].mean(), np.nonzero(alpha)[0].mean() - 6, '10 mm höher = kleinere Bildzeile'
        )
        wieder, _ = self._alpha()
        self.assertTrue(np.array_equal(alpha, wieder), 'deterministisch')

    def test_endpunkte_liefern_fenster_und_png_mit_cacheheader(self):
        client = Client(HTTP_HOST='127.0.0.1')
        fenster = client.get('/api/character/brauen/fenster/?geschlecht=female').json()
        self.assertEqual(fenster['fenster'], [0.38, 0.14, 0.62, 0.28])
        self.assertEqual(fenster['vorgabe']['dichte'], 1.0)
        self.assertIn('grenzen', fenster)
        antwort = client.get('/api/character/brauen/bild/?geschlecht=female&dichte=1.2')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort['Content-Type'], 'image/png')
        self.assertIn('max-age', antwort['Cache-Control'])
        bild = Image.open(io.BytesIO(b''.join(antwort.streaming_content)))
        self.assertEqual(bild.mode, 'RGBA')

    @staticmethod
    def kunstbogen():
        t = np.linspace(0, 1, 30)
        links = [[0.48 - 0.06 * x, 0.20 + 0.02 * np.sin(np.pi * x)] for x in t]
        rechts = [[0.52 + 0.06 * x, 0.20 + 0.02 * np.sin(np.pi * x)] for x in t]
        return {
            'fassung': Brauenbogen.FASSUNG,
            'fenster': [0.38, 0.14, 0.62, 0.28],
            'mm_je_uv': 800.0,
            'form': [2048, 2048],
            'links': [[float(u), float(v)] for u, v in links],
            'rechts': [[float(u), float(v)] for u, v in rechts],
        }
