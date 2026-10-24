# -*- coding: utf-8 -*-
"""Ai2d3dtabellen — die vier Tabellen der Liste `/2d-3d-AI/` als djangoBase-Tabellen (24.10.2026), Reiter für Reiter wie `/mesh-3D-AI/`.

Edgar: „mach eine Kopie von Dashboard - Mesh3d-AI …“, dann „Ich sagte eine Kopie der Mesh3d-Ai jobs … keine Gerechnet Spalten, keine Jobauswahl zum Löschen usw“. Darum stehen hier die Spalten
VON Mesh3D-AI (die Klassen dort sind die Quelle, nichts abgeschrieben): Jobs (`Ai2d3djobtabelle`: Exporte mit Wahrheit), Test (`Ai2d3dtesttabelle`: echte Fotos), Formtraining und Formvarianten
(`Mesh3daiformtrainingtabelle`, `Mesh3daiformvariantentabelle` — 2d-3d-AI hat noch kein Training, also keine Zeilen).
"""

from .ai2d3djobs import Ai2d3djobs
from .ai2d3djobtabelle import Ai2d3djobtabelle
from .ai2d3dtesttabelle import Ai2d3dtesttabelle
from .mesh3daiformtrainingtabelle import Mesh3daiformtrainingtabelle
from .mesh3daiformvariantentabelle import Mesh3daiformvariantentabelle

__all__ = ['Ai2d3dtabellen']


class Ai2d3dtabellen:
    KLASSE = 'auftragstabelle mesh3daitabelle ai2d3dtabelle'

    @classmethod
    def alle(cls):
        """Der Kontext der Liste: je Reiter die Tabelle (Schlüssel wie in `mesh3dai_liste.html`)."""
        jobs = Ai2d3djobs.alle()
        exporte = [j for j in jobs if j['art'] == 'export']
        tests = [j for j in jobs if j['art'] == 'foto']
        return {
            'tabelle': cls._tabelle(Ai2d3djobtabelle.SCHLUESSEL, Ai2d3djobtabelle.spalten(), [Ai2d3djobtabelle.zeile(j) for j in exporte],
                                    'Noch kein Job: ein Ordner unter 3DObjects/modelsExport mit <Name>.json und vier Fotos wird einer.'),
            'testtabelle': cls._tabelle(Ai2d3dtesttabelle.SCHLUESSEL, Ai2d3dtesttabelle.spalten(), Ai2d3dtesttabelle.zeilen(tests), 'Noch kein Test.'),
            'formtraining': cls._tabelle('ai2d3d-formtraining', Mesh3daiformtrainingtabelle.SPALTEN, [], 'Noch kein Trainingslauf für 2d-3d-AI.'),
            'formvarianten': cls._tabelle('ai2d3d-formvarianten', Mesh3daiformvariantentabelle.SPALTEN, [], 'Noch keine Formvariante für 2d-3d-AI.'),
        }

    @classmethod
    def _tabelle(cls, schluessel, spalten, zeilen, leer):
        return {'key': schluessel, 'spalten': list(spalten), 'zeilen': zeilen, 'klasse': cls.KLASSE, 'leer': leer}
