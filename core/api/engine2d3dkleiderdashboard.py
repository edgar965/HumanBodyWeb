# -*- coding: utf-8 -*-
"""Engine2d3dKleiderdashboard — die Seite „Haar Engine" unter Dashboard (30.09.2026).

Kopie der Seite „BlenderModel" (`Blendermodelldashboard`): die Tabelle der Aufträge mit Duplizieren und
Löschen. Dazu ein Formular (Name, Fotos mit Rollen), das einen Auftrag anlegt — die Seite hat keine Reiter,
sie ist der ganze Bereich. Die Rollen für das Formular kommen ohne die schweren Teile des Katalogs
(Ollama-Abfrage, Modellverfügbarkeit): Die Seite braucht nur die Liste.
"""

from django.shortcuts import render

from ..dienste.engine2d3dkleidertabelle import Engine2d3dKleidertabelle
from ..dienste.meshoptionen import Meshoptionen
from ..models import Engine2d3dKleiderauftrag

__all__ = ['Engine2d3dKleiderdashboard']


class Engine2d3dKleiderdashboard:
    @staticmethod
    def seite(request):
        return render(
            request,
            'engine2d3dkleider.html',
            {
                'tabelle': Engine2d3dKleidertabelle(Engine2d3dKleiderauftrag.objects.all()).tabelle(),
                'rollen': [{'wert': w, 'text': t} for w, t in Meshoptionen.ROLLEN],
            },
        )
