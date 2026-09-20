# -*- coding: utf-8 -*-
"""Nur die Hauptbilder bauen den Körper (20.09.2026) — Edgar: „Nimm die Proportionen /
Schätzungen aus den ersten 2 Hauptbildern … ab sofort den Gesamtkörper nur anhand der
Hauptbilder aus der Combo bauen." Ohne Datenbank, ohne Netz:

1. Ohne Markierung: die ersten zwei Körper-Kandidaten (vorn/hinten/Seite, Zeilenreihenfolge
   über `reihe`) tragen alles, die übrigen Körperbilder 0; Summe 1.
2. Ohne Hauptbild zählen alle gleich; dreiviertel ist kein Hauptbild.
3. Markiert (`hauptbild`, zweite Box): nur die markierten zählen, auch wenn sie in der
   Tabelle hinten stehen; die unmarkierte erste Zeile bekommt 0.
4. `mittel` mischt Zeilen mit diesen Gewichten (Sabotage: gleich gewichtet käme etwas anderes).
5. `kopf`: Kopf-Hauptbild vorn vor Seite vor hinten; markiert schlägt Reihe; ohne Kopfbild None.
6. `Bildmodellmischung` mit `mischung: haupt` schreibt `gewichte` und nimmt nur die Hauptbilder.
"""

from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from core.dienste.bildmodellhauptgewicht import Bildmodellhauptgewicht
from core.dienste.bildmodellmischung import Bildmodellmischung


def _job(bilder):
    return SimpleNamespace(bilder=bilder, optionen={}, ergebnis={})


def _bild(datei, kategorie, ansicht, reihe=None, betas=None):
    b = {'datei': datei, 'kategorie': kategorie, 'ansicht': ansicht, 'gewicht': 1.0}
    if reihe:
        b['reihe'] = reihe
    if betas is not None:
        b['schaetzung'] = {'betas': betas, 'backend': 'gvhmr'}
    return b


class GewichteTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.bilder = [
            _bild('vorn.jpg', 'koerper', 'vorne', reihe=1),
            _bild('hinten.jpg', 'koerper', 'hinten', reihe=2),
            _bild('pose.jpg', 'koerper', 'vorne', reihe=3),
            _bild('dreiviertel.jpg', 'koerper', 'dreiviertel'),
            _bild('kopf_seite.jpg', 'kopf', 'seite'),
            _bild('kopf_vorn.jpg', 'kopf', 'vorne'),
        ]
        self.hg = Bildmodellhauptgewicht(_job(self.bilder))

    def test_nur_die_ersten_zwei_ohne_markierung(self):
        koerper = [b for b in self.bilder if b['kategorie'] == 'koerper']
        g = self.hg.gewichte(koerper)
        self.assertAlmostEqual(g['vorn.jpg'], 0.5)
        self.assertAlmostEqual(g['hinten.jpg'], 0.5)
        self.assertEqual((g['pose.jpg'], g['dreiviertel.jpg']), (0.0, 0.0))
        self.assertAlmostEqual(sum(g.values()), 1.0)

    def test_markierte_hauptbilder_schlagen_die_reihe(self):
        koerper = [b for b in self.bilder if b['kategorie'] == 'koerper']
        self.bilder[2]['hauptbild'] = True   # pose.jpg, Zeile 3
        g = self.hg.gewichte(koerper)
        self.assertEqual(g, {'vorn.jpg': 0.0, 'hinten.jpg': 0.0, 'pose.jpg': 1.0, 'dreiviertel.jpg': 0.0})
        self.bilder[0]['hauptbild'] = True
        g = self.hg.gewichte(koerper)
        self.assertEqual((g['vorn.jpg'], g['pose.jpg'], g['hinten.jpg']), (0.5, 0.5, 0.0))
        self.assertEqual([b['datei'] for b in self.hg.hauptbilder()], ['vorn.jpg', 'pose.jpg'])

    def test_nur_hauptbilder_oder_keines(self):
        g = self.hg.gewichte(self.bilder[:2])
        self.assertEqual(set(g.values()), {0.5})
        g = self.hg.gewichte([self.bilder[3]])  # dreiviertel allein: kein Hauptbild
        self.assertEqual(g, {'dreiviertel.jpg': 1.0})

    def test_mittel_gewichtet(self):
        koerper = self.bilder[:3]
        werte = [[0.0], [6.0], [3.0]]
        self.assertAlmostEqual(float(self.hg.mittel(koerper, werte)[0]), 3.0)  # ½·0 + ½·6, pose zählt 0
        self.bilder[2]['hauptbild'] = True
        self.assertAlmostEqual(float(self.hg.mittel(koerper, werte)[0]), 3.0)  # nur pose: 3
        self.bilder[2]['hauptbild'] = False
        self.bilder[1]['hauptbild'] = True
        self.assertAlmostEqual(float(self.hg.mittel(koerper, werte)[0]), 6.0)  # nur hinten: 6

    def test_kopf_vorn_vor_seite(self):
        self.assertEqual(self.hg.kopf(self.bilder)['datei'], 'kopf_vorn.jpg')
        self.assertEqual(self.hg.kopf(self.bilder[:5])['datei'], 'kopf_seite.jpg')
        self.assertIsNone(self.hg.kopf(self.bilder[:4]))
        self.bilder[4]['hauptbild'] = True   # Seite markiert: schlägt das unmarkierte vorn
        self.assertEqual(self.hg.kopf(self.bilder)['datei'], 'kopf_seite.jpg')


