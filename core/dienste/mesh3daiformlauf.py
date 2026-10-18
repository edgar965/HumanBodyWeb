# -*- coding: utf-8 -*-
"""Mesh3daiformlauf — EIN Trainingslauf der gemeinsamen Netze für seine Seite /mesh-3D-AI/formtraining/<lauf>/ (18.10.2026).

Edgar: „Ich möchte die Jobs auch öffnen können und Resultate sehen, mach Vorschlag“ → „mach deinen Vorschlag“ (Vorschlag 1: Seite je Lauf mit Kurve, Tabelle je Gruppe, Vergleich mit dem
vorigen Lauf, Kopfmessung, Log). Gelesen wird nur, was auf der Platte liegt:
  * `lauf_ergebnis.json`  Einstellungen, Verlauf, Ergebnis je Figur (`je_figur`) und je Gruppe (`zusammen`) — erst am Ende des Trainings geschrieben;
  * `lauf.log`            Kopfzeile, Epochenzeilen (während des Laufs die einzige Quelle des Verlaufs), Schlusszeilen;
  * `formen_pruefung_echt.json`  echte Nachrechnung (`ProjektTemp/_wegwerf/mesh3dai_form_pruefen.py`: Figur aus den Reglern gebaut, RMS über 25.182 Körperpunkte) — nur, wenn gerechnet;
  * `ProjektTemp/mia_daten/kopffehler_<lauf>.json`  Kopfmessung je Region (`mesh3dai_kopffehler_messen.py`) — die Ablage dieses Skripts, nicht der Laufordner.
Verglichen wird mit dem jüngsten FERTIGEN Lauf derselben Art, der vorher begann (ohne Probeläufe).

    Mesh3daiformlauf.lesen(name) -> None | {lauf, ergebnis, formen, echt, kopf, verlauf, kopfzeile, log, log_weg, vorgaenger: None | {lauf, ergebnis, kopf}}
"""

import json
import logging
import re
import time
from pathlib import Path

from django.conf import settings

from .mesh3daiformtraining import Mesh3daiformtraining

logger = logging.getLogger('core')

__all__ = ['Mesh3daiformlauf']


class Mesh3daiformlauf:
    ECHT = 'formen_pruefung_echt.json'
    KOPF = ('ProjektTemp', 'mia_daten', 'kopffehler_%s.json')
    NAME = re.compile(r'^[0-9A-Za-z][0-9A-Za-z._-]*$')
    #: so viele Zeilen des Logs zeigt die Seite (die jüngsten); ein Formlauf schreibt rund 100
    LOG_ZEILEN = 400

    @classmethod
    def finden(cls, name):
        """Der Ordner des Laufs — nur ein direkter Unterordner von `_vorstufe/laeufe/`, sonst None (kein Pfad aus der Adresse)."""
        if not cls.NAME.match(name or ''):
            return None
        p = Mesh3daiformtraining.ordner() / name
        return p if p.is_dir() and p.parent == Mesh3daiformtraining.ordner() else None

    @classmethod
    def lesen(cls, name, jetzt=None):
        p = cls.finden(name)
        if p is None:
            return None
        jetzt = time.time() if jetzt is None else jetzt
        lf = Mesh3daiformtraining.lauf(p, jetzt)
        ergebnis = cls._json(p / Mesh3daiformtraining.ERGEBNIS) or {}
        zeilen = cls._zeilen(p / Mesh3daiformtraining.LOG)
        verlauf = ergebnis.get('verlauf') or Mesh3daiformtraining.verlauf_aus_log(zeilen)
        return {'lauf': lf, 'ergebnis': ergebnis, 'formen': cls._json(p / Mesh3daiformtraining.FORMEN) or {}, 'echt': cls._json(p / cls.ECHT),
                'kopf': cls.kopfmessung(p.name), 'verlauf': [v for v in verlauf if isinstance(v, dict)],
                'kopfzeile': zeilen[0] if zeilen else '', 'log': zeilen[-cls.LOG_ZEILEN:], 'log_weg': max(0, len(zeilen) - cls.LOG_ZEILEN),
                'vorgaenger': cls.vorgaenger(lf, jetzt)}

    @classmethod
    def vorgaenger(cls, lf, jetzt):
        """Der jüngste fertige Lauf derselben Art, der vor diesem begann (ohne Probeläufe) — mit Ergebnis und Kopfmessung; None, wenn es keinen gibt."""
        for andere in Mesh3daiformtraining.laeufe(jetzt):
            if andere['name'] == lf['name'] or andere['zustand'] != 'fertig' or andere['probe'] or andere['art'] != lf['art']:
                continue
            if (andere['start'] or 0, andere['name']) >= (lf['start'] or 0, lf['name']):
                continue
            p = Mesh3daiformtraining.ordner() / andere['name']
            return {'lauf': andere, 'ergebnis': cls._json(p / Mesh3daiformtraining.ERGEBNIS) or {}, 'kopf': cls.kopfmessung(andere['name'])}
        return None

    @classmethod
    def kopfmessung(cls, name):
        teile = cls.KOPF[:-1] + (cls.KOPF[-1] % name,)
        return cls._json(Path(settings.TOOLS_ROOT).joinpath(*teile))

    @staticmethod
    def _zeilen(datei):
        try:
            return datei.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            return []

    @staticmethod
    def _json(datei):
        if not datei.is_file():
            return None
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            logger.warning('Mesh3daiformlauf: %s nicht lesbar (wird gerade geschrieben?)', datei)
            return None
