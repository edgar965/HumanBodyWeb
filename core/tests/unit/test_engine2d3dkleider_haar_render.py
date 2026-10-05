# -*- coding: utf-8 -*-
"""Haar der Vorab-Bühne, Socke ohne Schaft und das allgemeine Render-Rezept (04.10.2026).

DIE ANLÄSSE
===========
Edgar am Auftrag 2026.10.04.11.11.44: „Haar textur und Größe total daneben" (die Frisur zeigte nur ihre orange Strähnengruppe, der Rest verschwand dunkel im Hintergrund),
„die Socken sehen wie Stiefel aus" (Bund +10…27 mm vom Bein, gemessen mit `_wegwerf/sapiens/socken_profil.py`) und „warum sehe ich Rendern … nicht" (der Knopf war nur bei
Randy möglich: nur dort lag eine `arbeit/render/rezept.json`).

WAS DIESE PRÜFUNG NICHT IST
===========================
Kunstbilder und Attrappen, kein Netz, keine Grafikkarte, kein Mitsuba. Dass die Frisur im Standmodell grau statt orange ist, dass die Socke am Bund anliegt und dass das Video wirklich
entsteht, zeigen nur Lauf und Probelauf (`ergebnis.haar`, `socken_profil.py`, `Render-Läufe`). Geschrieben am 04.10.2026, nicht gelaufen.

BDD - GEGEBEN / DANN
====================
    Ein Foto mit Haarklasse, ein Saum aus Weiß am Rand            ... die Haarfarbe ist die Mitte des Haars, der Saum zählt nicht; ohne Haar `(None, 0)`
    Die Segmentierung kennt die Haarfarbe                          ... das Vorab-Haar wird erst umgefärbt, dann mit DIESER Farbe getönt
    Sie kennt sie nicht, die Frisur hat eine Netzfarbe             ... umfärben und tönen mit der Netzfarbe; ohne beides bleibt das Haar, wie es ist
    Eine Socke und ein Hemd mit gleich weit abstehendem Netz       ... die Socke liegt höchstens `HOECHST` an, das Hemd bis `ABSTAND_MAX`
    Option `koerper.tor`                                           ... Vorgabe „anhalten", „melden" nur wenn gewählt; der Lauf der Kette trägt sie (`Engine2d3dKleiderkoerperlauf.tor`)
    Ein Auftrag ohne eigene rezept.json                            ... das allgemeine Rezept; mit eigener geht deren Rezept vor; `einrichten` kopiert, `figur.json` bleibt
"""

import json
from pathlib import Path
from types import SimpleNamespace

from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderrender import Engine2d3dKleiderrender
from core.dienste.engine2d3dkleiderrenderallgemein import Engine2d3dKleiderrenderallgemein
from core.dienste.fotohuelle import Fotohuelle
from core.dienste.standvorabkleider import Standvorabkleider

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np  # noqa: E402
from sapiens_foto import Sapiensfoto  # noqa: E402
from sapiens_klassen import Sapiensklassen  # noqa: E402


class DieHaarfarbeDerFotos(SimpleTestCase):
    HAAR = (120, 118, 115)

    def _foto(self):
        """40 × 40: die Person beginnt bei Zeile 12, Haar liegt in 10..30 × 10..30; Zeile 10–11 (außerhalb der Person) und die drei Zeilen am Rand (12–14, gemischt mit Weiß) zählen nicht."""
        alpha = np.ones((40, 40), dtype=bool)
        labels = np.zeros((40, 40), dtype=np.uint8)
        labels[10:30, 10:30] = Sapiensklassen.NAMEN.index('Hair')
        bild = np.full((40, 40, 3), 60, dtype=np.uint8)
        bild[10:30, 10:30] = self.HAAR
        bild[10:15, 10:30] = 255                      # Weiß vom Hintergrund im Alpha-Saum und davor
        alpha[:12, :] = False
        return labels, bild, alpha

    def test_die_mitte_des_haars_zaehlt_nicht_der_weisse_saum(self):
        labels, bild, alpha = self._foto()
        farbe, pixel = Sapiensfoto.haarfarbe(labels, bild, alpha)
        self.assertEqual(farbe, list(self.HAAR))
        self.assertGreater(pixel, 0)

    def test_ohne_haar_keine_farbe(self):
        labels, bild, alpha = self._foto()
        labels[:] = 0
        self.assertEqual(Sapiensfoto.haarfarbe(labels, bild, alpha), (None, 0))


