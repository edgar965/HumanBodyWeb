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
from .mesh3daidazwinkel import Mesh3daidazwinkel
from .mesh3daiergebnisfigur import Mesh3daiergebnisfigur
from .mesh3daiwege import Mesh3daiwege

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
    def probe(cls, job, nr, weg=None):
        """`{figur, figur_ergebnis, ergebnis_quelle, ziel, ergebnis, weg}` für die Probe `nr` — oder `None`, wenn die Figur fehlt.

        19.10.2026 spätabends (Edgar: „das Ergebnis soll direkt aus der KI kommen“): `figur` ist nur noch das ZIEL. Das Ergebnis bekommt seine eigene Figur (`Mesh3daiergebnisfigur`: vorhergesagte
        Form oder Grundfigur, Grundhaut, keine Kleider) und die Winkel des Wegs, dessen Rig die Seite zeigt (`Mesh3daiwege`, `Mesh3daidazwinkel`) — vorher kamen sie immer vom Netz direkt
        (MannLaufen „Pose kaputt (Beine)“: Winkel des Netzes direkt, starr auf das Rig der Vorstufe gelegt)."""
        figur = cls.figur(job)
        if figur is None:
            return None
        ordner = Mesh3daidatensatz.ordner(job['ordner'])
        try:
            knochen = json.loads((ordner / 'kinematik.json').read_text(encoding='utf-8'))['knochen']
        except (OSError, ValueError, KeyError):
            knochen = None
        lauf = Mesh3daidaten.lauf(job['ordner'])
        try:
            lauf_e = json.loads((lauf / 'lauf_ergebnis.json').read_text(encoding='utf-8')) if lauf is not None else {}
        except (OSError, ValueError):
            lauf_e = {}
        # Tripo-Jobs haben keine eigene `kinematik.json` (19.10.2026 spätabends: das Ergebnis blieb deshalb leer) — die Winkel des KI-Laufs gehören zur vorhergesagten Figur (`ergebnis_figur.modell`
        # liegt in deren Ordner, dort auch ihre `kinematik.json`, dieselbe Knochenliste).
        knochen_ergebnis = knochen
        fig = (lauf_e.get('ergebnis_figur') or {}).get('modell')
        if fig:
            try:
                knochen_ergebnis = json.loads((Path(fig).parent / 'kinematik.json').read_text(encoding='utf-8'))['knochen']
            except (OSError, ValueError, KeyError):
                pass
        ziel = ergebnis = None
        kanaele = ordner / 'proben' / ('%04d' % int(nr)) / 'kanaele.npz'
        if knochen and kanaele.is_file():
            with np.load(kanaele) as z:
                ziel = cls.drehung(knochen, z['winkel'])
        wege = Mesh3daiwege.lesen(lauf, len(knochen)) if knochen and lauf is not None else None
        if wege and int(nr) in wege['proben']:
            weg = weg if weg in wege['proben'][int(nr)] else wege['standard']
            ergebnis = cls.drehung(knochen, Mesh3daidazwinkel.aus_drehungen(wege['proben'][int(nr)][weg][1], knochen))
        elif knochen_ergebnis and lauf is not None:
            weg = None
            with np.load(lauf / 'vorhersagen.npz') as v:
                for gruppe in Mesh3daidaten.GRUPPEN:
                    if gruppe + '_winkel' not in v.files:
                        continue
                    treffer = np.nonzero(v[gruppe + '_nr'] == int(nr))[0]
                    if len(treffer):
                        ergebnis = cls.drehung(knochen_ergebnis, v[gruppe + '_winkel'][treffer[0]])
                        break
        aus = Mesh3daiergebnisfigur.fuer(job, nr, lauf_e)
        # Kleider aus der KI (20.10.2026): bei Tripo-Jobs die Stücke, die die Testseite wirksam gewählt hat (`Mesh3daiergebniskleider`), im Browser mit der Haltung der KI gehäutet
        from .mesh3daiergebniskleider import Mesh3daiergebniskleider
        ki = Mesh3daiergebniskleider.fuer(lauf_e, job.get('geschlecht') if job.get('geschlecht') in Mesh3daiergebnisfigur.GRUNDHAUT else 'weiblich')
        if ki is not None:
            # Haut aus Stufe 2 der KI (21.10.2026 nachts, OlesiaWalk): die Kacheln beim Test des Laufs — sonst bleibt die Grundhaut
            from .mesh3daiprobenhaut import Mesh3daiprobenhaut
            haut = Mesh3daiprobenhaut.fuer_test(job)
            if haut:
                aus['figur'] = dict(aus['figur'], fototextur=haut['fototextur'])
                aus['quelle'] = aus['quelle'].replace(Mesh3daiergebnisfigur.TEXT_HAUT, haut['quelle'])
        # Grundjobs (20.10.2026, MannLaufen …): die Kleider der Probe (`Mesh3daiprobenkleider`), nur wenn sie für DIESE Ergebnisfigur gerechnet sind; Haltung = der gezeigte Weg
        if ki is None and not (lauf_e.get('ergebnis_figur') or {}).get('modell'):
            from .mesh3daiprobenkleider import Mesh3daiprobenkleider
            ki = Mesh3daiprobenkleider.fuer(job, nr, aus['figur'], weg if wege and int(nr) in wege['proben'] else None)
            # Haut aus der KI (21.10.2026, Hautkopf): die Kacheln der Probe, nur wenn sie für DIESE Ergebnisfigur gerechnet sind — sonst bleibt die Grundhaut
            from .mesh3daiprobenhaut import Mesh3daiprobenhaut
            haut = Mesh3daiprobenhaut.fuer(job, nr, aus['figur'])
            if haut:
                aus['figur'] = dict(aus['figur'], fototextur=haut['fototextur'])
                aus['quelle'] = aus['quelle'].replace(Mesh3daiergebnisfigur.TEXT_HAUT, haut['quelle'])
        return {'figur': figur, 'figur_ergebnis': aus['figur'], 'ergebnis_quelle': aus['quelle'], 'ergebnis_form': aus['form'], 'ziel': ziel, 'ergebnis': ergebnis,
                'weg': weg if wege and int(nr) in wege['proben'] else None, 'lauf': lauf.name if lauf else None, 'ki_kleider': ki}
