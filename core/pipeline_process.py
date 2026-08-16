# -*- coding: utf-8 -*-
"""PipelineProzess — die EINE Stelle, an der ML-Subprozesse gestartet werden.

WARUM (Review 12.08.2026)
------------------------
Django (Python 3.14) startet die Pipelines in der ML-Umgebung (Python 3.10) und
liest deren stdout zeilenweise als Fortschrittskanal. Sechs Startstellen, drei
unterschiedliche Ausstattungen:

* Zeichensatz: NUR EINE der vier Stellen setzte `encoding='utf-8',
  errors='replace'`. Die anderen verließen sich auf die Windows-Landeseinstellung
  — hier gemessen `cp1252`, UTF-8-Modus aus. Gibt eine ML-Bibliothek etwas
  außerhalb von cp1252 aus (Fortschrittsbalken, ein Pfad mit Umlaut wie
  `0030_BallettLänger.mp4`), kommt im besten Fall Buchstabensalat an, im
  schlechteren stirbt die Leseschleife mit `UnicodeDecodeError` — und der Auftrag
  gilt als gescheitert, während die Pipeline auf der Grafikkarte weiterrechnet.
* stderr: Fünf von sechs Stellen räumten stderr mit einem eigenen Faden ab, die
  OpenPose-Stelle nicht — bei `stderr=PIPE`. OpenPose/Caffe schreibt dort viel.
  Läuft der Pipe-Puffer (etwa 64 KB) voll, blockiert der Kindprozess beim
  Schreiben, während Django auf die nächste stdout-Zeile wartet. Beide warten
  dann aufeinander.

Deshalb wird hier gestartet und nicht mehr in den Aufrufstellen. Die Deutung
der Zeilen bleibt bei den Aufrufern — sie ist je Pipeline verschieden (`TOTAL:`,
`STATUS:`, tqdm) und soll nicht in einen Helfer gepresst werden.

WARUM AUCH STDOUT IN EINEM EIGENEN FADEN GELESEN WIRD (Sparring, 13.08.2026)
----------------------------------------------------------------------------
Die erste Fassung übergab `proc.stdout` an den Aufrufer, der darüber lief:

    for zeile in proc.stdout:        # ALT
        ...
    pp.warten(timeout=1800)

Diese Schleife läuft bis zum Dateiende, also bis das Kind stdout schliesst.
Hängt das Kind vorher — CUDA-Hänger, ein Modell-Download, der nie zurückkommt,
eine Frage auf stdin —, blockiert sie **unbegrenzt**. Der Timeout darunter wird
nie erreicht; er bewacht nur den Rest nach dem Dateiende. Der Auftrag steht
dann für immer auf „läuft", und die Grafikkarte bleibt belegt.

Deshalb liest jetzt ein Faden stdout leer und legt die Zeilen in eine
Warteschlange; der Aufrufer holt sie mit Zeitgrenze ab. Zwei Entscheidungen
dabei, beide gegen einen ersten Entwurf aus dem Sparring:

* **Die Warteschlange ist unbegrenzt.** Mit `maxsize` blockiert der Lesefaden,
  sobald der Verbraucher langsamer ist als die Pipeline (jede Zeile schreibt in
  die Datenbank) — dann läuft der Pipe-Puffer voll und das Kind blockiert beim
  Schreiben. Das wäre genau der Klemmer, gegen den dieser Helfer gebaut wurde,
  nur eine Ebene tiefer. Der Rückstau gehört in den Pipe-Puffer des
  Betriebssystems, nicht in den eigenen Faden. Wer stdout gar nicht liest,
  übergibt `stdout_lesen=False` — dann geht es nach DEVNULL und wächst nichts.
* **Die Zeitgrenze ist Sache der Aufrufstelle.** Es gibt kein allgemeines
  Kriterium für „still, aber lebt": GVHMR lädt beim ersten Lauf minutenlang
  Gewichte, Torch/CUDA startet stumm, MocapNET rechnet Stapel ohne Ausgabe.
  Der Helfer liefert den Mechanismus, die Zahl kommt von aussen — und `None`
  heisst weiterhin „warte ewig", wie vorher.

WAS DIESE KLASSE NICHT ÄNDERT
-----------------------------
Die bestehende Prüfung der Aufrufer bleibt gültig und wird bewusst nicht
ersetzt: Rückgabewert prüfen, Ausgabedatei prüfen, STOP_FLAG beachten, teilweise
erzeugte BVH-Dateien retten. Das war schon vorher sauber gebaut.
"""
import logging
import os
import queue
import subprocess
import threading

logger = logging.getLogger('core')


class PipelineStille(TimeoutError):
    """Der Subprozess hat zu lange nichts geschrieben — als Hänger gewertet.

    Eigene Klasse, damit die Aufrufer sie von `subprocess.TimeoutExpired`
    unterscheiden können: Diese hier bedeutet „lief noch, sagte aber nichts
    mehr", jene „war nach dem Dateiende noch nicht beendet"."""