class DasVorabHaar(SimpleTestCase):
    class Attrappe:
        def __init__(self):
            self.aufrufe = []

        def haar_umfaerben(self, kennung):
            self.aufrufe.append(('umfaerben', kennung))
            return self

        def haar_farbe(self, farbe):
            self.aufrufe.append(('farbe', farbe))
            return self

    def test_mit_der_fotofarbe_erst_umfaerben_dann_toenen(self):
        modell = self.Attrappe()
        Standvorabkleider._haar_faerben(modell, 'mavick_hair_style', '#595150', [0.8, 0.8, 0.78])
        self.assertEqual([a[0] for a in modell.aufrufe], ['umfaerben', 'farbe'])
        self.assertEqual(modell.aufrufe[0][1], 'mavick_hair_style')
        rot, gruen, blau = (int(modell.aufrufe[1][1][i:i + 2], 16) for i in (1, 3, 5))
        self.assertTrue(rot == gruen == blau, 'unbuntes Haar bleibt unbunt (wie Runde 1)')
        self.assertGreater(rot, 0x59, 'die helle Fotofarbe tönt heller als die Netzfarbe #595150')

    def test_ohne_fotofarbe_gilt_die_netzfarbe(self):
        modell = self.Attrappe()
        Standvorabkleider._haar_faerben(modell, 'kin_hair', '#595150', None)
        self.assertEqual([a[0] for a in modell.aufrufe], ['umfaerben', 'farbe'])

    def test_ohne_jede_farbe_bleibt_das_haar_wie_es_ist(self):
        modell = self.Attrappe()
        Standvorabkleider._haar_faerben(modell, 'kin_hair', None, None)
        self.assertEqual(modell.aufrufe, [])

    def test_die_fotofarbe_kommt_aus_der_segmentierung(self):
        ordner = Path(self.enterContext(Pruefablage.ordner()))
        (ordner / 'segmentierung.json').write_text(json.dumps({'kennzahlen': {'haarfarbe': {'rgb': [204, 102, 51], 'pixel': 10}}}), encoding='utf-8')
        ablage = SimpleNamespace(segmentierung=lambda name='': ordner / name)
        with mock_ablage(ablage):
            self.assertEqual(Standvorabkleider.haarfarbe(SimpleNamespace(kennung='x')), [0.8, 0.4, 0.2])

    def test_ohne_segmentierung_keine_fotofarbe(self):
        ordner = Path(self.enterContext(Pruefablage.ordner()))
        ablage = SimpleNamespace(segmentierung=lambda name='': ordner / name)
        with mock_ablage(ablage):
            self.assertIsNone(Standvorabkleider.haarfarbe(SimpleNamespace(kennung='x')))


def mock_ablage(ablage):
    from unittest import mock
    return mock.patch('core.daten.engine2d3dkleiderablage.Engine2d3dKleiderablage', lambda kennung: ablage)


class DieSockeLiegtAn(SimpleTestCase):
    def test_die_grenzen_je_stueck(self):
        self.assertEqual(Fotohuelle.HOECHST[Fotohuelle.FUESSE], 0.008)
        self.assertNotIn(1, Fotohuelle.HOECHST)           # das Hemd darf bis `ABSTAND_MAX` locker fallen
        self.assertLess(Fotohuelle.HOECHST[Fotohuelle.FUESSE], Fotohuelle.ABSTAND_MAX)

    def test_aufliegen_nimmt_den_hoechstwert_des_stuecks(self):
        huelle = Fotohuelle.__new__(Fotohuelle)           # nur die Rechnung, kein Netz
        seitwaerts = np.array([[1.0, 0.0, 0.0]])
        self.assertAlmostEqual(float(huelle._aufliegen(seitwaerts, 0.002, 0.008)[0]), 0.008)
        self.assertAlmostEqual(float(huelle._aufliegen(seitwaerts, 0.002)[0]), Fotohuelle.ABSTAND_MAX)


