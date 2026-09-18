# -*- coding: utf-8 -*-
"""SMPL-Referenzkoerper fuer die Szene: Liste und Netz.

    GET /api/character/smpl-figur/               {figuren: [{name, anzeige,
                                                  geschlecht, bytes, masse_vorhanden}]}
    GET /api/character/smpl-figur/<name>/netz/   {name, geschlecht, punkte,
                                                  dreiecke, hoehe, masse}

Warum es diese Figur gibt: `core/dienste/smplfigur.py`.
"""

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from ..daten.netzantwort import Netzantwort
from ..dienste.smplfigur import Smplfiguren

logger = logging.getLogger("core")

__all__ = ["Smplfigur"]


class Smplfigur:
    """Lesende Endpunkte auf die SMPL-Koerper des GarmentCode-Klons."""

    @staticmethod
    @require_GET
    def liste(request):
        return JsonResponse({"figuren": Smplfiguren.liste()})

    @staticmethod
    @require_GET
    def netz(request, name):
        if not Smplfiguren.kennt(name):
            return JsonResponse({"fehler": "Unbekannter SMPL-Körper"}, status=404)
        try:
            punkte, dreiecke = Smplfiguren.netz(name)
            masse = Smplfiguren.masse(name)
        except (OSError, ValueError) as fehler:
            logger.warning("SMPL-Koerper %s nicht lesbar: %s", name, fehler)
            return JsonResponse({"fehler": str(fehler)}, status=500)
        return JsonResponse(
            {
                "name": name,
                "geschlecht": Smplfiguren.geschlecht(name),
                "smpl": Smplfiguren.ist_smpl(name),
                "punkte": punkte.tolist(),
                "dreiecke": dreiecke.tolist(),
                "hoehe": (float(punkte[:, 1].max() - punkte[:, 1].min()) if len(punkte) else 0.0),
                "masse": {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in masse.items()},
                # Das Skelett kommt MIT dem Netz, nicht ueber einen zweiten
                # Endpunkt: Die Gelenke werden aus genau diesen Punkten
                # gerechnet, und ein zweiter Aufruf koennte ein anderes Netz
                # treffen (Formregler, Geschlechtswechsel). `null` heisst
                # „dieser Koerper hat keine SMPL-Topologie".
                "skelett": Smplfiguren.skelett(name, punkte),
                # Ohne Hautgewichte bleibt die Figur beim Abspielen starr —
                # das Skelett bewegt sich, das Netz nicht.
                "hautgewichte": Netzantwort.hautgewichte(Smplfiguren.haut(name, punkte)),
            }
        )
