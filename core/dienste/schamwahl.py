# -*- coding: utf-8 -*-
"""Schamwahl — wie ein Blender-Import die Scham einbaut: Eigen (alte Methode) oder DAZ (neue).

Edgar (11.10.2026): „in Einstellungen mache eine neue Seite Genesis, darin die zwei Optionen, wie die Scham eingebaut wird, die alte Methode (Eigen) oder die neue (DAZ)."
Die Wahl liegt in `AppSettings.ui_prefs` unter `SCHLUESSEL` (Seite Einstellungen → Genesis, `seite_genesis_einstellungen.py`); gelesen wird sie am Ende jedes Imports
(`Blendimportschamdaz`, aus `Blendimportlauf._modell`).

    eigen   das Stück „<Name> Scham" aus dem Original der .blend (`Blendimportscham`): der Teil des Körpers, den die Figur nicht trägt, mit Fläche und Haut des Originals — der Weg bis 10.10.2026.
    daz     zusätzlich das Daz-Geograft „Anatomical Elements" (`Dazgeograftangepasst`), an das Eigen-Stück angepasst und gemessen (`Schammessung`); das Modell des Imports trägt dann dieses Stück.

Vorgabe ist `eigen`: Es ist der Weg, den Edgar am 11.10.2026 ausdrücklich haben wollte („Cute Girl alt … mit der Eigen Scham").
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Schamwahl']


class Schamwahl:
    SCHLUESSEL = 'genesis_scham_methode'
    EIGEN = 'eigen'
    DAZ = 'daz'
    VORGABE = EIGEN
    #: Wert → Anzeigetext, in der Reihenfolge der Auswahl.
    WAHLEN = {
        EIGEN: 'Eigen (alte Methode): Fläche und Haut der Scham aus dem Original der .blend',
        DAZ: 'DAZ (neue Methode): Daz-Geograft, an das Original angepasst und gemessen',
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
        except Exception as fehler:  # noqa: BLE001 — ohne Datenbank baut der Import trotzdem, mit der Vorgabe
            logger.warning('Schamwahl: Einstellung nicht lesbar (%s) — %s', fehler, cls.VORGABE)
            return cls.VORGABE
