# -*- coding: utf-8 -*-
u"""Texturschichten an Kleid und Haar (30.09.2026, nachts) — Kunstdaten, keine Bibliothek, keine Ablage in 3DObjects.

1. `G9uvraster`: ein Viereck aus zwei Dreiecken füllt seine UV-Fläche, Lage und Normale je Texel stimmen (Ecken, Mitte).
2. `Fotoprojektion`: ein Punkt vor der Kamera landet auf dem Pixel, das die Normierung vorgibt; Rückseite zählt nicht;
   ein Punkt außerhalb der Teilmaske bleibt ungetroffen.
3. `G9faltenkarte.karte`: die Normale kippt in Richtung der Welle, außerhalb der Maske bleibt sie flach.
4. `G9texturschicht`: Decal über einer Grundfarbe (Pillow, Wegwerfordner), Foto mit Anteil, Normalen-Mischung; die
   Ablagepfade und Reglernamen von `G9kleidtexturen` (`bild.<schicht>`), `werte` liest nur `bild.*`.
5. `ModellTexturMixin`: `kleid_fototextur` merkt den Wunsch und stellt `bild.foto`, `kleid_farbe_je_stueck` tönt nur das
   eine Stück, die neuen Funktionen stehen in `hilfe()`.
6. `Haarengineblender._straehnen`/`_eingang`: Ketten aus Segmenten, Socketnamen aus Schlüsselwörtern.

Sabotage-Gegenproben: in `G9uvraster._baryzentrisch` das Klemmen weglassen → Fall 1 rot (Ecken laufen über); in
`Fotoprojektion.farben` `** self.AUSRICHTUNG` weglassen → Fall 2 bleibt grün (die Rückseite prüft `clip`), aber
`drin` weglassen → rot.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.faltenkarte import G9faltenkarte
from Genesis9.kleidtexturen import G9kleidtexturen
from Genesis9.modellmitkleidern import ModellMitKleidern
from Genesis9.texturschicht import G9texturschicht
from Genesis9.uvraster import G9uvraster
from iterationen2d3d.fotoprojektion import Fotoprojektion

from ._pruefablage import Pruefablage


class UvrasterTest(SimpleTestCase):
    databases = set()

    def _viereck(self):
        punkte = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 2.0, 0.0], [0.0, 2.0, 0.0]])
        uv = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
        dreiecke = np.array([[0, 1, 2], [0, 2, 3]])
        gruppen = [{'name': 'Stoff', 'index_ab': 0, 'index_anzahl': 6}]
        return G9uvraster(punkte, dreiecke, uv, gruppen, groesse=64)

    def test_1_viereck_fuellt_die_uv_flaeche(self):
        karte = self._viereck().karte({'name': 'Stoff', 'index_ab': 0, 'index_anzahl': 6})
        self.assertGreater(karte['maske'].mean(), 0.97)
        # Zeile 0 ist v = 1 (oben, y = 2), Spalte 0 ist u = 0 (x = 0); Mitte bei (0,5, 1,0).
        np.testing.assert_allclose(karte['lage'][32, 32], [0.5, 1.0, 0.0], atol=0.03)
        np.testing.assert_allclose(karte['lage'][1, 1], [0.02, 1.95, 0.0], atol=0.05)
        np.testing.assert_allclose(karte['lage'][62, 62], [0.98, 0.05, 0.0], atol=0.05)
        self.assertTrue(np.all(np.abs(karte['normale'][karte['maske']][:, 2]) > 0.99))
        alle = self._viereck().alle()
        self.assertEqual(list(alle), ['Stoff'])

    def test_2_fotoprojektion_normierung_und_masken(self):
        # Kamera: Mitte (0, 1, 0), halbe Bildhöhe 1,2 m, Render 100 × 150; Kasten des Renders: cx 50, Zeilen 10…140.
        p = Fotoprojektion(mitte=[0.0, 1.0, 0.0], halb=1.2, render_groesse=(100, 150))
        hf, bf = 150, 100
        u, v = p.projizieren([[0.0, 1.0, 0.5]], 0.0, (50.0, 10.0, 140.0), hf, bf)
        self.assertAlmostEqual(float(u[0]), bf / 2)                       # auf der Achse → Bildmitte
        # Bildhöhe 150 px entspricht 2,4 m; y = 1 ist die Mitte des Renders (Zeile 75), normiert:
        # (75 − 10) · 141/130 + 4,5
        self.assertAlmostEqual(float(v[0]), (75.0 - 10.0) * (hf * 0.94 / 130.0) + 0.03 * hf, places=5)
        # Ein Punkt links der Figur (+x) liegt bei Winkel 0 links im Bild? Kamera vorn: x_cam = (c, 0, −s) = +x → rechts.
        u2, _v2 = p.projizieren([[0.3, 1.0, 0.0]], 0.0, (50.0, 10.0, 140.0), hf, bf)
        self.assertGreater(float(u2[0]), float(u[0]))
        foto = np.zeros((hf, bf, 3), np.float32)
        foto[:, :, 0] = 1.0                                                # rot überall
        maske = np.ones((hf, bf), bool)
        teil = np.zeros((hf, bf), bool)
        teil[:, :60] = True                                                # nur die linke Bildhälfte gehört dem Teil
        p.ansicht(0.0, (50.0, 10.0, 140.0), foto, maske, teil)
        farbe, getroffen = p.farben([[0.0, 1.0, 0.5], [0.0, 1.0, 0.5], [0.4, 1.0, 0.5]],
                                    [[0.0, 0.0, 1.0], [0.0, 0.0, -1.0], [0.0, 0.0, 1.0]])
        self.assertTrue(getroffen[0])
        np.testing.assert_allclose(farbe[0], [1.0, 0.0, 0.0])
        self.assertTrue(getroffen[1])                                      # Rückseite: Rückfall auf „gesehen"
        self.assertFalse(getroffen[2])                                     # außerhalb der Teilmaske (rechts)

    def test_3_faltenkarte_kippt_die_normale(self):
        karte = self._viereck().karte({'name': 'Stoff', 'index_ab': 0, 'index_anzahl': 6})
        gewicht = karte['maske'].astype(np.float64)
        bild = G9faltenkarte.karte(karte, gewicht, abstand_cm=50.0, tiefe=1.0, richtung='laengs')
        n = bild * 2.0 - 1.0
        innen = karte['maske'].copy()
        innen[:2, :] = innen[-2:, :] = innen[:, :2] = innen[:, -2:] = False
        self.assertGreater(float(np.abs(n[innen][:, 1]).max()), 0.5)     # längs: die Welle läuft über y → Kippen in v
        self.assertLess(float(np.abs(n[innen][:, 0]).max()), 0.05)
        self.assertTrue(np.allclose(bild[~karte['maske']], [0.5, 0.5, 1.0]))
        with self.assertRaises(ValueError):
            G9faltenkarte.karte(karte, gewicht, richtung='schraeg')


class TexturschichtTest(SimpleTestCase):
    databases = set()

    def test_4_komposition_und_ablage(self):
        with Pruefablage.ordner('kleidtexturen') as ordner:
            self._komposition(ordner)

    def _komposition(self, ordner):
        from pathlib import Path

        from PIL import Image
        ordner = Path(ordner)
        daz = ordner / 'daz.png'
        Image.fromarray(np.full((8, 8, 3), 200, np.uint8)).save(daz)
        decal = ordner / 'decal.png'
        rgba = np.zeros((8, 8, 4), np.uint8)
        rgba[:4, :, :3] = (255, 0, 0)
        rgba[:4, :, 3] = 255                                               # obere Hälfte rot, deckend
        Image.fromarray(rgba, 'RGBA').save(decal)
        ziel = ordner / 'aus.png'
        G9texturschicht.albedo(daz, [0.5, 1.0, 1.0], [('decal_x', 1.0, decal)], ziel, 64)
        bild = np.asarray(Image.open(ziel).convert('RGB'))
        np.testing.assert_allclose(bild[1, 1], [255, 0, 0], atol=1)
        np.testing.assert_allclose(bild[6, 6], [100, 200, 200], atol=1)   # Daz × Farbfaktor
        G9texturschicht.albedo(None, None, [('foto', 0.5, daz)], ziel, 64)
        np.testing.assert_allclose(np.asarray(Image.open(ziel).convert('RGB'))[3, 3], [227, 227, 227], atol=1)
        n = ordner / 'n.png'
        nk = np.full((8, 8, 3), 128, np.uint8)
        nk[..., 0] = 255                                                   # stark nach +x gekippt
        nk[..., 2] = 255
        Image.fromarray(nk).save(n)
        G9texturschicht.normalen(None, [('falten_y', 1.0, n)], ziel, 64, G9kleidtexturen.FLACH)
        aus = np.asarray(Image.open(ziel).convert('RGB')).astype(float) / 255.0 * 2 - 1
        self.assertGreater(float(aus[2, 2, 0]), 0.5)
        self.assertAlmostEqual(float(np.linalg.norm(aus[2, 2])), 1.0, places=1)
        # Ablage, Regler, Werte — ohne die Platte anzufassen.
        self.assertEqual(G9kleidtexturen.pfad('shirt', 'Trim Arms', 'foto').name, 'shirt__trim-arms__foto_f1.png')
        self.assertEqual(G9kleidtexturen.werte({'bild.foto': 0.7, 'eigen.x': 1, 'bild.decal_a': 0}), {'foto': 0.7})
        self.assertEqual(G9kleidtexturen.art_von('decal_brust'), 'decal')
        self.assertIsNone(G9kleidtexturen.datei('../x.png'))
        with self.assertRaises(ValueError):
            G9kleidtexturen.ablegen('shirt', 'Foto!', {})

    def test_5_rezeptfunktionen_der_textur(self):
        namen = {n for n, _s, _t in ModellMitKleidern.hilfe()}
        for f in ('kleid_fototextur', 'haar_fototextur', 'kleid_decal', 'kleid_falten', 'kleid_farbe_je_stueck',
                  'kleid_schnitt', 'haar_knoten', 'bild_wert', 'kleid_falten_backen', 'haar_curl', 'haar_braid',
                  'haar_profil', 'haar_duplizieren', 'haar_interpolieren'):
            self.assertIn(f, namen, f)
        m2 = ModellMitKleidern().haar_profil('pixie', 2.0, 0.4)
        self.assertEqual((m2.haar['pixie.profil.wurzel'], m2.haar['pixie.profil.spitze']), (2.0, 0.4))
        m = ModellMitKleidern().kleid_nur('shirt').kleid_fototextur('shirt', 0.8)
        self.assertEqual(m.fotowuensche, {'shirt': 'kleidung'})
        self.assertEqual(m.kleidung['shirt.bild.foto'], 0.8)
        self.assertNotIn('fotowuensche', m.als_dict())
        m.kleid_farbe_je_stueck('shirt', '#102030').kleid_farbe('#ffffff')
        self.assertEqual(m.stueckfarbe('kleidung', 'shirt'), '#102030')
        self.assertEqual(m.stueckfarbe('kleidung', 'hose'), '#ffffff')
        m.kleid_farbe_je_stueck('shirt', '')
        self.assertEqual(m.stueckfarbe('kleidung', 'shirt'), '#ffffff')
        with self.assertRaises(ValueError):
            m.bild_wert('kleidung', 'shirt', 'quatsch', 1.0)
        m.haar_anteil('kin_hair', 0.3, ort={'sektor': (30, 150)})
        self.assertEqual(m.haar['kin_hair.ort.sektor_b'], 150.0)
        m.haar_anteil('kin_hair', 0.3)
        self.assertNotIn('kin_hair.ort.sektor_b', m.haar)
        with self.assertRaises(ValueError):
            m.haar_knoten('pixie', 'kurz', 'trim')                        # keine Runde, kein Arbeiter
        with self.assertRaises(ValueError):
            m.kleid_schnitt('oberteil', regler='kein dict')

    def test_6_straehnen_und_socketnamen(self):
        from core.dienste.haarengineblender import Haarengineblender
        ketten = Haarengineblender._straehnen([[0, 1], [1, 2], [5, 6]], 7)
        self.assertEqual([k.tolist() for k in ketten], [[0, 1, 2], [5, 6]])
        self.assertEqual(Haarengineblender._eingang('length_factor'), 'Length Factor')
        self.assertEqual(Haarengineblender._eingang('curl_radius'), 'Curl Radius')
