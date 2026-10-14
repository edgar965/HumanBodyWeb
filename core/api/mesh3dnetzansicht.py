# -*- coding: utf-8 -*-
"""Mesh3dnetzansichtendpunkte — die vereinfachte Netz-Kopie der 3D-Ansicht (11.10.2026), siehe `Mesh3dnetzansicht`.

GET  /api/mesh3d/<kennung>/netzansicht/   die Kopie (`?v=<Änderungszeit des Originals>` → ein Jahr im Zwischenspeicher); bei einem kleinen Netz (`unnoetig`) das Netz selbst; 404, solange es nichts gibt
POST /api/mesh3d/<kennung>/netzansicht/   den Bau anstoßen (eigener Prozess) → {status}; ändert nichts, wenn die Kopie schon da ist oder gebaut wird
"""

from django.http import Http404, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.mesh3dnetzansicht import Mesh3dnetzansicht
from ..dienste.mesh3dzustand import Mesh3dzustand

__all__ = ['Mesh3dnetzansichtendpunkte']


class Mesh3dnetzansichtendpunkte:
    @staticmethod
    @require_GET
    def datei(request, kennung):
        if Mesh3dzustand.stand(kennung) is None:
            raise Http404()
        ansicht = Mesh3dnetzansicht(kennung)
        quelle = ansicht.quelle()
        if quelle is None:
            raise Http404()
        if ansicht.zustand()['status'] == 'unnoetig':          # klein genug: das Netz selbst (die Mesh-Ansicht ohne Auftrag „Mesh to 3D“ braucht es)
            return Auftragsdatei.antwort(request, quelle, kennung=request.GET.get('v'))
        if not ansicht.aktuell(quelle):
            raise Http404()
        return Auftragsdatei.antwort(request, ansicht.pfad(), kennung=request.GET.get('v'))

    @staticmethod
    @require_POST
    def anstossen(request, kennung):
        if Mesh3dzustand.stand(kennung) is None:
            return JsonResponse({'error': 'Kein Auftrag %s' % kennung}, status=404)
        return JsonResponse({'ok': True, **Mesh3dnetzansicht(kennung).anstossen()})
