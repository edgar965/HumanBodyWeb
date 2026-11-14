"""Bausteine vom 04.11.2026 abends (Session3dTools, Lauf 9 und 10), ohne Figur, alle auf Kunstdaten; die mit Tensoren auf der Karte, wenn sie da ist (`Kostuemgpu`):
    1  `G9meshfinger._aussen`: außerhalb längs der Zielnormale positiv, innen 0
    2  `Kostuemhautfarbe.farbton_abstand`: Helligkeit zählt nicht (ein Glanzlicht bleibt beim Hautton)
    3  `Kostuemhautfarbe._bartsaum`: ohne Kern nichts, mit Kern nur zusammenhängende Flächen in der Farbe des Kerns
    4  `Meshgenesisfotogelenke.quelle`/`aktuell`: ohne Foto kein Schritt, ältere Ablage wird neu gerechnet
    5  `Kostuemsegmentierung._kennt_vorrat`: eine Ablage ohne einen Begriff des Vorrats taugt nicht
    6  `Meshgenesismeshanliegend.klassen`: ein schmaler Rand macht ein großes Stück nicht zu Haut
    7  `Kostuembindung._anhang`: ein Stück mit festem Träger hängt nicht an Punkten eines fremden Glieds
    8  `Kostuemgliedverdeckung.verdecken`: ein Stück, das die Hand einhüllt, verdeckt sie ganz, auch wenn wenig dahinter liegt
    9  `Kostuemkoerpervorn.pruefen`: rot ab `GRENZE`
   10  `Fotogenesisgenesiszeile.fuer`: jeder Test aus Fotos hat die dritte Zeile, ein Export nicht
Sabotage (von Hand): in `_aussen` das Vorzeichen drehen → Fall 1 rot; in `farbton_abstand` `[:, 1:]` weglassen → Fall 2 rot; in `_bartsaum` den Abbruch ohne Kern entfernen → Fall 3 rot; `MIN_RAND_ANTEIL` auf 0 → Fall 6 rot;
in `_anhang` `traegt` weglassen → Fall 7 rot; `HUELLE` auf 2 → Fall 8 rot; in `Fotogenesisgenesiszeile.fuer` wieder nach dem PSHuman-Netz fragen → Fall 10 rot.
"""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import torch
from django.conf import settings
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402

sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))


class FussImSchuhTest(unittest.TestCase):
    databases = []

    def test_aussen_laengs_der_normale(self):
        from Genesis9.meshfinger import G9meshfinger as F
        ziel = torch.tensor([[0.0, 0.0, 0.0]], dtype=torch.float64)
        normale = torch.tensor([[0.0, -1.0, 0.0]], dtype=torch.float64)            # Sohle: Normale nach unten
        ph = torch.tensor([[0.0, -0.03, 0.0], [0.0, 0.02, 0.0]], dtype=torch.float64)
        wert = F._aussen(ph, ziel, normale, torch.tensor([0, 0]))
        self.assertAlmostEqual(float(wert[0]), 0.03)
        self.assertEqual(float(wert[1]), 0.0)


