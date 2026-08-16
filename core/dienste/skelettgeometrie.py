# -*- coding: utf-8 -*-
"""Skelettgeometrie — die Geometrie des DEF-Skeletts, einmal geladen.

Aus core/api/retarget.py herausgeloest (Umbau 15.08.2026). Vorher war der
Zwischenspeicher eine Modulvariable mit `global`; als Klassenattribut ist er an
die Sache gebunden, die ihn braucht.
"""
from django.conf import settings


class Skelettgeometrie:
    """Knochen und Gewichte des DEF-Skeletts, je Prozess einmal gelesen."""

    _gemerkt = None

    @classmethod
    def holen(cls):
        if cls._gemerkt is None:
            from humanbody_core.skeleton import SkeletonGeometry
            skelett = str(settings.HUMANBODY_DATA_DIR / 'def_skeleton.json')
            gewichte = str(settings.HUMANBODY_DATA_DIR / 'skin_weights_base.json')
            cls._gemerkt = SkeletonGeometry.from_json(skelett, gewichte)
        return cls._gemerkt

    @classmethod
    def vergessen(cls):
        """Nach einem Datenwechsel (Testseite „Neu laden") den Speicher leeren."""
        cls._gemerkt = None
