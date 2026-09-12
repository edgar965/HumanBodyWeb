# -*- coding: utf-8 -*-
u"""Die Nacharbeit rechnet gegen Haut PLUS getragene Stuecke (11.09.2026).

Edgar, mit Bild: „Hose NACH dem T-Shirt bauen funktioniert nicht, es wird
an Koerper angepasst, sollte UEBER dem T-Shirt sein." Die Simulation hatte
die Hose ueber das T-Shirt gelegt; das Anlegen zog den Bund danach auf
2 mm vor die HAUT — durch das T-Shirt hindurch.

Kunstkoerper: ein flacher Kasten, oben bei y = 0,1. Ueber der rechten
Haelfte (x > 0) liegt ein „T-Shirt" bei y = 0,12; der Stoff liegt ueberall
bei y = 0,115 — rechts also ZWISCHEN T-Shirt und Haut. Angelegt auf 2 mm
muss er links auf 0,102 landen (Haut) und rechts auf 0,122 (ueber dem
T-Shirt). Ohne das T-Shirt in der Haut (die Sabotage) landet er rechts
auf 0,102 — genau Edgars Bild.
"""
import io
import json
import os
import tempfile

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from GarmentCode.gemeinsamablage import Gemeinsamablage
from GarmentCode.hautmitstoff import Hautmitstoff
from GarmentCode.stoffnacharbeit import Stoffnacharbeit
from GarmentCode.baufeineinstellung import Baufeineinstellung


def _kasten():
    u"""Dichter Kasten 1 x 0,2 x 1 um den Ursprung (Punkte, Dreiecke)."""
    import trimesh
    netz = trimesh.creation.box(extents=(1.0, 0.2, 1.0))
    for _ in range(4):
        netz = netz.subdivide()
    return np.asarray(netz.vertices), np.asarray(netz.faces)


def _gitter(y, x0=-0.4, x1=0.4, n=17):
    u"""Ein triangulierter Stoffteppich bei Hoehe y (Punkte, Dreiecke)."""
    xs = np.linspace(x0, x1, n)
    zs = np.linspace(-0.4, 0.4, n)
    punkte = np.array([[x, y, z] for z in zs for x in xs])
    dreiecke = []
    for i in range(n - 1):
        for j in range(n - 1):
            a = i * n + j
            dreiecke.append([a, a + 1, a + n])
            dreiecke.append([a + 1, a + n + 1, a + n])
    return punkte, np.asarray(dreiecke)


