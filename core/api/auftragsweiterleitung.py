# -*- coding: utf-8 -*-
"""Auftragsweiterleitung — alte `/process/<uuid>/…`-Adressen auf die Kennung.

Bis zum 16.09.2026 hießen die Auftragsseiten nach der UUID. Die Adressen
stehen in Browserverläufen, Lesezeichen, Logs und im Tagebuch; sie sollen
nicht in eine 404 laufen, sondern dauerhaft (301) auf
`/process/<kennung>/<rest>` zeigen. Nur GET — die Formulare (start, stop,
delete) schicken POST an die neuen Adressen.
"""

from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404

from ..models import BVHJob


class Auftragsweiterleitung:
    @staticmethod
    def alt(request, job_id, rest=''):
        job = get_object_or_404(BVHJob, id=job_id)
        return HttpResponsePermanentRedirect('/process/%s/%s' % (job.kennung, rest))
