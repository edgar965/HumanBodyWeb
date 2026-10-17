# -*- coding: utf-8 -*-
"""Mesh3dailaeufe — der jüngste Trainingslauf eines Jobs, wie er auf der Platte steht (14.10.2026).

Das Trainingsskript (`ProjektTemp/_wegwerf/mesh3dai_ursula_netz.py`) legt je Lauf einen Ordner `3DObjects/mesh3dai/<Modell>/_laeufe/<JJJJ.MM.TT.HH.MM>_<Name>/` an:
`lauf.log` (laufend, Zeile für Zeile geschrieben) und — erst am Ende — `lauf_ergebnis.json` (Verlauf und Maße je Gruppe). Hier wird nur gelesen:

    Mesh3dailaeufe.letzter('Ursula1') -> None | {name, status, vor_s, epochen, epoche, verlauf, dauer_s, proben, masse, zeilen}

    status   fertig         `lauf_ergebnis.json` liegt da
             laeuft         kein Ergebnis, das Log wurde in den letzten `FRIST_S` Sekunden geschrieben (Vermutung aus der Dateizeit, kein Prozess geprüft)
             ohne_ergebnis  kein Ergebnis, das Log ist älter — abgebrochen oder ein Probelauf (`--probe`)
    epoche   die letzte Epoche im Log (das Skript schreibt die ersten drei und dann jede zehnte), epochen = Zahl aus der ersten Zeile „Netz: … N Epochen …"
    verlauf  die letzten Werte: training_mm (Verlust der Epoche), pruefung_mm / spagat_mm (nur alle 10 Epochen)
    masse    {gruppe: {netz_mm, netz_median_mm, netz_p95_mm, mittlere_pose_mm, a_pose_mm, unter_10mm_prozent}} aus dem Ergebnis, sonst {}

Die Zeilenform des Logs gehört dem Trainingsskript (`Epoche   3  {'epoche': 3, 'training_mm': 162.07}  (2 s)`); ändert sie sich, fehlen hier Epoche und Verlauf — die letzten Logzeilen stehen weiter da.
Liest bei jedem Aufruf neu (kleine Dateien, kein Zwischenspeicher).
"""

import ast
import json
import logging
import re
import time

from .mesh3daidatensatz import Mesh3daidatensatz

logger = logging.getLogger('core')

__all__ = ['Mesh3dailaeufe']


class Mesh3dailaeufe:
    #: Setzung: Das Skript schreibt in den ersten drei Epochen je Epoche, danach nur jede zehnte; zehn Minuten ohne neue Zeile und ohne Ergebnis gelten nicht mehr als „läuft".
    FRIST_S = 600
    ZEILEN = 6
    MASSE = ('netz_mm', 'netz_median_mm', 'netz_p95_mm', 'mittlere_pose_mm', 'a_pose_mm', 'unter_10mm_prozent')
    _EPOCHE = re.compile(r'^Epoche\s+\d+\s+(\{.*\})\s+\((\d+) s\)\s*$')
    _KOPF = re.compile(r'(\d+) Epochen')

    @classmethod
    def letzter(cls, modell):
        """Der jüngste Lauf (Ordnername beginnt mit dem Zeitpunkt, die Namensfolge ist die zeitliche) oder `None`."""
        ordner = Mesh3daidatensatz.ordner(modell) / '_laeufe'
        if not ordner.is_dir():
            return None
        laeufe = sorted(p for p in ordner.iterdir() if p.is_dir())
        return cls._lesen(laeufe[-1]) if laeufe else None

    @classmethod
    def _lesen(cls, lauf):
        log = lauf / 'lauf.log'
        ergebnis = cls._ergebnis(lauf / 'lauf_ergebnis.json')
        text = log.read_text(encoding='utf-8', errors='replace') if log.is_file() else ''
        zeilen = [z.rstrip() for z in text.splitlines() if z.strip()]
        vor_s = round(time.time() - log.stat().st_mtime) if log.is_file() else None
        epochen = next((int(m.group(1)) for m in map(cls._KOPF.search, zeilen[:1]) if m), None)
        eintraege = cls._epochen(zeilen)
        letzte = eintraege[-1] if eintraege else {}
        return {
            'name': lauf.name,
            'status': cls._status(ergebnis, vor_s),
            'vor_s': vor_s,
            'epochen': ergebnis.get('epochen', epochen) if ergebnis else epochen,
            'epoche': letzte.get('epoche'),
            'verlauf': cls._verlauf(eintraege),
            'dauer_s': ergebnis.get('dauer_s') if ergebnis else None,
            'proben': ergebnis.get('proben') if ergebnis else None,
            'masse': cls._masse(ergebnis),
            'zeilen': zeilen[-cls.ZEILEN:],
        }

    @classmethod
    def _status(cls, ergebnis, vor_s):
        if ergebnis:
            return 'fertig'
        return 'laeuft' if vor_s is not None and vor_s <= cls.FRIST_S else 'ohne_ergebnis'

    @classmethod
    def _epochen(cls, zeilen):
        """Die Epochenzeilen des Logs als Dicts (`epoche`, `training_mm`, ggf. `pruefung_mm`, `spagat_mm`)."""
        eintraege = []
        for zeile in zeilen:
            treffer = cls._EPOCHE.match(zeile)
            if not treffer:
                continue
            try:
                eintraege.append(ast.literal_eval(treffer.group(1)))
            except (ValueError, SyntaxError):
                logger.warning('Mesh3dailaeufe: Epochenzeile nicht lesbar: %s', zeile[:120])
        return eintraege

    @staticmethod
    def _verlauf(eintraege):
        """Je Messgröße der jüngste vorhandene Wert (Prüfposen und Spagat stehen nur in jeder zehnten Zeile)."""
        werte = {}
        for eintrag in eintraege:
            werte.update({k: v for k, v in eintrag.items() if k != 'epoche'})
        return werte

    @staticmethod
    def _ergebnis(datei):
        if not datei.is_file():
            return None
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            logger.warning('Mesh3dailaeufe: %s nicht lesbar (wird gerade geschrieben?)', datei)
            return None

    @classmethod
    def _masse(cls, ergebnis):
        if not ergebnis:
            return {}
        return {gruppe: {k: m[k] for k in cls.MASSE if k in m} for gruppe, m in (ergebnis.get('maße') or {}).items()}
