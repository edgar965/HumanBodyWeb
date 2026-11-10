# -*- coding: utf-8 -*-
"""Meshgenesisstand — der Stand des echten Datensatzes und Trainings eines Jobs, für die Statuskarte der Jobseite (14.10.2026).

Edgar: „aktualisierst du alle paar Minuten den Trainingsstand auf der Ursula Seite?" → „mach das, alle paar Minuten, damit es die Trainings nicht beeinträchtigt" und „einstellbar, wie viele Minuten".
Die Seite fragt `GET /api/meshgenesis/<job>/stand/` im Takt von `intervall_minuten` (Einstellungen → Mesh-Genesis, `Meshgenesisstandwahl`); die Antwort liest nur Dateien:

    {job, zeit, intervall_minuten,
     datensatz: {vorhanden, geplant}          Meshgenesisdatensatz — fertige Proben von geplanten
     lauf: None | {name, status, vor_s, epochen, epoche, verlauf, dauer_s, proben, masse, zeilen}      Meshgenesislaeufe — der jüngste Trainingslauf}

Eine Abfrage kostet einen Verzeichnislauf (ein Stat je Probe, rund 180) und zwei kleine Dateien — kein Prozess, keine GPU, keine Datenbank außer dem einen Einstellungswert.
Das ist ECHT, anders als der Rest der Jobseite (Attrappe): die Karte steht darüber und sagt es.
"""

from datetime import datetime

from .meshgenesisdatensatz import Meshgenesisdatensatz
from .meshgenesislaeufe import Meshgenesislaeufe
from .meshgenesisstandwahl import Meshgenesisstandwahl

__all__ = ['Meshgenesisstand']


class Meshgenesisstand:
    @staticmethod
    def lesen(job):
        """`job` ist eine Zeile aus `Meshgenesisattrappe.stammdaten()` (Kennung, Name, Modell, Ordner des Datensatzes)."""
        return {
            'job': job['id'],
            'zeit': datetime.now().isoformat(timespec='seconds'),
            'intervall_minuten': Meshgenesisstandwahl.gewaehlt(),
            'datensatz': Meshgenesisdatensatz.zaehlen(job['ordner']),
            'lauf': Meshgenesislaeufe.letzter(job['ordner']),
        }
