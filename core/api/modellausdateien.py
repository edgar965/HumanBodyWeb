# -*- coding: utf-8 -*-
"""Modellausdateien — die Seite „Modell aus Dateien" mit den Reitern „3D", „Mesh" und „Mesh to 3D".

„Mesh to 3D" (27.09.2026): ein hochgeladenes Menschen-Netz wird zur Genesis-9-Figur
(`Meshfigurauftrag`, `Meshfigurlauf`).

Edgar (26.09.2026): „brauch ich einen zweiten Tab. Aktueller Tabname: 3D, neuer Tab:
Mesh." Der Reiter 3D ist das bisherige Dashboard (Genesis-9-Figur aus Fotos,
`Bildmodellauftrag`), der Reiter Mesh baut ein freies Netz aus Fotos (`Meshauftrag`).
Welcher Reiter offen ist, entscheidet die Seite (`#mesh` in der Adresse oder der
zuletzt gewählte) — der Server liefert beide.
"""

from django.shortcuts import render

from ..dienste.bildmodellpersonkatalog import Bildmodellpersonkatalog
from ..dienste.bildmodelltabelle import Bildmodelltabelle
from ..dienste.meshfiguroptionen import Meshfiguroptionen
from ..dienste.meshfigurtabelle import Meshfigurtabelle
from ..dienste.meshoptionen import Meshoptionen
from ..dienste.meshtabelle import Meshtabelle
from ..models import Bildmodellauftrag, Meshauftrag, Meshfigurauftrag

__all__ = ['Modellausdateien']


class Modellausdateien:
    @staticmethod
    def dashboard(request):
        return render(
            request,
            'bildmodell.html',
            {
                'tabelle': Bildmodelltabelle(Bildmodellauftrag.objects.all()).tabelle(),
                'typen': Bildmodellauftrag.TYP_CHOICES,
                'testfiguren': Bildmodellpersonkatalog.testfiguren(),
                'mesh_tabelle': Meshtabelle(Meshauftrag.objects.all()).tabelle(),
                'mesh_katalog': Meshoptionen.katalog(),
                # Reiter „Mesh to 3D" (Netz → Genesis-9-Figur, 27.09.2026)
                'meshfigur_tabelle': Meshfigurtabelle(Meshfigurauftrag.objects.all()).tabelle(),
                'meshfigur_katalog': Meshfiguroptionen.katalog(),
            },
        )
