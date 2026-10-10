# -*- coding: utf-8 -*-
"""Blendimportbackenwahl — womit der Blender-Import die Haut bäckt: lokal (GPU, ohne Blender) oder mit Blender.

Edgar (10.10.2026): „ich möchte blender für alle Usecases ersetzt haben. Die Pipeline soll einstellbar sein, mach dazu ein Option Backen bei
Einstellungen - Charakter, mit Option ‚Lokal' und ‚Blender'". Die Wahl liegt in `AppSettings.ui_prefs` unter `SCHLUESSEL` (Seite Einstellungen →
Charakter, `szenenseite.py`). Gelesen wird sie, wenn der Schritt „haut" beginnt — ein laufender Import behält seine Wahl bis zum nächsten Lauf.

    lokal    `core/dienste/hautbacken`: dieselben Rechenwege wie Cycles (aus dem Blender-Quelltext übernommen), auf der GPU mit NVIDIA Warp.
             Das Material wird als Knotengraph aus dem Export gelesen (`blendmaterialgraph.py`), nicht von Blender ausgewertet.
    blender  Cycles „Selected to Active" (`blendbacken.py`) — der Weg bis zum 10.10.2026; bleibt als Gegenprobe und für Material, das der lokale
             Weg nicht kennt (er sagt dann, welcher Knoten fehlt, und rät nicht).
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Blendimportbackenwahl']


class Blendimportbackenwahl:
    SCHLUESSEL = 'blendimport_backen'
    LOKAL = 'lokal'
    BLENDER = 'blender'
    VORGABE = LOKAL
    #: Wert → Anzeigetext, in der Reihenfolge der Auswahl.
    WAHLEN = {
        LOKAL: 'Lokal (GPU, ohne Blender)',
        BLENDER: 'Blender (Cycles)',
    }

    @classmethod
    def aus(cls, prefs):
        """Die Wahl aus einem `ui_prefs`-Dict; Unbekanntes heißt Vorgabe."""
        wert = str((prefs or {}).get(cls.SCHLUESSEL) or cls.VORGABE)
        return wert if wert in cls.WAHLEN else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Die gespeicherte Wahl — ohne lesbare Einstellungen (keine Datenbank) die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — ohne Datenbank backt es trotzdem, mit der Vorgabe
            logger.warning('Blendimportbackenwahl: Einstellung nicht lesbar (%s) — %s', fehler, cls.VORGABE)
            return cls.VORGABE