class HautmitstoffTest(SimpleTestCase):

    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.koerper, cls.flaechen = _kasten()
        cls.shirt, _ = _gitter(0.12, x0=0.0, x1=0.35)

    def test_stoffpunkte_haengen_hinter_der_haut_mit_deren_normale(self):
        haut = Hautmitstoff(self.koerper, self.flaechen)
        self.assertTrue(haut.leer)
        self.assertTrue(haut.aufnehmen(self.shirt, 'shirt'))
        punkte, normalen = haut.haut()
        self.assertEqual(len(punkte), len(self.koerper) + len(self.shirt))
        # Die Normale eines Shirt-Punkts ist die der Haut darunter: +y.
        oben = normalen[len(self.koerper):]
        self.assertGreater(float(oben[:, 1].min()), 0.99)
        self.assertEqual(haut.stuecke, ['shirt'])
        self.assertFalse(haut.aufnehmen([[0, 0, 0]], 'zu wenig'))

    def test_angelegt_wird_ueber_dem_getragenen_stueck(self):
        stoff, dreiecke = _gitter(0.115)
        haut = Hautmitstoff(self.koerper, self.flaechen)
        haut.aufnehmen(self.shirt, 'shirt')
        neu, bilanz = haut.anleger(dreiecke).anlegen(stoff, 2.0)
        links = neu[stoff[:, 0] < -0.1, 1]
        rechts = neu[(stoff[:, 0] > 0.1) & (stoff[:, 0] < 0.3), 1]
        self.assertAlmostEqual(float(np.median(links)), 0.102, places=3)
        self.assertAlmostEqual(float(np.median(rechts)), 0.122, places=3)
        self.assertGreater(bilanz['angelegt'], len(stoff) * 0.9)

    def test_ohne_das_stueck_landet_der_stoff_auf_der_haut(self):
        u"""Die Sabotage-Gegenprobe: genau Edgars Bild."""
        stoff, dreiecke = _gitter(0.115)
        haut = Hautmitstoff(self.koerper, self.flaechen)
        neu, _ = haut.anleger(dreiecke).anlegen(stoff, 2.0)
        rechts = neu[(stoff[:, 0] > 0.1) & (stoff[:, 0] < 0.3), 1]
        self.assertAlmostEqual(float(np.median(rechts)), 0.102, places=3)

    def test_knapp_unter_dem_saum_bleibt_der_stoff_ueber_dem_stueck(self):
        u"""Die Saumregel: Ein Punkt 5 mm neben der Kante des Stuecks findet
        die Haut naeher (3 mm) als das Stueck (5,4 mm) — und muss trotzdem
        DAVOR liegen, sonst steht die Kante als Zacke durch (drei rote
        Stellen im Rendering, 11.09.2026). 5 cm weiter liegt er auf der Haut.

        Haut und Stueck hier als dichte Gitter mit Normale +y, ohne
        trimesh: Der Kasten oben ist zu grob, um „Haut naeher als Saum"
        auf 5 mm darzustellen."""
        from GarmentCode.hautmitstoff import Stoffanlegenmitstoff
        from GarmentCode.stoffanlegen import Stoffanlegen
        haut, _ = _gitter(0.100, x0=-0.2, x1=0.2, n=81)          # 5 mm Raster
        shirt, _ = _gitter(0.105, x0=0.0, x1=0.2, n=41)
        stoff, dreiecke = _gitter(0.103, x0=-0.1, x1=0.1, n=41)
        oben = np.tile([0.0, 1.0, 0.0], (len(haut), 1))
        oben_s = np.tile([0.0, 1.0, 0.0], (len(shirt), 1))
        punkte = np.vstack([haut, shirt]); normalen = np.vstack([oben, oben_s])
        anleger = Stoffanlegenmitstoff(punkte, normalen, dreiecke)
        anleger.stuecke_setzen([shirt], [oben_s])
        neu, _ = anleger.anlegen(stoff, 2.0)
        knapp = np.isclose(stoff[:, 0], -0.005)
        weit = np.isclose(stoff[:, 0], -0.05)
        self.assertAlmostEqual(float(np.median(neu[knapp, 1])), 0.107, places=3)
        self.assertAlmostEqual(float(np.median(neu[weit, 1])), 0.102, places=3)
        # Gegenprobe: der Basisweg (euklidisch naechster Hautpunkt) legt den
        # knappen Punkt auf die Haut — genau der Fehler.
        ohne, _ = Stoffanlegen(punkte, normalen, dreiecke).anlegen(stoff, 2.0)
        self.assertAlmostEqual(float(np.median(ohne[knapp, 1])), 0.102, places=3)

    def test_die_korrektur_holt_den_stoff_ueber_das_stueck(self):
        stoff, dreiecke = _gitter(0.115)
        haut = Hautmitstoff(self.koerper, self.flaechen)
        haut.aufnehmen(self.shirt, 'shirt')
        neu, _ = haut.korrektur(dreiecke).anwenden(stoff, abstand_mm=1.0)
        rechts = neu[(stoff[:, 0] > 0.1) & (stoff[:, 0] < 0.3), 1]
        self.assertGreater(float(np.median(rechts)), 0.1205)

    def test_aus_rig_liest_die_punkte_und_uebergeht_muell(self):
        ordner = tempfile.mkdtemp(dir=str(settings.BASE_DIR / 'logs'))
        gut = os.path.join(ordner, 'a_rig.json')
        kaputt = os.path.join(ordner, 'b_rig.json')
        try:
            with open(gut, 'w', encoding='utf-8') as datei:
                json.dump({'punkte': self.shirt.tolist()}, datei)
            with open(kaputt, 'w', encoding='utf-8') as datei:
                datei.write('kein json')
            haut = Hautmitstoff(self.koerper, self.flaechen)
            self.assertTrue(haut.aus_rig(gut))
            self.assertFalse(haut.aus_rig(kaputt))
            self.assertFalse(haut.aus_rig(os.path.join(ordner, 'fehlt_rig.json')))
            self.assertEqual(haut.stuecke, ['a_rig.json'])
        finally:
            for pfad in (gut, kaputt):
                if os.path.exists(pfad):
                    os.remove(pfad)
            os.rmdir(ordner)