class PipelineProzess:
    """Startet einen Subprozess mit einheitlichem Zeichensatz und abgeräumten Strömen.

        p = PipelineProzess.starten(cmd, cwd=..., env_extra={'CUDA_VISIBLE_DEVICES': '0'})
        for zeile in p.stdout_zeilen(stille_timeout=300):
            ...
        p.warten(timeout=1800)
        if p.proc.returncode != 0:
            raise RuntimeError(p.fehlertext())
    """

    #: So viele stderr-Zeilen werden behalten. Mehr braucht keine Fehlermeldung,
    #: und ein Modell-Download mit Fortschrittsbalken schreibt Zehntausende.
    STDERR_ZEILEN = 400

    #: Endemarke in der stdout-Warteschlange. Eine eigene Kennung statt `None`,
    #: damit eine leere Zeile aus der Pipeline nicht als Ende gelesen wird.
    _ENDE = object()

    def __init__(self, proc, stderr_zeilen, faeden, stdout_q):
        self.proc = proc
        self._stderr_zeilen = stderr_zeilen
        self._faeden = [f for f in faeden if f is not None]
        self._stdout_q = stdout_q

    # ------------------------------------------------------------------- Starten

    @classmethod
    def starten(cls, cmd, cwd=None, env_extra=None, stderr_sammeln=True,
                stdout_lesen=True):
        """Subprozess starten. Beide Ströme sind UTF-8-dekodiert.

        `stderr_sammeln=True` liest stderr in einem eigenen Faden mit (gegen den
        vollen Puffer) und behält die letzten Zeilen für die Fehlermeldung.

        `stdout_lesen=True` liest auch stdout in einem eigenen Faden in eine
        Warteschlange; abgeholt wird über `stdout_zeilen()`. `False` schickt
        stdout nach DEVNULL — für Aufrufstellen, die den Fortschritt anders
        verfolgen (OpenPose zählt geschriebene JSON-Dateien). Vorher stand
        stdout dort auf PIPE, ohne dass jemand las: derselbe volle Puffer,
        derselbe Klemmer wie bei stderr, nur noch nicht aufgefallen."""
        env = cls.umgebung(env_extra)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if stdout_lesen else subprocess.DEVNULL,
            stderr=subprocess.PIPE if stderr_sammeln else subprocess.DEVNULL,
            text=True,
            bufsize=1,                      # zeilenweise, sonst kommt Fortschritt in Schüben
            encoding='utf-8',
            errors='replace',               # ein Ersatzzeichen ist besser als ein Absturz
            cwd=str(cwd) if cwd else None,
            env=env,
        )
        zeilen, stderr_faden, stdout_faden, stdout_q = [], None, None, None
        if stderr_sammeln:
            stderr_faden = threading.Thread(target=cls._stderr_lesen,
                                            args=(proc.stderr, zeilen), daemon=True)
            stderr_faden.start()
        if stdout_lesen:
            stdout_q = queue.Queue()
            stdout_faden = threading.Thread(target=cls._stdout_lesen,
                                            args=(proc.stdout, stdout_q), daemon=True)
            stdout_faden.start()
        return cls(proc, zeilen, [stderr_faden, stdout_faden], stdout_q)

    @staticmethod
    def umgebung(env_extra=None):
        """Umgebung für den Kindprozess.

        `PYTHONIOENCODING` und `PYTHONUTF8` wirken auf der ANDEREN Seite: Sie
        bringen den Kindprozess dazu, UTF-8 zu schreiben — `encoding='utf-8'`
        allein sagt nur, wie wir lesen. Beides gehört zusammen.

        `PYTHONUNBUFFERED` sorgt dafür, dass der Fortschritt fortlaufend
        ankommt; ohne das puffert Python blockweise, sobald die Ausgabe nicht an
        ein Terminal geht, und die Anzeige springt.

        `os.environ` wird geerbt (die Pipelines brauchen PATH und CUDA-Variablen),
        aber `PYTHONPATH`/`PYTHONHOME` werden entfernt: Django läuft in 3.14, die
        Pipelines in 3.10 — ein geerbter Suchpfad zieht Pakete der falschen
        Version herein."""
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        env['PYTHONUNBUFFERED'] = '1'
        for schluessel in ('PYTHONPATH', 'PYTHONHOME'):
            env.pop(schluessel, None)
        if env_extra:
            env.update({k: str(v) for k, v in env_extra.items()})
        return env

    @property
    def stderr_zeilen(self):
        """Die mitgelesenen stderr-Zeilen (dieselbe Liste, die weiter gefüllt wird).

        Die Aufrufer in `views.py` bauen daraus ihre Fehlermeldungen; sie geben
        die Liste weiter, statt sie zu kopieren, damit auch Zeilen enthalten sind,
        die erst nach dem Zugriff eintreffen."""
        return self._stderr_zeilen

    @staticmethod
    def _stderr_lesen(strom, ziel):
        # KEIN Lock um Anhängen und Kürzen, und das ist geprüft: `str.join` und
        # `list(...)` auf der Leserseite sind C-Funktionen, die den GIL nicht
        # abgeben — ein anderer Faden läuft währenddessen gar nicht. Zwei
        # Modelle haben hier unabhängig ein Datenrennen vorhergesagt;
        # `Docu/gegenprobe_stderr_race.py` hat es mit 3,2 Mio. Anhänge- und
        # 434.000 Lesevorgängen nicht auslösen können (13.08.2026).
        # ACHTUNG: Diese Zusicherung fällt mit dem GIL. Die Gegenprobe prüft
        # `sys._is_gil_enabled()` mit und schlägt an, wenn sie nicht mehr gilt.
        try:
            for zeile in strom:
                ziel.append(zeile)
                if len(ziel) > PipelineProzess.STDERR_ZEILEN:
                    del ziel[:-PipelineProzess.STDERR_ZEILEN]
        except (ValueError, OSError):
            pass                     # Strom wurde geschlossen — der Prozess ist fertig

    @classmethod
    def _stdout_lesen(cls, strom, ziel_q):
        """stdout leerlesen — ohne Rücksicht darauf, ob jemand abholt."""
        try:
            for zeile in strom:
                ziel_q.put(zeile)
        except (ValueError, OSError):
            pass                     # Strom geschlossen
        finally:
            ziel_q.put(cls._ENDE)    # auch im Fehlerfall: sonst wartet der Abholer ewig

    # ------------------------------------------------------------------- Abholen

    def stdout_zeilen(self, stille_timeout=None):
        """Zeilen von stdout, bis der Prozess sie schliesst.

        `stille_timeout=None` wartet unbegrenzt (wie die alte Schleife über
        `proc.stdout`). Mit einer Zahl gilt: Kommt so viele Sekunden lang keine
        Zeile, wird der Prozess als hängend betrachtet — er wird BEENDET und
        `PipelineStille` geworfen.

        Das Beenden geschieht hier und nicht beim Aufrufer, weil sonst jede
        Aufrufstelle wieder ihren eigenen Aufräumcode bekäme; genau das war die
        Krankheit. Und ein Prozess, den wir gerade für hängend erklärt haben,
        darf die Grafikkarte nicht weiter belegen."""
        if self._stdout_q is None:
            raise RuntimeError('Mit stdout_lesen=False gestartet — es gibt keine Zeilen')
        while True:
            try:
                zeile = self._stdout_q.get(timeout=stille_timeout)
            except queue.Empty:
                logger.error('PipelineProzess: keine Ausgabe seit %s s — Prozess %s '
                             'wird beendet', stille_timeout, self.proc.pid)
                self.beenden()
                raise PipelineStille(
                    'Pipeline hat seit %s Sekunden nichts geschrieben und wurde '
                    'beendet' % stille_timeout)
            if zeile is self._ENDE:
                return
            yield zeile

    # -------------------------------------------------------------------- Warten

    def warten(self, timeout=None):
        """Auf das Ende warten und die Lesefäden einsammeln."""
        try:
            self.proc.wait(timeout=timeout)
        finally:
            for faden in self._faeden:
                faden.join(timeout=5)
        return self.proc.returncode

    def fehlertext(self, max_zeichen=4000):
        """Die letzten stderr-Zeilen, gekürzt — für Fehlermeldungen."""
        return ''.join(self._stderr_zeilen)[-max_zeichen:].strip()

    def beenden(self, warten_s=10):
        """Prozessbaum beenden UND auf sein Ende warten.

        `taskkill /T` statt `proc.kill()`: Die Pipelines starten selbst weiter
        (ffmpeg, Torch-Arbeiter). Ein `kill` auf den Vater lässt die Kinder mit
        belegtem Grafikspeicher zurück — beim nächsten Lauf fehlt dann VRAM.

        DAS WARTEN AM ENDE ist neu (Sparring, 13.08.2026): `taskkill` kehrt
        zurück, sobald es die Beendigung angestossen hat, nicht wenn sie fertig
        ist. Wer danach sofort den nächsten Lauf startet, findet den
        Grafikspeicher noch belegt. Bleibt der Prozess auch dann stehen, folgt
        `kill()` als letztes Mittel."""
        if self.proc.poll() is not None:
            return
        angestossen = False
        if os.name == 'nt':
            try:
                subprocess.run(['taskkill', '/PID', str(self.proc.pid), '/T', '/F'],
                               capture_output=True, timeout=15)
                angestossen = True
            except (OSError, subprocess.SubprocessError):
                logger.warning('PipelineProzess: taskkill fehlgeschlagen, nutze kill()')
        if not angestossen:
            # Auch der Weg für Nicht-Windows: ohne ihn würde unten auf einen
            # Prozess gewartet, den niemand beendet hat.
            try:
                self.proc.kill()
            except OSError:
                pass
        try:
            self.proc.wait(timeout=warten_s)
        except subprocess.TimeoutExpired:
            logger.warning('PipelineProzess: Prozess %s lebt nach %s s noch — kill()',
                           self.proc.pid, warten_s)
            try:
                self.proc.kill()
                self.proc.wait(timeout=5)
            except (OSError, subprocess.SubprocessError):
                logger.exception('PipelineProzess: kill() fehlgeschlagen')
