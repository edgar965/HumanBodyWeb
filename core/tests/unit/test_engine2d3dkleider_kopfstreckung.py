# -*- coding: utf-8 -*-
"""08.10.2026, „augen sind noch kaputt" und „messfehler sind noch gigantisch": `Engine2d3dKleiderkopfstreckung` (Kopfnetz senkrecht strecken, Option `koerper.kopfstreckung`), die Lider sind nicht mehr im
Landmarkmorph (`Meshfigurlandmarkmorphe.BEREICHE`) und `G9pyrenderreihenfolge` (Wimpern/Brauen nach der Haut zeichnen) — Kunstdaten, kein Render, keine echte Ablage."""
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from core.dienste.engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen as Optionen
from core.dienste.engine2d3dkleiderkopfstreckung import Engine2d3dKleiderkopfstreckung as Streckung
from core.dienste.engine2d3dkleidergesichtslage import Engine2d3dKleiderGesichtslage as Lage
from core.dienste.meshfigurlandmarkmorphe import Meshfigurlandmarkmorphe
from django.test import SimpleTestCase
from Genesis9.pyrenderreihenfolge import G9pyrenderreihenfolge as Reihenfolge

from ._pruefablage import Pruefablage


class DieStreckung(SimpleTestCase):
    def test_1_faktor_ist_eins_plus_prozent_und_begrenzt(self):
        self.assertEqual(Streckung.faktor(0), 1.0)
        self.assertEqual(Streckung.faktor(-5), 1.0)
        self.assertEqual(Streckung.faktor(None), 1.0)
        self.assertEqual(Streckung.faktor('abc'), 1.0)
        self.assertAlmostEqual(Streckung.faktor(11), 1.11, places=9)
        self.assertAlmostEqual(Streckung.faktor(400), 1.0 + Streckung.HOECHSTENS / 100.0, places=9)      # mehr als ein Viertel ist kein Gesicht

    def test_2_zielname_traegt_die_fassung(self):
        quelle = Path('kopf') / 'mesh.glb'
        self.assertEqual(Streckung.ziel(quelle, 11).name, 'mesh_gestreckt_110.glb')
        self.assertNotEqual(Streckung.ziel(quelle, 11), Streckung.ziel(quelle, 6))                      # zwei Werte, zwei Dateien (`artefakte-benennen.md`)

    def test_3_gestreckt_macht_das_netz_hoeher_und_laesst_das_original(self):
        import trimesh

        with Pruefablage.ordner('streckung_') as ordner:
            quelle = Path(ordner) / 'mesh.glb'
            trimesh.Scene(trimesh.creation.box(extents=(0.2, 0.3, 0.25))).export(str(quelle), file_type='glb')
            vorher = trimesh.load(str(quelle), process=False).bounds
            ziel = Streckung.gestreckt(quelle, 11)
            self.assertNotEqual(ziel, quelle)
            self.assertTrue(quelle.is_file())
            nachher = trimesh.load(str(ziel), process=False).bounds
            hoehe_vorher, hoehe_nachher = vorher[1][1] - vorher[0][1], nachher[1][1] - nachher[0][1]
            self.assertAlmostEqual(hoehe_nachher / hoehe_vorher, 1.11, places=3)
            self.assertAlmostEqual((nachher[1][0] - nachher[0][0]) / (vorher[1][0] - vorher[0][0]), 1.0, places=6)     # Breite und Tiefe bleiben
            self.assertAlmostEqual((nachher[1][2] - nachher[0][2]) / (vorher[1][2] - vorher[0][2]), 1.0, places=6)
            self.assertAlmostEqual(float(nachher[0][1] + nachher[1][1]) / 2, float(vorher[0][1] + vorher[1][1]) / 2, places=6)   # um die Mitte

    def test_4_ohne_streckung_die_quelle_und_ein_zweiter_aufruf_schreibt_nicht_neu(self):
        import trimesh

        with Pruefablage.ordner('streckung_') as ordner:
            quelle = Path(ordner) / 'mesh.glb'
            trimesh.Scene(trimesh.creation.box(extents=(0.2, 0.3, 0.25))).export(str(quelle), file_type='glb')
            self.assertEqual(Streckung.gestreckt(quelle, 0), quelle)
            erste = Streckung.gestreckt(quelle, 8)
            stand = erste.stat().st_mtime_ns
            self.assertEqual(Streckung.gestreckt(quelle, 8), erste)
            self.assertEqual(erste.stat().st_mtime_ns, stand)


