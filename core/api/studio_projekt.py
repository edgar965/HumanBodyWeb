# -*- coding: utf-8 -*-
"""Studioprojekte und Szenen auf dem Server ablegen und lesen.

Aus core/api/studio.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befund `freie-funktionen`): sechs freie Funktionen, keine
Klasse. Die Pfadpruefung fuer Szenendateien stand zweimal wortgleich hier und
viermal in `api/modelldateien.py` — sie liegt jetzt in `daten/modellpfad.py`.
"""

import json
import logging
import os
import re

from django.conf import settings
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..atomic_write import AtomarSchreiber
from ..daten.modellpfad import Modellpfad
from ..safe_paths import SafePath, PfadAbgelehnt
from ..daten.anfragerumpf import Anfragerumpf

#: EIN Logger fuer das Modul. Vorher stand `import logging; log =
#: logging.getLogger('core')` zweimal in je einer Funktion — `scene_list`
#: hatte damit keinen, und die dort nachgetragene Zeile waere ein NameError
#: gewesen (gefunden 17.08.2026 durch `logs_namen_pruefen.py`).
log = logging.getLogger('core')


class Studioprojekte:
    """Szenen im Modellordner und `.studio.json`-Projekte auf der Platte."""

    #: Endung einer Szenendatei.
    SZENE = '.scene.json'
    #: Muster der Projektdateien im Projektordner.
    PROJEKTMUSTER = '*.studio.json'

    @staticmethod
    def _modellordner():
        return str(settings.HUMANBODY_MODELS_DIR)

    # -------------------------------------------------------------- Szenen

    @staticmethod
    @require_GET
    def szenenliste(request):
        """Alle Szenendateien (`.scene.json`) mit Figurenzahl."""
        ordner = Studioprojekte._modellordner()
        szenen = []
        if os.path.isdir(ordner):
            for dateiname in sorted(os.listdir(ordner)):
                if not dateiname.endswith(Studioprojekte.SZENE):
                    continue
                szenen.append(Studioprojekte._szeneneintrag(ordner, dateiname))
        return JsonResponse({'scenes': szenen})

    @staticmethod
    def _szeneneintrag(ordner, dateiname):
        name = dateiname[:-len(Studioprojekte.SZENE)]
        pfad = os.path.join(ordner, dateiname)
        try:
            with open(pfad, 'r', encoding='utf-8') as datei:
                daten = json.load(datei)
        except (json.JSONDecodeError, IOError):
            log.warning('Szene %s nicht lesbar — ohne Figurenzahl gelistet',
                        pfad, exc_info=True)
            return {'name': name, 'label': name, 'character_count': 0}
        return {'name': name, 'label': daten.get('name', name),
                'character_count': len(daten.get('characters', []))}

    @staticmethod
    @require_GET
    def szene(request, name):
        """Der Inhalt EINER Szenendatei."""
        pfad = Modellpfad.geprueft(Studioprojekte._modellordner(), name,
                                   Studioprojekte.SZENE)
        if pfad is None:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        if not os.path.isfile(pfad):
            return HttpResponseNotFound('Scene not found: %s' % name)
        with open(pfad, 'r', encoding='utf-8') as datei:
            return JsonResponse(json.load(datei))

    @staticmethod
    @csrf_exempt
    @require_POST
    def szene_sichern(request):
        """Eine Szenendatei schreiben."""
        name, daten, fehler = Anfragerumpf.name_und_daten(request)
        if fehler:
            return fehler
        sauber = re.sub(r'[^\w\s\-]', '', name).strip()
        ordner = Studioprojekte._modellordner()
        pfad = (Modellpfad.geprueft(ordner, sauber, Studioprojekte.SZENE)
                if sauber else None)
        if pfad is None:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        os.makedirs(ordner, exist_ok=True)
        # Anders als bei den Modellen bleibt hier der ANGEZEIGTE Name stehen —
        # der Dateiname ist die bereinigte Fassung.
        daten['name'] = name
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump(daten, datei, indent=2, ensure_ascii=False)
        return JsonResponse({'ok': True,
                             'filename': '%s%s' % (sauber,
                                                   Studioprojekte.SZENE)})

    # ----------------------------------------------------------- Projekte

    @staticmethod
    @csrf_exempt
    @require_POST
    def projekt_sichern(request):
        """Ein BVH-Studio-Projekt als JSON auf die Platte schreiben.

        POST /api/studio/project-save/
        JSON: { path: "voller/pfad.studio.json", project: {...} }

        Pfad wird ueber SafePath geprueft (12.08.2026): vorher schrieb dieser
        Endpunkt an JEDE Stelle der Platte, ohne CSRF-Token und damit auch von
        einer fremden Webseite ausloesbar. Geschrieben wird ueber
        AtomarSchreiber, damit zwei gleichzeitige Speichervorgaenge keine halbe
        Datei hinterlassen.
        """
        daten, fehler = Anfragerumpf.lesen(request)
        if fehler:
            return fehler
        projekt = daten.get('project')
        if not projekt:
            return JsonResponse({'error': 'path + project required'},
                                status=400)
        try:
            ziel = SafePath.fuer_studio_projekte().pruefe(daten.get('path'))
        except PfadAbgelehnt as fehler:
            return JsonResponse({'error': str(fehler)}, status=403)
        try:
            AtomarSchreiber.json_schreiben(ziel, projekt)
        except Exception as fehler:                              # noqa: BLE001
            log.exception('[studio] Project save failed: %s', ziel)
            return JsonResponse({'error': str(fehler)}, status=500)
        log.info('[studio] Project saved: %s', ziel)
        return JsonResponse({'ok': True, 'path': str(ziel)})

    @staticmethod
    @require_GET
    def projekt_laden(request):
        """Ein BVH-Studio-Projekt von der Platte lesen.

        GET /api/studio/project-load/?path=voller/pfad.studio.json
        """
        try:
            pfad = SafePath.fuer_studio_projekte().pruefe(
                request.GET.get('path'))
        except PfadAbgelehnt as fehler:
            return JsonResponse({'error': str(fehler)}, status=403)
        if not pfad.is_file():
            # Kein voller Pfad in der Antwort: Das waere eine Auskunft
            # darueber, was auf der Platte liegt. Der Pfad steht im Protokoll.
            log.info('[studio] Project not found: %s', pfad)
            return JsonResponse({'error': 'File not found'}, status=404)
        try:
            with open(str(pfad), 'r', encoding='utf-8') as datei:
                projekt = json.load(datei)
        except Exception as fehler:                              # noqa: BLE001
            log.exception('[studio] Project load failed: %s', pfad)
            return JsonResponse({'error': str(fehler)}, status=500)
        log.info('[studio] Project loaded: %s', pfad)
        return JsonResponse({'ok': True, 'project': projekt,
                             'path': str(pfad)})

    @staticmethod
    @require_GET
    def projektliste(request):
        """Die Projektdateien im eingestellten Projektordner.

        GET /api/studio/project-list/?dir=pfad
        """
        roh = (request.GET.get('dir') or '').strip()
        if not roh:
            return JsonResponse({'files': []})
        try:
            ordner = SafePath.fuer_studio_projekte().pruefe(roh)
        except PfadAbgelehnt as fehler:
            return JsonResponse({'error': str(fehler)}, status=403)
        if not ordner.is_dir():
            return JsonResponse({'files': []})
        dateien = []
        for datei in sorted(ordner.glob(Studioprojekte.PROJEKTMUSTER)):
            angaben = datei.stat()
            dateien.append({
                'name': datei.stem.replace('.studio', ''),
                'path': str(datei),
                'size': angaben.st_size,
                'modified': angaben.st_mtime,
            })
        return JsonResponse({'files': dateien})
