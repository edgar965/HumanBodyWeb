# -*- coding: utf-8 -*-
"""Ein Wert, der da sein muss — für Prüfungen, die Optionales weiterreichen.

WARUM (Code Review 17.09.2026, Language Server): Über hundert Prüfungen
reichen einen Wert, der laut Signatur auch ``None`` sein kann, direkt an
``assertLess``, ``len`` oder einen Index weiter. Der Language Server meldet
jede Stelle — zu Recht: kommt ``None``, stirbt die Prüfung an einem
``TypeError`` in der Zusicherung statt an einer Aussage. ``Sicher.wert``
sagt es vorher, und der Typ ist danach verengt.
"""

from typing import Optional, TypeVar

T = TypeVar("T")


class Sicher:
    """``Sicher.wert(x)`` — ``x``, oder ein ``AssertionError`` mit Aussage."""

    @staticmethod
    def wert(wert: Optional[T], was: str = "Wert") -> T:
        assert wert is not None, "%s fehlt (None)" % was
        return wert
