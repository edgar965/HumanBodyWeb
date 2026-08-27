# -*- coding: utf-8 -*-
"""Die BVH-Bibliothek auflisten und einzelne Dateien ausliefern.

Aus core/api/retarget.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befund `freie-funktionen`): vier freie Funktionen, jetzt
Methoden von `Bvhauslieferung`. Die Wurzel der Bibliothek wurde dreimal aus
`HUMANBODY_BVH_DIR` zurueckgerechnet — jetzt einmal.
"""

import json
import os
import re

from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST


class Bvhauslieferung:
    """Bewegungsdateien der Bibliothek listen, ausliefern und ablegen."""

    @staticmethod
    def wurzel():
        """Das Verzeichnis UEBER den Kategorieordnern."""
        return os.path.dirname(str(settings.HUMANBODY_BVH_DIR))

    @staticmethod
    @require_GET
    def animationen(request):
        """Alle BVH-Animationen nach Kategorie — siehe Animationsliste."""
        from ..dienste.animationsliste import Animationsliste
        return JsonResponse({'categories': Animationsliste().nach_kategorie()})

    @staticmethod
    def _ausliefern(pfad, name):
        return FileResponse(open(pfad, 'rb'), content_type='text/plain',
                            filename='%s.bvh' % name)

    @staticmethod
    def datei(request, name):
        """Aeltere Adresse: eine Datei direkt aus dem MocapNET-Ordner."""
        pfad = os.path.join(str(settings.HUMANBODY_BVH_DIR), '%s.bvh' % name)
        if not os.path.isfile(pfad):
            return HttpResponseNotFound('BVH not found: %s' % name)
        return Bvhauslieferung._ausliefern(pfad, name)

    @staticmethod
    def datei_der_kategorie(request, category, name):
        """Eine Datei aus einem Kategorieordner."""
        wurzel = Bvhauslieferung.wurzel()
        pfad = os.path.normpath(os.path.join(wurzel, category, '%s.bvh' % name))
        if not pfad.startswith(os.path.normpath(wurzel)):
            return HttpResponseNotFound('Invalid path')
        if not os.path.isfile(pfad):
            return HttpResponseNotFound('BVH not found: %s/%s'
                                        % (category, name))
        return Bvhauslieferung._ausliefern(pfad, name)

    @staticmethod
    @csrf_exempt
    @require_POST
    def sichern(request):
        """Eine BVH-Animation in ihren Kategorieordner schreiben."""
        try:
            rumpf = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        kategorie = rumpf.get('category', '').strip()
        name = rumpf.get('name', '').strip()
        inhalt = rumpf.get('bvh_content', '')
        if not kategorie or not name or not inhalt:
            return JsonResponse(
                {'error': 'category, name, and bvh_content required'},
                status=400)
        # Wortzeichen, Leerzeichen, Bindestriche und Punkte bleiben stehen.
        name = re.sub(r'[^\w\s\-.]', '', name).strip()
        kategorie = re.sub(r'[^\w\s\-.]', '', kategorie).strip()
        if not name or not kategorie:
            return JsonResponse({'error': 'Invalid name or category'},
                                status=400)
        wurzel = Bvhauslieferung.wurzel()
        ordner = os.path.normpath(os.path.join(wurzel, kategorie))
        ziel = os.path.normpath(os.path.join(ordner, '%s.bvh' % name))
        if not ziel.startswith(os.path.normpath(wurzel)):
            return JsonResponse({'error': 'Invalid path'}, status=400)
        os.makedirs(ordner, exist_ok=True)
        with open(ziel, 'w', encoding='utf-8') as datei:
            datei.write(inhalt)
        return JsonResponse({'ok': True,
                             'path': '%s/%s.bvh' % (kategorie, name)})
