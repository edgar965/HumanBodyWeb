# -*- coding: utf-8 -*-
"""Mesh3daitrainingsdatum — wann an den Daten eines Jobs zuletzt ein Netz fertig trainiert wurde (17.10.2026).

Edgar: „mach eine Spalte in /mesh-3D-AI/#jobs mit dem Datum wann die zum letzten Mal trainiert wurden".
Ein Training zählt, wenn sein Laufordner ein `lauf_ergebnis.json` hat (das Trainingsskript schreibt es erst am Ende) — Zeitpunkt ist die Änderungszeit dieser Datei,
also das ENDE des Trainings (der Ordnername trägt den Start). Gesucht wird an zwei Stellen:
  * `3DObjects/mesh3dai/<Job>/_laeufe/*` — die Läufe der Jobseite (auch die des gemeinsamen Netzes, das für jeden Job einen Ordner anlegt);
  * `3DObjects/mesh3dai/_vorstufe/laeufe/*` — die Netze der Vorstufe und der Form, wenn `training_daten` ODER `paare` den Job nennt (seit 19.10.2026 lernt das Formtraining 2 auch aus den
    Trainingspaaren, `--paare`; sie stehen nur in `paare`, nicht in `training_daten` — die Tabelle zeigte deshalb bei allen Paaren „nie“, Edgar: „die sind alle nicht trainiert??“).
Probeläufe (Name endet auf `_probe`) und `_diagnose/` zählen nicht. Liest bei jedem Aufruf neu (wenige kleine Dateien).
Bei einem Paar sind die Läufe unter `_laeufe/` Ergebnisse der Kette auf dem Tripo-Netz, kein Training — dort fragt die Tabelle nur `wo=('vorstufe',)`.

    Mesh3daitrainingsdatum.letztes('Ursula1', wo=('job', 'vorstufe')) -> None | {'zeit': float (Unix), 'lauf': Ordnername, 'art': 'job' | 'vorstufe', 'mit': [Jobs des Trainings]}
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
    def letztes(cls, job, wo=('job', 'vorstufe')):
        kandidaten = (cls._im_job(job) if 'job' in wo else []) + (cls._gemeinsam(job) if 'vorstufe' in wo else [])
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
            ergebnis = cls._lesen(lauf / cls.ERGEBNIS)
            mit = list(ergebnis.get('training_daten') or []) + list(ergebnis.get('paare') or [])
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
