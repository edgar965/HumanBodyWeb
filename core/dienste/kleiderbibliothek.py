# -*- coding: utf-8 -*-
"""Kleiderbibliothek — der eine, geteilte Katalog der Kleidungsstuecke.

Herausgeloest aus `core/api/kleidungsbibliothek.py` (18.08.2026). Dort stand er
als Modulvariable mit faulem Aufbau:

    _garment_library = None

    def _get_garment_library():
        global _garment_library
        if _garment_library is None:
            _garment_library = GarmentLibrary(...)
            _garment_library.scan()
        return _garment_library

WARUM DAS EIN BEFUND IST (Sparring mit Nemotron, 18.08.2026): Daphne beantwortet
Anfragen NEBENLAEUFIG in Faeden. Treffen zwei Anfragen ein, bevor der Katalog
steht, sehen BEIDE `None`, beide bauen eine `GarmentLibrary` und beide fahren
`scan()` ueber das Kleiderverzeichnis. Der langsamere gewinnt und ueberschreibt
den anderen; Anfragen, die den ersten schon in der Hand hatten, arbeiten mit
einem Katalog weiter, den niemand mehr kennt. Kostenpunkt ist nicht nur der
doppelte Verzeichnisdurchlauf — es ist ein Zustand, den man am Ergebnis nicht
sieht.

Jetzt: EIN Schloss, doppelt geprueft, und sichtbar wird der Katalog erst NACH
dem `scan()` — dieselbe Regel wie bei `Charakterdaten` (dort stand deshalb
einmal eine leere Morph-Liste im Prozess).
"""

import logging
import threading

from django.conf import settings

logger = logging.getLogger(__name__)


class Kleiderbibliothek:
    """Zugriff auf den `GarmentLibrary`-Katalog."""

    _katalog = None
    _schloss = threading.Lock()

    @classmethod
    def holen(cls):
        """Der Katalog — beim ersten Aufruf eingelesen."""
        if cls._katalog is not None:
            return cls._katalog
        with cls._schloss:
            if cls._katalog is None:
                cls._katalog = cls._einlesen()
        return cls._katalog

    @classmethod
    def _einlesen(cls):
        from GarmentFitter import GarmentLibrary
        katalog = GarmentLibrary(str(settings.HUMANBODY_GARMENT_LIBRARY_DIR))
        katalog.scan()
        logger.info('Kleiderbibliothek eingelesen: %d Stuecke',
                    len(getattr(katalog, 'catalog', []) or []))
        return katalog

    @classmethod
    def neu_einlesen(cls):
        """Nach einer Aenderung auf der Platte — unter demselben Schloss."""
        with cls._schloss:
            cls._katalog = cls._einlesen()
        return cls._katalog
