# -*- coding: utf-8 -*-
u"""Umapythonfiguren — gebaute UMA-Figuren im Prozess halten.

WARUM (Edgar, 08.09.2026: „Beim Modell UMA Python habe ich immer noch keine
Portierung. Ich moechte doch ein Male, Female, Elf usw. auswaehlen, genau so
wie UMA das macht!")
=====================================================================
Ein Bau kostet gemessen 6 bis 14 Sekunden: acht Slot-Assets, davon fuenf
ueber 2 MB, jedes mit vollem Typbaum. Die Reglerstellung dagegen kostet
0,07 s — sie rechnet nur Knochen und Haut neu.

Deshalb wird die GEBAUTE Figur gehalten und je Reglerzug nur `punkte()`
gerufen. Ohne das waere ein Regler unbenutzbar.

DAS SCHLOSS IST NICHT ZIERAT
============================
Daphne beantwortet Anfragen nebenlaeufig. Treffen zwei Anfragen fuer
dieselbe Rasse ein, bevor der Bau steht, baut sie sonst BEIDE — 14 Sekunden
zweimal, und der langsamere ueberschreibt den anderen. Dieselbe Regel wie
bei `Kleiderbibliothek` (18.08.2026) und `Charakterdaten` (16.08.2026):
erst bauen, dann sichtbar machen, alles unter einem Schloss.
"""
import logging
import threading

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Umapythonfiguren']


class Umapythonfiguren:
    u"""Zugriff auf `UMA_Python.Figur`, je Rasse einmal gebaut."""

    #: Wieviele Rassen gleichzeitig gehalten werden. Eine Figur belegt
    #: gemessen rund 16.000 Punkte mit fuenf Gewichten — ein paar Megabyte.
    #: Drei reichen fuer den Fall, den Edgar nennt (Male, Female, Elf).
    PLAETZE = 3

    _schloss = threading.RLock()
    _gebaut = {}          # rasse -> Gebaut
    _reihenfolge = []
    _figur = None

    # ------------------------------------------------------------ Zugang

    @classmethod
    def figur(cls):
        u"""Der Zugang zum UMA-Projekt (Katalog und GUID-Index)."""
        if cls._figur is None:
            with cls._schloss:
                if cls._figur is None:
                    from UMA_Python import Figur
                    cls._figur = Figur(cls.projekt())
        return cls._figur

    @staticmethod
    def projekt():
        u"""Das Unity-Projekt. Aus den Settings, nie eingetippt."""
        return settings.UMA_PROJEKT

    @classmethod
    def rassen(cls):
        u"""Die Rassennamen, wie der Katalog sie fuehrt."""
        return cls.figur().rassen()

    # -------------------------------------------------------------- Bauen

    @classmethod
    def bauen(cls, rasse, kleidung=None):
        u"""Die gebaute Figur einer Rasse — beim ersten Mal gerechnet."""
        with cls._schloss:
            vorhanden = cls._gebaut.get(rasse)
            if vorhanden is not None:
                cls._vormerken(rasse)
                return vorhanden
        gebaut = cls.figur().bauen(rasse, kleidung=kleidung)
        with cls._schloss:
            cls._gebaut[rasse] = gebaut
            cls._vormerken(rasse)
            cls._aufraeumen()
        logger.info('UMA Python: %s gebaut (%d Punkte, %d Knochen)',
                    rasse, len(gebaut.netz.punkte), len(gebaut.netz.knochen))
        return gebaut

    @classmethod
    def _vormerken(cls, rasse):
        if rasse in cls._reihenfolge:
            cls._reihenfolge.remove(rasse)
        cls._reihenfolge.append(rasse)

    @classmethod
    def _aufraeumen(cls):
        while len(cls._reihenfolge) > cls.PLAETZE:
            alt = cls._reihenfolge.pop(0)
            cls._gebaut.pop(alt, None)

    @classmethod
    def vergessen(cls):
        u"""Alles verwerfen — fuer Tests und nach einem Asset-Import."""
        with cls._schloss:
            cls._gebaut.clear()
            cls._reihenfolge.clear()
            cls._figur = None
