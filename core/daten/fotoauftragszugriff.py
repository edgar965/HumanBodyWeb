# -*- coding: utf-8 -*-
"""Fotoauftragszugriff — den Auftrag EINMAL nachschlagen, statt zweimal.

`api/fotoauftraege.py` und `api/fotoabgleich.py` bearbeiten denselben
`PhotoAnalysisJob` und hatten dafuer je eine eigene Kopie derselben sechs
Zeilen: Modell holen, `objects.get`, `DoesNotExist` abfangen, sonst None. Das
Werkzeug `doppelrumpf` meldet genau das (27.08.2026).

Zwei Kopien einer Nachschlage-Funktion sind nicht schlimm, solange sie gleich
bleiben. Beim naechsten Umbau bleibt eine zurueck — und die Endpunkte
antworten dann auf denselben Fehler unterschiedlich.

Der Import des Modells steht IN der Methode: `core/models` zieht die ganze
App-Registrierung nach, und diese Klasse liegt in `daten/`, wo sonst nichts
von Django abhaengt.
"""

import json

from django.http import JsonResponse


class Fotoauftragszugriff:
    """Zugang zu einem `PhotoAnalysisJob` und die Antwort, wenn es ihn nicht gibt."""

    @staticmethod
    def holen(job_id):
        """Der Auftrag — oder None, wenn es ihn nicht (mehr) gibt."""
        from ..models import PhotoAnalysisJob
        try:
            return PhotoAnalysisJob.objects.get(id=job_id)
        # stumm gewollt: „Auftrag geloescht" ist der Normalfall, sobald
        # ein zweiter Tab offen ist. Die 404-Antwort SAGT es dem Aufrufer;
        # ein Logeintrag je Aufruf waere Rauschen.
        except PhotoAnalysisJob.DoesNotExist:
            return None

    @staticmethod
    def nicht_gefunden():
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    @staticmethod
    def mit_rumpf(request, job_id):
        """Auftrag UND JSON-Rumpf — oder die fertige Fehlerantwort.

        WARUM ZUSAMMEN (Befund `doppelcode`, 28.08.2026): Diese acht Zeilen

            job = Fotoauftragszugriff.holen(job_id)
            if job is None:
                return Fotoauftragszugriff.nicht_gefunden()
            try:
                rumpf = json.loads(request.body)
            except (json.JSONDecodeError, ValueError):
                return JsonResponse({'ok': False, 'error': 'Invalid JSON'},
                                    status=400)

        standen an DREI Endpunkten wortgleich. Sie gehoeren zusammen: Beide
        beantworten dieselbe Frage — „habe ich ueberhaupt etwas, womit ich
        arbeiten kann?" — und beide enden in einer Antwort, nicht in einem
        Wert.

        @returns (job, rumpf, antwort). Ist `antwort` gesetzt, gibt der
                 Aufrufer sie zurueck und hoert auf; sonst sind `job` und
                 `rumpf` gefuellt.
        """
        job = Fotoauftragszugriff.holen(job_id)
        if job is None:
            return None, None, Fotoauftragszugriff.nicht_gefunden()
        try:
            rumpf = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return None, None, JsonResponse(
                {'ok': False, 'error': 'Invalid JSON'}, status=400)
        return job, rumpf, None


#: DER NAME (29.08.2026, Befund `namens-dubletten`): Die Datei hiess
#: `fotoauftrag.py` — genau wie `core/models/fotoauftrag.py`, das den
#: `PhotoAnalysisJob` traegt. Zwei Dateien gleichen Namens mit
#: verschiedenem Inhalt sind eine Stolperstelle bei jeder Suche. Das
#: Modell behaelt den Namen, der Helfer heisst nach seiner Aufgabe.
