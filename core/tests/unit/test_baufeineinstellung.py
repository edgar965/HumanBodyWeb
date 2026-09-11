# -*- coding: utf-8 -*-
"""Die zwei Bauregler: Hautabstand und Netzfeinheit.

Sie kommen aus einem Formular, also als Text und aus dem Netz — geprüft wird
deshalb nicht nur der gute Fall, sondern auch Unsinn, Leere und Grenzen.
"""
import os
import re
from unittest import TestCase

from GarmentCode.baufeineinstellung import Baufeineinstellung


class VorgabenBleibenDieAltenWerte(TestCase):
    """Wer nichts anfasst, baut mit den Werten aus dem Code.

    Die Zahlen stehen hier absichtlich ausgeschrieben: Wer eine Vorgabe
    aendert, soll den Test brechen sehen und beide Stellen nachziehen —
    Konstante und Reglerbeschriftung. Der Hautabstand ging am 09.09.2026
    von 6,0 auf 1,0 mm (Messreihe in `stoffkorrektur.py`)."""

    def test_ohne_angabe_gelten_die_alten_konstanten(self):
        fein = Baufeineinstellung()
        self.assertEqual(fein.hautabstand_mm, 1.0)
        self.assertEqual(fein.aufloesung, 1.0)

    def test_die_vorgabe_ist_der_wert_der_stoffkorrektur(self):
        """Sonst bauten Reglerstellung und Code verschiedene Ergebnisse."""
        from GarmentCode.stoffkorrektur import Stoffkorrektur
        self.assertEqual(Baufeineinstellung.HAUTABSTAND_VORGABE,
                         Stoffkorrektur.ABSTAND_MM)

    def test_leeres_formularfeld_gilt_als_keine_angabe(self):
        fein = Baufeineinstellung(hautabstand_mm='', aufloesung='')
        self.assertEqual(fein.hautabstand_mm, 1.0)
        self.assertEqual(fein.aufloesung, 1.0)

    def test_auf_der_vorgabe_gilt_nichts_als_abweichend(self):
        self.assertFalse(Baufeineinstellung().abweichend)

    def test_ein_geaenderter_wert_ist_abweichend(self):
        self.assertTrue(Baufeineinstellung(hautabstand_mm=3).abweichend)
        self.assertTrue(Baufeineinstellung(aufloesung=2).abweichend)


class WerteAusDemNetzWerdenGeprueft(TestCase):

    def test_text_aus_dem_formular_wird_zur_zahl(self):
        fein = Baufeineinstellung(hautabstand_mm='3.5', aufloesung='1.5')
        self.assertEqual(fein.hautabstand_mm, 3.5)
        self.assertEqual(fein.aufloesung, 1.5)

    def test_unlesbarer_wert_faellt_auf_die_vorgabe(self):
        fein = Baufeineinstellung(hautabstand_mm='viel', aufloesung='fein')
        self.assertEqual(fein.hautabstand_mm, 1.0)
        self.assertEqual(fein.aufloesung, 1.0)

    def test_nan_faellt_auf_die_vorgabe(self):
        """`float('nan')` ist lesbar und trotzdem unbrauchbar — es vergleicht
        sich mit nichts, und jede Klemmung liesse es durch."""
        fein = Baufeineinstellung(hautabstand_mm=float('nan'))
        self.assertEqual(fein.hautabstand_mm, 1.0)

    def test_zu_gross_wird_geklemmt(self):
        fein = Baufeineinstellung(hautabstand_mm=500, aufloesung=99)
        self.assertEqual(fein.hautabstand_mm, Baufeineinstellung.HAUTABSTAND_MAX)
        self.assertEqual(fein.aufloesung, Baufeineinstellung.AUFLOESUNG_MAX)

    def test_negativer_hautabstand_wird_geklemmt(self):
        """Ein negativer Abstand hiesse „in die Haut schieben" — genau der
        Zustand, gegen den die Stoffkorrektur da ist."""
        self.assertEqual(Baufeineinstellung(hautabstand_mm=-5).hautabstand_mm,
                         0.0)

    def test_aufloesung_null_wird_geklemmt(self):
        """`resolution_scale` 0 ergäbe ein Netz ohne Punkte."""
        self.assertEqual(Baufeineinstellung(aufloesung=0).aufloesung,
                         Baufeineinstellung.AUFLOESUNG_MIN)

    def test_null_hautabstand_ist_erlaubt(self):
        """0 mm ist eine gültige Ansage („gar nicht korrigieren") und darf
        nicht als „keine Angabe" durchrutschen."""
        self.assertEqual(Baufeineinstellung(hautabstand_mm=0).hautabstand_mm,
                         0.0)

    def test_aus_anfrage_liest_die_formularfelder(self):
        fein = Baufeineinstellung.aus_anfrage(
            {'hautabstand_mm': '2.5', 'aufloesung': '1.8'})
        self.assertEqual(fein.hautabstand_mm, 2.5)
        self.assertEqual(fein.aufloesung, 1.8)

    def test_aus_anfrage_ohne_felder_nimmt_die_vorgaben(self):
        fein = Baufeineinstellung.aus_anfrage({})
        self.assertEqual(fein.hautabstand_mm, 1.0)
        self.assertEqual(fein.aufloesung, 1.0)

    def test_als_dict_nennt_alle_werte(self):
        werte = Baufeineinstellung(hautabstand_mm=3, aufloesung=2).als_dict()
        self.assertEqual(werte, {'hautabstand_mm': 3.0, 'aufloesung': 2.0,
                                 'anliegen_mm': None})

    # --- Anliegen (Leggings, 11.09.2026) --------------------------------

    def test_anliegen_ist_ohne_angabe_aus(self):
        self.assertIsNone(Baufeineinstellung().anliegen_mm)
        self.assertIsNone(Baufeineinstellung.aus_anfrage({}).anliegen_mm)
        self.assertFalse(Baufeineinstellung().abweichend)

    def test_anliegen_null_und_unter_dem_minimum_ist_aus(self):
        self.assertIsNone(Baufeineinstellung(anliegen_mm='0').anliegen_mm)
        self.assertIsNone(Baufeineinstellung(anliegen_mm=0.3).anliegen_mm)

    def test_anliegen_aus_dem_formular(self):
        fein = Baufeineinstellung.aus_anfrage({'anliegen_mm': '2'})
        self.assertEqual(fein.anliegen_mm, 2.0)
        self.assertTrue(fein.abweichend)
        self.assertEqual(fein.als_dict()['anliegen_mm'], 2.0)

    def test_anliegen_wird_geklemmt(self):
        self.assertEqual(Baufeineinstellung(anliegen_mm=99).anliegen_mm, 15.0)
        self.assertIsNone(Baufeineinstellung(anliegen_mm=-3).anliegen_mm)


