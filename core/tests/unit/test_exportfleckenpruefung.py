# -*- coding: utf-8 -*-
u"""Der Fleckenprüfer muss fremde Farbe im eigenen Umriss finden — und
legitime Verdeckung durch ein anderes Teil in Ruhe lassen.

DER VORFALL (27.09.2026): Edgar meldete „regression — im obj … die gleichen
Fehler bei den Schuhen" mit einer Nahaufnahme hautfarbener Flecken auf dem
Schuh. Gemessen am echten Export (Damira1/DanceKurz): 16,8 % der Schuh-
Silhouette zeigten Hautfarbe statt der einzigen Schuhfarbe (`mat_16`, keine
eigene Bildkarte — jede Abweichung IST ein Fund, keine Textur könnte sie
erklären). Derselbe erste Messversuch am Kleid schlug fälschlich mit 9,5 %
an — Ursache war NICHT das Kleid, sondern Haarsträhnen, die legitim vor dem
Ausschnitt hängen; nach Beschränkung der Vergleichsszene auf Körper+Kleid
(ohne Haare) fiel der Wert auf 0,45 %. Beide Zahlen kommen hier als Fälle vor.

Kein Blender nötig — gemalte Bilder mit denselben Eigenschaften, in
Millisekunden.
"""
from pathlib import Path

from django.test import SimpleTestCase
from PIL import Image

from core.dienste.exportfleckenpruefung import Exportfleckenpruefung
from core.projekt_temp import ProjektTemp

SCHUH = (150, 62, 58)
HAUT = (205, 160, 140)


def kreis_malen(pfad, groesse=120, radius=50, flecken=()):
    u"""Ein Kreis in `SCHUH`-Farbe, durchsichtiger Rest — `flecken` ist eine
    Liste von (x, y, r) für hautfarbene Kreise darin, wie der durchsteckende
    Fuß."""
    bild = Image.new('RGBA', (groesse, groesse), (0, 0, 0, 0))
    mitte = groesse // 2
    for y in range(groesse):
        for x in range(groesse):
            if (x - mitte) ** 2 + (y - mitte) ** 2 <= radius ** 2:
                bild.putpixel((x, y), (*SCHUH, 255))
    for fx, fy, fr in flecken:
        for y in range(max(0, fy - fr), min(groesse, fy + fr)):
            for x in range(max(0, fx - fr), min(groesse, fx + fr)):
                if (x - fx) ** 2 + (y - fy) ** 2 <= fr ** 2:
                    bild.putpixel((x, y), (*HAUT, 255))
    bild.save(pfad)
    return pfad


def silhouette_malen(pfad, groesse=120, radius=50):
    u"""Dieselbe Kreisform, aber als reine Maske (Alpha) — wie `exportbild.py
    --nur` sie für EIN Teil liefert."""
    bild = Image.new('RGBA', (groesse, groesse), (0, 0, 0, 0))
    mitte = groesse // 2
    for y in range(groesse):
        for x in range(groesse):
            if (x - mitte) ** 2 + (y - mitte) ** 2 <= radius ** 2:
                bild.putpixel((x, y), (255, 255, 255, 255))
    bild.save(pfad)
    return pfad


class ExportfleckenpruefungTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ordner = Path(ProjektTemp.ordner('test_exportflecken'))
        cls.silhouette = silhouette_malen(cls.ordner / 'silhouette.png')

    def test_1_reine_flaeche_ist_nicht_fleckig(self):
        vergleich = kreis_malen(self.ordner / 'sauber.png')
        b = Exportfleckenpruefung(vergleich, self.silhouette).bericht()
        self.assertEqual(b['hauptfarbe'], list(SCHUH) if isinstance(b['hauptfarbe'], list) else tuple(SCHUH))
        self.assertEqual(b['fleckenanteil'], 0.0)
        self.assertFalse(b['fleckig'])

    def test_2_hautfarbener_fleck_schlaegt_an(self):
        u"""DER VORFALL, nachgebaut: ein hautfarbener Kreis mittig im Schuh —
        wie der durchsteckende Fuß, 16,8 % gemessen am echten Export."""
        vergleich = kreis_malen(self.ordner / 'fleck.png', flecken=[(60, 60, 22)])
        b = Exportfleckenpruefung(vergleich, self.silhouette).bericht()
        self.assertGreater(b['fleckenanteil'], 0.10)
        self.assertTrue(b['fleckig'])

    def test_3_kante_allein_loest_nicht_aus(self):
        u"""Ein winziger Fleck (Antialiasing-Rauschen an der Kante) darf
        nicht anschlagen — sonst meldet die Prüfung jede Renderkante
        (`analysewerkzeuge.md`: Fehlalarme sind teurer als fehlende Befunde)."""
        vergleich = kreis_malen(self.ordner / 'kante.png', flecken=[(90, 90, 3)])
        b = Exportfleckenpruefung(vergleich, self.silhouette).bericht()
        self.assertLess(b['fleckenanteil'], Exportfleckenpruefung.SCHWELLE)
        self.assertFalse(b['fleckig'])

    def test_4_fremdes_teil_davor_ist_kein_fleck_wenn_ausgeschlossen(self):
        u"""DIE EIGENE FALLE (27.09.2026, Kleid): Haare, die vor dem Kleid
        hängen, sehen im VOLLBILD wie ein Fleck aus. Wird die Vergleichsszene
        vorher auf Körper+Teil beschränkt (hier: nachgebaut durch ein Bild
        OHNE den Fremdkörper), verschwindet der Fehlalarm."""
        mit_haar = kreis_malen(self.ordner / 'mit_haar.png', flecken=[(60, 30, 12)])
        b_falsch = Exportfleckenpruefung(mit_haar, self.silhouette).bericht()
        self.assertTrue(b_falsch['fleckig'], 'Gegenprobe: mit Fremdkörper schlägt es an')

        ohne_haar = kreis_malen(self.ordner / 'ohne_haar.png')
        b_richtig = Exportfleckenpruefung(ohne_haar, self.silhouette).bericht()
        self.assertFalse(b_richtig['fleckig'])

    def test_5_leere_silhouette_ist_kein_absturz(self):
        leer = Path(self.ordner / 'leer.png')
        Image.new('RGBA', (120, 120), (0, 0, 0, 0)).save(leer)
        b = Exportfleckenpruefung(self.ordner / 'sauber.png', leer).bericht()
        self.assertEqual(b['punkte'], 0)
        self.assertFalse(b['fleckig'])

    def test_6_unterschiedliche_bildgroesse_wirft_verstaendlichen_fehler(self):
        klein = Path(self.ordner / 'klein.png')
        Image.new('RGBA', (10, 10), (0, 0, 0, 0)).save(klein)
        with self.assertRaises(ValueError):
            Exportfleckenpruefung(self.ordner / 'sauber.png', klein).bericht()
