# -*- coding: utf-8 -*-
"""Mesh to 3D, 12.10.2026: der Stoffzug „nur wo der Stoff nah anliegt“ (`kleidung = nah`) und die Einstellung `kleidung_zug` der Mesh-3D-Aufträge.

Anlass (Zauberer, Robe): der Zug `weich` (alles Tuch bis 15 cm vom Käfigpunkt zieht ihn unter seine Oberfläche) blähte den Körper auf die Robe auf — Oberschenkel 103,5 gegen 64,0 cm an Edgars Figur,
ohne Zug 51,4 cm (Grundfigur 53,8). `nah` zieht nur Tuch bis `kleidung_reichweite_cm` (7) Abstand. Hier: Optionen, Durchreichung der Einstellung und Quelltext-Wächter der Kette; der Rechenfall (Reichweite) braucht
torch und steht in `test_meshfigur_reichweite.py` (python10). Sabotage-Gegenprobe: in `blendimportfigur.py` die Zeile `roh['kleidung'] = self.kleidung_zug` streichen → `test_weg_netz_reicht_die_wahl_durch` wird rot.
"""

import unittest

from core.dienste.blendimportfigur import Blendimportfigur
from core.dienste.blendimporteinstellungen import Blendimporteinstellungen
from core.dienste.meshfiguroptionen import Meshfiguroptionen

from ._wrappersuchpfad import MESHTO3D, Wrappersuchpfad

Wrappersuchpfad.setzen()


class OptionenTest(unittest.TestCase):
    def test_nah_ist_ein_wert_der_option_kleidung_und_die_vorgabe_bleibt_weich(self):
        katalog = {e['schluessel']: e for e in Meshfiguroptionen.katalog()['optionen']}
        self.assertIn('nah', [w['wert'] for w in katalog['kleidung']['werte']])
        self.assertEqual(Meshfiguroptionen.pruefen({})['kleidung'], 'weich')
        self.assertEqual(Meshfiguroptionen.pruefen({'kleidung': 'nah'})['kleidung'], 'nah')

    def test_reichweite_vorgabe_7_und_klemmung(self):
        self.assertEqual(Meshfiguroptionen.pruefen({})['kleidung_reichweite_cm'], 7)
        self.assertEqual(Meshfiguroptionen.pruefen({'kleidung_reichweite_cm': 99})['kleidung_reichweite_cm'], 20)
        self.assertEqual(Meshfiguroptionen.pruefen({'kleidung_reichweite_cm': 0})['kleidung_reichweite_cm'], 2)
        self.assertEqual(Meshfiguroptionen.pruefen({'kleidung_reichweite_cm': 'x'})['kleidung_reichweite_cm'], 7)


class MeshdreiEinstellungTest(unittest.TestCase):
    """Die Einstellung `kleidung_zug` des Imports wird beim Weg „netz“ zur Option `kleidung` von „Mesh to 3D“."""

    def test_einstellung_im_katalog_mit_drei_werten_und_vorgabe_weich(self):
        eintrag = Blendimporteinstellungen.eintrag('kleidung_zug')
        self.assertEqual([w for w, _ in eintrag['werte']], ['weich', 'nah', 'ignorieren'])
        self.assertEqual(Blendimporteinstellungen.pruefen({})['kleidung_zug'], 'weich')
        self.assertEqual(Blendimporteinstellungen.pruefen({'kleidung_zug': 'nah'})['kleidung_zug'], 'nah')
        self.assertEqual(Blendimporteinstellungen.pruefen({'kleidung_zug': 'quatsch'})['kleidung_zug'], 'weich')

    def test_weg_netz_reicht_die_wahl_durch(self):
        for wahl in ('weich', 'nah', 'ignorieren'):
            self.assertEqual(Blendimportfigur(None, 'x', 'masculine', netz=True, kleidung_zug=wahl).optionen()['kleidung'], wahl)

    def test_ohne_wahl_und_bei_unbekanntem_wert_gilt_die_vorgabe_von_mesh_to_3d(self):
        self.assertEqual(Blendimportfigur(None, 'x', 'masculine', netz=True).optionen()['kleidung'], 'weich')
        self.assertEqual(Blendimportfigur(None, 'x', 'masculine', netz=True, kleidung_zug='quatsch').optionen()['kleidung'], 'weich')

    def test_weg_teile_behaelt_wie_haut(self):
        """Die Blender-Kette hat keine Kleidung im Netz: die Wahl gilt nur beim Weg „netz“."""
        self.assertEqual(Blendimportfigur(None, 'x', 'feminine', netz=False, kleidung_zug='nah').optionen()['kleidung'], 'wie_haut')

    def test_der_lauf_reicht_die_einstellung_an_die_figur(self):
        from pathlib import Path

        quelle = (Path(__file__).resolve().parents[2] / 'dienste' / 'blendimportlauf.py').read_text(encoding='utf-8')
        self.assertIn("kleidung_zug=self.stand['einstellungen'].get('kleidung_zug')", quelle)


class KetteTest(unittest.TestCase):
    def test_der_runner_reicht_die_reichweite_an_den_abstand(self):
        runner = (MESHTO3D / '_run_meshfigur.py').read_text(encoding='utf-8')
        self.assertIn("kleidung_reichweite=float(self.daten.optionen.get('kleidung_reichweite_cm', 7)) / 100.0", runner)
        abstand = (MESHTO3D / 'meshfigur_abstand.py').read_text(encoding='utf-8')
        self.assertIn("ZIEHT = ('weich', 'nah')", abstand)
        self.assertIn('self.kleid_reichweite = ', abstand)

    def test_die_registrierung_legt_in_beiden_runden_die_menge_fest(self):
        """Runde 1 (nach der ersten Körperstufe, wenn `bedeckt` steht) UND Runde 2: wer die Zeile streicht, lässt `nah` in der Runde wie `weich` ziehen (Aufschaukeln)."""
        quelle = (MESHTO3D / 'meshfigur_registrierung.py').read_text(encoding='utf-8')
        self.assertEqual(quelle.count('self.nah = self.reichweite_festlegen()'), 2)
        self.assertIn('self.modell.vorwaerts(grund=True)', quelle)
        modell = (MESHTO3D / 'meshfigur_modell.py').read_text(encoding='utf-8')
        self.assertIn('def grundruhe(self)', modell)
        self.assertIn('def vorwaerts(self, grund=False)', modell)

    def test_der_zug_nimmt_die_festgelegte_maske(self):
        stoff = (MESHTO3D / 'meshfigur_abstandstoff.py').read_text(encoding='utf-8')
        self.assertIn("if self.kleidung == 'nah' and self.kleid_nah is not None and self._nah_haut is self.haut:", stoff)
        self.assertIn('passt = passt & self.kleid_nah', stoff)


if __name__ == '__main__':
    unittest.main()
