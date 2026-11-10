# -*- coding: utf-8 -*-
"""Meshgenesisabnahmewahl — ab wie wenigen FEHLERn im Abgleich ein Trainingsjob der Stufe 2 als OK gilt (22.10.2026).

Edgar: „die Fehler müssen auf unter 10 gehen, erst dann starte die anderen Jobs“ → „Mach die Fehleranzahl einstellbar bis ein Trainingsjob OK ist“. Davor: „wenn das ergebnis so schlecht ist,
dann ist das training doch nicht beendet!“ — gezählt werden die FEHLER von `AbgleichEingabeZiel` (Ergebnis ↔ Ziel, Ruhe und Pose), nicht der Trainingsverlust.
Ein Job ist OK, wenn er WENIGER FEHLER hat als der Wert. Der Wert liegt in `AppSettings.ui_prefs` (Formular als JSON an `/api/ui-prefs/`, wie `Meshgenesisstufe2wahl`); er gehört NICHT zur
Fassung eines Laufs (er ändert keine Rechnung, nur das Urteil). Gelesen von `ProjektTemp/_wegwerf/meshgenesis_stufe2_lauf.py` und `meshgenesis_stufe2_alle.py`.
"""

import logging
from .hautentlichtung import Hautentlichtung

logger = logging.getLogger('core')

__all__ = ['Meshgenesisabnahmewahl']


class Meshgenesisabnahmewahl:
    SCHLUESSEL = 'meshgenesis_stufe2_fehler_ok'
    VORGABE = 10
    MINIMUM = 1
    MAXIMUM = 1000

    aus = classmethod(Hautentlichtung.aus.__func__)          # dieselbe Rechnung wie `Hautentlichtung.aus` (bis 08.11.2026 eine Kopie hier)

    @classmethod
    def gewaehlt(cls):
        """Der gespeicherte Wert — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Meshgenesisabnahmewahl: Einstellung nicht lesbar (%s) — Vorgabe %d', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def ok(cls, fehler, grenze=None):
        """Ist ein Job mit `fehler` FEHLERn OK? (weniger als die Grenze)"""
        return fehler < (cls.gewaehlt() if grenze is None else grenze)
