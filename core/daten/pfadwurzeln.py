# -*- coding: utf-8 -*-
"""Pfadwurzeln — WO ueberhaupt gelesen und geschrieben werden darf.

Herausgeloest aus `core/safe_paths.py` (309 Zeilen, 18.08.2026). Die Datei
beantwortete zwei verschiedene Fragen: „welche Verzeichnisse sind erlaubt?" und
„ist DIESER Pfad in Ordnung?". Die erste haengt an Einstellungen und Projekt-
struktur und aendert sich mit ihnen; die zweite ist reine Pruefarbeit und soll
sich moeglichst NIE aendern.

`TOOLS_ROOT` ist BEWUSST KEINE Wurzel. Der erste Wurf hatte sie drin — die
Live-Pruefung zeigte sofort, dass damit `A:\\3DTools\\evil.json`,
`…\\HumanBodyWeb\\media_evil\\…` und jeder Pfad im Projekt durchgehen, also auch
`ui/settings.py`, `.git/` und die `.npy`-Morphdaten. Ein Waechter, der das
gesamte Arbeitsverzeichnis freigibt, ist keiner (12.08.2026).
"""

import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')


class Pfadwurzeln:
    """Die erlaubten Verzeichnisse je Aufgabe."""

    @staticmethod
    def medien():
        return Path(settings.MEDIA_ROOT)

    @staticmethod
    def projekt_standard():
        """Vorgabe-Verzeichnis der Studio-Projekte (wie in den Einstellungen)."""
        return Path(settings.TOOLS_ROOT) / 'HumanBody' / 'data' / 'studio_projects'

    @classmethod
    def studio_projekte(cls):
        return ([cls.medien(), cls.projekt_standard()]
                + cls.aus_einstellungen('studio_project_path', 'studio_bvh_input',
                                        'studio_bvh_output'))

    @classmethod
    def bvh(cls, wurzel):
        """Die BVH-Kategoriewurzel plus die eingestellten Ordner."""
        return ([wurzel, cls.medien()]
                + cls.aus_einstellungen('studio_bvh_input', 'studio_bvh_output'))

    @classmethod
    def ausgabe(cls):
        return [cls.medien()] + cls.aus_einstellungen('studio_video_output')

    @classmethod
    def videos(cls):
        return ([cls.medien()]
                + cls.aus_einstellungen('studio_video_output', 'studio_bvh_input'))

    @classmethod
    def aus_einstellungen(cls, *schluessel):
        """Vom Nutzer eingestellte Verzeichnisse (leer, wenn nicht gesetzt)."""
        try:
            from ..models import AppSettings
            prefs = AppSettings.load().ui_prefs or {}
        except Exception:                                        # noqa: BLE001
            logger.exception('SafePath: Einstellungen nicht lesbar')
            return []
        return [Path(prefs[k]) for k in schluessel if (prefs.get(k) or '').strip()]
