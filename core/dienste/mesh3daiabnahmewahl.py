# -*- coding: utf-8 -*-
"""Mesh3daiabnahmewahl — ab wie wenigen FEHLERn im Abgleich ein Trainingsjob der Stufe 2 als OK gilt (22.10.2026).

Edgar: „die Fehler müssen auf unter 10 gehen, erst dann starte die anderen Jobs“ → „Mach die Fehleranzahl einstellbar bis ein Trainingsjob OK ist“. Davor: „wenn das ergebnis so schlecht ist,
dann ist das training doch nicht beendet!“ — gezählt werden die FEHLER von `AbgleichEingabeZiel` (Ergebnis ↔ Ziel, Ruhe und Pose), nicht der Trainingsverlust.
Ein Job ist OK, wenn er WENIGER FEHLER hat als der Wert. Der Wert liegt in `AppSettings.ui_prefs` (Formular als JSON an `/api/ui-prefs/`, wie `Mesh3daistufe2wahl`); er gehört NICHT zur
Fassung eines Laufs (er ändert keine Rechnung, nur das Urteil). Gelesen von `ProjektTemp/_wegwerf/mesh3dai_stufe2_lauf.py` und `mesh3dai_stufe2_alle.py`.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Mesh3daiabnahmewahl']


class Mesh3daiabnahmewahl:
    SCHLUESSEL = 'mesh3dai_stufe2_fehler_ok'
    VORGABE = 10
    MINIMUM = 1
    MAXIMUM = 1000

    @classmethod
    def aus(cls, prefs):
        """Der Wert aus einem `ui_prefs`-Dict; was keine ganze Zahl im erlaubten Bereich ist, ist die Vorgabe."""
        try:
            w = int(str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip())
        except ValueError:
            return cls.VORGABE
        return w if cls.MINIMUM <= w <= cls.MAXIMUM else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Der gespeicherte Wert — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Mesh3daiabnahmewahl: Einstellung nicht lesbar (%s) — Vorgabe %d', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def ok(cls, fehler, grenze=None):
        """Ist ein Job mit `fehler` FEHLERn OK? (weniger als die Grenze)"""
        return fehler < (cls.gewaehlt() if grenze is None else grenze)
