# -*- coding: utf-8 -*-
"""Wächter für den Fortschritt der 2D-Erkennung.

WARUM (17.08.2026): Diese Auswertung stand zweimal wortgleich in
`erkennung2d.py` — einmal für MediaPipe, einmal für die neuen Erkenner. Beim
Zusammenlegen zu `Erkennungsfortschritt` musste dreierlei erhalten bleiben, und
keines davon war vorher geprüft:

* **Die Drosselung.** Der Wrapper meldet mit `--progress-interval 1` jede
  Frame. Ohne die Sperre schreibt eine 30-fps-Pipeline dreißigmal je Sekunde in
  die Datenbank.
* **Der Anteil 45 %.** Die 2D-Erkennung ist der erste Abschnitt; danach kommt
  MocapNET. Eine 100 hier wäre eine Lüge auf dem Balken.
* **Die Uhr bei `TOTAL:`.** Der Erkenner meldet die Gesamtzahl erst, nachdem er
  seine Modelle geladen hat. Ginge die Ladezeit in die Bildrate ein, wäre die
  Restzeit am Anfang um ein Vielfaches zu hoch.

Kein Datenbankzugriff: Der Auftrag ist eine Attrappe, die sich merkt, wie oft
`save()` gerufen wurde. Genau diese Zahl ist der Gegenstand des ersten Tests.
"""

from django.test import SimpleTestCase

from core.pipelines.erkennungsfortschritt import Erkennungsfortschritt
from core.tests.attrappen import AuftragsAttrappe


class ErkennungsfortschrittTest(SimpleTestCase):

    def _leser(self, gesamt=100, name=''):
        self.job = AuftragsAttrappe()
        return Erkennungsfortschritt(self.job, gesamt, jetzt=0.0, name=name)

    def test_gedrosselt_auf_eine_meldung_je_sekunde(self):
        leser = self._leser()
        self.assertTrue(leser.zeile_lesen('PROGRESS:10/100', jetzt=5.0))
        self.assertFalse(leser.zeile_lesen('PROGRESS:11/100', jetzt=5.2))
        self.assertTrue(leser.zeile_lesen('PROGRESS:20/100', jetzt=6.5))
        self.assertEqual(self.job.speicherungen, 2)

    def test_prozent_bleibt_unter_dem_anteil(self):
        """Auch bei 100 % der Erkennung ist der Lauf erst zu 45 % fertig."""
        leser = self._leser()
        leser.zeile_lesen('PROGRESS:100/100', jetzt=10.0)
        self.assertEqual(self.job.progress, Erkennungsfortschritt.ANTEIL)

    def test_bildrate_und_restzeit_stehen_in_der_meldung(self):
        leser = self._leser()
        leser.zeile_lesen('PROGRESS:50/100', jetzt=10.0)
        self.assertIn('50 / 100 frames', self.job.progress_detail)
        self.assertIn('5.0 fps', self.job.progress_detail)
        self.assertIn('~10s left', self.job.progress_detail)

    def test_total_setzt_die_uhr_zurueck(self):
        """Ohne das ginge die Modell-Ladezeit in die Bildrate ein."""
        leser = self._leser(gesamt=0)
        leser.zeile_lesen('TOTAL:200', jetzt=30.0)      # 30 s Modelle laden
        self.assertEqual(leser.gesamt, 200)
        leser.zeile_lesen('PROGRESS:100/200', jetzt=40.0)
        # 100 Bilder in 10 s, nicht in 40 s.
        self.assertIn('10.0 fps', self.job.progress_detail)

    def test_status_wird_mit_namen_gemeldet(self):
        leser = self._leser(name='RTMPose')
        self.assertTrue(leser.zeile_lesen('STATUS:Lade Gewichte', jetzt=1.0))
        self.assertEqual(self.job.progress_detail, 'RTMPose: Lade Gewichte')

    def test_ohne_namen_kein_vorsatz(self):
        """MediaPipe meldete nie mit Vorsatz — das muss so bleiben."""
        leser = self._leser()
        leser.zeile_lesen('PROGRESS:1/100', jetzt=1.0)
        self.assertTrue(self.job.progress_detail.startswith('1 / 100'))

    def test_unlesbare_zeilen_aendern_nichts(self):
        leser = self._leser()
        for zeile in ('Loading neural network', '', 'PROGRESS:abc',
                      'TOTAL:viele', 'done'):
            with self.subTest(zeile=zeile):
                self.assertFalse(leser.zeile_lesen(zeile, jetzt=99.0))
        self.assertEqual(self.job.speicherungen, 0)

    def test_null_bilder_ergibt_keinen_fortschritt(self):
        """Ohne Bezugsgröße ist kein Prozentwert berechenbar."""
        leser = self._leser(gesamt=0)
        self.assertFalse(leser.zeile_lesen('PROGRESS:5', jetzt=5.0))

    def test_anfangsmeldung_mit_und_ohne_gesamtzahl(self):
        leser = self._leser(gesamt=250)
        leser.anfangsmeldung('mediapipe')
        self.assertEqual(self.job.status, 'mediapipe')
        self.assertEqual(self.job.progress, 0)
        self.assertEqual(self.job.progress_detail, '0 / 250 frames')

        leser = self._leser(gesamt=0, name='YOLO11')
        leser.anfangsmeldung('detecting_2d')
        self.assertEqual(self.job.progress_detail, 'Starting YOLO11...')
