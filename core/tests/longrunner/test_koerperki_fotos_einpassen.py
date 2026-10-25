# -*- coding: utf-8 -*-
"""Das Einpassen eines Kunstkörpers in zwei Ansichten mit `KoerperKI_Fotos.fotoeinpassung.Fotoeinpassung` (24.10.2026, 2d-3d-AI) — im LongRunner, weil 200 Schritte auf der CPU ~6 s brauchen.

WARUM: Edgar, 24.10.2026: „es gibt in mesh3d-ai auch die iterative vorgehensweise zu den Kleidern, Körper … das kannst du für die Bilder auch übernehmen“. Im ersten Lauf an EdgarTrip
(`ProjektTemp/_wegwerf/ai2d3d/nurfotos_einpassen.py`, 24.10.2026 14:26–14:42) wurde Runde 2 abgelehnt (mittlere Deckung 0,724 → 0,646), Stufe B begann trotzdem mit den Kameras der abgelehnten
Runde — `rechnen` hatte sie in die übergebenen Ansichten geschrieben — und endete bei 0,609. Seither ändert `rechnen` die Ansichten nicht und gibt die eingepassten zurück
(`erg['ansichten']`); der Aufrufer übernimmt sie nur mit der Runde.
Wahrheit: Maßstab 1,1 und Verschiebung (3, −2, 4) cm, zwei Fotos (vorn 0°, links 90°), Kamera 100 px/m fest. Start: Maßstab 1, keine Verschiebung. Mit festem Kameramaßstab muss die FORM
die Größe stellen.
"""
import math
import sys
import unittest

import numpy as np
import torch
import torch.nn.functional as F
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.umrissziel import Umrissziel  # noqa: E402
from KoerperKI_Fotos.fotoeinpassung import Fotoeinpassung  # noqa: E402
from KoerperKI_Fotos.posenpunkte import Posenpunkte  # noqa: E402

from ..unit._einpasskoerper import Einpasskoerper  # noqa: E402


class KleinesZiel(Umrissziel):
    """Weniger Haut- und Randpunkte — dieselbe Rechnung, schneller auf der CPU."""

    HAUT_PUNKTE = 400
    RAND_PUNKTE = 400


class DasEinpassen(unittest.TestCase):
    S, T, HW = 100.0, (80.0, 110.0), (220, 160)
    MASSSTAB, VERSCHIEBUNG = 1.1, (0.03, -0.02, 0.04)

    @classmethod
    def maske(cls, x, r, s, t):
        """Bildpunkte der Punkte x gesetzt und um einen Bildpunkt verbreitert."""
        uv = Fotoeinpassung.bild(x, r, s, t).round().long()
        h, w = cls.HW
        m = torch.zeros(cls.HW)
        drin = (uv[:, 0] >= 0) & (uv[:, 0] < w) & (uv[:, 1] >= 0) & (uv[:, 1] < h)
        m[uv[drin, 1], uv[drin, 0]] = 1.0
        return F.max_pool2d(m[None, None], 3, 1, 1)[0, 0] > 0.5

    @classmethod
    def setUpClass(cls):
        cls.dicht = Einpasskoerper(abstand=0.01)
        x, p, _e, _d, _w = cls.dicht.koerper(torch.tensor([cls.MASSSTAB]), torch.tensor(cls.VERSCHIEBUNG), mit_gelenken=True)
        cls.ansichten = []
        for name, winkel in (('vorne.jpg', 0), ('links.jpg', 90)):
            r = Fotoeinpassung._dreh(torch.tensor(math.radians(winkel)), torch.tensor(0.0))
            t = torch.tensor(cls.T)
            person = cls.maske(x, r, cls.S, t)
            uv = Fotoeinpassung.bild(p, r, cls.S, t)
            gelenke = {g: (uv[cls.dicht.index(k)], 1.0) for g, k, _p, _f in Posenpunkte.GELENKE}
            cls.ansichten.append({'name': name, 'winkel': winkel, 'ziel': KleinesZiel(person, person), 'gelenke': gelenke, 's': cls.S, 't': np.array(cls.T, np.float32),
                                  's_fest': True, 'kopf_ziel': uv[cls.dicht.index('head')], 'delta': 0.0, 'nick': 0.0})
        km = Einpasskoerper()
        e = Fotoeinpassung(km, cls.ansichten, {'index': km.index('head'), 'versatz': torch.zeros(3), 'drehung': None})
        e.SCHRITTE = (150, 50)
        cls.vorher = {a['name']: dict(a, t=a['t'].copy()) for a in cls.ansichten}
        cls.erg = e.rechnen(torch.zeros(3), log=lambda *_: None)

    def deckung(self, a, r, roh, kamera):
        return a['ziel'].deckung(self.maske(self.dicht.koerper(r, roh), *kamera))

    def test_form_stellt_die_groesse(self):
        self.assertAlmostEqual(float(self.erg['r'][0]), self.MASSSTAB, delta=0.03)

    def test_deckung_nachher_hoch_und_besser_als_vorher(self):
        for a in self.ansichten:
            vorher = self.deckung(a, torch.ones(1), torch.zeros(3), Fotoeinpassung.kamera_aus(self.vorher[a['name']], 'cpu'))
            nachher = self.deckung(a, self.erg['r'], self.erg['roh'], self.erg['kameras'][a['name']])
            self.assertGreater(nachher, 0.9, (a['name'], vorher, nachher))
            self.assertGreater(nachher, vorher + 0.05, (a['name'], vorher, nachher))

    def test_gelenke_treffen_im_bild(self):
        for a in self.ansichten:
            uv = Fotoeinpassung.bild(self.erg['p'], *self.erg['kameras'][a['name']])
            for g, k, _p, _f in Posenpunkte.GELENKE:
                if Fotoeinpassung._nahe_seite(a['winkel'], g):
                    rest = float((uv[self.dicht.index(k)] - a['gelenke'][g][0]).norm())
                    self.assertLess(rest, 2.0, (a['name'], g, rest))

    def test_kameramassstab_bleibt_fest(self):
        for a in self.ansichten:
            self.assertAlmostEqual(self.erg['masse'][a['name']]['s'], self.S, places=2)

    def test_ansichten_unveraendert_eingepasste_im_ergebnis(self):
        """Der Aufrufer entscheidet, ob er die Kameras einer Runde übernimmt (abgelehnte Runde 2 im ersten EdgarTrip-Lauf, siehe Modul-Docstring)."""
        for a in self.ansichten:
            v = self.vorher[a['name']]
            self.assertEqual((a['delta'], a['nick'], a['s']), (v['delta'], v['nick'], v['s']), a['name'])
            self.assertTrue(np.array_equal(a['t'], v['t']), a['name'])
        neu = {a['name']: a for a in self.erg['ansichten']}
        self.assertEqual(sorted(neu), sorted(self.vorher))
        for name, a in neu.items():
            self.assertIs(a['ziel'], self.vorher[name]['ziel'])
            self.assertTrue(torch.allclose(torch.as_tensor(a['t']), self.erg['kameras'][name][2], atol=1e-4))
            self.assertAlmostEqual(a['s'], float(self.erg['kameras'][name][1]), places=4)
