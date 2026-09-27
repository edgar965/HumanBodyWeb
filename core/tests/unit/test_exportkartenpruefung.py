# -*- coding: utf-8 -*-
u"""Der Prüfer, der die verdrehten Karten findet — und keine Fehlalarme wirft.

Ein eigener Prüfer ist so viel wert wie seine Gegenproben
(`~/.claude/rules/analysewerkzeuge.md`: Fehlalarme sind teurer als fehlende
Befunde). Deshalb steht hier beides:

* eine SAUBERE Ausgabe, die er durchwinken muss,
* dieselbe Ausgabe mit gespiegelter Karte, die er melden muss,
* eine Karte OHNE leeren Rand, bei der er schweigen muss, weil er dort
  blind ist — genau die Stelle, an der ein zu eifriger Prüfer Unsinn meldet.

Gebaut wird eine winzige `.obj` mit zwei Flächen auf einer 8x8-Karte: oben
eine gefüllte Insel, unten leerer Rand. Kein Genesis 9, keine Bilder aus dem
Projekt — der Fall muss in Millisekunden laufen.
"""
from pathlib import Path

from django.test import SimpleTestCase
from PIL import Image

from core.dienste.exportkartenpruefung import Exportkartenpruefung
from core.projekt_temp import ProjektTemp

#: Karte 16x16: eine Hälfte Haut, die andere leerer Rand.
#:
#: Die Haut RAUSCHT — und das ist kein Zierrat, sondern der Kern der
#: Unterscheidung: Der leere Rand einer exportierten Karte ist EINE flache
#: Farbe, echter Bildinhalt hat viele. Die erste Fassung des Testbilds hatte
#: nur vier Hauttöne im Abstand von zwei Stufen; damit galt jeder davon als
#: Randfarbe und der Prüfer meldete Unsinn.
KANTE = 16
RAND = (183, 188, 194)
HAUT = (200, 150, 120)


def karte_schreiben(pfad, gefuellt_oben=True, ganz_voll=False):
    import random
    wuerfel = random.Random(7)          # fest, damit der Fall reproduzierbar ist
    bild = Image.new('RGB', (KANTE, KANTE), RAND)
    halb = KANTE // 2
    zeilen = range(0, halb) if gefuellt_oben else range(halb, KANTE)
    for y in (range(KANTE) if ganz_voll else zeilen):
        for x in range(KANTE):
            bild.putpixel((x, y), tuple(
                max(0, min(255, k + wuerfel.randint(-12, 12))) for k in HAUT))
    bild.save(pfad)


def ausgabe_schreiben(ordner, name, v_oben=True, **karte):
    u"""Zehn Flächen, alle mit UV in der OBEREN Kartenhälfte (v = 0,75).

    `v_oben=False` legt sie stattdessen nach unten (v = 0,25) — damit lässt
    sich prüfen, dass der Prüfer nicht einfach immer dasselbe sagt. Zehn
    statt zwei, weil der Prüfer einen Mindestanteil verlangt: ein einzelner
    Ausreißer ist kein Befund.
    """
    ordner = Path(ordner)
    v = 0.75 if v_oben else 0.25
    obj = ordner / f'{name}.obj'
    punkte = ''.join(f'v {i} 0 0\n' for i in range(12))
    uv = ''.join(f'vt {0.05 + 0.07 * i:.3f} {v}\n' for i in range(12))
    flaechen = ''.join(f'f {i + 1}/{i + 1} {i + 2}/{i + 2} {i + 3}/{i + 3}\n' for i in range(10))
    obj.write_text(f'mtllib {name}.mtl\n{punkte}{uv}usemtl haut\n{flaechen}', encoding='utf-8')
    (ordner / f'{name}.mtl').write_text(
        f'newmtl haut\nKd 1.0000 1.0000 1.0000\nd 1.0000\nmap_Kd {name}.png\n', encoding='utf-8')
    karte_schreiben(ordner / f'{name}.png', **karte)
    return obj


class ExportkartenpruefungTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ordner = Path(ProjektTemp.ordner('test_exportkarten'))

    def test_1_saubere_ausgabe_wird_durchgewinkt(self):
        u"""UV oben, Insel oben — jede Fläche trifft Farbe."""
        obj = ausgabe_schreiben(self.ordner, 'sauber', v_oben=True, gefuellt_oben=True)
        bericht = Exportkartenpruefung(obj).bericht()
        self.assertEqual(bericht['gesamt']['flaechen'], 10)
        self.assertEqual(bericht['gesamt']['leer'], 0)
        self.assertEqual(bericht['verdacht_gespiegelt'], [])

    def test_2_karte_auf_dem_kopf_wird_gemeldet(self):
        u"""DER VORFALL: die Insel liegt unten in der Datei, die UV zeigen
        nach oben. Jede Fläche trifft leeren Rand — und die Gegenrichtung
        wäre sauber. Genau das war an `DamiraFein.obj` zu messen."""
        obj = ausgabe_schreiben(self.ordner, 'verdreht', v_oben=True, gefuellt_oben=False)
        bericht = Exportkartenpruefung(obj).bericht()
        self.assertEqual(bericht['gesamt']['leer'], 10, 'alle Flächen treffen leeren Rand')
        self.assertEqual(bericht['verdacht_gespiegelt'], ['haut'],
                         'die Gegenrichtung ist sauber — die Karte steht auf dem Kopf')
        self.assertEqual(bericht['material']['haut']['leer_gespiegelt'], 0)

    def test_3_volle_karte_erzeugt_keinen_fehlalarm(self):
        u"""Eine Karte ohne leeren Rand (flächig gefüllt, wie manche
        Haarkarte) sagt nichts aus. Der Prüfer muss dort SCHWEIGEN statt zu
        raten — ein Fehlalarm verdeckt die echten Befunde."""
        obj = ausgabe_schreiben(self.ordner, 'voll', v_oben=True, ganz_voll=True)
        bericht = Exportkartenpruefung(obj).bericht()
        self.assertEqual(bericht['verdacht_gespiegelt'], [])
        self.assertLess(bericht['material']['haut']['rand_im_bild'], 0.01,
                        'die Karte hat keinen leeren Rand — der Prüfer ist hier blind')

    def test_4_fehlende_karte_wird_benannt_statt_verschwiegen(self):
        obj = ausgabe_schreiben(self.ordner, 'ohnebild', v_oben=True)
        (self.ordner / 'ohnebild.png').unlink()
        bericht = Exportkartenpruefung(obj).bericht()
        self.assertEqual(bericht['material']['haut'], {'fehlt': 'ohnebild.png'})

    def test_5_bericht_laesst_sich_lesen(self):
        obj = ausgabe_schreiben(self.ordner, 'lesbar', v_oben=True, gefuellt_oben=False)
        zeilen = Exportkartenpruefung.zeilen(Exportkartenpruefung(obj).bericht())
        self.assertTrue(any('AUF DEM KOPF' in z for z in zeilen), zeilen)
        self.assertTrue(any('SUMME' in z for z in zeilen), zeilen)
