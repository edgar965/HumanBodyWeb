# -*- coding: utf-8 -*-
"""Mesh3daitrainingsdatum — wann an den Daten eines Jobs zuletzt ein Netz fertig trainiert wurde (17.10.2026).

Edgar: „mach eine Spalte in /mesh-3D-AI/#jobs mit dem Datum wann die zum letzten Mal trainiert wurden".
Ein Training zählt, wenn sein Laufordner ein `lauf_ergebnis.json` hat (das Trainingsskript schreibt es erst am Ende) — Zeitpunkt ist die Änderungszeit dieser Datei,
also das ENDE des Trainings (der Ordnername trägt den Start). Gesucht wird an zwei Stellen:
  * `3DObjects/mesh3dai/<Job>/_laeufe/*` — die Läufe der Jobseite (auch die des gemeinsamen Netzes, das für jeden Job einen Ordner anlegt);
  * `3DObjects/mesh3dai/_vorstufe/laeufe/*` — die Netze der Vorstufe und der Form, wenn `training_daten` den Job nennt.
Probeläufe (Name endet auf `_probe`) und `_diagnose/` zählen nicht. Liest bei jedem Aufruf neu (wenige kleine Dateien).

    Mesh3daitrainingsdatum.letztes('Ursula1') -> None | {'zeit': float (Unix), 'lauf': Ordnername, 'art': 'job' | 'vorstufe', 'mit': [Jobs des Trainings]}
"""

import json
import logging

from .mesh3daidatensatz import Mesh3daidatensatz

logger = logging.getLogger('core')

__all__ = ['Mesh3daitrainingsdatum']


class Mesh3daitrainingsdatum:
    ERGEBNIS = 'lauf_ergebnis.json'
    GEMEINSAM = ('_vorstufe', 'laeufe')

    @classmethod
    def letztes(cls, job):
        kandidaten = cls._im_job(job) + cls._gemeinsam(job)
        return max(kandidaten, key=lambda k: k['zeit']) if kandidaten else None

    @classmethod
    def _im_job(cls, job):
        ordner = Mesh3daidatensatz.ordner(job) / '_laeufe'
        aus = []
        for lauf in cls._fertige(ordner):
            ergebnis = cls._lesen(lauf / cls.ERGEBNIS)
            aus.append({'zeit': (lauf / cls.ERGEBNIS).stat().st_mtime, 'lauf': lauf.name, 'art': 'job', 'mit': list(ergebnis.get('training_daten') or [job])})
        return aus

    @classmethod
    def _gemeinsam(cls, job):
        ordner = Mesh3daidatensatz.ordner(cls.GEMEINSAM[0]) / cls.GEMEINSAM[1]
        aus = []
        for lauf in cls._fertige(ordner):
            mit = list(cls._lesen(lauf / cls.ERGEBNIS).get('training_daten') or [])
            if str(job) in mit:
                aus.append({'zeit': (lauf / cls.ERGEBNIS).stat().st_mtime, 'lauf': lauf.name, 'art': 'vorstufe', 'mit': mit})
        return aus

    @classmethod
    def _fertige(cls, ordner):
        if not ordner.is_dir():
            return []
        return [p for p in ordner.iterdir() if p.is_dir() and not p.name.endswith('_probe') and (p / cls.ERGEBNIS).is_file()]

    @staticmethod
    def _lesen(datei):
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            logger.warning('Mesh3daitrainingsdatum: %s nicht lesbar (wird gerade geschrieben?)', datei)
            return {}
