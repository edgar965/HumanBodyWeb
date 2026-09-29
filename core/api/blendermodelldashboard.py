# -*- coding: utf-8 -*-
"""Blendermodelldashboard — die Seite „BlenderModel" unter Dashboard (29.09.2026).

Edgar: „mach ein neues Menü Dashboard - BlenderModel, das eine Kopie der Seite, Struktur und
Jobergebnissen ist wie `/modell-aus-dateien/#meshto3d`". Ein Formular (Name, Fotos mit Rollen, Optionen)
und darunter die Tabelle der Aufträge — gebaut wie der Reiter „Mesh to 3D" (`_meshfigur_reiter.html`),
mit Fotos statt eines Netzes als Eingang. Die Seite hat keine Reiter: Sie ist der ganze Bereich.
"""

from django.shortcuts import render

from ..dienste.blendermodelltabelle import Blendermodelltabelle
from ..models import Blendermodellauftrag

__all__ = ['Blendermodelldashboard']


class Blendermodelldashboard:
    @staticmethod
    def seite(request):
        return render(
            request,
            'blendermodell.html',
            {'tabelle': Blendermodelltabelle(Blendermodellauftrag.objects.all()).tabelle()},
        )
