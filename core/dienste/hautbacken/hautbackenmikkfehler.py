# -*- coding: utf-8 -*-
"""Hautbackenmikkfehler — die MikkTSpace-Hülle ließ sich nicht bauen oder laden (mit der Ursache im Text, nie ein stiller Rückfall auf eine Näherung)."""

__all__ = ['Hautbackenmikkfehler']


class Hautbackenmikkfehler(RuntimeError):
    """Kein Visual Studio gefunden, der Übersetzer scheiterte, die DLL ließ sich nicht laden, oder die Hülle meldete einen Fehlercode."""
