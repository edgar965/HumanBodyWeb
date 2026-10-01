# -*- coding: utf-8 -*-
"""Renderwahl — womit „2D3D Kleider" rendert: Mitsuba 3 (Vorgabe) oder pyrender.

Edgar (01.10.2026): „Behalte aber pyrender, mach eine Einstellung auf einer neuen Seite 2d3dKleider wo man beide
auswählen kann, default mitsuba". Die Wahl liegt in `AppSettings.ui_prefs` unter `SCHLUESSEL` (Seite Einstellungen →
2D3D Kleider, `seite_kleider2d3d_einstellungen.py`) und gilt für alles, was `Genesishaarrender` rendert: Runden (Bild,
Kennbild, Kopf), Fotoprojektion, Film. Gelesen beim Anlegen des Renderers — ein laufender Arbeitsprozess behält seine
Wahl bis zum nächsten Renderer (Runde, Film).

Gemessen (01.10.2026, dieselbe Runde am Auftrag „ki+backen", warm, abwechselnd): pyrender 62,2 s, Mitsuba 72,1 s,
davon Rendern 11,3 / 12,1 s; Note pyrender 1,820, Mitsuba 1,725 bei gleicher IoU. Film je Bild pyrender 0,62–0,69 s,
Mitsuba 0,46–0,55 s. Nur Mitsuba zeigt Stranghaar als Strähnen (pyrender: Dreiecke ohne Fläche, unsichtbar);
Normalkarten können beide, pyrender bekommt sie bisher nicht mitgegeben.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Renderwahl']


class Renderwahl:
    SCHLUESSEL = 'kleider2d3d_renderer'
    MITSUBA = 'mitsuba'
    PYRENDER = 'pyrender'
    VORGABE = MITSUBA
    #: Wert → Anzeigetext, in der Reihenfolge der Auswahl.
    WAHLEN = {
        MITSUBA: 'Mitsuba 3 (Pfadverfolgung auf der Grafikkarte)',
        PYRENDER: 'pyrender (OpenGL)',
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
        except Exception as fehler:  # noqa: BLE001 — ohne Datenbank rendert es trotzdem, mit der Vorgabe
            logger.warning('Renderwahl: Einstellung nicht lesbar (%s) — %s', fehler, cls.VORGABE)
            return cls.VORGABE
