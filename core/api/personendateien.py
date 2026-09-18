# -*- coding: utf-8 -*-
"""Personendateien — das BVH einer weiteren Person eines Auftrags.

`GET /api/bvh/<job_id>/person/<n>/` liefert `bvh_file_personen[n-2]` als
Text — Person 1 ist `serve_bvh`. Eigenes Modul, weil `api/dateien.py`
(`Auftragsdateien`) mit 265 Zeilen voll ist (14.09.2026).
"""

from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404

from ..models import BVHJob
from .dateien import Auftragsdateien


class Personendateien:
    """Ein Einstieg je Person, wie `Auftragsdateien.bvh_gesicht`."""

    @staticmethod
    def bvh(request, job_id, person):
        job = get_object_or_404(BVHJob, id=job_id)
        weitere = job.bvh_file_personen or []
        stelle = int(person) - 2
        if stelle < 0 or stelle >= len(weitere):
            return HttpResponseNotFound("Kein BVH für Person %s" % person)
        return Auftragsdateien.textantwort(weitere[stelle])
