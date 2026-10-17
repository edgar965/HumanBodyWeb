# -*- coding: utf-8 -*-
"""Mesh3daistandwahl — wie oft die Jobseite von Mesh3D-AI den Stand des Trainings abfragt, in Minuten (14.10.2026).

Edgar: „mach das, alle paar Minuten, damit es die Trainings nicht beeinträchtigt" und „einstellbar, wie viele Minuten es sein sollen. Mach eine Seite Einstellungen – Mesh3D-AI".
Der Wert liegt in `AppSettings.ui_prefs` unter `SCHLUESSEL` (Seite Einstellungen → Mesh3D-AI, `seite_mesh3dai_einstellungen.py`, Formular als JSON an `/api/ui-prefs/` wie bei Genesis);
gelesen wird er bei JEDER Abfrage (`Mesh3daistand`, Antwortfeld `intervall_minuten`), eine offene Seite übernimmt eine Änderung also nach ihrer nächsten Abfrage.

Unbekanntes, Unlesbares oder Ungültiges heißt Vorgabe; Zahlen außerhalb von `MINIMUM`…`MAXIMUM` werden auf die Grenze gesetzt (das Formular begrenzt sie ohnehin).
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Mesh3daistandwahl']


class Mesh3daistandwahl:
    SCHLUESSEL = 'mesh3dai_stand_minuten'
    #: Setzung: „alle paar Minuten" — fünf. Eine Abfrage liest einen Verzeichnislauf (Stat je Probe) und ein kleines Log; das Training merkt sie nicht, die Seite soll trotzdem nicht ständig fragen.
    VORGABE = 5
    MINIMUM = 1
    MAXIMUM = 240

    @classmethod
    def aus(cls, prefs):
        """Die Minuten aus einem `ui_prefs`-Dict (ganze Zahl, begrenzt); alles andere ist die Vorgabe."""
        try:
            minuten = int(str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip())
        except ValueError:
            return cls.VORGABE
        return min(max(minuten, cls.MINIMUM), cls.MAXIMUM)

    @classmethod
    def gewaehlt(cls):
        """Die gespeicherte Wahl — ohne lesbare Einstellungen (keine Datenbank) die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — die Abfrage soll auch ohne Datenbank antworten, mit der Vorgabe
            logger.warning('Mesh3daistandwahl: Einstellung nicht lesbar (%s) — %d Minuten', fehler, cls.VORGABE)
            return cls.VORGABE