class BartTest(unittest.TestCase):
    databases = []

    def test_farbton_ohne_helligkeit(self):
        from meshgenesis_kostuem_hautfarbe import Kostuemhautfarbe as H
        ton = torch.tensor([44.0, 2.0, 9.0], dtype=torch.float64)
        haar = torch.tensor([57.0, 0.0, 4.5], dtype=torch.float64)
        licht = torch.tensor([[60.0, 2.5, 8.5]], dtype=torch.float64)              # Glanzlicht: heller als das Haar, Farbton der Haut
        self.assertLess(float(H.farbton_abstand(licht, ton)[0]), float(H.farbton_abstand(licht, haar)[0]))
        self.assertLess(float(H.abstand(licht, haar)[0]), float(H.abstand(licht, ton)[0]))        # mit L* läge es näher am Haar: der Fehler von vorher

    @staticmethod
    def _streifen():
        """Vier Flächen in einer Reihe: Haar (Kern), Bartfarbe, Bartfarbe, Haut."""
        from meshgenesis_kostuem_hautfarbe import Kostuemhautfarbe as H
        from meshgenesis_kostuemarten import Kostuemarten as A
        from meshgenesis_kostuemgpu import Kostuemgpu
        h = H.__new__(H)
        h.k = Kostuemgpu.an()
        g = h.k.g
        h.fs = torch.tensor([[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5]], device=g)
        h.lab = torch.tensor([[57.0, 0.0, 4.5], [55.0, 0.2, 4.0], [58.0, 0.1, 4.2], [44.0, 2.0, 9.0]], dtype=torch.float64, device=g)
        h.inhalt = torch.full((4,), 1.0, dtype=torch.float64, device=g)
        h.kante = 0.01
        art = torch.tensor([A.nummer('haar'), A.nummer('haut'), A.nummer('haut'), A.nummer('haut')], device=g)
        im_ton = torch.tensor([False, False, False, True], device=g)
        ton = h.lab[3]
        return h, art, im_ton, ton, A.nummer('haut'), A.nummer('haar'), g

    def test_ohne_kern_nichts(self):
        h, art, im_ton, ton, haut, haar, _g = self._streifen()
        neu, m2 = h._bartsaum(art.clone(), im_ton, ton, 6, haut, haar, None)
        self.assertEqual(m2, 0.0)
        self.assertEqual(neu.tolist(), art.tolist())

    def test_mit_kern_waechst_nur_der_bart(self):
        h, art, im_ton, ton, haut, haar, g = self._streifen()
        kern = torch.tensor([True, False, False, False], device=g)
        neu, m2 = h._bartsaum(art.clone(), im_ton, ton, 6, haut, haar, kern)
        self.assertEqual(neu.tolist(), [haar, haar, haar, haut])
        self.assertEqual(m2, 2.0)


class FotoSchrittTest(unittest.TestCase):
    databases = []

    def setUp(self):
        wurzel = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf'
        wurzel.mkdir(parents=True, exist_ok=True)
        self.t = Path(tempfile.mkdtemp(dir=wurzel))
        self.addCleanup(shutil.rmtree, self.t, ignore_errors=True)

    def test_ohne_foto_kein_schritt(self):
        from meshgenesis_fotogelenke import Meshgenesisfotogelenke as F
        self.assertIsNone(F.quelle(self.t))
        self.assertFalse(F.aktuell(self.t))
        (self.t / 'foto').mkdir()
        (self.t / 'foto' / 'foto.png').write_bytes(b'x')
        self.assertIsNone(F.quelle(self.t))                                     # Foto ohne Maske reicht nicht

    def test_aeltere_ablage_gilt_nicht(self):
        from meshgenesis_fotogelenke import Meshgenesisfotogelenke as F
        o = self.t / 'foto'
        o.mkdir()
        (o / 'foto.jpg').write_bytes(b'x')
        (o / 'maske.png').write_bytes(b'x')
        d = F.datei(self.t)
        Npztorch.speichern(d, namen=np.array(['a']), k2=np.zeros((1, 2)), k3=np.zeros((1, 3)), umriss=np.zeros(4))
        self.assertTrue(F.aktuell(self.t))
        os.utime(d, (1, 1))
        self.assertFalse(F.aktuell(self.t))


