# -*- coding: utf-8 -*-
"""Startaufraeumen — die drei Fälle nach einem Serverneustart.

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

from core.dienste.startaufraeumen import Startaufraeumen
from core.tests.unit._aufraeumen_basis import AufraeumenBasis


class FertigTest(AufraeumenBasis):

    def test_vorhandene_bvh_macht_den_auftrag_fertig(self):
        job = self.auftrag()
        pfad = self.bvh(job)
        Startaufraeumen().durchgehen()
        job.refresh_from_db()
        self.assertEqual(job.status, 'complete')
        self.assertEqual(job.progress, 100)
        self.assertEqual(job.bvh_file, str(pfad))
        self.assertIn('recovered', job.progress_detail)

    def test_bvh_schlaegt_lebende_pid(self):
        """Reihenfolge: Das Ergebnis zählt, nicht der Prozess."""
        job = self.auftrag()
        self.bvh(job)
        self.pid(job)
        Startaufraeumen().durchgehen()
        job.refresh_from_db()
        self.assertEqual(job.status, 'complete')
        self.assertEqual(self.beobachtet, [], 'kein Beobachter mehr nötig')

    def test_pid_datei_wird_entfernt(self):
        job = self.auftrag()
        self.bvh(job)
        self.pid(job, lebt=False)
        Startaufraeumen().durchgehen()
        self.assertFalse((self.ordner(job) / 'pipeline.pid').exists())

    def test_rumpfdatei_gilt_nicht_als_ergebnis(self):
        """50 Byte BVH = Kopf ohne Bewegung."""
        job = self.auftrag()
        self.bvh(job, bytes_=50)
        Startaufraeumen().durchgehen()
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')


class WeiterTest(AufraeumenBasis):

    def test_lebende_pid_wird_weiter_beobachtet(self):
        job = self.auftrag()
        nummer = self.pid(job)
        Startaufraeumen().durchgehen()
        job.refresh_from_db()
        self.assertEqual(job.status, 'processing', 'bleibt laufend')
        self.assertEqual(self.beobachtet, [(str(job.id), nummer)])

    def test_tote_pid_gilt_als_gescheitert(self):
        job = self.auftrag()
        self.pid(job, lebt=False)
        Startaufraeumen().durchgehen()
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertEqual(self.beobachtet, [])

    def test_unlesbare_pid_datei_ist_kein_absturz(self):
        job = self.auftrag()
        (self.ordner(job) / 'pipeline.pid').write_text('kaputt')
        Startaufraeumen().durchgehen()
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')


class GescheitertTest(AufraeumenBasis):

    def test_hinweis_passt_zum_knopf(self):
        job = self.auftrag()
        Startaufraeumen().durchgehen()
        job.refresh_from_db()
        self.assertIn('Neu starten', job.error_message)

    def test_fertige_auftraege_werden_nicht_angefasst(self):
        job = self.auftrag(status='complete')
        job.progress_detail = 'unberührt'
        job.save()
        zaehler = Startaufraeumen().durchgehen()
        job.refresh_from_db()
        self.assertEqual(job.progress_detail, 'unberührt')
        self.assertEqual(sum(zaehler.values()), 0)

    def test_zaehler_nennt_alle_drei_faelle(self):
        fertig = self.auftrag()
        self.bvh(fertig)
        laeuft = self.auftrag()
        self.pid(laeuft, nummer=4712)
        self.auftrag()
        self.assertEqual(Startaufraeumen().durchgehen(),
                         {'fertig': 1, 'weiter': 1, 'gescheitert': 1})
