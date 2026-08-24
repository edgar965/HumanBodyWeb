# -*- coding: utf-8 -*-
"""Logbeobachter — den Fortschritt aus der Logdatei eines Unterprozesses lesen.

Herausgelöst aus `werkzeuge._monitor_pipeline_log` (67 Zeilen). Die SMPL-Pipelines
schreiben ihre Ausgabe in eine DATEI, nicht in eine Pipe — nur so übersteht ein
Lauf einen Django-Neustart. Diese Klasse ist das `tail` darauf.

WARUM DIE DATEI JEDE RUNDE NEU GEÖFFNET WIRD
============================================
Ein offen gehaltenes Handle bekäme ein Abschneiden oder eine Rotation der Datei
nicht mit, und beim ersten Durchgang existiert sie oft noch gar nicht (der
Kindprozess legt sie erst an). Gelesen wird nur ab der letzten Stelle
(`self.stelle`) — je Runde ein paar Zeilen, nicht die ganze Datei.

WAS AUS EINER ZEILE GELESEN WIRD
================================
Zwei Formen, weil die Wrapper unterschiedlich melden:

    tqdm:  ` 42%|████      | 42/100`   ->  42 %
    Bruch: `Frame 42 / 100`            ->  42 %

Der Deckel bei 95 % ist Absicht: Fertig ist der Lauf erst, wenn die BVH
geschrieben ist. Ein Fortschritt von 100 % neben dem Zustand „läuft" hat schon
einmal zu der Frage geführt, warum nichts passiert.
"""

import logging
import re
import time

logger = logging.getLogger('core')


class Logbeobachter:
    """Liest die Logdatei eines laufenden Prozesses und meldet den Fortschritt."""

    #: tqdm-Balken: ` 42%|…`
    PROZENT = re.compile(r'(\d+)%\|')
    #: Bruchform: `42 / 100`
    BRUCH = re.compile(r'(\d+)\s*/\s*(\d+)')
    #: Höchster Wert, den die Beobachtung meldet (siehe Modul-Docstring).
    DECKEL = 95
    #: Wie oft in die Datei gesehen wird.
    TAKT_S = 1
    #: Frühestens so oft wird der Auftrag geschrieben.
    SPERRE_S = 0.5
    LAENGE_ZEILE = 80
    LAENGE_MELDUNG = 100

    def __init__(self, job, logdatei, bilder, proc=None, pid=None):
        self.job = job
        self.logdatei = logdatei
        self.bilder = bilder
        self.proc = proc
        self.pid = pid
        self.stelle = 0
        self._letzte_meldung = 0.0

    # ------------------------------------------------------------------ Ablauf

    def verfolgen(self):
        """Läuft, bis der Prozess endet."""
        while self.lebt():
            time.sleep(self.TAKT_S)
            neu = self.nachschub()
            if neu:
                self.auswerten(neu)

    def lebt(self):
        """Läuft der beobachtete Prozess noch?

        Mit `proc` (eigener Start) über `poll()`, mit `pid` (Wiederaufnahme nach
        einem Serverneustart) über das Betriebssystem. Die PID-Prüfung steht in
        `prozesspruefung.py` und NICHT in `werkzeuge.py`: Von dort kommt der
        Aufruf hierher, und zwei Module, die einander brauchen, hat das Werkzeug
        `abhaengigkeiten` sofort als Zyklus gemeldet.
        """
        if self.proc is not None:
            return self.proc.poll() is None
        from .prozesspruefung import Prozesspruefung
        return Prozesspruefung.lebt(self.pid)

    def nachschub(self):
        """Was seit dem letzten Blick dazugekommen ist — oder `''`."""
        try:
            with open(self.logdatei, 'r', encoding='utf-8',
                      errors='replace') as datei:
                datei.seek(self.stelle)
                neu = datei.read()
                self.stelle = datei.tell()
                return neu
        except (FileNotFoundError, OSError):
            # stumm gewollt: Beim ersten Durchgang gibt es die Logdatei oft noch
            # nicht; der Prozess schreibt sie erst. Eine Meldung je Sekunde je
            # Auftrag waere das Log voll und wuerde nichts sagen.
            return ''

    # ---------------------------------------------------------------- Auswerten

    def auswerten(self, text, jetzt=None):
        """Die LETZTE Zeile des Nachschubs deuten und melden.

        Nur die letzte: Ein tqdm-Balken schreibt viele Zeilen je Sekunde, und
        interessant ist der neueste Stand. Gedrosselt auf `SPERRE_S`, sonst wird
        der Auftrag mehrmals je Sekunde geschrieben.
        """
        jetzt = jetzt if jetzt is not None else time.time()
        if jetzt - self._letzte_meldung < self.SPERRE_S:
            return False
        zeilen = [z.strip() for z in text.splitlines() if z.strip()]
        if not zeilen:
            return False
        self._letzte_meldung = jetzt
        zeile = zeilen[-1]
        anteil = self.anteil(zeile)
        if anteil is not None:
            self.job.progress = anteil
        self.job.progress_detail = self.meldung(zeile)
        self.job.save(update_fields=['progress', 'progress_detail', 'updated_at'])
        return True

    @classmethod
    def anteil(cls, zeile):
        """Prozent aus der Zeile — oder `None`, wenn keine Zahl darin steht."""
        prozent = cls.PROZENT.search(zeile)
        if prozent:
            return min(int(prozent.group(1)), cls.DECKEL)
        bruch = cls.BRUCH.search(zeile)
        if bruch:
            jetzt, gesamt = int(bruch.group(1)), int(bruch.group(2))
            if gesamt > 0:
                return min(int(jetzt / gesamt * cls.DECKEL), cls.DECKEL)
        return None

    def meldung(self, zeile):
        text = zeile[:self.LAENGE_ZEILE]
        if self.bilder:
            text = '%s — %d frames' % (text, self.bilder)
        return text[:self.LAENGE_MELDUNG]