class VorratTest(unittest.TestCase):
    databases = []

    def test_ablage_ohne_begriff_taugt_nicht(self):
        from meshgenesis_kostuem_segmentierung import Blendimportbegriffe, Kostuemsegmentierung as S
        wurzel = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf'
        seg = Path(tempfile.mkdtemp(dir=wurzel))
        self.addCleanup(shutil.rmtree, seg, ignore_errors=True)
        Npztorch.speichern(seg / 'teile_flaechen.npz', begriffe=np.array(['beard', 'hat']))
        with mock.patch.object(Blendimportbegriffe, 'vorrat', return_value=[{'phrase': 'beard'}, {'phrase': 'hat'}]):
            self.assertTrue(S._kennt_vorrat(seg))
        with mock.patch.object(Blendimportbegriffe, 'vorrat', return_value=[{'phrase': 'beard'}, {'phrase': 'glove'}]):
            self.assertFalse(S._kennt_vorrat(seg))


class AnliegendTest(unittest.TestCase):
    databases = []

    @staticmethod
    def _flaeche(stoff, zeilen=40):
        """Waagerechte Ebene (y = 0) im 1-cm-Raster: fünf Spalten Haut, daneben `stoff` Spalten Stoff ohne Stufe. → Punkte, Dreiecke, Klasse, Art.
        Waagerecht seit 07.11.2026: Die Regel „lang“ (`Meshgenesismeshanliegend.TIEF_HOEHE`) misst die Höhe y im Ziel; eine senkrechte Ebene ohne Figur läge zu 35 % „unter dem Schritt“."""
        from Genesis9.meshziel import G9meshziel
        from meshgenesis_kostuemarten import Kostuemarten
        spalten = 5 + stoff
        x, y = torch.meshgrid(torch.arange(spalten, dtype=torch.float64) * 0.01, torch.arange(zeilen, dtype=torch.float64) * 0.01, indexing='ij')
        punkte = torch.stack([x.flatten(), torch.zeros(spalten * zeilen, dtype=torch.float64), y.flatten()], 1)
        i = torch.arange(spalten * zeilen).reshape(spalten, zeilen)
        a, b, c, d = i[:-1, :-1].flatten(), i[1:, :-1].flatten(), i[1:, 1:].flatten(), i[:-1, 1:].flatten()
        dreiecke = torch.cat([torch.stack([a, b, c], 1), torch.stack([a, c, d], 1)])
        klasse = torch.where(x.flatten() < 0.045, G9meshziel.HAUT, G9meshziel.KLEID)
        art = torch.full((spalten * zeilen,), Kostuemarten.ARTEN.index('oberteil'))
        return punkte, dreiecke, klasse, art

    def test_breiter_rand_liegt_an(self):
        from Genesis9.meshziel import G9meshziel
        from meshgenesis_meshanliegend import Meshgenesismeshanliegend as A
        neu, bericht = A.klassen(*self._flaeche(40))
        self.assertTrue(bericht['oberteil']['anliegend'])
        self.assertTrue(bool((neu == G9meshziel.HAUT).all()))

    def test_schmaler_rand_sagt_nichts_ueber_das_stueck(self):
        from Genesis9.meshziel import G9meshziel
        from meshgenesis_meshanliegend import Meshgenesismeshanliegend as A
        p, d, klasse, art = self._flaeche(400)
        neu, bericht = A.klassen(p, d, klasse, art)
        self.assertGreaterEqual(bericht['oberteil']['rand'], A.MIN_RAND)              # die alte Regel wäre durchgegangen
        self.assertEqual(bericht['oberteil']['ohne_stufe'], 1.0)
        self.assertFalse(bericht['oberteil']['anliegend'])
        self.assertEqual(int((neu == G9meshziel.HAUT).sum()), int((klasse == G9meshziel.HAUT).sum()))


