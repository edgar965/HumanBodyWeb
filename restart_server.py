# -*- coding: utf-8 -*-
u"""Den Entwicklungsserver dieses Projekts neu starten — und NUR diesen.

WAS DIESES SKRIPT ANGERICHTET HAT (10.09.2026)
==============================================
Die alte Fassung suchte Prozesse so:

    if 'python' in text and 'manage.py' in text and 'runserver' in text:
        proc.kill()

Darauf passt jeder Django-Entwicklungsserver auf diesem Rechner. Beim Lauf
um 14:39 hat es neben den beiden eigenen auch

    A:\\shortlongx\\pythonVENV\\Scripts\\python.exe manage.py runserver_dual
        [::]:5020 --noreload --nostatic

erwischt — ein fremdes Projekt, das nichts mit 3DTools zu tun hat. Edgar
arbeitet regelmässig mit mehreren Projekten gleichzeitig; ein Werkzeug, das
„alle Django-Server" trifft, ist damit ein Werkzeug, das fremde Arbeit
abbricht.

Zwei weitere Fehler kamen im selben Lauf ans Licht:

* Gestartet wurde mit ``python`` aus dem PATH statt mit dem Interpreter
  dieses Projekts. Auf diesem Rechner ist das ein anderer Python ohne die
  Pakete — der Server kam gar nicht hoch.
* Danach meldete das Skript trotzdem ``Server restarted!``. Es hat nie
  nachgesehen, ob etwas antwortet. Eine Erfolgsmeldung ohne Prüfung ist
  schlimmer als gar keine, weil man ihr glaubt und den Fehler woanders
  sucht.

WIE ES JETZT ERKENNT, WAS IHM GEHOERT
=====================================
Über den PORT, nicht über die Kommandozeile: Wer auf 8081 lauscht, ist
dieser Server — das ist eindeutig und kann keinen fremden treffen. Dazu
sein Elternprozess, aber nur, wenn der aus demselben Verzeichnis läuft
(``runserver`` startet sich für das automatische Neuladen selbst noch
einmal als Kind).

Bekommt psutil die Verbindungen nicht zu sehen (unter Windows braucht das
je nach Rechtelage mehr als ein normaler Benutzer hat), gibt es einen
zweiten Weg: Kommandozeile UND Arbeitsverzeichnis müssen passen. Wessen
Verzeichnis sich nicht lesen lässt, bleibt am Leben — im Zweifel lieber
ein Server zu viel als ein fremder weniger.
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import psutil

__all__ = ['Serverneustart']


class Serverneustart:
    u"""Beendet den Server dieses Projekts und startet ihn wieder."""

    #: Der Port, auf dem HumanBodyWeb lauscht.
    PORT = 8081

    #: Das Projektverzeichnis — der Ordner, in dem dieses Skript liegt.
    WURZEL = Path(__file__).resolve().parent

    #: So lange wird auf den neuen Server gewartet, bevor es als
    #: fehlgeschlagen gilt.
    START_FRIST_S = 60

    #: Und so lange auf das Ende des alten.
    ENDE_FRIST_S = 10

    # ------------------------------------------------------------ Finden

    @classmethod
    def am_port(cls):
        u"""Die PIDs, die auf unserem Port lauschen."""
        pids = set()
        try:
            for verbindung in psutil.net_connections(kind='inet'):
                if (verbindung.status == psutil.CONN_LISTEN
                        and verbindung.laddr
                        and verbindung.laddr.port == cls.PORT
                        and verbindung.pid):
                    pids.add(verbindung.pid)
        # stumm gewollt: Skript ohne Logger — die Meldung geht auf die Konsole, der zweite Weg folgt
        except (psutil.AccessDenied, PermissionError, OSError):
            print(u'  (Verbindungen nicht lesbar — nehme den zweiten Weg)')
        return pids

    @classmethod
    def im_projekt(cls):
        u"""Django-Server, deren Arbeitsverzeichnis unser Projekt IST.

        Der zweite Weg, wenn der Port nichts hergibt. Die Kommandozeile
        allein genügt hier ausdrücklich nicht — genau daran ist die alte
        Fassung gescheitert.
        """
        pids = set()
        for prozess in psutil.process_iter(['pid', 'cmdline']):
            try:
                if not cls._ist_runserver(prozess.info['cmdline'] or []):
                    continue
                if not cls._hier(prozess):
                    continue
                pids.add(prozess.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # stumm gewollt: Ein Prozess, den wir nicht lesen dürfen,
                # ist keiner, den wir beenden dürfen.
                continue
        return pids

    @classmethod
    def _ist_runserver(cls, teile):
        u"""Ist das wirklich ein `manage.py runserver`?

        Auf den ZUSAMMENGESETZTEN Text zu prüfen wäre zu grob: Ein
        Diagnoseskript, das mit `python -c "…manage.py…runserver…"` nach
        genau diesen Servern sucht, trägt die Wörter selbst in seiner
        Kommandozeile — und würde sich beenden. Deshalb müssen es eigene
        Argumente sein.
        """
        manage = any(t.lower().endswith('manage.py') for t in teile)
        server = any(t.lower().startswith('runserver') for t in teile)
        return manage and server

    @classmethod
    def _hier(cls, prozess):
        u"""Läuft der Prozess aus unserem Projektverzeichnis?"""
        try:
            return Path(prozess.cwd()).resolve() == cls.WURZEL
        # stumm gewollt: ein Prozess, dessen Ordner nicht lesbar ist, gehoert nicht zu uns
        except (psutil.AccessDenied, psutil.NoSuchProcess, OSError, ValueError):
            return False

    @classmethod
    def _mit_eltern(cls, pids):
        u"""Den Autoreload-Elternprozess dazunehmen — wenn er hierher gehört."""
        vollstaendig = set(pids)
        for pid in pids:
            try:
                eltern = psutil.Process(pid).parent()
            # stumm gewollt: wer gerade verschwunden ist, braucht keinen Elternprozess mehr
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            if eltern is None or not cls._hier(eltern):
                continue
            try:
                teile = eltern.cmdline() or []
            # stumm gewollt: ein fremder oder verschwundener Elternprozess bleibt unangetastet
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            if cls._ist_runserver(teile):
                vollstaendig.add(eltern.pid)
        return vollstaendig

    # ----------------------------------------------------------- Beenden

    @classmethod
    def beenden(cls):
        u"""Den alten Server abräumen. Gibt zurück, wie viele es waren."""
        # BEIDE Wege, nicht nur einer: Wer am Port lauscht, ist der aktive
        # Server; im Projektverzeichnis liegen daneben oft noch Reste
        # früherer Läufe (`runserver` startet sich zum Neuladen selbst als
        # Kind, und ein gescheiterter Start bleibt als Elternprozess
        # zurück). Gemessen nach einem Neustart: vier Prozesse, von denen
        # nur einer lauschte. Beide Wege sind an dieses Projekt gebunden,
        # zusammen also genauso sicher wie einer.
        pids = cls.am_port() | cls.im_projekt()
        pids = cls._mit_eltern(pids)
        if not pids:
            print(u'Kein laufender Server auf Port %d gefunden.' % cls.PORT)
            return 0
        for pid in sorted(pids):
            try:
                prozess = psutil.Process(pid)
                print(u'  beende %d: %s' % (pid, ' '.join(prozess.cmdline())))
                prozess.terminate()
            # stumm gewollt: Skript ohne Logger — die Meldung steht auf der Konsole
            except (psutil.NoSuchProcess, psutil.AccessDenied) as fehler:
                print(u'  %d nicht beendbar: %s' % (pid, fehler))
        lebende = [psutil.Process(p) for p in pids if psutil.pid_exists(p)]
        _, uebrig = psutil.wait_procs(lebende, timeout=cls.ENDE_FRIST_S)
        for prozess in uebrig:
            try:
                print(u'  %d reagiert nicht — harter Abbruch' % prozess.pid)
                prozess.kill()
            # stumm gewollt: wer beim harten Abbruch schon weg ist, ist erledigt
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return len(pids)

    # ------------------------------------------------------------ Starten

    @classmethod
    def python(cls):
        u"""Der Interpreter, mit dem gestartet wird.

        `sys.executable` — also derselbe, mit dem dieses Skript läuft. Der
        hat psutil und damit auch alles andere aus dieser Umgebung. `python`
        aus dem PATH ist auf diesem Rechner ein anderer, und der Server kam
        damit nicht hoch.
        """
        return sys.executable

    @classmethod
    def starten(cls):
        kennzeichen = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        return subprocess.Popen(
            [cls.python(), str(cls.WURZEL / 'manage.py'),
             'runserver', str(cls.PORT)],
            cwd=str(cls.WURZEL), creationflags=kennzeichen)

    @classmethod
    def erreichbar(cls, frist_s=1.0):
        u"""Antwortet der Port? Über 127.0.0.1, nie über `localhost`.

        (`~/.claude/rules/zeit-messen.md`: Die IPv6-Auflösung von `localhost`
        kostet unter Windows Sekunden und täuscht eine Grundlast vor.)
        """
        try:
            with socket.create_connection(('127.0.0.1', cls.PORT), frist_s):
                return True
        # stumm gewollt: keine Verbindung heisst der Server ist (noch) nicht da — genau die Frage
        except OSError:
            return False

    @classmethod
    def warten(cls):
        u"""Auf den neuen Server warten — und ehrlich melden, was daraus wurde."""
        ende = time.time() + cls.START_FRIST_S
        while time.time() < ende:
            if cls.erreichbar():
                return True
            time.sleep(0.5)
        return False

    # --------------------------------------------------------------- Lauf

    @classmethod
    def lauf(cls):
        print(u'Server neu starten — %s, Port %d' % (cls.WURZEL, cls.PORT))
        cls.beenden()
        print(u'Starte mit %s …' % cls.python())
        prozess = cls.starten()
        if cls.warten():
            print(u'Server läuft (PID %d), Port %d antwortet.'
                  % (prozess.pid, cls.PORT))
            return 0
        # KEINE ERFOLGSMELDUNG OHNE PRUEFUNG — genau daran ist die alte
        # Fassung gescheitert.
        print(u'FEHLGESCHLAGEN: Port %d antwortet nach %d s nicht.'
              % (cls.PORT, cls.START_FRIST_S))
        if prozess.poll() is not None:
            print(u'Der Prozess ist bereits beendet (Rückgabewert %s).'
                  % prozess.returncode)
        print(u'Zum Nachsehen ohne Fenster:\n  %s manage.py runserver %d'
              % (cls.python(), cls.PORT))
        return 1


if __name__ == '__main__':
    os.chdir(str(Serverneustart.WURZEL))
    raise SystemExit(Serverneustart.lauf())
