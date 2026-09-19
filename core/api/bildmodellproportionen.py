# -*- coding: utf-8 -*-
"""Bildmodellproportionenendpunkte — die Eingaben des Proportionen-Popups ablegen.

Edgar (19.09.2026): „Mit einem Popup kommt ein Fenster, wo ich diese anpassen
kann. Diese Proportionen nutzt du dann für deine Berechnung."

POST `api/bildmodell/<id>/proportionen/` mit `{proportionen: {schluessel: cm},
linien: {datei: {linien}}}` schreibt die geprüften Werte
(`Bildmodelloptionen.proportionen_pruefen`) nach `job.optionen.proportionen` —
leer heißt „keine Vorgabe", das rohe Zielnetz gilt — und die im Popup gezogenen
Linien (`Bildmodellfotolinien.linien_pruefen`, Pixel des Fotos je Bild) nach
`job.optionen.proportionen_linien`. Wirksam werden sie mit dem nächsten Lauf ab „Anpassung"
(`Bildmodellzielproportionen` formt das Zielnetz); der Start-Endpunkt behält
sie, wenn der Aufruf keine eigenen mitbringt.

POST `api/bildmodell/<id>/reihenfolge/` mit `{reihenfolge: [datei, …]}` nummeriert die
Zeilen der Bildtabelle (Spalte „Nr.", editierbar — Edgar, 20.09.2026); die Nummer steht
als `reihe` am Bild, `Bildmodellfotolinien.hauptbilder` sortiert danach.
"""

import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.bildmodellfotolinien import Bildmodellfotolinien
from ..dienste.bildmodelloptionen import Bildmodelloptionen
from ..models import Bildmodellauftrag

__all__ = ['Bildmodellproportionenendpunkte']


class Bildmodellproportionenendpunkte:
    """Zwei Endpunkte: Proportionen stellen, Reihenfolge der Bildtabelle."""

    @staticmethod
    @require_POST
    def reihenfolge(request, job_id):
        """`{reihenfolge: [datei, …]}` — die Zeilen der Bildtabelle in dieser Reihe
        (Spalte „Nr.", `bilder[].reihe`); Antwort mit den neuen `fotolinien`."""
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Kein JSON'}, status=400)
        linien = Bildmodellfotolinien(job)
        nummern = linien.reihenfolge(rumpf.get('reihenfolge'))
        if not nummern:
            return JsonResponse({'error': 'Keine bekannten Dateien in der Reihenfolge'}, status=400)
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'reihe': nummern, 'fotolinien': linien.alle()})

    @staticmethod
    @require_POST
    def stellen(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            rumpf = {}
        werte = Bildmodelloptionen.proportionen_pruefen(rumpf.get('proportionen'))
        optionen = dict(job.optionen or {})
        optionen['proportionen'] = werte
        if 'linien' in rumpf:
            optionen[Bildmodellfotolinien.OPTION] = Bildmodellfotolinien.linien_pruefen(rumpf.get('linien'))
        job.optionen = optionen
        job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'proportionen': werte,
                             'linien': optionen.get(Bildmodellfotolinien.OPTION) or {}})