class HandschuhTest(unittest.TestCase):
    databases = []

    def test_anhang_nur_am_traeger(self):
        from meshgenesis_kostuem_bindung import Kostuembindung
        from meshgenesis_kostuem_rueckhaeutung import Kostuemrueckhaeutung
        from meshgenesis_kostuemarten import ALLE
        from meshgenesis_kostuemgpu import Kostuemgpu
        k, t = Kostuemgpu.an(), Kostuemgpu.an().t
        r = Kostuemrueckhaeutung.__new__(Kostuemrueckhaeutung)
        r.k = k
        r.knochen_stelle = k.feld(np.array([ALLE.index('hand'), ALLE.index('bein')]), t.int64)
        b = Kostuembindung.__new__(Kostuembindung)
        b.k, b.rueck = k, r
        lage = k.feld(np.zeros((2, 3)) + [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0]], t.float64)
        gw = k.feld(np.array([[255, 0], [255, 0]], dtype=np.uint8))
        bein = (None, k.feld(np.array([[1, 0], [1, 0]]), t.int64), gw)
        hand = (None, k.feld(np.array([[0, 1], [0, 1]]), t.int64), gw)
        eingang = {'handschuh': lage, 'hose': lage}
        self.assertIsNone(b._anhang('handschuh', eingang, {'hose': bein}, ('hand', 'arm')))
        self.assertEqual(int(b._anhang('handschuh', eingang, {'hose': hand}, ('hand', 'arm'))[0].sum()), 2)
        self.assertEqual(int(b._anhang('freie', {'freie': lage, 'hose': lage}, {'hose': bein}, None)[0].sum()), 2)      # ohne festen Träger wie bisher

    def test_huelle_verdeckt_die_ganze_hand(self):
        from meshgenesis_kostuem_gliedverdeckung import Kostuemgliedverdeckung as V
        punkte = np.array([[0, 0, 0], [0.01, 0, 0], [0, 0.01, 0], [0.01, 0.01, 0]], dtype=np.float64)
        dreiecke = np.array([[0, 1, 2], [1, 3, 2]])
        knochen, gewicht = np.zeros((4, 1), dtype=np.int64), np.full((4, 1), 255)
        kin = [{'name': 'l_hand', 'gruppe': 'hand'}]
        leer = np.zeros(2, dtype=bool)
        nah = punkte + [0.0, 0.0, 0.02]
        fern = punkte + [0.0, 0.0, 0.5]
        self.assertTrue(V.verdecken([leer], ['zubehoer'], dreiecke, knochen, gewicht, kin, punkte, [nah])[0][0].all())
        self.assertFalse(V.verdecken([leer], ['zubehoer'], dreiecke, knochen, gewicht, kin, punkte, [fern])[0][0].any())
        self.assertFalse(V.verdecken([leer], ['zubehoer'], dreiecke, knochen, gewicht, kin)[0][0].any())            # ohne Lage nur `ANTEIL`


class KoerperVorTest(unittest.TestCase):
    databases = []

    def test_rot_ab_grenze(self):
        from meshgenesis_kostuem_koerpervorn import Kostuemkoerpervorn as V
        gezaehlt = []
        z = {V.NAME: {}}
        V.pruefen(z, lambda _z, fehler, _t: gezaehlt.append(fehler), {'bild': {'vorne': {'koerper_vor_kleidung': V.GRENZE + 0.01}, 'hinten': {'koerper_vor_kleidung': V.GRENZE - 0.01},
                                                                              'links': {'koerper_vor_kleidung': None}}})
        self.assertEqual(gezaehlt, [True, False])


class LayoutTest(unittest.TestCase):
    databases = []

    def test_jeder_test_aus_fotos_hat_die_dritte_zeile(self):
        from core.dienste.fotogenesisgenesiszeile import Fotogenesisgenesiszeile as G
        wurzel = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf'
        ordner = Path(tempfile.mkdtemp(dir=wurzel))
        self.addCleanup(shutil.rmtree, ordner, ignore_errors=True)
        ohne = G.fuer({'art': 'foto', 'netze': [], 'test': None, 'ordner': ordner})
        self.assertIsNone(ohne['test'])
        self.assertIsNone(ohne['meshgenesis'])
        self.assertIn('Noch kein Mesh-Genesis-Test', ohne['hinweise']['meshgenesis'])
        self.assertIsNone(G.fuer({'art': 'export', 'netze': [], 'test': None}))
