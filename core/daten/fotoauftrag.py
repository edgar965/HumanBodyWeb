# -*- coding: utf-8 -*-
"""Fotoauftrag — den Auftrag EINMAL nachschlagen, statt zweimal.

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

from django.http import JsonResponse


class Fotoauftrag:
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
