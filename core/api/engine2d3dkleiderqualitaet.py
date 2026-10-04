# -*- coding: utf-8 -*-
"""Engine2d3dKleiderqualitaetendpunkt — die Handwertung der Liste von „2D3D Kleider" speichern (03.10.2026).

POST /api/engine2d3dkleider/<id>/qualitaet/     {feld: 'mesh' | '3d' | 'textur' | 'mesh_gesamt' | 'kleider' | 'haar' | 'gesicht' | 'koerper',
                                                 wert: Rang ab 1 oder null}
                                                → {ok, feld, wert (der Rang, den der Lauf jetzt hat, 0 = nicht bewertet),
                                                   raenge: {id: Rang} für ALLE bewerteten Läufe der Spalte}

Der Rang ist eindeutig je Spalte (`Engine2d3dKleiderrang`): Ein vergebener Rang schiebt die anderen Läufe nach hinten, deshalb liefert die
Antwort die ganze Rangliste — die Liste im Browser stellt damit auch die Felder der anderen Zeilen nach, ohne neu zu laden.

Keine Neuberechnung, kein Lauf-Zustand: Es ist eine Kennzeichnung (`Engine2d3dKleiderqualitaet`), also auch erlaubt, während der Auftrag
rechnet. Geschrieben werden nur die Zeilen, deren Rang sich ändert, und nur diese eine Spalte — weder `updated_at` (das Datum der
Tabellenbilder, `?v=`) noch ein anderes Feld ändert sich.
"""

import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.engine2d3dkleiderqualitaet import Engine2d3dKleiderqualitaet
from ..dienste.engine2d3dkleiderrang import Engine2d3dKleiderrang
from ..models import Engine2d3dKleiderauftrag

__all__ = ['Engine2d3dKleiderqualitaetendpunkt']


class Engine2d3dKleiderqualitaetendpunkt:
    @staticmethod
    @require_POST
    def setzen(request, job_id):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            rumpf = {}
        rumpf = rumpf if isinstance(rumpf, dict) else {}
        spalte = Engine2d3dKleiderqualitaet.spalte(str(rumpf.get('feld') or ''))
        if spalte is None:
            return JsonResponse({'error': 'Unbekanntes Feld: %s' % rumpf.get('feld')}, status=400)
        try:
            rang = Engine2d3dKleiderqualitaet.normieren(rumpf.get('wert'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        raenge = Engine2d3dKleiderrang.setzen(job, spalte, rang)
        return JsonResponse({'ok': True, 'feld': rumpf['feld'], 'wert': raenge.get(str(job.pk), 0), 'raenge': raenge})
