# -*- coding: utf-8 -*-
"""Architektur2d3dblender — die Daten der Tabelle „Wie liefe das mit Blender" im Reiter „Tools" der Seite Hilfe → Architektur → 2D3D (03.10.2026).

Edgar: „mach bei den Tools einen Vergleich, wie das mit Blender laufen würde. Also eine Tabelle, wo rechts die Blender-Spalte ist. Blender hat für alles auch Tools, wie eine
eigene Modellerzeugung, Kleider usw." Die Zeilen stehen je Abschnitt in einer Datei `blendervergleich<name>.py` (Klasse `Blendervergleich<Name>`, Schema in `ZEILEN`): links das
lokale Werkzeug mit Aufruf und Klassen, rechts das Blender-Werkzeug mit dem Aufruf aus Python und dem Stand (`STAENDE`). Die lokalen Klassen prüft diese Klasse gegen den Code
(`Architektur2d3dklassen.zeile`); Fehlendes steht als Befund auf der Seite. Was Blender 5.2.2 hat, hat der Verfasser der Zeile in einem Blender-Lauf nachgesehen (Beleg im Test und im Bericht).
"""

import importlib
import logging
from pathlib import Path

from .architektur2d3dklassen import Architektur2d3dklassen

logger = logging.getLogger('core')

__all__ = ['Architektur2d3dblender']


class Architektur2d3dblender:
    #: Stand des Blender-Werkzeugs → Beschriftung. Die Reihenfolge ist die der Zählung auf der Seite.
    STAENDE = {
        'genutzt': 'im Projekt benutzt',
        'gemessen': 'gegen den Solver gemessen',
        'vorhanden': 'in Blender vorhanden, im Projekt nicht benutzt',
        'addon': 'nur als Add-on',
        'keins': 'in Blender kein Werkzeug im Kern',
    }
    PFAD = Path(__file__).resolve().parent
    NICHT_GEMESSEN = 'nicht gemessen'
    #: Reihenfolge der Abschnitte nach `KENNUNG`; nicht genannte folgen alphabetisch nach Dateiname.
    REIHENFOLGE = ['blender-modell', 'blender-kleider', 'blender-haar', 'blender-textur', 'blender-bild']

    @classmethod
    def abschnittsklassen(cls):
        """Jede Datei `blendervergleich<name>.py` mit der Klasse `Blendervergleich<Name>` (Schema siehe Moduldocstring)."""
        gefunden = []
        for datei in sorted(cls.PFAD.glob('blendervergleich*.py')):
            stem = datei.stem
            try:
                modul = importlib.import_module('.' + stem, __package__)
            except Exception as fehler:    # noqa: BLE001 — ein kaputter Abschnitt darf die Seite nicht kippen; er steht als Befund darin
                logger.warning('Architektur 2D3D Blender-Vergleich: %s nicht ladbar: %s', stem, fehler)
                gefunden.append((stem, None, str(fehler)))
                continue
            klasse = getattr(modul, stem.capitalize(), None)
            if klasse is None or not hasattr(klasse, 'KENNUNG'):
                gefunden.append((stem, None, 'Klasse %s mit KENNUNG fehlt' % stem.capitalize()))
                continue
            gefunden.append((stem, klasse, ''))
        rang = {k: i for i, k in enumerate(cls.REIHENFOLGE)}
        return sorted(gefunden, key=lambda g: (rang.get(getattr(g[1], 'KENNUNG', ''), len(rang)), g[0]))

    @classmethod
    def zeit(cls, text):
        """{text, gemessen}: eine Zeit zählt als gemessen, wenn der Text eine Zahl enthält; „nicht gemessen" und „entfällt" sind Aussagen ohne Zahl."""
        return {'text': text, 'gemessen': any(c.isdigit() for c in text)}

    @classmethod
    def zeile(cls, kennung, roh, geprueft, befunde):
        """`roh` hat acht Einträge (ohne Zeiten) oder zehn (mit `zeit_lokal`, `zeit_blender`); fehlende Zeiten stehen als „nicht gemessen"."""
        if len(roh) not in (8, 10):
            befunde.append('%s / %s: %d Einträge statt 8 oder 10' % (kennung, roh[0] if roh else '?', len(roh)))
            roh = tuple(roh) + ('',) * max(0, 8 - len(roh))
        aufgabe, lokal, lokal_aufruf, klassen, blender, blender_aufruf, stand, unterschied = roh[:8]
        zeiten = roh[8:10] if len(roh) >= 10 else (cls.NICHT_GEMESSEN, cls.NICHT_GEMESSEN)
        if stand not in cls.STAENDE:
            befunde.append('%s / %s: unbekannter Stand „%s"' % (kennung, aufgabe, stand))
        karten = []
        for eintrag in klassen:
            eintrag = tuple(eintrag)
            if eintrag not in geprueft:
                geprueft[eintrag] = Architektur2d3dklassen.zeile(*eintrag)
            info = geprueft[eintrag]
            if info['fehlt']:
                befunde.append('%s / %s: %s (%s)' % (kennung, aufgabe, info['klasse'], info['fehlt']))
            karten.append({'klasse': info['klasse'], 'modul': info['modul'], 'fehlt': info['fehlt']})
        return {'aufgabe': aufgabe, 'lokal': lokal, 'lokal_aufruf': lokal_aufruf, 'klassen': karten, 'blender': blender,
                'blender_aufruf': blender_aufruf, 'stand': stand, 'stand_text': cls.STAENDE.get(stand, stand), 'unterschied': unterschied,
                'zeit_lokal': cls.zeit(zeiten[0]), 'zeit_blender': cls.zeit(zeiten[1])}

    @classmethod
    def abschnitt(cls, stem, klasse, fehler, geprueft):
        if klasse is None:
            return {'kennung': stem, 'titel': stem, 'einleitung': '', 'zeilen': [], 'befunde': ['%s: %s' % (stem, fehler)]}
        befunde = []
        zeilen = [cls.zeile(klasse.KENNUNG, z, geprueft, befunde) for z in klasse.ZEILEN]
        return {'kennung': klasse.KENNUNG, 'titel': klasse.TITEL, 'einleitung': klasse.EINLEITUNG, 'zeilen': zeilen, 'befunde': befunde}

    @classmethod
    def kontext(cls):
        geprueft = {}
        abschnitte = [cls.abschnitt(stem, klasse, fehler, geprueft) for stem, klasse, fehler in cls.abschnittsklassen()]
        alle = [z for a in abschnitte for z in a['zeilen']]
        return {
            'abschnitte': abschnitte,
            'zaehlung': [{'stand': s, 'text': t, 'anzahl': sum(1 for z in alle if z['stand'] == s)} for s, t in cls.STAENDE.items()],
            'zeilen': len(alle),
            'zeiten_beide': sum(1 for z in alle if z['zeit_lokal']['gemessen'] and z['zeit_blender']['gemessen']),
            'befunde': [b for a in abschnitte for b in a['befunde']],
        }