class MischungTest(SimpleTestCase):
    databases = set()

    def test_haupt_ist_vorgabe_und_gewichtet(self):
        bilder = [
            _bild('vorn.jpg', 'koerper', 'vorne', reihe=1, betas=[1.0] * 10),
            _bild('hinten.jpg', 'koerper', 'hinten', reihe=2, betas=[1.0] * 10),
            _bild('pose.jpg', 'koerper', 'vorne', reihe=3, betas=[4.0] * 10),
        ]
        aus = Bildmodellmischung({}, _job(bilder)).mischen(bilder, [])
        self.assertEqual(aus['mischung'], 'haupt')
        self.assertAlmostEqual(aus['betas'][0], 1.0, places=4)  # nur vorn + hinten, pose zählt 0
        self.assertEqual(aus['gewichte']['pose.jpg'], 0.0)
        bilder[2]['hauptbild'] = True
        aus = Bildmodellmischung({}, _job(bilder)).mischen(bilder, [])
        self.assertAlmostEqual(aus['betas'][0], 4.0, places=4)  # markiert: nur pose
        bilder[2]['hauptbild'] = False
        # Median bliebe wählbar — und ergäbe 1,0.
        aus = Bildmodellmischung({'mischung': 'median'}, _job(bilder)).mischen(bilder, [])
        self.assertEqual((aus['mischung'], aus['betas'][0]), ('median', 1.0))
        self.assertIsNone(aus['gewichte'])
        self.assertTrue(np.isfinite(aus['betas']).all())


class KopfwahlTest(SimpleTestCase):
    databases = set()

    def test_nie_die_rueckansicht(self):
        # Damira bekam den FLAME-Kopf aus `09_cr1` (Rücken), weil der Kasten dort am größten war.
        bilder = [
            _bild('ruecken.jpg', 'koerper', 'hinten', reihe=2),
            _bild('vorn.jpg', 'koerper', 'vorne', reihe=1),
            _bild('kopf.jpg', 'kopf', 'vorne'),
        ]
        bilder[0]['gesichtsschaetzung'] = {'flame_vertices_path': 'ruecken_gesicht_flame.npy'}
        bilder[0]['gesicht'] = {'hoehe': 0.9}
        bilder[1]['gesichtsschaetzung'] = {'flame_vertices_path': 'vorn_gesicht_flame.npy'}
        bilder[1]['gesicht'] = {'hoehe': 0.1}
        m = Bildmodellmischung({}, None)
        self.assertEqual(m._kopf(bilder), 'vorn_gesicht_flame.npy')
        # Mit Kopf-Hauptbild und FLAME dort gewinnt das Kopfbild.
        bilder[2]['gesichtsschaetzung'] = {'flame_vertices_path': 'kopf_gesicht_flame.npy'}
        m = Bildmodellmischung({}, SimpleNamespace(bilder=bilder, optionen={}, ergebnis={}, kennung='x'))
        self.assertEqual(m._kopf(bilder), 'kopf_gesicht_flame.npy')
        # Nur die Rückansicht hat ein FLAME: dann keins.
        self.assertIsNone(Bildmodellmischung({}, None)._kopf(bilder[:1]))
