# -*- coding: utf-8 -*-
"""Geschichtete Augenkarten (Iris über Lederhaut) werden zu EINEM Bild gelegt (`G9augenebenen`, 09.10.2026).

Edgar: „Augen ändern funktioniert nicht beim aktuellen Modell Damira — die Augen sind glasig / grau", „alle Modelle sollen alle Augen
kriegen können". Die Presets Amala, Fabrice, Kat, Laura, Matt und Ty liefern Lederhaut (JPG) und Iris (PNG, halb so hoch) als Ebenen eines
`image_library`-Eintrags; `G9material` nahm nur die erste Ebene — weiße Augäpfel ohne Iris.

1. Die kleinere Iris-Ebene liegt UNSKALIERT oben links auf der Leinwand (gemessen an `G9_Eyes01_D.jpg`: Pupille bei 0,25 der Höhe), die
   untere Hälfte bleibt Lederhaut.
2. `transparency` einer Ebene ist ihre Deckkraft.
3. Mit nur EINER Bildebene wird nichts gelegt: `bild` gibt wie bisher den Daz-Pfad der ersten Ebene, und die Ablage bleibt leer.
4. Nur die Augengruppen werden gelegt; andere Gruppen (Haut mit Makeup-Ebenen, `G9schminke`) behalten die erste Ebene.
5. Der Name hängt am Stand der Bilddateien: gleiche Ebenen → gleicher Name, eine geänderte Datei → neuer Name.
6. Ohne Beschreibung gibt es kein Bild; fremde Namen (`../x.jpg`) werden abgewiesen, `ist_eigen` erkennt nur `augen/<16 Hex>.jpg`.

Sabotage-Gegenprobe: in `bild` die Zeile `gelegt = cls._vormerken(eintrag)` durch `gelegt = None` ersetzen → Fall 1 und 2 rot; die Gruppenprüfung
(`gruppe in cls.GRUPPEN`) streichen → Fall 4 rot; `paste(…, (0, 0))` durch `resize(groesse)` ersetzen → Fall 1 rot.

Nicht gelaufen (09.10.2026) — läuft nur auf Ansage.
"""

import os
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.augenebenen import G9augenebenen
from Genesis9.material import G9material
from Genesis9.pfade import G9pfade
from PIL import Image

from ._pruefablage import Pruefablage

GROESSE = 64


class _Doc:
    u"""Nur das, was `G9augenebenen.bild` vom DSON-Dokument braucht."""

    def __init__(self, eintrag):
        self._eintrag = eintrag

    def eintrag(self, kennung):
        return self._eintrag


class AugenebenenTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        gebaut = Pruefablage.ordner('augenebenen_')
        self.ordner = Path(gebaut.__enter__())
        self.addCleanup(gebaut.__exit__, None, None, None)
        self.bibliothek = self.ordner / 'bibliothek'
        self.bibliothek.mkdir()
        self.ablage = self.ordner / 'ablage'
        self.ablage.mkdir()
        Image.new('RGB', (GROESSE, GROESSE), (200, 200, 200)).save(self.bibliothek / 'sclera.png')
        Image.new('RGBA', (GROESSE, GROESSE // 2), (255, 0, 0, 255)).save(self.bibliothek / 'iris.png')
        umleitungen = [
            mock.patch.object(G9material, 'datei', classmethod(lambda cls, rel: self._datei(rel))),
            mock.patch.object(G9pfade, 'ablage', classmethod(lambda cls: self.ablage)),
        ]
        for umleitung in umleitungen:
            umleitung.start()
            self.addCleanup(umleitung.stop)

    def _datei(self, relativ):
        ziel = self.bibliothek / str(relativ).rsplit('/', 1)[-1]
        return ziel if ziel.is_file() else None

    @staticmethod
    def _ebenen(deckkraft=1.0, iris=True):
        basis = {'label': 'Base', 'color': [1, 1, 1], 'transparency': 1, 'operation': 'blend_source_over'}
        lederhaut = {'url': '/Runtime/Textures/DAZ/Eyes/Split/sclera.png', 'label': 'Sclera', 'transparency': 1}
        schicht = {'url': '/Runtime/Textures/DAZ/Eyes/Split/iris.png', 'label': 'Iris', 'transparency': deckkraft}
        return {'map': [basis, lederhaut] + ([schicht] if iris else [])}

    def _gelegt(self, eintrag):
        name = G9augenebenen.bild(_Doc(eintrag), '#Eye%20Color', 'Eye Left')
        self.assertTrue(G9augenebenen.ist_eigen(name), name)
        datei = G9augenebenen.datei(name.split('/', 1)[1])
        self.assertIsNotNone(datei, 'das gelegte Bild fehlt')
        return name, Image.open(datei).convert('RGB')

    def test_1_iris_liegt_unskaliert_oben_links(self):
        _, bild = self._gelegt(self._ebenen())
        self.assertEqual(bild.size, (GROESSE, GROESSE))
        rot = bild.getpixel((GROESSE // 2, GROESSE // 4))        # mitten in der oberen Hälfte: Iris
        grau = bild.getpixel((GROESSE // 2, GROESSE * 3 // 4))   # untere Hälfte: Lederhaut
        self.assertGreater(rot[0], 200)
        self.assertLess(rot[1], 60)
        self.assertTrue(all(abs(w - 200) < 12 for w in grau), grau)

    def test_2_transparenz_ist_die_deckkraft(self):
        _, bild = self._gelegt(self._ebenen(deckkraft=0.5))
        r, g, b = bild.getpixel((GROESSE // 2, GROESSE // 4))
        self.assertTrue(180 < r < 240 and 70 < g < 140, (r, g, b))      # Mitte zwischen Rot und Grau

    def test_3_eine_bildebene_wird_nicht_gelegt(self):
        eintrag = self._ebenen(iris=False)
        name = G9augenebenen.bild(_Doc(eintrag), '#x', 'Eye Left')
        self.assertEqual(name, '/Runtime/Textures/DAZ/Eyes/Split/sclera.png')
        ordner = self.ablage / G9augenebenen.ORDNER
        self.assertFalse(ordner.exists() and any(ordner.iterdir()), 'bei einer Bildebene wird nichts abgelegt')

    def test_4_nur_die_augengruppen_werden_gelegt(self):
        name = G9augenebenen.bild(_Doc(self._ebenen()), '#x', 'Head')
        self.assertEqual(name, '/Runtime/Textures/DAZ/Eyes/Split/sclera.png')

    def test_5_der_name_haengt_am_stand_der_dateien(self):
        eintrag = self._ebenen()
        erster = G9augenebenen.bild(_Doc(eintrag), '#x', 'Eye Left')
        self.assertEqual(erster, G9augenebenen.bild(_Doc(eintrag), '#x', 'Eye Right'), 'gleiche Ebenen, gleiches Bild')
        iris = self.bibliothek / 'iris.png'
        stand = iris.stat().st_mtime_ns
        os.utime(iris, ns=(stand + 5_000_000_000, stand + 5_000_000_000))
        self.assertNotEqual(erster, G9augenebenen.bild(_Doc(eintrag), '#x', 'Eye Left'), 'Datei geändert: neues Bild')

    def test_6_ohne_beschreibung_und_fremde_namen_gibt_es_nichts(self):
        self.assertIsNone(G9augenebenen.datei('0123456789abcdef.jpg'))
        self.assertIsNone(G9augenebenen.datei('../../x.jpg'))
        self.assertFalse(G9augenebenen.ist_eigen('augen/../x.jpg'))
        self.assertFalse(G9augenebenen.ist_eigen('schminke/0123456789abcdef.jpg'))
        self.assertTrue(G9augenebenen.ist_eigen('augen/0123456789abcdef.jpg'))