class DasKoerperTor(SimpleTestCase):
    def test_vorgabe_anhalten_melden_nur_wenn_gewaehlt(self):
        from core.dienste.engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen as Optionen
        self.assertEqual(Optionen.pruefen({})['tor'], 'anhalten')
        self.assertEqual(Optionen.pruefen({'tor': 'melden'})['tor'], 'melden')
        self.assertEqual(Optionen.pruefen({'tor': 'unsinn'})['tor'], 'anhalten')
        self.assertIn('tor', [e['schluessel'] for e in Optionen.katalog()['optionen']])

    def test_der_lauf_der_kette_kennt_die_wahl(self):
        from core.dienste.engine2d3dkleiderkoerperlauf import Engine2d3dKleiderkoerperlauf
        aussen = SimpleNamespace(job=SimpleNamespace(optionen={}), ablage=None, optionen={'basis': 'masculine'}, Angehalten=Exception)
        self.assertEqual(Engine2d3dKleiderkoerperlauf(aussen, {'tor': 'melden'}).tor, 'melden')
        self.assertEqual(Engine2d3dKleiderkoerperlauf(aussen, {}).tor, 'anhalten')


class DasAllgemeineRezept(SimpleTestCase):
    def _render(self, ordner):
        render = Engine2d3dKleiderrender.__new__(Engine2d3dKleiderrender)
        render.job = SimpleNamespace(kennung='x')
        render._datei = lambda name: ordner / name
        return render

    def test_ohne_eigenes_rezept_das_allgemeine(self):
        ordner = Path(self.enterContext(Pruefablage.ordner()))
        rezept = self._render(ordner).rezept()
        self.assertIsNotNone(rezept, 'die Vorlage Figurfilm/standfilm liegt im Projekt')
        self.assertTrue(rezept['allgemein'])
        self.assertEqual(Path(rezept['programme']), ordner / 'film')
        self.assertFalse((ordner / 'film').exists(), 'rezept() schreibt nichts — der Zustand der Seite fragt es bei jeder Abfrage')

    def test_ein_eigenes_rezept_geht_vor(self):
        ordner = Path(self.enterContext(Pruefablage.ordner()))
        (ordner / 'rezept.json').write_text(json.dumps({'programme': 'A:/irgendwo', 'name': 'render'}), encoding='utf-8')
        rezept = self._render(ordner).rezept()
        self.assertEqual(rezept['programme'], 'A:/irgendwo')
        self.assertNotIn('allgemein', rezept)

    def test_einrichten_kopiert_die_programme_und_laesst_figur_json_stehen(self):
        ordner = Path(self.enterContext(Pruefablage.ordner()))
        allgemein = Engine2d3dKleiderrenderallgemein(ordner)
        ziel = allgemein.einrichten()
        for name in Engine2d3dKleiderrenderallgemein.PROGRAMME + Engine2d3dKleiderrenderallgemein.ZUSTAND:
            self.assertTrue((ziel / name).is_file(), name)
        (ziel / 'figur.json').write_text('{"glb": "eigener.glb"}', encoding='utf-8')
        (ziel / 'video_bauen.py').write_text('veraltet', encoding='utf-8')
        allgemein.einrichten()
        self.assertEqual(json.loads((ziel / 'figur.json').read_text(encoding='utf-8')), {'glb': 'eigener.glb'}, 'figur.json ist Zustand des Auftrags')
        self.assertNotEqual((ziel / 'video_bauen.py').read_text(encoding='utf-8'), 'veraltet', 'die Programme kommen bei jedem Lauf von der Vorlage')
