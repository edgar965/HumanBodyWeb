# -*- coding: utf-8 -*-
"""Sapiens2 als wählbare Modellfamilie im Schritt „Segmentierung" (09.10.2026).

DER ANLASS
==========
Edgar (09.10.2026, „mach alles"): Sapiens2 (facebookresearch/sapiens2) prüfen und — nur wenn messbar besser oder gleich — als Modellfamilie in die Sapiens-Einstellungen. Gemessen
(`.claude/rules/segmentierung-fashn-sapiens2.md`): Sapiens2 0.4B lässt bei Randy 1,7 % statt 35 % der freigestellten Person ohne Etikett, bei Edgar gleich. Eingebaut als Werte
`sapiens2-0.4b` / `sapiens2-0.8b` der Option `modell`; die Etiketten kommen in den 28 Klassen von Sapiens heraus (`Eyeglass` → `Apparel`), damit alles danach gleich bleibt.

WAS DIESE PRÜFUNG NICHT IST
===========================
Kein Modelllauf (torch fehlt in python14): nur die Klassentabelle, die Gewichtstabelle und die Optionen. Dass Sapiens2 auf Fotos läuft, zeigt der Probelauf
(`ProjektTemp/_wegwerf/sapiens2/sapiens2_probe.py`) und der Runner-Lauf im Tagebuch. Geschrieben am 09.10.2026, nicht gelaufen.

BDD - GEGEBEN / DANN
====================
    die 29 Klassen von Sapiens2           ... jede landet auf der GLEICHNAMIGEN Sapiens-Klasse, `Eyeglass` auf `Apparel`, der Hintergrund auf 0
    Größe `sapiens2-0.4b`                  ... ist Sapiens2, Datei unter `<HF_HOME>/sapiens/` mit dem Namen von Hugging Face; `1b` ist es nicht
    die Option `modell`                    ... kennt beide Sapiens2-Werte, Vorgabe bleibt `1b`; ein anderer Wert ist eine Rechenoption („passt nicht mehr")
Sabotage-Gegenprobe (gedacht, nicht gelaufen): `UMBENENNUNG = {}` → `Sapiensklassen.NAMEN.index('Eyeglass')` wirft ValueError → der erste Test wird rot.
"""
import os

from django.test import SimpleTestCase

from core.dienste.engine2d3dkleidersegmentierungsoptionen import Engine2d3dKleidersegmentierungsoptionen as Optionen

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from sapiens2_modell import Sapiens2modell  # noqa: E402
from sapiens_gewichte import Sapiensgewichte  # noqa: E402
from sapiens_klassen import Sapiensklassen  # noqa: E402


class Sapiens2Klassen(SimpleTestCase):
    def test_jede_klasse_landet_auf_der_gleichnamigen_und_die_brille_auf_zubehoer(self):
        tabelle = Sapiens2modell.nach_sapiens()
        self.assertEqual(len(tabelle), 29)
        for nr, name in enumerate(Sapiens2modell.NAMEN):
            erwartet = 'Apparel' if name == 'Eyeglass' else name
            self.assertEqual(Sapiensklassen.NAMEN[tabelle[nr]], erwartet, name)
        self.assertEqual(int(tabelle[0]), 0)
        self.assertEqual(set(Sapiens2modell.NAMEN) - {'Eyeglass'}, set(Sapiensklassen.NAMEN))


class Sapiens2Gewichte(SimpleTestCase):
    def test_die_groessen_von_sapiens2(self):
        self.assertTrue(Sapiensgewichte.ist_sapiens2('sapiens2-0.4b'))
        self.assertFalse(Sapiensgewichte.ist_sapiens2('1b'))
        pfad = Sapiensgewichte.pfad('H', 'sapiens2-0.4b')
        self.assertEqual(pfad, os.path.join('H', 'sapiens', 'sapiens2_0.4b_seg.safetensors'))
        self.assertEqual(Sapiensgewichte.eintrag('sapiens2-0.4b')[2], 1626451404)                # Größe der am 09.10.2026 geladenen Datei
        self.assertEqual(Sapiensgewichte.VORGABE, '1b')

    def test_die_option_kennt_sapiens2_und_die_vorgabe_bleibt(self):
        werte = {w for e in Optionen.KATALOG if e['schluessel'] == 'modell' for w, _ in e['werte']}
        self.assertTrue({'sapiens2-0.4b', 'sapiens2-0.8b'} <= werte)
        self.assertEqual(Optionen.vorgaben()['modell'], '1b')
        self.assertEqual(Optionen.pruefen({'modell': 'sapiens2-0.4b'})['modell'], 'sapiens2-0.4b')
        self.assertNotEqual(Optionen.rechenoptionen({'modell': 'sapiens2-0.4b'}), Optionen.rechenoptionen({}))
