# -*- coding: utf-8 -*-
"""BVH-Studio und Theatre: Projekte, Ton, Szenenobjekte, Video.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `globaler-zustand`): sechs freie
Funktionen und drei Verzeichnisse, die beim IMPORT aus `settings` gerechnet
wurden. Ein solcher Wert haelt sich bis zum Prozessende und geht an jedem
`override_settings` vorbei — die Verzeichnisse sind jetzt Methoden.

Dazu: Drei Funktionen holten sich mit `logging.getLogger('core')` einen eigenen
Logger, obwohl das Modul schon einen fuehrt.
"""

import json
import logging
import os
import pathlib
import uuid

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..daten.hochgeladen import Hochgeladen

logger = logging.getLogger('core')


class Studioendpunkte:
    """Ton, Szenenobjekte, Lichtvorgaben und Bodentexturen des Studios."""

    #: Groesste zulaessige Tondatei (50 MB).
    TON_MAXIMUM = 50 * 1024 * 1024
    #: Tonformate, die der Browser abspielen kann.
    TONFORMATE = frozenset({'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac',
                            '.webm'})
    #: Was als Szenenobjekt hochgeladen werden darf (Netze und Texturen).
    OBJEKTFORMATE = frozenset({'obj', 'glb', 'gltf', 'fbx', 'mtl', 'jpg',
                               'jpeg', 'png', 'webp', 'bmp', 'tga'})
    #: Bildformate der Bodentexturen.
    BODENFORMATE = ('.jpg', '.jpeg', '.png', '.webp')
    #: So lang darf eine Buendelkennung hoechstens sein.
    BUENDEL_LAENGE = 32

    # -------------------------------------------------------- Verzeichnisse

    @staticmethod
    def bodentexturen_ordner():
        return settings.BASE_DIR / 'static' / 'assets' / 'floor_textures'

    @staticmethod
    def szenenobjekte_ordner():
        return settings.MEDIA_ROOT / 'scene_objects'

    @staticmethod
    def lichtvorgaben_ordner():
        return settings.HUMANBODY_ROOT / 'data' / 'theatre_presets'

    # ------------------------------------------------------- Einstellungen

    @staticmethod
    def theatre_einstellungen(request):
        """Die Theatre-Vorgaben zum automatischen Laden."""
        from core.models import AppSettings
        gespeichert = AppSettings.load()
        return JsonResponse({
            'model': gespeichert.theatre_default_model or '',
            'animation': gespeichert.theatre_default_animation or '',
            'preset': gespeichert.theatre_default_preset or 'ballet_stage',
            'video_format': gespeichert.theatre_video_format or 'mp4',
            'video_resolution': gespeichert.theatre_video_resolution or '1080p',
            'video_fps': gespeichert.theatre_video_fps or 30,
            'video_quality': gespeichert.theatre_video_quality or 'high',
        })

    # ----------------------------------------------------------------- Ton

    @staticmethod
    @csrf_exempt
    @require_POST
    def ton_hochladen(request):
        """Tondatei fuer ein BVH-Studio-Projekt ablegen.

        POST /api/studio/audio-upload/
        Antwort: { ok: true, url: '/media/studio_audio/xxx.mp3' }
        """
        datei = request.FILES.get('audio')
        if not datei:
            return JsonResponse({'error': 'No audio file provided'}, status=400)
        if datei.size > Studioendpunkte.TON_MAXIMUM:
            return JsonResponse(
                {'error': 'File too large (%dMB). Max 50MB.'
                          % (datei.size // (1024 * 1024))}, status=400)
        endung = pathlib.Path(datei.name).suffix.lower()
        if endung not in Studioendpunkte.TONFORMATE:
            return JsonResponse(
                {'error': 'Unsupported format: %s. Allowed: %s'
                          % (endung, ', '.join(sorted(
                              Studioendpunkte.TONFORMATE)))}, status=400)
        ordner = os.path.join(settings.MEDIA_ROOT, 'studio_audio')
        os.makedirs(ordner, exist_ok=True)
        name = '%s%s' % (uuid.uuid4().hex, endung)
        try:
            Hochgeladen.ablegen(os.path.join(ordner, name), datei)
        except Exception as fehler:
            logger.error('[studio] Audio upload failed: %s', fehler)
            return JsonResponse({'error': str(fehler)}, status=500)
        logger.info('[studio] Audio uploaded: %s (%d bytes) -> %s',
                    datei.name, datei.size, name)
        return JsonResponse({'ok': True,
                             'url': '%sstudio_audio/%s'
                                    % (settings.MEDIA_URL, name)})

    # -------------------------------------------------------- Lichtvorgaben

    @staticmethod
    def lichtvorgaben(request):
        """Alle Theatre-Lichtvorgaben.

        GET /api/studio/theatre-presets/
        Antwort: { presets: [{ name, label, lightCount, description }] }
        """
        ordner = Studioendpunkte.lichtvorgaben_ordner()
        vorgaben = []
        if ordner.is_dir():
            for datei in sorted(ordner.glob('*.json')):
                try:
                    with open(datei, 'r', encoding='utf-8') as offen:
                        daten = json.load(offen)
                except Exception as fehler:
                    logger.error('[theatre-presets] Failed to read %s: %s',
                                 datei, fehler)
                    continue
                vorgaben.append({
                    'name': datei.stem,
                    'label': daten.get('label', datei.stem),
                    'description': daten.get('description', ''),
                    'lightCount': len(daten.get('lights', [])),
                })
        return JsonResponse({'presets': vorgaben})

    @staticmethod
    def lichtvorgabe(request, name):
        """Die JSON-Beschreibung EINER Lichtvorgabe.

        GET /api/studio/theatre-preset/<name>/
        """
        datei = Studioendpunkte.lichtvorgaben_ordner() / ('%s.json' % name)
        if not datei.is_file():
            return JsonResponse({'error': 'Preset nicht gefunden'}, status=404)
        try:
            with open(datei, 'r', encoding='utf-8') as offen:
                return JsonResponse(json.load(offen))
        except Exception as fehler:
            logger.exception('studio_theatre_preset_detail: unerwarteter Fehler')
            return JsonResponse({'error': str(fehler)}, status=500)

    # ------------------------------------------------------- Bodentexturen

    @staticmethod
    def bodentexturen(request):
        """Alle verfuegbaren Bodentexturen.

        GET /api/studio/floor-textures/
        Antwort: { textures: [{ name, label, url }] }
        """
        texturen = [{'name': 'none', 'label': 'Keine (Farbe)', 'url': ''}]
        ordner = Studioendpunkte.bodentexturen_ordner()
        if ordner.is_dir():
            for datei in sorted(ordner.glob('*')):
                if datei.suffix.lower() not in Studioendpunkte.BODENFORMATE:
                    continue
                texturen.append({
                    'name': datei.stem,
                    'label': datei.stem.replace('_', ' ').title(),
                    'url': '/static/assets/floor_textures/%s' % datei.name,
                })
        return JsonResponse({'textures': texturen})

    # ------------------------------------------------------ Szenenobjekte

    @staticmethod
    @csrf_exempt
    @require_POST
    def objekt_hochladen(request):
        """Ein 3D-Objekt fuer den BVH-Studio ablegen.

        POST /api/studio/scene-object-upload/  (Formularfeld `object`)
        Antwort: { ok, url, name, ext }
        """
        if 'object' not in request.FILES:
            return JsonResponse({'error': 'Kein object File'}, status=400)
        hochgeladen = request.FILES['object']
        endung = (hochgeladen.name.rsplit('.', 1)[-1]
                  if '.' in hochgeladen.name else '').lower()
        if endung not in Studioendpunkte.OBJEKTFORMATE:
            return JsonResponse(
                {'error': 'Format "%s" nicht unterstützt' % endung}, status=400)
        ordner, name, buendel = Studioendpunkte._ablageort(request, hochgeladen,
                                                           endung)
        ordner.mkdir(parents=True, exist_ok=True)
        try:
            Hochgeladen.ablegen(ordner / name, hochgeladen)
        except Exception as fehler:
            logger.exception('studio_scene_object_upload: unerwarteter Fehler')
            return JsonResponse({'error': str(fehler)}, status=500)
        logger.info('[scene-object] Uploaded: %s (%d bytes)',
                    ordner / name, hochgeladen.size)
        return JsonResponse({
            'ok': True,
            'url': '%sscene_objects/%s%s' % (settings.MEDIA_URL,
                                             '%s/' % buendel if buendel else '',
                                             name),
            'name': hochgeladen.name,
            'ext': endung,
        })

    @staticmethod
    def _ablageort(request, hochgeladen, endung):
        """(Ordner, Dateiname, Buendel) — Buendel behaelt Originalnamen.

        Alle Dateien EINES Imports gehen in denselben Unterordner, damit die
        Texturverweise in der MTL-Datei ueber die Originalnamen aufgehen.
        """
        roh = request.POST.get('bundleId', '').strip()
        buendel = ''.join(z for z in roh if z.isalnum() or z in '-_')
        buendel = buendel[:Studioendpunkte.BUENDEL_LAENGE]
        wurzel = Studioendpunkte.szenenobjekte_ordner()
        if buendel:
            return wurzel / buendel, hochgeladen.name.replace(' ', '_'), buendel
        stamm = hochgeladen.name.rsplit('.', 1)[0].replace(' ', '_')
        return wurzel, '%s_%s.%s' % (stamm, uuid.uuid4().hex[:8], endung), ''
