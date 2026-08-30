# -*- coding: utf-8 -*-
u"""Was jeder Pipeline-Lauf mitbringt: Auftrag, Video, Ausgabeordner.

BEFUND `doppelcode` (30.08.2026)
===============================
Vier Läufe (`Erkennung2d`, `V4Lauf`, `Hybridlauf`, `Smpllauf`) begannen mit
demselben Konstruktor und trugen dieselbe Obergrenze für die Fehlerausgabe —
letztere sogar unter ZWEI Namen:

    MAX_ERROR_CHARS = 2000     erkennung2d.py, mocapnet4.py, smpllauf.py
    MAX_FEHLERZEICHEN = 2000   auftragslauf.py

Vier Kopien einer Zahl sind harmlos, solange niemand sie ändert. Wer sie aber
anhebt, weil eine Meldung abgeschnitten ankam, findet drei davon — und die
vierte Pipeline schneidet weiter mittendrin ab. Das sieht dann nach einem
Fehler DIESER Pipeline aus.

DIE EINSTELLUNGEN KOMMEN ERST AUF NACHFRAGE. `AppSettings.load()` liest die
Datenbank; im Konstruktor hätte das jeden Lauf eine Abfrage gekostet, auch die,
die nie danach fragen (`Erkennung2d`). Als Eigenschaft wird sie einmal geholt
und danach gehalten.
"""
from ..models import AppSettings


class Pipelinelauf:
    u"""Gemeinsame Grundlage der Video-zu-BVH-Läufe."""

    #: So viele Zeichen der Fehlerausgabe landen in der Meldung. Mehr sprengt
    #: die Anzeige, weniger schneidet die eigentliche Ursache ab — sie steht
    #: bei Python-Tracebacks am ENDE, deshalb wird von hinten geschnitten.
    MAX_FEHLERZEICHEN = 2000

    def __init__(self, job, video_path, output_dir):
        self.job = job
        self.video_path = video_path
        self.output_dir = output_dir
        self.params = job.pipeline_params or {}
        self._einstellungen = None

    @property
    def einstellungen(self):
        u"""Die Anwendungseinstellungen — einmal geholt, dann gehalten."""
        if self._einstellungen is None:
            self._einstellungen = AppSettings.load()
        return self._einstellungen

    @property
    def stamm(self):
        u"""Dateiname des Auftrags ohne Endung — Grundlage der Ausgabenamen."""
        return self.job.name.rsplit('.', 1)[0]

    @classmethod
    def fehlerausschnitt(cls, text):
        u"""Das Ende der Fehlerausgabe, auf `MAX_FEHLERZEICHEN` gekürzt."""
        return (text or '')[-cls.MAX_FEHLERZEICHEN:]
