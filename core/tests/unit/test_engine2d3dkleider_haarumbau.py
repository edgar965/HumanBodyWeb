# -*- coding: utf-8 -*-
"""Haarumbau, Haltung im Startrezept, Fotohaut Fassung 2 und der Tönungsfaktor des Renders (05.10.2026, Edgar: „Das Haar in der Vorlage soll perfekt auf ein Haar aus Genesis umgebaut werden … untersuche richtig
und fixe", nach Runde 1 von Sapiens 2: Hemd hell, Arme gespreizt, Gesicht mit Schmieren, Haar auf der Stirn).

1. `Haarumbau._schneiden`: Dreiecke unter der Haarlinie fallen weg, Gruppen (Indizes) und Texturen (Dreiecke) zählen neu; Stranghaar und Bart bleiben; nichts zu schneiden → dasselbe Teil.
2. `Haarumbau.anwenden`: ohne Ablage, bei langem Haar oder ohne Hülle bleibt das Haar, wie es ist; sonst Frisur + Kappe.
3. `Haarumbau.anzeigefarbe`: Tönung × 2 × Grau-Mittel × `KARTEN_HELL`.
4. `Haarkappe.kurzhaarig` und `grad_je_punkt`: Radius des Netzhaars zwischen −37° und 0° unter 0,17 m.
5. `Mitsubamaterial.textur`: der Faktor wird nach linear gerechnet (vorher: unumgerechnet → Hemd 47 % zu hell).
6. `Fotoprojektion.ansicht(ausschluss=…)` und die Konstanten der Fotohaut Fassung 2 (Kopfkachel ausgenommen, neu gerechnet bei Fassung 1).
7. `Standvorabkleider.haltungszeilen` (die Zeilen der Haltung aus `haltung_foto`) und `_haar_faerben(hell=…)`.
8. `Iterationsoptionen.haarumbau`: Vorgabe an, „aus" schaltet ab.

Sabotage: in `Mitsubamaterial.textur` `cls.linear(` streichen → Fall 5 rot; in `Haarumbau._schneiden` die Zählung `davor` weglassen → Fall 1 rot; `AUSGENOMMEN = ()` → Fall 6 rot.
"""

import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.modellmitkleidern import ModellMitKleidern
from iterationen2d3d.fotoprojektion import Fotoprojektion

from core.dienste.haarfarbmessung import Haarfarbmessung
from core.dienste.haarkappe import Haarkappe
from core.dienste.haarklemme import Haarklemme
from core.dienste.haarumbau import Haarumbau
from core.dienste.iterationsoptionen import Iterationsoptionen
from core.dienste.koerperfotoprojektion import Koerperfotoprojektion
from core.dienste.mitsubamaterial import Mitsubamaterial
from core.dienste.standvorabkleider import Standvorabkleider

PROJEKTTEMP = Path(__file__).resolve().parents[3] / 'ProjektTemp'
MITTE = np.array([0.0, 1.6, 0.0])


class _Linie:
    """Eine Kappe, deren Haarlinie bei y = 1,6 liegt: darüber (y > 1,6) Haar (grad > 0), darunter nicht."""

    def grad_je_punkt(self, punkte, reichweite=None):
        return (np.asarray(punkte)[:, 1] - 1.6) * 100.0


def _karte(radius_nacken):
    """Hülle des Netzhaars: 0,12 m rundum, im Bereich −37°…0° (Nacken) `radius_nacken`."""
    karte = np.full((36, 72), 0.12)
    el = (np.arange(36) + 0.5) * 5.0 - 90.0
    karte[(el >= Haarkappe.UNTEN) & (el <= 0.0)] = radius_nacken
    return karte


def _teil():
    """Vier Dreiecke in zwei Gruppen (je zwei): Dreieck 0 und 2 liegen über der Linie (bleiben), 1 und 3 darunter (fallen weg)."""
    punkte = np.array([[0, 1.7, 0], [0.1, 1.7, 0], [0, 1.7, 0.1],           # Dreieck 0: darüber
                       [0, 1.5, 0], [0.1, 1.5, 0], [0, 1.5, 0.1],           # Dreieck 1: darunter
                       [0, 1.8, 0], [0.1, 1.8, 0], [0, 1.8, 0.1],           # Dreieck 2: darüber
                       [0, 1.4, 0], [0.1, 1.4, 0], [0, 1.4, 0.1]], dtype=float)    # Dreieck 3: darunter
    dreiecke = np.arange(12).reshape(-1, 3)
    return {'art': 'haar', 'sorte': 'mavick_hair_style', 'punkte': punkte, 'dreiecke': dreiecke,
            'gruppen': [{'name': 'a', 'index_ab': 0, 'index_anzahl': 6}, {'name': 'b', 'index_ab': 6, 'index_anzahl': 6}],
            'textur': [{'ab': 0, 'anzahl': 2, 'albedo': 'a.png', 'faktor': (1, 1, 1)}, {'ab': 2, 'anzahl': 2, 'albedo': 'b.png', 'faktor': (1, 1, 1)}]}


