# -*- coding: utf-8 -*-
"""Hautknotenfabrik — welche Klasse rechnet welchen Blender-Knotentyp. Ein Typ, der hier fehlt, ist ein Befund (`Hautgraph` nennt ihn), keine stille Näherung."""

from .hautknotenattribut import Hautknotenattribut
from .hautknotenbereich import Hautknotenbereich
from .hautknotenbild import Hautknotenbild
from .hautknotenbump import Hautknotenbump
from .hautknotenfarbe import Hautknotenfarbe
from .hautknotenkoordinate import Hautknotenkoordinate
from .hautknotenmathe import Hautknotenmathe
from .hautknotenmix import Hautknotenmix
from .hautknotennormalkarte import Hautknotennormalkarte
from .hautknotentabelle import Hautknotentabelle
from .hautknotentrenner import Hautknotentrenner

__all__ = ['Hautknotenfabrik']


class Hautknotenfabrik:
    KLASSEN = (Hautknotenattribut, Hautknotenbereich, Hautknotenbild, Hautknotenbump, Hautknotenfarbe, Hautknotenkoordinate, Hautknotenmathe, Hautknotenmix,
               Hautknotennormalkarte, Hautknotentabelle, Hautknotentrenner)
    TABELLE = {typ: klasse for klasse in KLASSEN for typ in klasse.TYPEN}

    @classmethod
    def bekannt(cls, typ):
        return typ in cls.TABELLE

    @classmethod
    def bauen(cls, schluessel, eintrag):
        """Der Knoten zum Eintrag des Graphen; `KeyError`, wenn der Typ unbekannt ist (`bekannt` vorher fragen)."""
        return cls.TABELLE[eintrag['typ']](schluessel, eintrag)
