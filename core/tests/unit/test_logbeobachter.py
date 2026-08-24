# -*- coding: utf-8 -*-
"""Logbeobachter — Fortschritt aus der Logdatei, mit nachgerechneten Prozenten.

WARUM (17.08.2026)
=================
`_monitor_pipeline_log` (67 Zeilen) beobachtet den einzigen Kanal, über den ein
laufender GVHMR-/WHAM-Lauf etwas von sich hören lässt. Ungedeckt war er, weil er
eine Endlosschleife um eine Datei ist, die ein anderer Prozess schreibt. Die
Deutung der Zeilen ist aber reine Rechnung — und dort steckt das, was der Nutzer
sieht.

DIE ZAHLEN
==========
    ' 42%|████      | 42/100'   -> 42   (tqdm-Balken schlägt den Bruch)
    'Frame 42 / 100'            -> 39   (42/100 × 95, abgeschnitten)
    '100%|██████████|'          -> 95   (Deckel — fertig ist erst die BVH)
    'lade Modell'               -> None (keine Zahl, nur Text als Meldung)

Der Deckel bei 95 ist Absicht: Ein Fortschritt von 100 % neben dem Zustand
„läuft" hat schon einmal zu der Frage geführt, warum nichts passiert.

DAS TAIL
========
Gelesen wird ab der letzten Stelle. Der Test schreibt zweimal in die Datei und
prüft, dass der zweite Aufruf NUR das Neue sieht — sonst wertet jede Runde die
ganze Datei aus und der Fortschritt springt zurück.
"""

from pathlib import Path

from django.test import SimpleTestCase

from core.pipelines.logbeobachter import Logbeobachter
from core.tests.attrappen import AuftragsAttrappe


class AnteilTest(SimpleTestCase):

    def test_tqdm_balken(self):
        self.assertEqual(Logbeobachter.anteil(' 42%|####      | 42/100'), 42)

    def test_bruchform_wird_auf_95_gestreckt(self):
        self.assertEqual(Logbeobachter.anteil('Frame 42 / 100'), 39)

    def test_deckel_bei_95(self):
        self.assertEqual(Logbeobachter.anteil('100%|##########|'), 95)
        self.assertEqual(Logbeobachter.anteil('Frame 100 / 100'), 95)

    def test_text_ohne_zahl_ergibt_nichts(self):
        self.assertIsNone(Logbeobachter.anteil('lade Modell'))

    def test_null_gesamt_teilt_nicht(self):
        self.assertIsNone(Logbeobachter.anteil('Frame 0 / 0'))


class NachschubTest(SimpleTestCase):

    def beobachter(self):
        from django.conf import settings
        ordner = Path(settings.BASE_DIR) / 'media' / 'tmp' / 'logtest'
        ordner.mkdir(parents=True, exist_ok=True)
        self.datei = ordner / 'pipeline.log'
        if self.datei.exists():
            self.datei.unlink()
        return Logbeobachter(AuftragsAttrappe(), self.datei, 120)

    def test_fehlende_datei_ist_kein_fehler(self):
        """Beim ersten Durchgang gibt es die Datei oft noch nicht."""
        self.assertEqual(self.beobachter().nachschub(), '')

    def test_nur_das_neue_wird_gelesen(self):
        beobachter = self.beobachter()
        self.datei.write_text('erste Zeile\n', encoding='utf-8')
        self.assertEqual(beobachter.nachschub(), 'erste Zeile\n')
        with open(self.datei, 'a', encoding='utf-8') as datei:
            datei.write('zweite Zeile\n')
        self.assertEqual(beobachter.nachschub(), 'zweite Zeile\n')

    def test_ohne_nachschub_kommt_leer(self):
        beobachter = self.beobachter()
        self.datei.write_text('x\n', encoding='utf-8')
        beobachter.nachschub()
        self.assertEqual(beobachter.nachschub(), '')


class AuswertenTest(SimpleTestCase):

    def beobachter(self, bilder=120):
        self.job = AuftragsAttrappe()
        return Logbeobachter(self.job, Path('gibtsnicht.log'), bilder)

    def test_letzte_zeile_zaehlt(self):
        """Ein tqdm-Balken schreibt viele Zeilen — der neueste Stand gilt."""
        beobachter = self.beobachter()
        beobachter.auswerten(' 10%|# |\n 40%|#### |\n', jetzt=100)
        self.assertEqual(self.job.progress, 40)

    def test_bilderzahl_steht_in_der_meldung(self):
        beobachter = self.beobachter()
        beobachter.auswerten('lade Modell\n', jetzt=100)
        self.assertEqual(self.job.progress_detail, 'lade Modell — 120 frames')

    def test_ohne_bilderzahl_nur_die_zeile(self):
        beobachter = self.beobachter(bilder=0)
        beobachter.auswerten('lade Modell\n', jetzt=100)
        self.assertEqual(self.job.progress_detail, 'lade Modell')

    def test_meldung_wird_gekuerzt(self):
        """Zwei Grenzen hintereinander: 80 für die Zeile, 100 für das Ganze.

        Nachgerechnet: 80 Zeichen Zeile + ' — 120 frames' (13) = 93, also
        unter der zweiten Grenze. Die 100 greift erst bei einer größeren
        Bilderzahl — deshalb bleiben hier 93 stehen.
        """
        beobachter = self.beobachter()
        beobachter.auswerten('x' * 300 + '\n', jetzt=100)
        self.assertEqual(len(self.job.progress_detail), 93)
        beobachter = self.beobachter(bilder=1234567890123456789)
        beobachter.auswerten('x' * 300 + '\n', jetzt=100)
        self.assertEqual(len(self.job.progress_detail), 100)

    def test_gedrosselt_auf_eine_meldung_je_halbe_sekunde(self):
        beobachter = self.beobachter()
        self.assertTrue(beobachter.auswerten(' 10%|# |\n', jetzt=100))
        self.assertFalse(beobachter.auswerten(' 20%|## |\n', jetzt=100.2))
        self.assertTrue(beobachter.auswerten(' 30%|### |\n', jetzt=100.6))
        self.assertEqual(self.job.speicherungen, 2)
        self.assertEqual(self.job.progress, 30)

    def test_leerer_nachschub_meldet_nichts(self):
        beobachter = self.beobachter()
        self.assertFalse(beobachter.auswerten('\n  \n', jetzt=100))
        self.assertEqual(self.job.speicherungen, 0)

    def test_textzeile_laesst_den_fortschritt_stehen(self):
        """Eine Zeile ohne Zahl darf den Balken nicht auf 0 zurücksetzen."""
        beobachter = self.beobachter()
        beobachter.auswerten(' 40%|#### |\n', jetzt=100)
        beobachter.auswerten('schreibe BVH\n', jetzt=101)
        self.assertEqual(self.job.progress, 40)