class DasSchneidenDerFrisur(SimpleTestCase):
    def test_1_unter_der_haarlinie_faellt_weg_und_gruppen_und_texturen_zaehlen_neu(self):
        neu = Haarumbau._schneiden(_teil(), _Linie())
        self.assertEqual(neu['dreiecke'].shape, (2, 3))
        self.assertEqual(neu['dreiecke'].tolist(), [[0, 1, 2], [6, 7, 8]])
        self.assertEqual([(g['index_ab'], g['index_anzahl']) for g in neu['gruppen']], [(0, 3), (3, 3)])         # Indizes: je 1 Dreieck
        self.assertEqual([(x['ab'], x['anzahl']) for x in neu['textur']], [(0, 1), (1, 1)])                       # Dreiecke
        self.assertEqual(neu['textur'][1]['albedo'], 'b.png')

    def test_2_stranghaar_bart_und_nichtshaar_bleiben(self):
        strang = dict(_teil(), kurven={'punkte': np.zeros((3, 3))})
        bart = dict(_teil(), sorte='x_beard')
        kleid = dict(_teil(), art='kleidung')
        for teil in (strang, bart, kleid):
            self.assertIs(Haarumbau._schneiden(teil, _Linie()), teil)

    def test_3_liegt_alles_ueber_der_linie_bleibt_das_teil_dasselbe(self):
        teil = _teil()
        teil['punkte'] = teil['punkte'] + np.array([0.0, 0.5, 0.0])
        self.assertIs(Haarumbau._schneiden(teil, _Linie()), teil)

    def test_4_die_anzeigefarbe_ist_toenung_mal_zwei_mal_grau_mal_kartenhelligkeit(self):
        farbe = Haarumbau.anzeigefarbe('#373737')
        self.assertAlmostEqual(farbe[0], 55 / 255.0 * 2.0 * 0.75 * Haarumbau.KARTEN_HELL, places=4)
        self.assertAlmostEqual(Haarumbau.anzeigefarbe('#ffffff')[0], 2.0 * 0.75 * Haarumbau.KARTEN_HELL, places=6)


class DerUmbauAlsGanzes(SimpleTestCase):
    @staticmethod
    def _koerper():
        return {'punkte': np.zeros((4, 3)), 'dreiecke': np.array([[0, 1, 2]]), 'haut': {}}

    def test_ohne_ablage_oder_ohne_haar_bleibt_alles(self):
        haar = [_teil()]
        self.assertIs(Haarumbau.anwenden(haar, self._koerper(), None, '#808080'), haar)
        self.assertEqual(Haarumbau.anwenden([], self._koerper(), SimpleNamespace(), '#808080'), [])

    def test_bei_langem_haar_oder_ohne_huelle_bleibt_das_haar(self):
        haar = [_teil()]
        with mock.patch.object(Haarklemme, 'fuer', return_value=Haarklemme(_karte(0.25), MITTE)):
            self.assertIs(Haarumbau.anwenden(haar, self._koerper(), SimpleNamespace(), '#808080'), haar)
        with mock.patch.object(Haarklemme, 'fuer', return_value=None):
            self.assertIs(Haarumbau.anwenden(haar, self._koerper(), SimpleNamespace(), '#808080'), haar)

    def test_ein_fehler_im_umbau_haelt_nichts_auf(self):
        haar = [_teil()]
        with mock.patch.object(Haarkappe, 'kurzhaarig', side_effect=RuntimeError('kaputt')):
            self.assertIs(Haarumbau.anwenden(haar, self._koerper(), SimpleNamespace(), '#808080'), haar)

    def test_kurzhaarig_nach_dem_radius_im_nacken(self):
        for radius, soll in ((0.12, True), (0.16, True), (0.19, False)):
            with mock.patch.object(Haarklemme, 'fuer', return_value=Haarklemme(_karte(radius), MITTE)):
                self.assertEqual(Haarkappe(SimpleNamespace(), self._koerper()).kurzhaarig(), soll, radius)
        with mock.patch.object(Haarklemme, 'fuer', return_value=None):
            self.assertFalse(Haarkappe(SimpleNamespace(), self._koerper()).kurzhaarig())


