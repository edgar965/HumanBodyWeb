# -*- coding: utf-8 -*-
u"""Auftragsarbeiter: der Lauf hängt nicht mehr am Serverprozess.

Befund Edgar (12.09.2026, „schlägt fehl, siehe logs"): Auftrag 9489ddb8 lief
drei Sekunden, dann lud der Entwicklungsserver neu (eine Python-Datei der
parallelen Sitzung) — und `Startaufraeumen` vermerkte „Server was restarted
while job was running". Vier Aufträge an einem Tag.

Hier steht, was seither gilt: `starten` wirft einen ABGELÖSTEN Prozess an
und notiert seine PID; `Startaufraeumen` lässt einen Auftrag mit lebendem
Arbeitsprozess in Ruhe; `Haenger` zählt ihn als lebenden Prozess; der
Befehl `auftrag_fahren` rechnet den Lauf und räumt seine PID-Datei weg;
`Auftragssteuerung` startet ohne `AUFTRAG_IM_SERVER` den Arbeiter, nicht
den Faden.
"""
import os
import subprocess

from django.core.management import call_command
from django.test import override_settings

from core.dienste.auftragsarbeiter import Auftragsarbeiter
from core.dienste.haenger import Haenger
from core.dienste.startaufraeumen import Startaufraeumen
from core.tests.unit._aufraeumen_basis import AufraeumenBasis


class Prozessattrappe:
    def __init__(self, pid=4242):
        self.pid = pid


class DerArbeiter(AufraeumenBasis):

    def test_starten_ruft_manage_py_auftrag_fahren_abgeloest(self):
        job = self.auftrag()
        gesehen = {}

        def popen(befehl, protokoll):
            gesehen['befehl'] = befehl
            return Prozessattrappe(4242)
        alt = Auftragsarbeiter._popen
        Auftragsarbeiter._popen = staticmethod(popen)
        self.addCleanup(setattr, Auftragsarbeiter, '_popen', alt)

        self.assertEqual(Auftragsarbeiter.starten(job.id), 4242)
        self.assertEqual(gesehen['befehl'][2:], ['auftrag_fahren', str(job.id)])
        self.assertTrue(gesehen['befehl'][1].endswith('manage.py'))
        self.assertEqual(Auftragsarbeiter.pid(job.id), 4242)
        self.assertTrue((self.ordner(job) / 'auftrag.log').exists())

    def test_abgeloest_heisst_eigene_gruppe_ohne_konsole(self):
        u"""Windows — hier laeuft der Server; anderswo sind die Flags 0."""
        flags = Auftragsarbeiter.flags()
        self.assertTrue(flags & subprocess.DETACHED_PROCESS)
        self.assertTrue(flags & subprocess.CREATE_NEW_PROCESS_GROUP)

    def test_ohne_pid_datei_lebt_niemand(self):
        job = self.auftrag()
        self.assertIsNone(Auftragsarbeiter.pid(job.id))
        self.assertFalse(Auftragsarbeiter.lebt(job.id))

    def test_eintragen_und_austragen(self):
        job = self.auftrag()
        Auftragsarbeiter.eintragen(job.id)
        self.assertEqual(Auftragsarbeiter.pid(job.id), os.getpid())
        Auftragsarbeiter.austragen(job.id)
        self.assertIsNone(Auftragsarbeiter.pid(job.id))
        Auftragsarbeiter.austragen(job.id)          # zweimal ist kein Fehler


class DerServerNachDemNeustart(AufraeumenBasis):

    def arbeiter(self, job, nummer=8080, lebt=True):
        (self.ordner(job) / Auftragsarbeiter.PID_DATEI).write_text(str(nummer))
        if lebt:
            self.lebt.add(nummer)

    def test_lebender_arbeiter_laesst_den_auftrag_laufen(self):
        job = self.auftrag()
        self.arbeiter(job)
        self.assertEqual(Startaufraeumen().durchgehen()['weiter'], 1)
        job.refresh_from_db()
        self.assertEqual(job.status, 'processing')
        self.assertEqual(job.error_message, '')
        self.assertEqual(self.beobachtet, [], 'kein Beobachter — der Arbeiter bucht selbst')

    def test_toter_arbeiter_faellt_auf_die_alten_faelle_zurueck(self):
        job = self.auftrag()
        self.arbeiter(job, lebt=False)
        Startaufraeumen().durchgehen()
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertEqual(job.error_message, Startaufraeumen.NEUSTART_HINWEIS)

    def test_der_haenger_zaehlt_den_arbeiter_als_lebend(self):
        job = self.auftrag()
        self.assertFalse(Haenger.prozess_lebt(str(job.id)))
        self.arbeiter(job)
        self.assertTrue(Haenger.prozess_lebt(str(job.id)))


class DerBefehl(AufraeumenBasis):

    def test_auftrag_fahren_rechnet_und_raeumt_die_pid_weg(self):
        from core.pipelines import auftragslauf as modul
        job = self.auftrag()
        gesehen = {}

        class Laufattrappe:
            def __init__(self, jid):
                gesehen['jid'] = jid

            def ausfuehren(self):
                gesehen['pid_beim_lauf'] = Auftragsarbeiter.pid(job.id)
        alt = modul.Auftragslauf
        modul.Auftragslauf = Laufattrappe
        self.addCleanup(setattr, modul, 'Auftragslauf', alt)

        call_command('auftrag_fahren', str(job.id))
        self.assertEqual(gesehen['jid'], str(job.id))
        self.assertEqual(gesehen['pid_beim_lauf'], os.getpid())
        self.assertIsNone(Auftragsarbeiter.pid(job.id), 'PID-Datei nach dem Lauf weg')

    def test_ein_unbekannter_auftrag_ist_ein_fehler(self):
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command('auftrag_fahren', '00000000-0000-0000-0000-000000000001')


class DieSteuerung(AufraeumenBasis):

    def test_ohne_schalter_startet_der_arbeiter_nicht_der_faden(self):
        from core.dienste.auftragssteuerung import Auftragssteuerung
        gestartet = []
        alt = Auftragsarbeiter.starten
        Auftragsarbeiter.starten = staticmethod(gestartet.append)
        self.addCleanup(setattr, Auftragsarbeiter, 'starten', alt)
        with override_settings(AUFTRAG_IM_SERVER=False):
            Auftragssteuerung._faden_starten('kennung-1')
        self.assertEqual(gestartet, ['kennung-1'])
