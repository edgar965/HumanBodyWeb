# -*- coding: utf-8 -*-
"""Haarenginedashboard — die Seite „Haar Engine" unter Dashboard (30.09.2026).

Kopie der Seite „BlenderModel" (`Blendermodelldashboard`): die Tabelle der Aufträge mit Duplizieren und
Löschen. Dazu ein Formular (Name, Fotos mit Rollen), das einen Auftrag anlegt — die Seite hat keine Reiter,
sie ist der ganze Bereich. Die Rollen für das Formular kommen ohne die schweren Teile des Katalogs
(Ollama-Abfrage, Modellverfügbarkeit): Die Seite braucht nur die Liste.
"""

from django.shortcuts import render

from ..dienste.haarenginetabelle import Haarenginetabelle
from ..dienste.meshoptionen import Meshoptionen
from ..models import Haarengineauftrag

__all__ = ['Haarenginedashboard']


class Haarenginedashboard:
    @staticmethod
    def seite(request):
        return render(
            request,
            'haarengine.html',
            {
                'tabelle': Haarenginetabelle(Haarengineauftrag.objects.all()).tabelle(),
                'rollen': [{'wert': w, 'text': t} for w, t in Meshoptionen.ROLLEN],
            },
        )
