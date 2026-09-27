# -*- coding: utf-8 -*-
"""Die Fotokacheln eines gespeicherten Genesis-Modells ausliefern (27.09.2026).

    GET /api/character/genesis9-figur/fototextur/<Modell>/<Datei>/

Die Dateien legt `Modelltexturen.sichern` beim Speichern nach `data/models/Texturen/<Modell>/`;
die Adresse trägt `?v=<Stand>`, darum darf der Browser sie lange behalten.
"""

from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET

from ..dienste.modelltexturen import Modelltexturen

__all__ = ['G9fototextur']


class G9fototextur:
    @staticmethod
    @require_GET
    def datei(request, modell, datei):
        pfad = Modelltexturen.datei(modell, datei)
        if pfad is None or not pfad.is_file():
            raise Http404('Keine Textur %s/%s' % (modell, datei))
        antwort = FileResponse(open(pfad, 'rb'), content_type=Modelltexturen.art(pfad))
        antwort['Cache-Control'] = 'max-age=604800' if request.GET.get('v') else 'no-cache'
        return antwort
