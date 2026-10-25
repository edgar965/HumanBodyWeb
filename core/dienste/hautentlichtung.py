# -*- coding: utf-8 -*-
"""Hautentlichtung — wie stark die Haut-KI das eingebackene Licht des Eingangs aus der Haut herausrechnet, in Prozent (25.10.2026).

Edgar: „Würde sagen, Du machst das einstellbar, in % die Entlichtung ist, bei Einstellungen - 2d-3d-ai. Default voll entlichtete haut“. Die Haut-KI (`KoerperKI_alle.hautnetz.Hautnetz`) gibt
je Texel eine Lichtkorrektur g aus (gelernt: Tripo-Haut ÷ wahre Haut, an den sechs Tripo-Jobs mit Wahrheit 0,70–1,59 je Kanal). 100 % = g ganz (Albedo, wie gelernt); 0 % = die gesehene Haut mit
dem Licht des Eingangs, die erzeugte Haut mit demselben Licht wieder belichtet; dazwischen g^p. Gespeichert in `AppSettings.ui_prefs` (Formular als JSON an `/api/ui-prefs/`), gelesen beim
Einsatz der Haut-KI (`mesh3dai/mesh3dai_hautki_einsatz.py`, `Hautkieinsatz`) — ein gerechneter Lauf bleibt, wie er ist.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Hautentlichtung']


class Hautentlichtung:
    SCHLUESSEL = 'haut_entlichtung'
    VORGABE = 100
    MINIMUM = 0
    MAXIMUM = 100

    @classmethod
    def aus(cls, prefs):
        """Prozent aus einem `ui_prefs`-Dict; was keine ganze Zahl von 0 bis 100 ist, ist die Vorgabe."""
        try:
            w = int(str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip())
        except ValueError:
            return cls.VORGABE
        return w if cls.MINIMUM <= w <= cls.MAXIMUM else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Der gespeicherte Wert in Prozent — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Hautentlichtung: Einstellung nicht lesbar (%s) — Vorgabe %d %%', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def anteil(cls):
        """Der gespeicherte Wert als Anteil 0 … 1 (so nimmt ihn `HautKI.rechnen`)."""
        return cls.gewaehlt() / 100.0