class NacharbeitTest(SimpleTestCase):

    databases = set()

    def test_die_nacharbeit_nimmt_getragene_rig_dateien(self):
        koerper, flaechen = _kasten()
        shirt, _ = _gitter(0.12, x0=0.0, x1=0.35)
        stoff, dreiecke = _gitter(0.115)
        ordner = tempfile.mkdtemp(dir=str(settings.BASE_DIR / 'logs'))
        pfad = os.path.join(ordner, 'shirt_rig.json')
        try:
            with open(pfad, 'w', encoding='utf-8') as datei:
                json.dump({'punkte': shirt.tolist()}, datei)
            arbeit = Stoffnacharbeit(koerper, flaechen, dreiecke, getragen=[pfad])
            self.assertIsNotNone(arbeit.haut)
            neu, _, anlage = arbeit.anwenden(stoff, anliegen_mm=2.0)
            self.assertEqual(anlage['ueber_getragene'], ['shirt_rig.json'])
            self.assertAlmostEqual(float(np.median(neu[(stoff[:, 0] > 0.1) & (stoff[:, 0] < 0.3), 1])),
                                   0.122, places=3)
            self.assertEqual(len(arbeit.normalen), len(stoff))
            # ohne getragene Stuecke: der bisherige Weg, Haut allein
            ohne = Stoffnacharbeit(koerper, flaechen, dreiecke)
            self.assertIsNone(ohne.haut)
            self.assertIsNone(Stoffnacharbeit(koerper, flaechen, dreiecke,
                                              getragen=['/gibt/es/nicht_rig.json']).haut)
        finally:
            os.remove(pfad)
            os.rmdir(ordner)

    def test_der_einzelbau_reicht_getragen_bis_zur_nacharbeit(self):
        quelle = io.open(settings.ASSETS_ROOT / 'GarmentCode' / 'drapierdienst.py',
                         encoding='utf-8').read()
        self.assertIn('Stoffnacharbeit(fein_p, fein_f, dreiecke, getragen, netzdatei)', quelle)
        lauf = quelle.index('def lauf(')
        self.assertIn('getragen=getragen', quelle[lauf:quelle.index('def _variantenordner', lauf)])


class GemeinsamTest(SimpleTestCase):

    databases = set()

    def test_je_stueck_gehoeren_die_anderen_zur_haut(self):
        koerper, flaechen = _kasten()
        shirt, _ = _gitter(0.12, x0=0.0, x1=0.35)
        stoff, dreiecke = _gitter(0.115)
        schnitt = {'vorlage': 'hose', 'fein': Baufeineinstellung(anliegen_mm=2.0)}
        neu, anlage, normalen = Gemeinsamablage._anlegen(
            schnitt, stoff, dreiecke, (koerper, flaechen), {'shirt': shirt})
        self.assertEqual(anlage['ueber_getragene'], ['shirt'])
        self.assertAlmostEqual(float(np.median(neu[(stoff[:, 0] > 0.1) & (stoff[:, 0] < 0.3), 1])),
                               0.122, places=3)
        self.assertEqual(len(normalen), len(stoff))
        # `_andere` liefert die korrigierten Punkte aller ANDEREN Teile
        korrigiert = np.arange(30, dtype=float).reshape(10, 3)
        teile = {'hose': {'indizes': [0, 1]}, 'shirt': {'indizes': [2, 3, 4]},
                 'leer': {'indizes': []}}
        andere = Gemeinsamablage._andere(teile, korrigiert, 'hose')
        self.assertEqual(sorted(andere), ['shirt'])
        self.assertEqual(andere['shirt'].tolist(), korrigiert[2:5].tolist())
        quelle = io.open(settings.ASSETS_ROOT / 'GarmentCode' / 'gemeinsamablage.py',
                         encoding='utf-8').read()
        self.assertIn("cls._andere(teile, korrigiert, schnitt.get('teil'))", quelle)
