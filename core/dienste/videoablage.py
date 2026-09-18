# -*- coding: utf-8 -*-
"""Videoablage — fertige Videos in den eingestellten Ausgabeordner legen.

Herausgeloest aus `core/api/dateien.py` (Befund `freie-funktionen`). Drei
Endpunkte legten dieselben vier Zeilen hin: Einstellung lesen, Ordner anlegen,
Ziel bilden, schreiben.

Der Ordner kommt aus den Einstellungen (`AppSettings.video_output_dir`) und wird
bei Bedarf angelegt -- der Nutzer stellt dort einen Pfad ein, der noch nicht
existiert, und erwartet zu Recht, dass das Speichern trotzdem klappt.
"""

import shutil
from pathlib import Path

from ..models import AppSettings


class Videoablage:
    """Der Ausgabeordner fuer Videos und das Schreiben hinein."""

    @staticmethod
    def ordner():
        """Der eingestellte Ausgabeordner, angelegt."""
        ziel = Path(AppSettings.load().video_output_dir)
        ziel.mkdir(parents=True, exist_ok=True)
        return ziel

    @staticmethod
    def kopieren(quelle, dateiname):
        """Eine fertige Datei in den Ausgabeordner kopieren."""
        ziel = Videoablage.ordner() / dateiname
        shutil.copy2(str(quelle), str(ziel))
        return ziel

    @staticmethod
    def schreiben(hochgeladen, dateiname):
        """Einen hochgeladenen Strom in den Ausgabeordner schreiben.

        Stueckweise (`chunks()`), nicht am Stueck: Eine Aufnahme aus dem Browser
        kann hunderte MB haben, und die muessen nicht alle gleichzeitig in den
        Arbeitsspeicher.
        """
        ziel = Videoablage.ordner() / dateiname
        with open(ziel, 'wb') as datei:
            for happen in hochgeladen.chunks():
                datei.write(happen)
        return ziel
