# -*- coding: utf-8 -*-
"""Bildmodellfreistellerendpunkte — Hintergrund eines Ausschnitts entfernen (20.09.2026).

POST /api/bildmodell/<id>/freisteller/<datei>/vorschau/       {schwelle, weich, rand, hintergrund}
                                                               → PNG (verkleinert); die Maske
                                                               entsteht beim ersten Aufruf (~6 s)
POST /api/bildmodell/<id>/freisteller/<datei>/speichern/      dieselben Regler → {ok, bild, textur,
                                                               texturbilder} — Ausschnitt ersetzt
POST /api/bildmodell/<id>/freisteller/<datei>/zuruecksetzen/  → wie speichern, Bild von vorher

Nicht, solange der Auftrag läuft (`_frei`): der Lauf liest die Ausschnitte gerade.
"""

import json
import logging

from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from ..daten.bildmodellablage import Bildmodellablage
from ..dienste.bildmodellfreisteller import Bildmodellfreisteller
from ..dienste.bildmodelltextur import Bildmodelltextur
from .bildmodelldateien import Bildmodelldateiendpunkte

logger = logging.getLogger('core')

__all__ = ['Bildmodellfreistellerendpunkte']


class Bildmodellfreistellerendpunkte:
    @staticmethod
    def _rumpf(request):
        try:
            return json.loads(request.body or b'{}')
        except ValueError:
            return {}

    @staticmethod
    def _dienst(job_id, datei):
        job, fehler = Bildmodelldateiendpunkte._frei(job_id)
        if fehler:
            return job, None, fehler
        if job.bild(datei) is None:
            raise Http404('Kein Bild %s' % datei)
        return job, Bildmodellfreisteller(job, Bildmodellablage(job.kennung)), None

    @staticmethod
    @require_POST
    def grundlage(request, job_id, datei):
        """Bild, Maske (und Abstandskarte) in Vorschaugröße — der Browser rechnet die Regler selbst
        (21.09.2026, Edgar: „die slider sollen sofort wirken")."""
        from ..dienste.bildmodellfreistellergrundlage import Bildmodellfreistellergrundlage

        job, dienst, fehler = Bildmodellfreistellerendpunkte._dienst(job_id, datei)
        if fehler:
            return fehler
        try:
            rumpf = Bildmodellfreistellerendpunkte._rumpf(request)
            aus = Bildmodellfreistellergrundlage(dienst).holen(datei, rumpf)
        except (RuntimeError, ValueError, OSError) as fehler:
            logger.warning('Bildmodell %s: Freisteller-Grundlage %s: %s', job.kennung, datei, fehler)
            return JsonResponse({'error': str(fehler)}, status=500)
        antwort = JsonResponse(aus)
        antwort['Cache-Control'] = 'no-store'
        return antwort

    @staticmethod
    @require_POST
    def vorschau(request, job_id, datei):
        job, dienst, fehler = Bildmodellfreistellerendpunkte._dienst(job_id, datei)
        if fehler:
            return fehler
        try:
            png = dienst.vorschau(datei, Bildmodellfreistellerendpunkte._rumpf(request))
        except (RuntimeError, ValueError, OSError) as fehler:
            logger.warning('Bildmodell %s: Freisteller-Vorschau %s: %s', job.kennung, datei, fehler)
            return JsonResponse({'error': str(fehler)}, status=500)
        antwort = HttpResponse(png, content_type='image/png')
        antwort['Cache-Control'] = 'no-store'
        return antwort

    @staticmethod
    def _antwort(job, eintrag):
        # `bildstand` wie im Zustand (`Bildmodellendpunkte._bilder`): Adresse des Ausschnitts wechselt.
        try:
            pfad = Bildmodellablage(job.kennung).datei(Bildmodellablage.ZUSCHNITT, eintrag.get('datei') or '')
            eintrag = dict(eintrag, bildstand=int(pfad.stat().st_mtime))
        except (OSError, ValueError):
            pass
        return JsonResponse({'ok': True, 'bild': eintrag, 'textur': Bildmodelltextur.hautton(job.bilder),
                             'texturbilder': Bildmodelltextur.liste(job.bilder)})

    @staticmethod
    @require_POST
    def speichern(request, job_id, datei):
        job, dienst, fehler = Bildmodellfreistellerendpunkte._dienst(job_id, datei)
        if fehler:
            return fehler
        try:
            eintrag = dienst.speichern(datei, Bildmodellfreistellerendpunkte._rumpf(request))
        except PermissionError as fehler:
            return Bildmodelldateiendpunkte._gesperrt(fehler)
        except (RuntimeError, ValueError, OSError) as fehler:
            logger.warning('Bildmodell %s: Freistellen %s: %s', job.kennung, datei, fehler)
            return JsonResponse({'error': str(fehler)}, status=500)
        return Bildmodellfreistellerendpunkte._antwort(job, eintrag)

    @staticmethod
    @require_POST
    def zuruecksetzen(request, job_id, datei):
        job, dienst, fehler = Bildmodellfreistellerendpunkte._dienst(job_id, datei)
        if fehler:
            return fehler
        try:
            eintrag = dienst.zuruecksetzen(datei)
        except PermissionError as fehler:
            return Bildmodelldateiendpunkte._gesperrt(fehler)
        except (RuntimeError, ValueError, OSError) as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return Bildmodellfreistellerendpunkte._antwort(job, eintrag)
