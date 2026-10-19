# -*- coding: utf-8 -*-
"""Mesh3daigenesis — was die Felder „Ziel“ und „Ergebnis“ der Jobseite brauchen, um die Figur mit dem Code der Charakter-Seite zu bauen (19.10.2026).

Edgar an Damira0Tripo: „Das Modell ist doch okay im Character View. Warum hast du eine andere Implementierung in dieser View?“ — „nutze den gleichen Code, verdammt nochmal!!!“ —
„untersuche alle Ansichten in allen views. es soll immer der gleiche Code genutzt werden wie der von Charakter“. Bis hierher zeigten Ziel und Ergebnis ein offline gebautes Anzeigenetz
(`Mesh3daiflaechennetz`) mit eigener Häutung; jede Eigenschaft der Charakter-Seite (Loch unter dem Anatomie-Stück, Normalen, Haut unter den Kleidern, Texturen) musste nachgebaut werden.
Jetzt baut der Browser die Figur mit `Genesis9Modell` (`gemeinsam/genesis9modell.js`) — derselbe Bau wie Charakter, Studio und Mesh-3D (`Meshfigurbuehne`). Dieser Dienst liefert nur dessen Eingaben:

    figur     die Figur des Jobs, wie sie gespeichert ist (`figur` aus `HumanBody/data/models/<Modell>.json` oder `<Datensatz>/modell.json` — Formvarianten, Trainingspaare); nur gelesen
    ziel      die Haltung der Probe als Daz-Gelenkwinkel `{knochen: {'rotation/x': Grad, …}}` (`proben/NNNN/kanaele.npz`, `mesh3dai_kinematik.py`) — `None`: die Figur steht in ihrer
              eigenen Pose (Trainingspaar: der Genesis-Export trägt sein Posenpreset)
    ergebnis  die vorhergesagte Haltung (`<gruppe>_winkel` im jüngsten Lauf) — `None`, wenn der Lauf keine Winkel trägt

Die Wurzel (`hip`) geht nicht mit: ihre Lage und Drehung legt die Seite über die Gelenke fest (Ausrichtung auf das Rig der Probe), wie die übrigen Felder ausgerichtet sind.
"""
import json
import logging
from pathlib import Path

import numpy as np
from django.conf import settings

from .mesh3daidaten import Mesh3daidaten
from .mesh3daidatensatz import Mesh3daidatensatz

logger = logging.getLogger('core')

__all__ = ['Mesh3daigenesis']


class Mesh3daigenesis:
    KANAELE = ('rotation/x', 'rotation/y', 'rotation/z')

    @staticmethod
    def figur(job):
        """`figur` der gespeicherten Figur des Jobs — oder `None` (mit Zeile im Log)."""
        datei = Mesh3daidatensatz.ordner(job['ordner']) / 'modell.json'
        if not datei.is_file():
            datei = Path(settings.HUMANBODY_MODELS_DIR) / ('%s.json' % job.get('modell'))
        try:
            figur = json.loads(datei.read_text(encoding='utf-8')).get('figur')
        except (OSError, ValueError) as fehler:
            logger.warning('Mesh3daigenesis: %s nicht lesbar (%s)', datei, fehler)
            return None
        if not isinstance(figur, dict) or figur.get('quelle') not in (None, 'genesis9'):
            logger.warning('Mesh3daigenesis: %s ist keine Genesis-Figur', datei)
            return None
        return figur

    @classmethod
    def drehung(cls, knochen, winkel):
        """Daz-Gelenkwinkel (138, 3) → `{knochen: {'rotation/x': Grad, …}}`, ohne die Wurzel und ohne Kanäle bei 0."""
        aus = {}
        for k, w in zip(knochen, np.asarray(winkel, dtype=float), strict=True):
            if k.get('eltern', 0) < 0:
                continue
            kanaele = {c: round(float(v), 4) for c, v in zip(cls.KANAELE, w, strict=True) if abs(v) > 1e-6}
            if kanaele:
                aus[k['name']] = kanaele
        return aus

    @classmethod
    def probe(cls, job, nr):
        """`{figur, ziel, ergebnis}` für die Probe `nr` — oder `None`, wenn die Figur fehlt."""
        figur = cls.figur(job)
        if figur is None:
            return None
        ordner = Mesh3daidatensatz.ordner(job['ordner'])
        try:
            knochen = json.loads((ordner / 'kinematik.json').read_text(encoding='utf-8'))['knochen']
        except (OSError, ValueError, KeyError):
            knochen = None
        ziel = ergebnis = None
        kanaele = ordner / 'proben' / ('%04d' % int(nr)) / 'kanaele.npz'
        if knochen and kanaele.is_file():
            with np.load(kanaele) as z:
                ziel = cls.drehung(knochen, z['winkel'])
        lauf = Mesh3daidaten.lauf(job['ordner'])
        if knochen and lauf is not None:
            with np.load(lauf / 'vorhersagen.npz') as v:
                for gruppe in Mesh3daidaten.GRUPPEN:
                    if gruppe + '_winkel' not in v.files:
                        continue
                    treffer = np.nonzero(v[gruppe + '_nr'] == int(nr))[0]
                    if len(treffer):
                        ergebnis = cls.drehung(knochen, v[gruppe + '_winkel'][treffer[0]])
                        break
        return {'figur': figur, 'ziel': ziel, 'ergebnis': ergebnis, 'lauf': lauf.name if lauf else None}
