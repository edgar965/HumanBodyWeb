# -*- coding: utf-8 -*-
"""Umapythonfiguren — gebaute UMA-Figuren im Prozess halten.

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
    """Zugriff auf `UMA_Python.Figur`, je Rasse einmal gebaut."""

    #: Wieviele Rassen gleichzeitig gehalten werden. Eine Figur belegt
    #: gemessen rund 16.000 Punkte mit fuenf Gewichten — ein paar Megabyte.
    #: Drei reichen fuer den Fall, den Edgar nennt (Male, Female, Elf).
    #: Seit die Kleidung zum Schluessel gehoert (25.09.2026) vier: je Rasse
    #: kann ein nackter und ein angezogener Bau nebeneinander liegen.
    PLAETZE = 4

    _schloss = threading.RLock()
    _gebaut = {}  # (rasse, kleidung) -> Gebaut
    _reihenfolge = []
    _figur = None

    # ------------------------------------------------------------ Zugang

    @classmethod
    def figur(cls):
        """Der Zugang zum UMA-Projekt (Katalog und GUID-Index)."""
        if cls._figur is None:
            with cls._schloss:
                if cls._figur is None:
                    from UMA_Python import Figur

                    cls._figur = Figur(cls.projekt())
        return cls._figur

    @staticmethod
    def projekt():
        """Das Unity-Projekt. Aus den Settings, nie eingetippt."""
        return settings.UMA_PROJEKT

    @classmethod
    def rassen(cls):
        """Die Rassennamen, wie der Katalog sie fuehrt."""
        return cls.figur().rassen()

    # -------------------------------------------------------------- Bauen

    @staticmethod
    def schluessel(rasse, kleidung=None):
        """Rasse UND Kleidung — sonst bekaeme eine angezogene Figur den
        nackten Bau derselben Rasse aus der Ablage (Edgar, 25.09.2026: „baue
        das für UMA"; bis dahin hiess der Schluessel nur `rasse`)."""
        return (rasse, tuple(sorted({str(n) for n in (kleidung or ()) if n})))

    @classmethod
    def bauen(cls, rasse, kleidung=None):
        """Die gebaute Figur einer Rasse mit dieser Kleidung — beim ersten Mal gerechnet."""
        schluessel = cls.schluessel(rasse, kleidung)
        with cls._schloss:
            vorhanden = cls._gebaut.get(schluessel)
            if vorhanden is not None:
                cls._vormerken(schluessel)
                return vorhanden
        gebaut = cls.figur().bauen(rasse, kleidung=list(schluessel[1]))
        with cls._schloss:
            cls._gebaut[schluessel] = gebaut
            cls._vormerken(schluessel)
            cls._aufraeumen()
        logger.info(
            'UMA Python: %s gebaut (%d Punkte, %d Knochen, %d Kleidungsrezepte)',
            rasse,
            len(gebaut.netz.punkte),
            len(gebaut.netz.knochen),
            len(gebaut.kleidung),
        )
        return gebaut

    @classmethod
    def mit_slot(cls, rasse, slot):
        """Ein gehaltener Bau der Rasse, der `slot` enthaelt — fuer die Texturen.

        Die Texturadresse traegt nur Rasse und Slot. Ein Kleidungsslot steckt
        nicht im nackten Bau; gesucht wird deshalb unter den gehaltenen Bauten
        dieser Rasse, und erst ohne Treffer der nackte gebaut.
        """
        from UMA_Python.szene import Szenenfigur

        with cls._schloss:
            kandidaten = [g for (r, _k), g in cls._gebaut.items() if r == rasse]
        for gebaut in kandidaten:
            if slot in Szenenfigur.texturen(gebaut):
                return gebaut
        return cls.bauen(rasse)

    @classmethod
    def _vormerken(cls, schluessel):
        if schluessel in cls._reihenfolge:
            cls._reihenfolge.remove(schluessel)
        cls._reihenfolge.append(schluessel)

    @classmethod
    def _aufraeumen(cls):
        while len(cls._reihenfolge) > cls.PLAETZE:
            alt = cls._reihenfolge.pop(0)
            cls._gebaut.pop(alt, None)

    @classmethod
    def vergessen(cls):
        """Alles verwerfen — fuer Tests und nach einem Asset-Import."""
        with cls._schloss:
            cls._gebaut.clear()
            cls._reihenfolge.clear()
            cls._figur = None