class DieKetteReichtDieWerteDurch(TestCase):
    """Ein Regler, der nirgends ankommt, bewegt sich stumm.

    Geprüft wird an der Quelle, nicht am laufenden Bau: Eine echte Drapierung
    dauert über 20 s und braucht ein Körpernetz.
    """

    @staticmethod
    def _quelle(*teile):
        """Eine Quelldatei, benannt relativ zum Projektstamm `A:\\3dTools`.

        Über `settings.BASE_DIR` (das ist `HumanBodyWeb`) und dessen
        Elternordner — die Kette läuft über beide Projekte, `GarmentCode`
        liegt daneben und nicht darunter.
        """
        from django.conf import settings
        stamm = os.path.dirname(os.path.abspath(str(settings.BASE_DIR)))
        with open(os.path.join(stamm, *teile), 'r', encoding='utf-8') as datei:
            return datei.read()

    @classmethod
    def _ohne_kommentare(cls, quelle):
        """Ohne Docstrings und `#`-Zeilen.

        Sonst findet der Test seine eigenen Begriffe in der Begründung, die
        erklärt, warum sie NICHT benutzt werden (Regel `analysewerkzeuge`).
        """
        ohne = re.sub(r'"""..*?"""', '', quelle, flags=re.S)
        ohne = re.sub(r"'''..*?'''", '', ohne, flags=re.S)
        return re.sub(r'#.*', '', ohne)

    def test_die_view_liest_die_feineinstellung(self):
        quelle = self._ohne_kommentare(
            self._quelle('HumanBodyWeb', 'core', 'api', 'garmentcode.py'))
        self.assertIn('Baufeineinstellung.aus_anfrage', quelle)
        self.assertIn('fein=fein', quelle)

    def test_die_view_meldet_zurueck_womit_gebaut_wurde(self):
        quelle = self._quelle('HumanBodyWeb', 'core', 'api', 'garmentcode.py')
        self.assertIn("ergebnis['feineinstellung']", quelle)

    def test_der_dienst_reicht_bis_zur_drapierung_durch(self):
        quelle = self._ohne_kommentare(
            self._quelle('Assets', 'GarmentCode', 'drapierdienst.py'))
        self.assertIn('aufloesung=fein.aufloesung', quelle)
        self.assertIn('anliegen_mm=fein.anliegen_mm', quelle)
        # Korrektur und Anlegen laufen seit dem 11.09.2026 in
        # `stoffnacharbeit.py` — dort muss der Hautabstand ankommen.
        nacharbeit = self._ohne_kommentare(
            self._quelle('Assets', 'GarmentCode', 'stoffnacharbeit.py'))
        self.assertIn('abstand_mm=hautabstand_mm', nacharbeit)
        self.assertIn('.anlegen(punkte, anliegen_mm, fest)', nacharbeit)

    def test_das_js_haengt_beide_werte_an_die_anfrage(self):
        quelle = self._quelle('HumanBodyWeb', 'static', 'viewer', 'scene',
                              'garmentcode_drapieren.js')
        self.assertIn('GarmentcodeBauregler.anhaengen(daten)', quelle)

    def test_die_vorlage_hat_beide_regler(self):
        quelle = self._quelle('HumanBodyWeb', 'templates',
                              '_garmentcode_panel.html')
        self.assertIn('gc-hautabstand', quelle)
        self.assertIn('gc-aufloesung', quelle)
        self.assertIn('gc-anliegen', quelle)

    def test_js_und_python_kennen_dieselben_vorgaben(self):
        """Zwei Vorgaben, die auseinanderlaufen, zeigen einen Wert an und
        bauen einen anderen."""
        quelle = self._quelle('HumanBodyWeb', 'static', 'viewer', 'scene',
                              'garmentcode_bauregler.js')
        self.assertIn('HAUTABSTAND_VORGABE = %.1f'
                      % Baufeineinstellung.HAUTABSTAND_VORGABE, quelle)
        self.assertIn('AUFLOESUNG_VORGABE = %.1f'
                      % Baufeineinstellung.AUFLOESUNG_VORGABE, quelle)
