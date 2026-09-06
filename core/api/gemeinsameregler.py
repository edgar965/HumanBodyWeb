# -*- coding: utf-8 -*-
u"""Die gemeinsame Reglertabelle für den Browser.

    GET /api/character/regler/gemeinsam/
        {gruppen: [{name, regler: [{name, anzeige, einheit, uma, humanbody, meta}]}],
         min, max}

Ein Eintrag nennt einen fachlichen Regler und je Welt, was dafür zu stellen
ist: `uma` sind DNA-Namen (Knochen), `humanbody` Morphnamen (Punkte), `meta`
ein Metaregler mit echter Einheit. Die Tabelle steht in
`humanbody_core.regler` — hier wird sie nur ausgeliefert.

Gefiltert wird NICHT: Welche Regler eine Figur wirklich hat, hängt an ihrer
UMA-Rasse beziehungsweise ihrem Körpertyp, und beides weiß der Browser
bereits (`inst.dna`, `state.morphDefs`). Der Latin-Körpertyp etwa führt gar
keine Gesichtsmorphs, männliche Typen keine Brustposition — solche Zeilen
blendet die Seite selbst aus. 06.09.2026.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from humanbody_core.regler import Reglertabelle

__all__ = ['Gemeinsameregler']


class Gemeinsameregler:

    @staticmethod
    @require_GET
    def tabelle(request):
        return JsonResponse({
            'min': Reglertabelle.MIN,
            'max': Reglertabelle.MAX,
            'gruppen': [{'name': name, 'regler': eintraege}
                        for name, eintraege in Reglertabelle.gruppen()],
        })
