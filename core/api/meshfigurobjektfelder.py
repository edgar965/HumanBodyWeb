# -*- coding: utf-8 -*-
"""Meshfigurobjektfeldendpunkt — die Gelenkkorrekturen (JCMs) eines Objekts aus dem Netz (14.10.2026).

GET /api/meshfigur/<id>/objektfelder/<datei>
    {datei, gruppe, felder: {kanal: {n, d, anzahl}}}   `n` Punktnummern der GLB (uint32), `d` Verschiebungen (float32, Meter, xyz je Punkt)

Dasselbe Format wie `felder/gelenke/` der Garderobe (`g9felder.py`), damit der Browser es mit `Genesis9felder.anwenden` auf das Objekt legt. Ein starres Objekt (Stab, Bart, Haar am Kopf) oder eins ohne Hautdatei
bekommt ein leeres Wörterbuch. Gerechnet wird beim ersten Mal in einem eigenen Faden (Kleidung 0,1–0,8 Mio. Punkte: einige Sekunden), danach kommt es aus `arbeit/objektfelder_<datei>.npz`.
"""

from asgiref.sync import sync_to_async
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from ..daten.meshfigurablage import Meshfigurablage
from ..daten.netzantwort import Netzantwort
from ..daten.netzausgabe import Netzausgabe
from ..dienste.meshfigurobjektfelder import Meshfigurobjektfelder
from ..models import Meshfigurauftrag

__all__ = ['Meshfigurobjektfeldendpunkt']


class Meshfigurobjektfeldendpunkt:

    @staticmethod
    @require_GET
    async def felder(request, job_id, name):
        try:
            felder = await sync_to_async(Meshfigurobjektfeldendpunkt._rechnen, thread_sensitive=False)(job_id, name)
        except ValueError as fehler:
            raise Http404(str(fehler)) from None
        return Netzausgabe.antwort({
            'datei': name, 'gruppe': Meshfigurobjektfelder.GRUPPE,
            'felder': {kanal: {'n': Netzantwort.feld(nummern, 'n', typ='uint32'), 'd': Netzantwort.feld(deltas, 'd'), 'anzahl': int(len(nummern))}
                       for kanal, (nummern, deltas) in felder.items()},
        }, request)

    @staticmethod
    def _rechnen(job_id, name):
        job = get_object_or_404(Meshfigurauftrag, pk=job_id)
        return Meshfigurobjektfelder(Meshfigurablage(job.kennung)).holen(name)
