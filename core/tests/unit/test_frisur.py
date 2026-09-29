"""Schritt „frisur" von „Mesh to 3D" (29.09.2026) — Hülle, Reglersuche, Haar-Eigen-Morphe, GLB, Optionen.

Edgar: „das haar soll aber etwas natürlicher anschauen" → „mach a-b, c als option parallel". Alles an
Kunstformen (Kugelschale als Frisur, Kugel als Kopf), ohne Daz-Bibliothek, ohne Datenbank, ohne GPU: die
echte Wahl über 17 Frisuren rechnet ~3 Minuten und gehört nicht in `unit`.
"""

import json
import struct
import unittest
from pathlib import Path

import numpy as np
from Genesis9.haareigenmorphe import G9haareigenmorphe
from Genesis9.kollision import G9kollision
from Haar.frisurregler import Frisurregler
from Haar.haarglb import Haarglb
from Haar.haarhuelle import Haarhuelle
from Haar.straehnenbild import Straehnenbild

from ._pruefablage import Pruefablage

MITTE = np.array([0.0, 1.6, 0.0])


def kugel(radius, n=6000, oben_ab=-1.0, zufall=0):
    """(n, 3) Punkte auf einer Kugel um MITTE, nur wo y/r ≥ `oben_ab` (−1 = ganze Kugel)."""
    zg = np.random.default_rng(zufall)
    d = zg.normal(size=(n * 3, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    d = d[d[:, 1] >= oben_ab][:n]
    return MITTE + radius * d


class HaarhuelleTest(unittest.TestCase):
    def setUp(self):
        self.h = Haarhuelle(MITTE)
        self.haut = self.h.karte(kugel(0.09, 20000))

    def test_gleiche_form_hat_abstand_null_und_volle_deckung(self):
        ziel = self.h.karte(kugel(0.12, 20000, oben_ab=0.0))
        a = self.h.abstand(ziel, ziel.copy(), self.haut)
        self.assertEqual((a['mm'], a['deckung']), (0.0, 1.0))

    def test_fehlendes_haar_kostet_seine_dicke(self):
        # Dieselben Punkte, nur die obere Hälfte — zwei getrennte Stichproben belegen am Rand verschiedene
        # Felder (0,03 mm „zu viel" aus dem Zufall, erster Lauf 29.09.2026).
        punkte = kugel(0.12, 20000, oben_ab=0.0)
        ziel = self.h.karte(punkte)
        halb = self.h.karte(punkte[(punkte[:, 1] - MITTE[1]) / 0.12 >= 0.5])
        a = self.h.abstand(ziel, halb, self.haut)
        self.assertGreater(a['fehlt_mm'], 5.0, 'die untere Hälfte fehlt, 3 cm dick')
        self.assertLess(a['deckung'], 0.6)
        self.assertEqual(a['zuviel_mm'], 0.0)

    def test_haar_vor_dem_gesicht_kostet_extra(self):
        """Ein Pony über den Augen lag nur Millimeter über der Haut und gewann (29.09.2026, Chrome)."""
        ziel = self.h.karte(kugel(0.12, 20000, oben_ab=0.5))
        frisur = self.h.karte(kugel(0.095, 20000, oben_ab=0.0))
        gesicht = np.zeros_like(self.haut, dtype=bool)
        gesicht[: self.h.hoehe // 2 + 4, :] = True          # alles bis knapp über dem Äquator
        ohne = self.h.abstand(ziel, frisur, self.haut)
        mit = self.h.abstand(ziel, frisur, self.haut, gesicht)
        self.assertEqual(ohne['gesicht_mm'], 0.0)
        self.assertGreater(mit['mm'] - ohne['mm'], 5.0)

    def test_proben_liegen_auf_der_flaeche(self):
        punkte = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [10, 10, 0]], dtype=float)
        p, f = Haarhuelle.proben(punkte, np.array([[0, 1, 2], [1, 3, 2]]), 500, mit_flaeche=True)
        self.assertTrue(np.allclose(p[:, 2], 0.0))
        self.assertGreater((f == 1).mean(), 0.9, 'das große Dreieck bekommt fast alle Proben')


class FrisurreglerTest(unittest.TestCase):
    def test_findet_den_wert_der_die_huelle_trifft(self):
        h = Haarhuelle(MITTE)
        haut = h.karte(kugel(0.09, 20000))
        ziel = h.karte(kugel(0.11, 20000, oben_ab=0.0))
        grund = kugel(0.10, 20000, oben_ab=0.0, zufall=1)
        weg = (grund - MITTE) / np.linalg.norm(grund - MITTE, axis=1, keepdims=True) * 0.02
        suche = Frisurregler(lambda p: h.abstand(ziel, h.karte(p), haut)['mm'], grund,
                             {'Volumen': weg, 'Nichts': weg * 0.01},
                             {'Volumen': (-1, 1), 'Nichts': (0, 1)}).suchen()
        self.assertAlmostEqual(suche['werte'].get('Volumen', 0.0), 0.5, delta=0.13)
        self.assertLess(suche['mm_nachher'], suche['mm_vorher'])
        self.assertEqual(suche['schwach'], ['Nichts'], 'unter 4 mm Wirkung sucht niemand')


class HaarEigenMorpheTest(unittest.TestCase):
    """Kunstkopf: Kugel r = 9 cm, Scheitel 1,69 m; Haar: Kappe plus ein Vorhang bis 1,20 m hinter dem Kopf."""

    def setUp(self):
        kopf = kugel(0.09, 4000)
        rumpf = np.column_stack([np.random.default_rng(3).uniform(-0.15, 0.15, 4000),
                                 np.random.default_rng(4).uniform(0.9, 1.45, 4000),
                                 np.random.default_rng(5).uniform(-0.08, 0.08, 4000)])
        koerper = np.vstack([kopf, rumpf])
        normalen = koerper - np.array([0.0, koerper[:, 1].mean(), 0.0])
        normalen /= np.linalg.norm(normalen, axis=1, keepdims=True)
        kappe = kugel(0.092, 1500, oben_ab=0.0)
        y = np.linspace(1.55, 1.2, 800)
        vorhang = np.column_stack([np.linspace(-0.08, 0.08, 800), y, np.full(800, -0.13)])
        self.haar = np.vstack([kappe, vorhang])
        self.m = G9haareigenmorphe(self.haar, kopf, (koerper, normalen, G9kollision.baum(koerper)))

    def test_laenge_zieht_nur_den_haengenden_teil_nach_unten(self):
        d = self.m.laenge()
        haengt = self.m.haengt > 0.05
        self.assertLess(float(d[haengt, 1].mean()), -0.1)
        self.assertLess(float(np.abs(d[self.m.haengt == 0]).max()), 0.02, 'die Kappe bleibt')

    def test_kurz_hebt_die_spitzen(self):
        d = self.m.kurz()
        tief = self.haar[:, 1] < 1.3
        self.assertGreater(float((self.haar + d)[tief, 1].min()), 1.35)

    def test_dichte_bewegt_die_kappe_kaum_und_das_haar_hinaus(self):
        weg = np.linalg.norm(self.m.dichte(), axis=1)
        self.assertLessEqual(float(weg.max()), G9haareigenmorphe.DICHTE_MAX_M + 1e-9)

    def test_dutt_landet_hinter_dem_hinterkopf(self):
        neu = self.haar + self.m.dutt()
        tief = self.m.haengt > 0.1
        self.assertLess(float(neu[tief, 2].max()), self.m.hinten - 0.01)
        self.assertGreater(float(neu[tief, 1].min()), self.m.nacken - 0.05)

    def test_alle_fuenf_kanaele_mit_anzeigenamen(self):
        k = self.m.rechnen()
        self.assertEqual({v['label'] for v in k.values()}, {'Länge', 'Kurz', 'Dichte', 'Wellig', 'Dutt'})
        self.assertTrue(all(v['delta'].shape == self.haar.shape for v in k.values()))


class HaarglbTest(unittest.TestCase):
    def test_punktfarben_und_bild_mit_maske_in_einer_datei(self):
        glb = Haarglb()
        glb.netz({'name': 'Karte', 'punkte': np.eye(3), 'flaechen': np.array([[0, 1, 2]]),
                  'uv': np.zeros((3, 2)), 'farben': Haarglb.linear(np.full((3, 3), 128)),
                  'bild': Straehnenbild.png(), 'maske': 0.4})
        with Pruefablage.ordner('frisur_') as ordner:
            pfad = Path(ordner) / 'karte.glb'
            laenge = glb.schreiben(pfad)
            daten = pfad.read_bytes()
        magie, fassung, gesamt = struct.unpack('<4sII', daten[:12])
        self.assertEqual((magie, fassung, gesamt, len(daten)), (b'glTF', 2, laenge, laenge))
        kopf_laenge = struct.unpack('<I', daten[12:16])[0]
        gltf = json.loads(daten[20:20 + kopf_laenge])
        attribute = gltf['meshes'][0]['primitives'][0]['attributes']
        self.assertEqual(set(attribute), {'POSITION', 'TEXCOORD_0', 'COLOR_0'})
        self.assertEqual(gltf['materials'][0]['alphaMode'], 'MASK')
        self.assertIn('baseColorTexture', gltf['materials'][0]['pbrMetallicRoughness'])

    def test_srgb_wird_linear(self):
        self.assertAlmostEqual(float(Haarglb.linear([128])[0]), 0.2158, places=3)

    def test_straehnenbild_hat_deckkraft_nur_auf_straehnen(self):
        from io import BytesIO

        from PIL import Image

        bild = np.asarray(Image.open(BytesIO(Straehnenbild.png())))
        self.assertEqual(bild.shape, (Straehnenbild.HOEHE, Straehnenbild.BREITE, 4))
        deckt = (bild[..., 3] > 100).mean()
        self.assertTrue(0.05 < deckt < 0.6, deckt)


class MeshfigurfrisurOptionenTest(unittest.TestCase):
    databases = []

    def test_vorgaben_und_unbekannte_werte(self):
        from core.dienste.meshfiguroptionen import Meshfiguroptionen

        o = Meshfiguroptionen.pruefen({'frisur': 'irgendwas', 'haarkarten': 'aus'})
        self.assertEqual((o['frisur'], o['haarkarten']), ('beste', 'aus'))
        o = Meshfiguroptionen.pruefen({})
        self.assertEqual((o['frisur'], o['haarkarten']), ('beste', 'an'))

    def test_frisur_steht_zwischen_vorschau_und_speichern(self):
        from core.dienste.meshfigurlauf import Meshfigurlauf

        s = Meshfigurlauf.SCHRITTE
        self.assertEqual(s.index('frisur'), s.index('vorschau') + 1)
        self.assertEqual(s[-1], 'speichern')
        self.assertEqual(Meshfigurlauf.BAENDER['frisur'][1], Meshfigurlauf.BAENDER['speichern'][0])
