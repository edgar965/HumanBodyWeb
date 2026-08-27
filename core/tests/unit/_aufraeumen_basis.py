# -*- coding: utf-8 -*-
"""Gemeinsame Umgebung der Startaufraeumen-Pruefungen.

WARUM (17.08.2026)
=================
Das stand in `CoreConfig.ready()` — 92 Zeilen, die bei JEDEM Serverstart laufen
und keinen Test hatten. Ein Fehler dort trifft die Aufträge des Nutzers direkt:
Im schlimmsten Fall gilt ein Lauf als gescheitert, dessen Ergebnis längst auf der
Platte liegt.

DIE REIHENFOLGE IST DER BEFUND
==============================
Zuerst die BVH, dann die PID. Wer erst die PID prüft, hängt einen Beobachter an
einen Prozess, dessen Arbeit fertig ist — der Auftrag bliebe auf „läuft" stehen.
Der Test `test_bvh_schlaegt_lebende_pid` nagelt das fest.

Und: Eine BVH von 50 Byte ist ein Rumpf ohne Bewegung; sie darf NICHT als
Ergebnis gelten (Grenze 100 Byte).
"""

from pathlib import Path

from django.test import TestCase, override_settings

from core.dienste import startaufraeumen as modul
from core.models import BVHJob


class AufraeumenBasis(TestCase):

    def setUp(self):
        from django.conf import settings
        self.wurzel = Path(settings.BASE_DIR) / 'media' / 'tmp' / 'starttest'
        umgebung = override_settings(MEDIA_ROOT=str(self.wurzel))
        umgebung.enable()
        self.addCleanup(umgebung.disable)
        self.beobachtet = []
        self.lebt = set()

        def lebt_pid(pid):
            return pid in self.lebt

        def beobachten(kennung, pid):
            self.beobachtet.append((kennung, pid))

        # Umgeleitet wird an der KLASSE, die den Namen fuehrt. Frueher stand
        # dazwischen `pipelines.werkzeuge` mit sechs Weiterleitungen; die Datei
        # ist am 27.08.2026 entfallen (Befund `freie-funktionen`), die Aufrufer
        # holen sich die Klassen direkt.
        from core.pipelines.prozesspruefung import Prozesspruefung
        from core.pipelines.wiederaufnahme import Wiederaufnahme
        self._alt = (Prozesspruefung.lebt, Wiederaufnahme.fahren)
        Prozesspruefung.lebt = staticmethod(lebt_pid)
        Wiederaufnahme.fahren = staticmethod(beobachten)
        self.addCleanup(self._zurueck, Prozesspruefung, Wiederaufnahme)
        # Threads wuerden den Test nichtdeterministisch machen: hier direkt rufen.
        self._alt_thread = modul.threading.Thread
        modul.threading.Thread = self._SofortFaden
        self.addCleanup(self._faden_zurueck)

    class _SofortFaden:
        def __init__(self, target=None, args=(), daemon=False):
            self._ziel, self._args = target, args

        def start(self):
            self._ziel(*self._args)

    def _zurueck(self, pruefung, wiederaufnahme):
        pruefung.lebt, wiederaufnahme.fahren = (staticmethod(self._alt[0]),
                                                staticmethod(self._alt[1]))

    def _faden_zurueck(self):
        modul.threading.Thread = self._alt_thread

    def auftrag(self, status='processing'):
        job = BVHJob.objects.create(name='tanz.mp4', pipeline='gvhmr',
                                    status=status)
        (self.ordner(job)).mkdir(parents=True, exist_ok=True)
        return job

    def ordner(self, job):
        return self.wurzel / 'output' / str(job.id)

    def bvh(self, job, bytes_=200, name='gvhmr_tanz.bvh'):
        pfad = self.ordner(job) / name
        pfad.write_text('x' * bytes_, encoding='utf-8')
        return pfad

    def pid(self, job, nummer=4711, lebt=True):
        (self.ordner(job) / 'pipeline.pid').write_text(str(nummer))
        if lebt:
            self.lebt.add(nummer)
        return nummer