class DerToenungsfaktorImRender(SimpleTestCase):
    def test_5_der_faktor_geht_als_srgb_in_die_multiplikation(self):
        from PIL import Image
        ordner = Path(tempfile.mkdtemp(prefix='mitsuba_', dir=str(PROJEKTTEMP)))
        try:
            pfad = ordner / 'grau.png'
            Image.fromarray(np.full((8, 8, 3), 191, dtype=np.uint8), 'RGB').save(pfad)                  # sRGB 0,75, wie die Schicht `grau`
            material = Mitsubamaterial.textur(str(pfad), (0.416, 0.392, 0.376), None, 64)
            feld = np.asarray(material['bsdf']['base_color']['data'])
            soll = Mitsubamaterial.linear(191 / 255.0) * Mitsubamaterial.linear(0.416)
            self.assertAlmostEqual(float(feld[0, 0, 0]), float(soll), places=4)
            # im Bild (sRGB) ergibt das etwa Fotofarbe = Grau × 2 × Tönung (0,31), nicht 0,50 wie mit dem unumgerechneten Faktor
            self.assertAlmostEqual(float(Mitsubamaterial.srgb(feld[0, 0, 0])), 0.30, delta=0.02)
        finally:
            shutil.rmtree(ordner, ignore_errors=True)


class DieFotohautFassung2(SimpleTestCase):
    def test_6_die_kopfkachel_bleibt_ohne_registrierung_und_alte_fassungen_werden_neu_gerechnet(self):
        self.assertIn(1001, Koerperfotoprojektion.AUSGENOMMEN)               # Foto nur über die Kopfregistrierung (`Kopfregistrierung`), sonst bleibt die gebackene
        self.assertEqual(Koerperfotoprojektion.FASSUNG, 4)                  # 3: Licht je Ansicht, Hände ohne Fotofarbe (05.10.2026); 4: Kopfkachel aus dem Vorderfoto (07.10.2026)
        for veraltet in (1, 2, 3):
            alt = SimpleNamespace(ergebnis={'fototextur': {'kacheln': {'1001': 'a.jpg'}, 'hautfoto': {'fassung': veraltet}}})
            self.assertTrue(Koerperfotoprojektion(alt, None).noetig(), 'Fassung %d wird neu gerechnet' % veraltet)
        neu = SimpleNamespace(ergebnis={'fototextur': {'kacheln': {'1001': 'a.jpg'}, 'hautfoto': {'fassung': Koerperfotoprojektion.FASSUNG}}})
        self.assertFalse(Koerperfotoprojektion(neu, None).noetig())

    def test_6b_der_ausschluss_nimmt_pixel_aus_der_erweiterten_teilmaske(self):
        projektion = Fotoprojektion(mitte=[0.0, 1.0, 0.0], halb=1.2, render_groesse=(20, 30))
        foto = np.zeros((30, 20, 3), np.float32)
        voll = np.ones((30, 20), bool)
        teil = np.zeros((30, 20), bool)
        teil[10:20, 5:15] = True
        ausschluss = np.zeros((30, 20), bool)
        ausschluss[:, :8] = True
        projektion.ansicht(0.0, (10.0, 0.0, 30.0), foto, voll, teil)
        projektion.ansicht(0.0, (10.0, 0.0, 30.0), foto, voll, teil, ausschluss)
        ohne, mit = projektion.ansichten[0]['drin'], projektion.ansichten[1]['drin']
        self.assertTrue(ohne[15, 5])
        self.assertFalse(mit[15, 5])                      # im Ausschluss
        self.assertTrue(mit[15, 12])                      # außerhalb bleibt es
        self.assertEqual(int((ohne & ~ausschluss != mit).sum()), 0)


