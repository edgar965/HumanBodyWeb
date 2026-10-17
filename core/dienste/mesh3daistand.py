# -*- coding: utf-8 -*-
"""Mesh3daistand — der Stand des echten Datensatzes und Trainings eines Jobs, für die Statuskarte der Jobseite (14.10.2026).

Edgar: „aktualisierst du alle paar Minuten den Trainingsstand auf der Ursula Seite?" → „mach das, alle paar Minuten, damit es die Trainings nicht beeinträchtigt" und „einstellbar, wie viele Minuten".
Die Seite fragt `GET /api/mesh3dai/<job>/stand/` im Takt von `intervall_minuten` (Einstellungen → Mesh3D-AI, `Mesh3daistandwahl`); die Antwort liest nur Dateien:

    {job, zeit, intervall_minuten,
     datensatz: {vorhanden, geplant}          Mesh3daidatensatz — fertige Proben von geplanten
     lauf: None | {name, status, vor_s, epochen, epoche, verlauf, dauer_s, proben, masse, zeilen}      Mesh3dailaeufe — der jüngste Trainingslauf}

Eine Abfrage kostet einen Verzeichnislauf (ein Stat je Probe, rund 180) und zwei kleine Dateien — kein Prozess, keine GPU, keine Datenbank außer dem einen Einstellungswert.
Das ist ECHT, anders als der Rest der Jobseite (Attrappe): die Karte steht darüber und sagt es.
"""

from datetime import datetime

from .mesh3daidatensatz import Mesh3daidatensatz
from .mesh3dailaeufe import Mesh3dailaeufe
from .mesh3daistandwahl import Mesh3daistandwahl

__all__ = ['Mesh3daistand']


class Mesh3daistand:
    @staticmethod
    def lesen(job):
        """`job` ist eine Zeile aus `Mesh3daiattrappe.stammdaten()` (Kennung, Name, Modell, Ordner des Datensatzes)."""
        return {
            'job': job['id'],
            'zeit': datetime.now().isoformat(timespec='seconds'),
            'intervall_minuten': Mesh3daistandwahl.gewaehlt(),
            'datensatz': Mesh3daidatensatz.zaehlen(job['ordner']),
            'lauf': Mesh3dailaeufe.letzter(job['ordner']),
        }
