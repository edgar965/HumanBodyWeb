# -*- coding: utf-8 -*-
u"""Auftragsarbeiter — ein Auftrag läuft in einem eigenen Prozess, nicht im Server.

WARUM (12.09.2026, Edgar: „schlägt fehl, siehe logs"): Auftrag 9489ddb8 lief
drei Sekunden, dann lud der Entwicklungsserver neu, weil eine Python-Datei
geändert worden war — und der Lauf hing an einem Faden IM Serverprozess.
`Startaufraeumen` fand danach weder BVH noch lebende PID und vermerkte:
„Server was restarted while job was running". Am selben Tag traf das vier
Aufträge; bei zwei parallelen Sitzungen am selben Baum lädt der Server
mehrmals in der Stunde neu.

Jetzt startet der Server für jeden Auftrag `manage.py auftrag_fahren <id>`
als ABGELÖSTEN Prozess (eigene Prozessgruppe, kein Konsolenfenster): Er
rechnet `Auftragslauf` wie bisher der Faden, schreibt den Fortschritt in
dieselbe Datenbank, und ein Neustart des Servers lässt ihn in Ruhe. Seine PID
steht in `<Auftragsordner>/auftrag.pid`, seine Ausgabe in `auftrag.log`;
`Startaufraeumen` und `Haenger` fragen zuerst danach.
"""
import logging
import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings

from ..pipelines.prozesspruefung import Prozesspruefung

logger = logging.getLogger('core')


class Auftragsarbeiter:
    u"""Der abgelöste Prozess, der einen Auftrag rechnet."""

    PID_DATEI = 'auftrag.pid'
    LOG_DATEI = 'auftrag.log'
    BEFEHL = 'auftrag_fahren'

    @staticmethod
    def ordner(job_id):
        return Path(settings.MEDIA_ROOT) / 'output' / str(job_id)

    @classmethod
    def pid_datei(cls, job_id):
        return cls.ordner(job_id) / cls.PID_DATEI

    @staticmethod
    def flags():
        u"""Abgelöst vom Server: eigene Gruppe, kein Fenster, wenn möglich
        aus dem Job-Objekt des Servers heraus (Windows); sonst 0.

        `CREATE_NO_WINDOW`, NICHT `DETACHED_PROCESS` (12.09.2026): Ein
        abgelöster Prozess hat gar keine Konsole — und `sys.executable` ist
        der venv-Starter, der den echten Interpreter als Kind startet. Ein
        Konsolenkind eines konsolenlosen Vaters bekommt eine NEUE, sichtbare
        Konsole: das cmd-Fenster beim Start jedes Auftrags. Mit
        `CREATE_NO_WINDOW` bekommt der Arbeiter eine eigene unsichtbare
        Konsole, die Interpreter, Wrapper und GEM erben (gemessen:
        `ProjektTemp/fensterprobe.py`)."""
        return (getattr(subprocess, 'CREATE_NO_WINDOW', 0)
                | getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
                | getattr(subprocess, 'CREATE_BREAKAWAY_FROM_JOB', 0))

    @classmethod
    def starten(cls, job_id):
        u"""Den Arbeitsprozess anwerfen; liefert seine PID."""
        ordner = cls.ordner(job_id)
        ordner.mkdir(parents=True, exist_ok=True)
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'),
                  cls.BEFEHL, str(job_id)]
        protokoll = open(ordner / cls.LOG_DATEI, 'ab')
        try:
            prozess = cls._popen(befehl, protokoll)
        finally:
            protokoll.close()
        cls.pid_datei(job_id).write_text(str(prozess.pid))
        logger.info('Auftrag %s: Arbeitsprozess %s gestartet', job_id, prozess.pid)
        return prozess.pid

    @classmethod
    def _popen(cls, befehl, protokoll):
        u"""`CREATE_BREAKAWAY_FROM_JOB` scheitert, wenn das Job-Objekt des
        Servers es verbietet — dann ohne."""
        gemeinsam = dict(cwd=str(settings.BASE_DIR), stdin=subprocess.DEVNULL,
                         stdout=protokoll, stderr=subprocess.STDOUT, close_fds=True)
        if os.name != 'nt':
            return subprocess.Popen(befehl, start_new_session=True, **gemeinsam)
        try:
            return subprocess.Popen(befehl, creationflags=cls.flags(), **gemeinsam)
        except OSError:
            flags = cls.flags() & ~getattr(subprocess, 'CREATE_BREAKAWAY_FROM_JOB', 0)
            return subprocess.Popen(befehl, creationflags=flags, **gemeinsam)

    @classmethod
    def pid(cls, job_id):
        u"""Die eingetragene PID oder None."""
        try:
            return int(cls.pid_datei(job_id).read_text().strip())
        except (FileNotFoundError, OSError, ValueError):
            return None

    @classmethod
    def lebt(cls, job_id):
        u"""Läuft der Arbeitsprozess dieses Auftrags noch?"""
        return Prozesspruefung.lebt(cls.pid(job_id))

    @classmethod
    def eintragen(cls, job_id):
        u"""Vom Arbeitsprozess selbst: die eigene PID hinterlegen (der Server
        schreibt sie schon, aber ein von Hand gestarteter Lauf nicht)."""
        cls.ordner(job_id).mkdir(parents=True, exist_ok=True)
        cls.pid_datei(job_id).write_text(str(os.getpid()))

    @classmethod
    def austragen(cls, job_id):
        u"""Am Ende des Arbeitsprozesses: die PID-Datei ist eine Notiz."""
        try:
            cls.pid_datei(job_id).unlink()
        except (FileNotFoundError, OSError):
            logger.debug('PID-Datei von %s schon weg', job_id, exc_info=True)
