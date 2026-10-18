# -*- coding: utf-8 -*-
"""Mesh3daiformvarianten — die synthetischen Figuren des Formtrainings (`3DObjects/mesh3dai/Form001` …) mit ihrem Datenstand, für den Reiter „Formtraining“ auf /mesh-3D-AI/ (18.10.2026).

Edgar: „Wo sehe ich deine Training-Jobs mit den synthetischen Daten?“ → „mach einen neuen Tab ‚Formtraining‘ und füge die Jobs in der gleichen Art und Weise ein“. Eine Formvariante ist ein Ordner
`FormNNN/` mit `modell.json` (Grundlage, Geschlecht, Gruppe training|pruefung, Regler — Kinder tragen Regler `g1:…`), `proben.json` (die geplanten Posen) und `proben/NNNN/`.
Der Datenlauf (`ProjektTemp/_wegwerf/mesh3dai_vorstufe_mia_daten_lauf.py`) schreibt je Probe zuerst `mia_v<n>_<k>.npz` (Make-It-Animatable, Phase B, in Blöcken auf der GPU) und danach
`apose_v9_<k>.npz` (A-Pose-Wolke Fassung 9, Phase C) — die Wolke liest das Formtraining. Gezählt wird je Probe, ob es mindestens eine Datei der Art gibt.

Zustand (nur von der Platte, kein Blick auf Prozesse):
  * fertig:          jede geplante Probe hat eine Wolke Fassung 9;
  * wird gerechnet:  die jüngste MIA- oder Wolkendatei ist jünger als `FRIST_AKTIV_S`;
  * mia:             MIA für jede Probe, Wolken fehlen noch (Phase C kommt erst nach allen Blöcken);
  * unvollständig / offen: sonst — eine Probe, die die MIA-Prüfung nicht besteht, bleibt dauerhaft ohne Datei.

    Mesh3daiformvarianten.alle()  -> [{name, grundlage, geschlecht, gruppe, kind, geplant, mia, wolken, mia_zeiten, wolken_zeiten, daten_zeit, zustand, lauf}]   (gemerkt für FRIST_S)
    Mesh3daiformvarianten.summe(alle) -> {figuren, fertig, aktiv, geplant, mia, wolken}

Rund 180 Ordner mit je ~12 Proben: ein `scandir` je Probe (die Änderungszeiten liefert Windows mit dem Verzeichnis).
"""

import json
import logging
import os
import re
import time
from pathlib import Path

from django.conf import settings

from .mesh3daiformtraining import Mesh3daiformtraining

logger = logging.getLogger('core')

__all__ = ['Mesh3daiformvarianten']


class Mesh3daiformvarianten:
    MUSTER = re.compile(r'^Form\d{3}$')
    MIA = 'mia_v'
    WOLKE = 'apose_v9_'
    FRIST_AKTIV_S = 1800.0
    FRIST_S = 30.0
    _ablage = {'zeit': 0.0, 'daten': None}

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai'

    @classmethod
    def leeren(cls):
        cls._ablage = {'zeit': 0.0, 'daten': None}

    @classmethod
    def alle(cls, jetzt=None):
        jetzt = time.time() if jetzt is None else jetzt
        if cls._ablage['daten'] is not None and 0 <= jetzt - cls._ablage['zeit'] < cls.FRIST_S:
            return cls._ablage['daten']
        wurzel = cls.ordner()
        laeufe = Mesh3daiformtraining.je_variante()
        daten = [cls.variante(p, laeufe.get(p.name), jetzt) for p in sorted(wurzel.iterdir())
                 if p.is_dir() and cls.MUSTER.match(p.name) and (p / 'modell.json').is_file()] if wurzel.is_dir() else []
        cls._ablage = {'zeit': jetzt, 'daten': daten}
        return daten

    @classmethod
    def variante(cls, p, lauf, jetzt):
        m = cls._json(p / 'modell.json') or {}
        geplant = cls._json(p / 'proben.json')
        geplant = len(geplant) if isinstance(geplant, list) else 0
        mia_zeiten, wolken_zeiten, neueste = cls._zaehlen(p / 'proben')
        mia, wolken = len(mia_zeiten), len(wolken_zeiten)
        regler = (m.get('figur') or {}).get('regler') or {}
        return {'name': p.name, 'grundlage': m.get('grundlage'), 'geschlecht': m.get('geschlecht'), 'gruppe': m.get('gruppe'),
                'kind': any(str(k).startswith('g1:') for k in regler), 'geplant': geplant, 'mia': mia, 'wolken': wolken,
                'mia_zeiten': mia_zeiten, 'wolken_zeiten': wolken_zeiten,
                'daten_zeit': neueste or None, 'zustand': cls._zustand(geplant, mia, wolken, neueste, jetzt), 'lauf': lauf}

    @classmethod
    def summe(cls, alle):
        return {'figuren': len(alle), 'fertig': sum(v['zustand'] == 'fertig' for v in alle), 'aktiv': sum(v['zustand'] == 'wird gerechnet' for v in alle),
                'geplant': sum(v['geplant'] for v in alle), 'mia': sum(v['mia'] for v in alle), 'wolken': sum(v['wolken'] for v in alle)}

    @classmethod
    def _zaehlen(cls, proben):
        """Je Probe mit mindestens einer Datei der Art die Zeit ihrer ERSTEN (für das Tempo im Reiter „Lauf Aktuell“) — `(mia_zeiten, wolken_zeiten, neueste)`."""
        mia_zeiten, wolken_zeiten = [], []
        neueste = 0.0
        if not proben.is_dir():
            return mia_zeiten, wolken_zeiten, neueste
        with os.scandir(proben) as eintraege:
            ordner = [e.path for e in eintraege if e.is_dir()]
        for pfad in ordner:
            erste = {'mia': None, 'wolke': None}
            with os.scandir(pfad) as dateien:
                for d in dateien:
                    if d.name.startswith(cls.MIA):
                        art = 'mia'
                    elif d.name.startswith(cls.WOLKE):
                        art = 'wolke'
                    else:
                        continue
                    t = d.stat().st_mtime
                    neueste = max(neueste, t)
                    erste[art] = t if erste[art] is None else min(erste[art], t)
            if erste['mia'] is not None:
                mia_zeiten.append(erste['mia'])
            if erste['wolke'] is not None:
                wolken_zeiten.append(erste['wolke'])
        return mia_zeiten, wolken_zeiten, neueste

    @classmethod
    def _zustand(cls, geplant, mia, wolken, neueste, jetzt):
        if geplant and wolken >= geplant:
            return 'fertig'
        if neueste and jetzt - neueste <= cls.FRIST_AKTIV_S:
            return 'wird gerechnet'
        if geplant and mia >= geplant:
            return 'mia'
        return 'unvollständig' if mia or wolken else 'offen'

    @staticmethod
    def _json(datei):
        if not datei.is_file():
            return None
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            logger.warning('Mesh3daiformvarianten: %s nicht lesbar', datei)
            return None
