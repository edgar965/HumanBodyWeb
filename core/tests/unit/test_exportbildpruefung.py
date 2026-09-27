# -*- coding: utf-8 -*-
u"""Der Bildprüfer muss farblose Stellen finden — und Weiß, das dazugehört, in Ruhe lassen.

Edgar hat dreimal „immer noch Fehler" gemeldet, und jedes Mal steckte eine
andere Ursache dahinter, aber immer dieselbe ERSCHEINUNG: eine Stelle der
Figur, die im fremden Programm farblos ist. Ein Prüfer, der danach sucht,
findet alle drei — solange er nicht bei jedem hellen Fleck Alarm schlägt.

Belegt am echten Fall (26.09.2026, Blender-Rendering von Damira1, 700x1000):

    fehlerhafte Ausgabe:  2,0 % farblos, Kniestreifen 13,7 %
    berichtigte Ausgabe:  0,1 % farblos, kein Streifen über 1,7 %

Hier wird nicht das 261-MB-Modell geprüft, sondern ein gemaltes Bild mit
denselben Eigenschaften — der Fall muss in Millisekunden laufen.
"""
from pathlib import Path

from django.test import SimpleTestCase
from PIL import Image

from core.dienste.exportbildpruefung import Exportbildpruefung
from core.projekt_temp import ProjektTemp

HAUT = (205, 160, 140)
BLAU = (30, 50, 200)
GRAU = (185, 190, 195)        # die Fehlfarbe: leerer Kartenrand


def figur_malen(pfad, fleck=None):
    u"""Durchsichtiger Hintergrund, in der Mitte eine „Figur": oben Haut,
    unten Kleid. `fleck` = (von_y, bis_y) setzt dort den grauen Fehler."""
    breite, hoehe = 100, 200
    bild = Image.new('RGBA', (breite, hoehe), (0, 0, 0, 0))
    for y in range(hoehe):
        farbe = HAUT if y < hoehe // 2 else BLAU
        if fleck and fleck[0] <= y < fleck[1]:
            farbe = GRAU
        for x in range(30, 70):
            bild.putpixel((x, y), (*farbe, 255))
    bild.save(pfad)
    return pfad


class ExportbildpruefungTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ordner = Path(ProjektTemp.ordner('test_exportbild'))

    def test_1_saubere_figur_ist_farbig(self):
        pfad = figur_malen(self.ordner / 'sauber.png')
        b = Exportbildpruefung(pfad).bericht()
        self.assertEqual(b['punkte'], 40 * 200, 'nur die Figur zählt, nicht der Hintergrund')
        self.assertEqual(b['farblos'], 0)

    def test_2_grauer_fleck_wird_gefunden_und_verortet(self):
        u"""DER VORFALL: hellgraue Flecken an Hals, Knie und Fingern, weil die
        Bildkarten auf dem Kopf standen. Am echten Modell schlug der
        Kniestreifen mit 13,7 % aus."""
        pfad = figur_malen(self.ordner / 'fleck.png', fleck=(120, 140))
        b = Exportbildpruefung(pfad).bericht()
        self.assertEqual(b['farblos'], 40 * 20)
        self.assertAlmostEqual(b['anteil'], 0.1, places=3)
        self.assertEqual(b['schlimmster']['nr'], 6, 'der Fleck liegt im siebten Zehntel')
        self.assertGreater(b['schlimmster']['anteil'], 0.9)

    def test_3_der_hintergrund_zaehlt_nicht_mit(self):
        u"""Das Rendering hat einen DURCHSICHTIGEN Hintergrund. Würde er
        mitgezählt, wäre jedes Bild „zu über 70 % farblos" — der Prüfer
        meldete dann immer Alarm und niemand sähe mehr hin."""
        pfad = figur_malen(self.ordner / 'hintergrund.png')
        b = Exportbildpruefung(pfad).bericht()
        self.assertLess(b['punkte'], 100 * 200)

    def test_4_dunkles_grau_ist_kein_befund(self):
        u"""Ein dunkler Schuh oder ein Schatten ist grau, aber nicht hell —
        die Fehlstellen waren HELLE Kartenränder. Ohne diese Grenze meldete
        der Prüfer jeden Schatten (`analysewerkzeuge.md`)."""
        breite, hoehe = 100, 200
        bild = Image.new('RGBA', (breite, hoehe), (0, 0, 0, 0))
        for y in range(hoehe):
            for x in range(30, 70):
                bild.putpixel((x, y), (40, 42, 44, 255))
        pfad = self.ordner / 'dunkel.png'
        bild.save(pfad)
        self.assertEqual(Exportbildpruefung(pfad).bericht()['farblos'], 0)

    def test_5_bericht_zeigt_die_streifen(self):
        pfad = figur_malen(self.ordner / 'lesbar.png', fleck=(120, 140))
        zeilen = Exportbildpruefung.zeilen(Exportbildpruefung(pfad).bericht())
        self.assertTrue(any('Streifen 6' in z for z in zeilen), zeilen)