class DieOption(SimpleTestCase):
    def test_1_vorgabe_aus_und_geklemmt(self):
        self.assertEqual(Optionen.pruefen({})['kopfstreckung'], 0)
        self.assertEqual(Optionen.pruefen({'kopfstreckung': 11})['kopfstreckung'], 11)
        self.assertEqual(Optionen.pruefen({'kopfstreckung': 99})['kopfstreckung'], 25)
        self.assertEqual(Optionen.pruefen({'kopfstreckung': -3})['kopfstreckung'], 0)
        self.assertEqual(Optionen.pruefen({'kopfstreckung': 'x'})['kopfstreckung'], 0)

    def test_2_der_katalog_kennt_sie(self):
        self.assertIn('kopfstreckung', [e['schluessel'] for e in Optionen.katalog()['optionen']])


class DieLandmarkmorphe(SimpleTestCase):
    def test_1_die_lider_sind_nicht_mehr_im_morph(self):
        self.assertEqual(set(Meshfigurlandmarkmorphe.BEREICHE), {'brauen', 'mund', 'nase'})
        alle = {i for ix in Meshfigurlandmarkmorphe.BEREICHE.values() for i in ix}
        self.assertFalse(alle & set(Lage.GRUPPEN['Augen']))                  # kein Lidpunkt zieht mehr (Edgar: „augen sind noch kaputt")
        self.assertEqual(set(Meshfigurlandmarkmorphe.BEREICHE['brauen']), set(Lage.GRUPPEN['Brauen']))


def _netz(faktor=1.0, textur_alpha=None, mitte=(0.0, 0.0, 0.0)):
    textur = None
    if textur_alpha is not None:
        quelle = np.full((4, 4, 4), 255, dtype=np.uint8)
        quelle[:, :, 3] = textur_alpha
        textur = SimpleNamespace(source=quelle, source_channels='RGBA')
    material = SimpleNamespace(baseColorFactor=[1.0, 1.0, 1.0, faktor], baseColorTexture=textur)
    punkte = np.asarray(mitte, dtype=float) + np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    return SimpleNamespace(name=None, primitives=[SimpleNamespace(material=material, positions=punkte)])


class DieZeichenfolge(SimpleTestCase):
    def test_1_alpha_in_der_textur_zaehlt(self):
        self.assertTrue(Reihenfolge.hat_alpha(_netz(textur_alpha=0)))               # Wimpern: Texel mit Alpha 0
        self.assertFalse(Reihenfolge.hat_alpha(_netz(textur_alpha=255)))            # Haut: RGBA, aber überall 255
        self.assertFalse(Reihenfolge.hat_alpha(_netz()))                            # keine Textur

    def test_2_farbfaktor_unter_eins_zaehlt(self):
        self.assertTrue(Reihenfolge.hat_alpha(_netz(faktor=0.5)))
        self.assertFalse(Reihenfolge.hat_alpha(_netz(faktor=1.0)))

    def test_3_der_sortierschluessel_haengt_nur_vom_inhalt_ab(self):
        a = SimpleNamespace(name=None, mesh=_netz(mitte=(0.0, 0.0, 0.0)))
        b = SimpleNamespace(name=None, mesh=_netz(mitte=(0.0, 0.0, 0.0)))
        c = SimpleNamespace(name=None, mesh=_netz(mitte=(0.5, 0.0, 0.0)))
        self.assertEqual(Reihenfolge._inhalt(a), Reihenfolge._inhalt(b))             # gleiche Teile, gleicher Schlüssel (nie eine Speicheradresse)
        self.assertNotEqual(Reihenfolge._inhalt(a), Reihenfolge._inhalt(c))
        self.assertEqual(sorted([c, a], key=Reihenfolge._inhalt)[0], a)
