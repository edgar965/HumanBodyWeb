# -*- coding: utf-8 -*-
"""Ai2d3dmeshversatz — welcher Versatz nach der Einpassung von Reglern und Haltung (`Ai2d3dmeshwahl`) die Genesis-Figur an die geometrische Figur bzw. das Netz legt (28.10.2026).

Edgar: „mach deinen Vorschlag“ (Hilfe → Architektur → Genesis, Abschnitt „Genesis als Mensch“). Gemessen an EdgarTrip (Lauf 2026.10.28.14.51, `ProjektTemp/_wegwerf/ai2d3d/diag_stufen.py`,
`diag_normalversatz.py`): IPNets freier Versatz je Punkt klappt 3.011 Dreiecke um und macht Handgelenke (0,91 / 0,87) und Knöchel (0,84 / 0,87) dünn; nur Regler und Haltung: 30
umgeklappt, Gelenke 0,99–1,01. Gespeichert in `AppSettings.ui_prefs` wie `Ai2d3dmeshwahl`, gelesen von `Genesis9.meshgenesis.G9meshgenesis.versatz_gewaehlt` beim nächsten Lauf
(2d-3d-AI und Mesh3D-AI).
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Ai2d3dmeshversatz']


class Ai2d3dmeshversatz:
    SCHLUESSEL = 'ai2d3d_mesh_versatz'
    VORGABE = 'normale'
    WERTE = (('normale', 'Längs der Normale — Kopf, Hände, Füße und Gelenke nur über Regler und Haltung'), ('frei', 'Frei je Punkt — wie im Original (IPNet SMPL+D)'))
    BESCHREIBUNG = {
        'normale': 'Nach Reglern und Haltung wird der Kopf allein noch einmal über seine Regler und die Haltung von Hals und Kopf an die Kopffläche gelegt. Danach wird '
                   'jeder Punkt des Körpers nur längs seiner eigenen Normale verschoben, geglättet und gedeckelt, und nur, wo das Ziel verlässlich ist (keine Falten, keine '
                   'umgestülpten Stellen). An Haut liegt die Figur danach auf der Fläche des Ziels, an Haar und Kleidung wird sie nur hineingeschoben. Kopf, Hände, Füße und '
                   'die Gelenkringe (Ellbogen, Handgelenk, Knie, Knöchel) bekommen keinen Versatz: Sie folgen nur Reglern und Haltung, nie dem oft kaputten Ziel; Regler, die '
                   'fast nur an Händen und Füßen wirken, bleiben auf der Startfigur. Messwerte: Hilfe → Architektur → Genesis, Abschnitt „Genesis als Mensch“.',
        'frei': 'Der Versatz des Originals: bei IPNet fit_SMPLD (jeder Punkt frei in 3D, mit Laplace-Glättung), bei transfer_model der fortgesetzte Rest. Liegt dichter am Ziel, '
                'übernimmt aber dessen kaputte Stellen: an EdgarTrip 3.011 umgeklappte Dreiecke, Handgelenke 0,91 / 0,87, Knöchel 0,84 / 0,87.',
    }

    @classmethod
    def aus(cls, prefs):
        w = str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip()
        return w if w in dict(cls.WERTE) else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Der gespeicherte Versatz — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Ai2d3dmeshversatz: Einstellung nicht lesbar (%s) — Vorgabe %s', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def text(cls, wert):
        return dict(cls.WERTE).get(wert, str(wert))
