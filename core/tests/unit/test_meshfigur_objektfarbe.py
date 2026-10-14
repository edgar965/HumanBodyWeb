# -*- coding: utf-8 -*-
"""Mesh-3D: Objekte aus einem Netz mit Farben je Punkt (14.10.2026, Damira S2 Frau: „Netz ohne Textur“ — Haar und Kleidung gab es dort nicht als Objekt).

    ScanTest      `Meshfigurscan.hat_aussehen/aussehen`: UV und Textur, sonst Farben je Punkt, sonst nichts
    SchreibenTest `Kleidungsobjekt.schreiben/Haarobjekt.schreiben(punktfarben=…)`: GLB mit `COLOR_0`, ein Punkt je Ausgangspunkt, die Hautdatei hat eine Zeile je Punkt
    DrahtTest     Quelltext: die drei Aufrufer (Haar, Kleidung, Bestandteile) fragen `hat_aussehen()` und geben `aussehen(…)` weiter

Sabotage: in `Meshfigurscan.aussehen` den Zweig für Farben streichen → `ScanTest` rot; in `Kleidungsobjekt.schreiben` `COLOR_0` weglassen (`vertex_colors` entfernen) → `SchreibenTest` rot.
Gesehen (Chrome, Kopie „Test Damira Farben je Punkt“): Haar 8.986 Punkte und Kleidung 7.185 Punkte als Objekte (`vertexColors` an); vorher stand an beiden „Netz ohne Textur“.
"""

import shutil
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.projekt_temp import ProjektTemp

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

WEB = Path(settings.BASE_DIR)


def quelltext(*teile):
    return WEB.joinpath(*teile).read_text(encoding='utf-8')


def vier_punkte():
    punkte = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)
    flaechen = np.array([[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])
    farben = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255], [10, 20, 30]], dtype=np.uint8)
    return punkte, flaechen, farben


class ScanTest(SimpleTestCase):
    databases = set()

    def test_ohne_jede_farbe_gibt_es_kein_aussehen(self):
        from meshfigur_scan import Meshfigurscan

        punkte, flaechen, _ = vier_punkte()
        self.assertFalse(Meshfigurscan(punkte, flaechen).hat_aussehen())

    def test_farben_je_punkt_reichen_und_kommen_nur_fuer_die_genutzten_punkte(self):
        from meshfigur_scan import Meshfigurscan

        punkte, flaechen, farben = vier_punkte()
        scan = Meshfigurscan(punkte, flaechen, punktfarben=farben)
        self.assertTrue(scan.hat_aussehen())
        wahl = np.array([True, False, False, False])                  # die erste Fläche: Punkte 0, 1, 2
        genutzt = np.unique(scan.flaechen[wahl].reshape(-1))
        aus = scan.aussehen(wahl, genutzt)
        self.assertEqual(set(aus), {'punktfarben'})
        np.testing.assert_array_equal(aus['punktfarben'], farben[[0, 1, 2]])

    def test_uv_und_textur_gelten_vor_den_farben(self):
        from meshfigur_scan import Meshfigurscan

        punkte, flaechen, farben = vier_punkte()
        uv = np.zeros((4, 3, 2))
        textur = np.zeros((2, 2, 3), dtype=np.uint8)
        scan = Meshfigurscan(punkte, flaechen, uv, textur, farben)
        wahl = np.array([False, True, False, True])
        aus = scan.aussehen(wahl, np.unique(scan.flaechen[wahl].reshape(-1)))
        self.assertEqual(set(aus), {'uv_ecken', 'textur'})
        self.assertEqual(len(aus['uv_ecken']), 2)
        ersatz = np.ones((4, 3, 2))
        self.assertEqual(float(scan.aussehen(wahl, [0], ersatz)['uv_ecken'].max()), 1.0, 'die UV des Aufrufers (Kleidung: Hautband umgefärbt) ersetzen die des Netzes')


class SchreibenTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = Path(ProjektTemp.ordner(prefix='objektfarbe_'))
        self.addCleanup(shutil.rmtree, self.ordner, ignore_errors=True)

    def _haut(self, anzahl):
        from Kleidung.hautdatei import Hautdatei

        index, gewicht = Hautdatei.starr(anzahl, 3)
        return {'index': index, 'gewicht': gewicht, 'knochen': ['a', 'b', 'c', 'd']}

    def _pruefen(self, schreiber, name):
        import trimesh

        punkte, flaechen, farben = vier_punkte()
        pfad = self.ordner / name
        brief = schreiber(str(pfad), punkte, flaechen, haut=self._haut(len(punkte)), punktfarben=farben)
        self.assertEqual(brief['punkte'], 4, 'ein Punkt je Ausgangspunkt, nichts verdoppelt')
        self.assertEqual(brief['haut']['punkte'], 4)
        geladen = trimesh.load(str(pfad), force='mesh', process=False)
        self.assertEqual(getattr(geladen.visual, 'kind', None), 'vertex', 'die GLB trägt COLOR_0, keine Textur')
        np.testing.assert_array_equal(np.asarray(geladen.visual.vertex_colors)[:, :3], farben)

    def test_kleidungsobjekt_mit_punktfarben(self):
        from Kleidung.kleidungsobjekt import Kleidungsobjekt

        self._pruefen(Kleidungsobjekt.schreiben, 'kleidung.glb')

    def test_haarobjekt_mit_punktfarben(self):
        from Haar.haarobjekt import Haarobjekt

        self._pruefen(Haarobjekt.schreiben, 'haar.glb')

    def test_ohne_textur_und_ohne_farben_ist_ein_fehler(self):
        from Kleidung.kleidungsobjekt import Kleidungsobjekt

        punkte, flaechen, _ = vier_punkte()
        with self.assertRaises(ValueError):
            Kleidungsobjekt.schreiben(str(self.ordner / 'x.glb'), punkte, flaechen)


class DrahtTest(SimpleTestCase):
    databases = set()

    def test_alle_drei_aufrufer_fragen_das_aussehen_statt_der_textur(self):
        for datei in ('meshfigurhaar.py', 'meshfigurkleidung.py', 'meshfigurteile.py'):
            text = quelltext('core', 'dienste', datei)
            self.assertIn('scan.hat_aussehen()', text, datei)
            self.assertIn('**scan.aussehen(', text, datei)
            self.assertNotIn('scan.uv_ecken is None or scan.textur is None', text, '%s: die alte Abfrage lässt ein Netz mit Farben je Punkt durchfallen' % datei)

    def test_ohne_uv_gibt_es_keinen_textursaum(self):
        text = quelltext('core', 'dienste', 'meshfigurkleidung.py')
        self.assertIn('or scan.uv_ecken is None:', text)
