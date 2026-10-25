# -*- coding: utf-8 -*-
"""Perspektivisches Einpassen eines Kunstkörpers mit fester Körpergröße (`KoerperKI_Fotos.fotoeinpassung.Fotoeinpassung`, 24.10.2026, 2d-3d-AI) — im LongRunner (CPU, einige Sekunden).

WARUM: Edgar, 24.10.2026: „mach B“ und „die körpergröße pro Job fest“. Der dritte Einpass-Lauf an EdgarTrip schrumpfte die Figur auf 1,435 m: beim Kopfmaßstab erscheint Edgar in den
Fotos 1,36–1,45 m groß (`ProjektTemp/_wegwerf/ai2d3d/perspektive_probe.py`), angegeben sind 1,85 m. Fotos aus 1,3–1,4 m Abstand mit 26-mm-Weitwinkel bilden den Kopf größer ab als die
Füße; eine Kamera mit EINEM Maßstab muss das als kleinere Figur lesen.
Wahrheit: Maßstab 1,1 (Körper 1,76 m), Verschiebung (3, −2, 4) cm; Lochkamera f = 300 px, 2 m vor dem Drehpunkt, von oben (vorn φ = 0,25, links φ = 0,15). Start wie
`nurfotos_einpassen.py`: Maßstab 1, s = Höhe der Maske / Angabe, t = Mitte des Maskenkastens, φ = 0. Die Angabe 1,76 m muss die Form stellen, der Rest die Kamera.
"""
import sys
import unittest

import numpy as np
import torch
import torch.nn.functional as F
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.fotoeinpassung import Fotoeinpassung  # noqa: E402
from KoerperKI_Fotos.posenpunkte import Posenpunkte  # noqa: E402

from ..unit._einpasskoerper import Einpasskoerper  # noqa: E402
from .test_koerperki_fotos_einpassen import KleinesZiel  # noqa: E402


class DasPerspektivischeEinpassen(unittest.TestCase):
    F_PX, Z, T, HW = 300.0, 2.0, (120.0, 170.0), (360, 240)
    MASSSTAB, VERSCHIEBUNG, HOEHE = 1.1, (0.03, -0.02, 0.04), 1.76
    FOTOS = (('vorne.jpg', 0, 0.25), ('links.jpg', 90, 0.15))

    @staticmethod
    def lochkamera(x, kamera):
        """Die Wahrheit unabhängig von `Fotoeinpassung.bild` gerechnet (sonst erzeugt der Test seine Fotos mit dem Code, den er prüft — eine Sabotage am Vorzeichen der Tiefe blieb so grün):
        Kameraort C = mitte + Rᵀ · (0, 0, f / s), Blick entlang −z′; Tiefe = Abstand längs des Blicks, Bild = f · (x_K, −y_K) / Tiefe + t."""
        r, s, t, f, mitte = kamera
        ort = mitte + r.T @ torch.tensor([0.0, 0.0, f / s])
        k = (x - ort) @ r.T
        return f * torch.stack([k[:, 0], -k[:, 1]], 1) / (-k[:, 2:3]) + t

    @classmethod
    def maske(cls, x, kamera, wahr=False):
        uv = (cls.lochkamera(x, kamera) if wahr else Fotoeinpassung.bild(x, *kamera)).round().long()
        h, w = cls.HW
        m = torch.zeros(cls.HW)
        drin = (uv[:, 0] >= 0) & (uv[:, 0] < w) & (uv[:, 1] >= 0) & (uv[:, 1] < h)
        m[uv[drin, 1], uv[drin, 0]] = 1.0
        return F.max_pool2d(m[None, None], 3, 1, 1)[0, 0] > 0.5

    @classmethod
    def setUpClass(cls):
        cls.mitte = torch.zeros(3)
        cls.dicht = Einpasskoerper(abstand=0.01)
        x, p, _e, _d, _w = cls.dicht.koerper(torch.tensor([cls.MASSSTAB]), torch.tensor(cls.VERSCHIEBUNG), mit_gelenken=True)
        cls.ansichten, cls.wahr = [], {}
        for name, winkel, nick in cls.FOTOS:
            kam = (Fotoeinpassung._dreh(torch.deg2rad(torch.tensor(float(winkel))), torch.tensor(nick)), cls.F_PX / cls.Z, torch.tensor(cls.T), cls.F_PX, cls.mitte)
            cls.wahr[name] = kam
            person = cls.maske(x, kam, wahr=True)
            uv = cls.lochkamera(p, kam)
            zeilen = torch.nonzero(person.any(1)).reshape(-1).float()
            spalten = torch.nonzero(person.any(0)).reshape(-1).float()
            cls.ansichten.append({'name': name, 'winkel': winkel, 'ziel': KleinesZiel(person, person),
                                  'gelenke': {g: (uv[cls.dicht.index(k)], 1.0) for g, k, _p, _f in Posenpunkte.GELENKE},
                                  's': float(zeilen[-1] - zeilen[0]) / cls.HOEHE, 't': np.array([(spalten[0] + spalten[-1]) / 2, (zeilen[0] + zeilen[-1]) / 2], np.float32),
                                  's_fest': False, 'kopf_ziel': uv[cls.dicht.index('head')], 'delta': 0.0, 'nick': 0.0, 'f': cls.F_PX})
        km = Einpasskoerper()
        e = Fotoeinpassung(km, cls.ansichten, {'index': km.index('head'), 'versatz': torch.zeros(3), 'drehung': None}, mitte=cls.mitte, hoehe=cls.HOEHE)
        e.SCHRITTE = (250, 100)
        cls.erg = e.rechnen(torch.zeros(3), log=lambda *_: None)

    def test_angegebene_groesse_stellt_die_form(self):
        self.assertAlmostEqual(float(self.erg['r'][0]), self.MASSSTAB, delta=0.02)

    def test_deckung_hoch(self):
        for a in self.ansichten:
            d = a['ziel'].deckung(self.maske(self.dicht.koerper(self.erg['r'], self.erg['roh']), self.erg['kameras'][a['name']]))
            self.assertGreater(d, 0.9, (a['name'], d))

    def test_kamera_steht_wo_sie_stand(self):
        """Abstand und Neigung kommen aus der Perspektive selbst (Kopf größer als Füße) — Probe gegen die Wahrheit."""
        for name, _w, nick in self.FOTOS:
            ort = self.erg['masse'][name]
            self.assertAlmostEqual(ort['abstand_m'], self.Z, delta=0.3, msg=(name, ort))
            self.assertAlmostEqual(ort['nick_grad'], float(np.degrees(nick)), delta=5.0, msg=(name, ort))

    def test_gelenke_treffen_im_bild(self):
        """Grenze 4 px (≈ 2,7 cm bei 150 px/m): nach dem Drehungs-Fix R_y(−w) gemessen höchstens 3,57 px, Knöchel vorn, weil die Ansicht vorn um 4,8° gedreht bleibt (Wahrheit 0°;
        `ProjektTemp/_wegwerf/ai2d3d/perspektive_gelenkreste.py`), alle anderen Gelenke unter 2 px."""
        for a in self.ansichten:
            uv = Fotoeinpassung.bild(self.erg['p'], *self.erg['kameras'][a['name']])
            for g, k, _p, _f in Posenpunkte.GELENKE:
                if Fotoeinpassung._nahe_seite(a['winkel'], g):
                    rest = float((uv[self.dicht.index(k)] - a['gelenke'][g][0]).norm())
                    self.assertLess(rest, 4.0, (a['name'], g, rest))