class DieHaltungImStartrezept(SimpleTestCase):
    def test_7_die_zeilen_der_haltung_aus_haltung_foto(self):
        job = SimpleNamespace(kennung='x', ergebnis={'kreislauf': {'haltung_foto': {'seitlich': 14.5, 'beuge': 22.6, 'arme': 5, 'beine': 8.9}}})
        self.assertEqual(Standvorabkleider.haltungszeilen(job), [
            'm.haltung(28.3)', "m.haltung_gelenk('l_forearm', 'y', -9.0)", "m.haltung_gelenk('r_forearm', 'y', 9.0)",
            "m.haltung_gelenk('l_thigh', 'z', 4.8)", "m.haltung_gelenk('r_thigh', 'z', -4.8)"])

    def test_7b_ohne_fotolandmarken_bleibt_die_a_pose(self):
        job = SimpleNamespace(kennung='x', ergebnis={'kreislauf': {}})
        with mock.patch('core.dienste.iterationsreferenz.Iterationsreferenz.laden', side_effect=OSError('keine Fotos')):
            self.assertEqual(Standvorabkleider.haltungszeilen(job), [])

    def test_7c_die_haartoenung_wird_durch_die_kartenhelligkeit_geteilt(self):
        render, buehne = ModellMitKleidern(), ModellMitKleidern()
        Standvorabkleider._haar_faerben(render, 'mavick_hair_style', None, [0.32, 0.32, 0.32], hell=0.64)
        Standvorabkleider._haar_faerben(buehne, 'mavick_hair_style', None, [0.32, 0.32, 0.32])
        self.assertEqual(render.farben['haar'], '#555555')     # 0,32 ÷ 0,64 ÷ 1,5 = 0,333
        self.assertEqual(buehne.farben['haar'], '#363636')     # 0,32 ÷ 1,5 = 0,213


class DieOptionHaarumbau(SimpleTestCase):
    def test_8_vorgabe_herrenhaar_an_baut_um_aus_schaltet_ab(self):
        self.assertEqual(Iterationsoptionen.haarumbau(SimpleNamespace(optionen=None)), 'herren')                       # Vorgabe seit 05.10.2026: das eigene Herrenhaar
        self.assertEqual(Iterationsoptionen.haarumbau(SimpleNamespace(optionen={'iterationen': {'runden': 3}})), 'herren')
        self.assertIs(Iterationsoptionen.haarumbau(SimpleNamespace(optionen={'iterationen': {'haarumbau': 'an'}})), True)   # Frisur umbauen
        self.assertIs(Iterationsoptionen.haarumbau(SimpleNamespace(optionen={'iterationen': {'haarumbau': 'aus'}})), False)
        self.assertEqual(Iterationsoptionen.pruefen({'haarumbau': 'quatsch'})['haarumbau'], 'herren')
        self.assertEqual((Iterationsoptionen.haarart('herren'), Iterationsoptionen.haarart('an'), Iterationsoptionen.haarart('aus')), ('herren', True, False))


class DieHaarfarbmessung(SimpleTestCase):
    """`Haarfarbmessung` (05.10.2026): Foto gegen Render über die Pixel, in denen BEIDE Haar zeigen — statt einer Wegwerf-Messung je Frisur."""

    def test_9_nur_gemeinsame_haarpixel_zaehlen_und_das_verhaeltnis_ist_render_durch_foto(self):
        foto, render = np.full((40, 40, 3), 200, np.uint8), np.full((40, 40, 3), 100, np.uint8)
        foto_haar, render_haar = np.zeros((40, 40), bool), np.zeros((40, 40), bool)
        foto_haar[5:35, 5:35] = True
        render_haar[10:40, 10:40] = True               # gemeinsam: 10…34 (25 × 25), nach 3 Pixeln Rand 19 × 19
        foto[:, :, 0][~foto_haar] = 0                  # außerhalb des Fotohaars andere Farbe: darf nicht in den Mittelwert
        n, f, r = Haarfarbmessung.ansicht(render, foto, foto_haar, render_haar)
        self.assertEqual(n, 19 * 19)
        np.testing.assert_allclose(f, 200 / 255)
        np.testing.assert_allclose(r, 100 / 255)
        aus = Haarfarbmessung.auswerten([(n, f, r), None])
        self.assertEqual((aus["verhaeltnis"], aus["pixel"]), (0.5, 19 * 19))

    def test_9b_zu_wenige_pixel_oder_keine_ansicht_geben_keine_aussage(self):
        klein = np.zeros((40, 40), bool)
        klein[10:20, 10:20] = True                     # nach dem Rand 4 × 4 = 16 < 50
        bild = np.zeros((40, 40, 3), np.uint8)
        self.assertIsNone(Haarfarbmessung.ansicht(bild, bild, klein, klein))
        self.assertIsNone(Haarfarbmessung.auswerten([None, None]))
