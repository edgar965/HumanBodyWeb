# -*- coding: utf-8 -*-
"""„Modell im System Speichern" (08.10.2026): das Modell liegt EXAKT unter dem Namen, den der Auftrag oben auf der Seite trägt.

Edgar: „das Modell soll exakt unter dem aktuellen Modellnamen gespeichert werden" — „also was oben steht". Die alte Regel der
Basisklasse (`Meshfigurspeichern._wunschname`: nur Buchstaben, Ziffern, Leerzeichen, Bindestrich) machte aus „Edgar 10 - Hunyan Kopf
2.0 Figur" ein „… Kopf 20 Figur". Sabotage-Gegenprobe: in `Engine2d3dKleiderspeichern._wunschname` die Zeile mit `VERBOTEN` durch
`re.sub(r'[^\\w\\s\\-]', '', str(wunsch)).strip()` ersetzen → `test_punkte_kommas_klammern_bleiben` muss rot werden.
"""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderspeichern import Engine2d3dKleiderspeichern
from core.dienste.meshfigurspeichern import Meshfigurspeichern


class WunschnameTest(SimpleTestCase):

    def setUp(self):
        # Ohne Auftrag: `_wunschname` rechnet nur auf dem Text, `__init__` braucht Lauf und Ablage.
        self.s = object.__new__(Engine2d3dKleiderspeichern)
        self.m = object.__new__(Meshfigurspeichern)

    def test_punkte_kommas_klammern_bleiben(self):
        for name in ('Edgar', 'Hunyan-Best', 'Edgar - Hunyan Regionen', 'Edgar 10 - Hunyan Kopf 2.0 Figur',
                     'Edgar 10 - Hunyan Kopf Streckung 1,11 (Handversuch, Augenmorph aus)', 'Äpfel & Öl (Größe 1,5)'):
            with self.subTest(name=name):
                self.assertEqual(self.s._wunschname(name), name)

    def test_nur_was_windows_nicht_kennt_faellt_weg(self):
        self.assertEqual(self.s._wunschname('a/b\\c:d?e*f"g<h>i|j'), 'abcdefghij')
        self.assertEqual(self.s._wunschname('x..y'), 'x.y')          # `Modellpfad` lehnt „..“ ab
        self.assertEqual(self.s._wunschname(' ende. '), 'ende')      # Punkt und Leerzeichen am Ende schneidet NTFS ab
        self.assertEqual(self.s._wunschname('   '), '')

    def test_geraetename_wird_abgelehnt(self):
        for name in ('CON', 'com1.txt'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.s._wunschname(name)

    def test_die_basisklasse_bleibt_bei_der_alten_regel(self):
        """„Mesh to 3D" und der Name aus der Option `modell` ändern sich nicht."""
        self.assertEqual(self.m._wunschname('A (1,5)'), 'A 15')


class SeitenverdrahtungTest(SimpleTestCase):
    """Die Kette ist erst dicht, wenn die letzte Schicht sie liest: der Knopf schickt den Namen von OBEN, nicht aus dem Feld unten."""

    @staticmethod
    def _text(*teile):
        return Path(settings.BASE_DIR).joinpath(*teile).read_text(encoding='utf-8')

    def test_der_knopf_nimmt_den_namen_oben_auf_der_seite(self):
        js = self._text('static', 'viewer', 'engine2d3dkleider', 'engine2d3dkleidersystemspeichern.js')
        self.assertIn("document.getElementById('auftrag-name')", js)
        self.assertIn("{ name }", js)
        self.assertNotIn("{ name: wunsch }", js)

    def test_die_vorlage_hat_den_namen_und_den_knopf(self):
        html = self._text('templates', 'engine2d3dkleider_auftrag.html')
        self.assertIn('id="auftrag-name"', html)
        self.assertIn('id="modell-im-system-speichern"', html)
        self.assertIn('id="modell-im-system-meldung"', html)
