# -*- coding: utf-8 -*-
u"""Hilfe -> Video to BVH: alle Pipelines in EINER Tabelle, mit Rang.

Auftrag Edgar (12.09.2026): „mach einen tabellarischen Vergleich aller, mit
Vor, Nachteile und Ranking auf einer neuen Seite Hilfe - Video to BVH" und
„die tabelle nach djangoBase vorbild, mit sortierbaren Spalten usw".

Die Daten kommen aus `core.dienste.pipelinevergleich.Pipelinevergleich`,
nicht aus der Vorlage — jede Zahl dort traegt ihre Messung (Video, Datum,
Skript). Die Tabelle ist eine djangoBase-Tabelle (`db-tabelle sortable`):
Sortierung und ziehbare Spaltenbreiten bindet `tabellen_auto.js` von
selbst, sobald die Klasse dasteht.
"""
from .hilfeseite import Hilfeseite
from ..dienste.eigenepipeline import Eigenepipeline
from ..dienste.pipelinevergleich import Pipelinevergleich


class VideoToBvhVergleich(Hilfeseite):
    u"""Die Vergleichstabelle aller Video-nach-BVH-Pipelines."""

    template_name = 'hilfe/video_to_bvh.html'
    AKTIV = 'hilfe_video_to_bvh'

    def kontext(self):
        return {
            'eintraege': Pipelinevergleich.rangfolge(),
            'messung': Pipelinevergleich.MESSUNG,
            'spalten': Pipelinevergleich.SPALTEN,
            'nicht_gelaufen': Pipelinevergleich.nicht_gelaufen(),
            'rang_von': len(Pipelinevergleich.mit_rang()),
            # Abschnitt „Eigene Pipeline: SMPL-X als Rueckgrat" (12.09.2026)
            'eigene': Eigenepipeline.kontext(),
        }
