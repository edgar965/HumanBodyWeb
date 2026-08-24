# -*- coding: utf-8 -*-
"""Kleidungsbibliothek: Bestand, Vorschau, Ausgabe.

Aus core/api/kleidung.py herausgeloest (Umbau 15.08.2026). Die Datei war beim
Aufteilen von character_api.py entstanden und hatte selbst 1.081 Zeilen mit 21
Endpunkten aus vier Themen — Stoffbau, Vorlagen, Schnittmuster und Bibliothek
standen nur durch Reihenfolge getrennt beieinander.
"""

import logging
from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import os
import re

from ..dienste.kleiderverwaltung import Kleiderverwaltung, KleiderFehler
from ..dienste.kleiderbibliothek import Kleiderbibliothek


logger = logging.getLogger(__name__)


def _get_garment_library():
    """Bisherige Aufrufform — siehe dienste/kleiderbibliothek.py.

    Der faule Aufbau stand hier ohne Schloss: Zwei parallele Anfragen vor dem
    ersten Einlesen bauten den Katalog zweimal (Sparring mit Nemotron,
    18.08.2026).
    """
    return Kleiderbibliothek.holen()


@require_GET
def garment_library(request):
    """Return list of available garments, grouped by category."""
    lib = _get_garment_library()
    category = request.GET.get('category', '')

    catalog = lib.catalog
    if category:
        catalog = [g for g in catalog if g['category'] == category]

    by_cat = {}
    for g in catalog:
        cat = g['category']
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(g)

    return JsonResponse({
        'categories': sorted(by_cat.keys()),
        'garments': by_cat,
        'total': len(catalog),
    })


@csrf_exempt
@require_POST
def garment_manage(request):
    """Kleider umbenennen, verschieben, kopieren, in den Papierkorb legen.

    POST /api/character/garment/manage/ mit JSON-Feld `action`:
      rename, move, copy, delete

    Die Arbeit macht `Kleiderverwaltung`; hier steht nur die HTTP-Schale — wie
    bei `bvh_manage`. Der Endpunkt FEHLTE bis zum 17.08.2026, obwohl die
    Kontextmenüs der Kleider- und der MakeHuman-Liste ihn von acht Stellen aus
    aufriefen: vier tote Aktionen in zwei Listen, ohne Hinweis für den Benutzer.

    Nach jeder Änderung ist der Bibliotheks-Cache hinfällig — die Kennung eines
    Kleides ist sein Pfad, und der hat sich gerade geändert.
    """
    global _garment_library
    try:
        daten = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    try:
        antwort = Kleiderverwaltung.ausfuehren(daten)
    except KleiderFehler as e:
        return JsonResponse({'error': e.text}, status=e.kennzahl)
    _garment_library = None
    return JsonResponse(antwort)


@require_GET
def garment_library_rescan(request):
    """Force rescan of garment library directory."""
    katalog = Kleiderbibliothek.neu_einlesen()
    return JsonResponse({'ok': True, 'count': len(katalog.catalog)})


@require_GET
def garment_download_available(request):
    """Return available MakeHuman asset packs for download."""
    from GarmentFitter import MakeHumanDownloader
    dl = MakeHumanDownloader(str(settings.HUMANBODY_GARMENT_LIBRARY_DIR))

    packs = dl.list_available_packs()
    builtin = []
    try:
        builtin = dl.list_builtin_assets()
    except Exception:
        logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)

    return JsonResponse({
        'packs': packs,
        'builtin_assets': builtin,
    })


@csrf_exempt
@require_POST
def garment_download(request):
    """Download MakeHuman assets (pack or individual).

    JSON body:
        pack_name — download a ZIP asset pack (e.g. 'shirts01')
        asset_name — download a single built-in asset
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    from GarmentFitter import MakeHumanDownloader
    dl = MakeHumanDownloader(str(settings.HUMANBODY_GARMENT_LIBRARY_DIR))

    pack_name = body.get('pack_name', '')
    asset_name = body.get('asset_name', '')

    if pack_name:
        installed = dl.download_pack(pack_name)
        # Force rescan
        global _garment_library
        _garment_library = None
        return JsonResponse({
            'ok': True,
            'installed': installed,
            'count': len(installed),
        })
    elif asset_name:
        garment_id = dl.download_builtin_asset(asset_name)
        _garment_library = None
        return JsonResponse({
            'ok': garment_id is not None,
            'garment_id': garment_id,
        })
    else:
        return JsonResponse({'error': 'pack_name or asset_name required'}, status=400)


@csrf_exempt
@require_POST
def garment_export(request):
    """Export a fitted garment to OBJ + weights files."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    garment_id = body.get('garment_id', '')
    name = body.get('name', 'garment').strip()
    if not garment_id or not name:
        return JsonResponse({'error': 'garment_id and name required'}, status=400)

    # Sanitize name
    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    if not safe_name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    export_dir = str(settings.HUMANBODY_GARMENT_EXPORT_DIR)
    os.makedirs(export_dir, exist_ok=True)

    # Path traversal check
    target = os.path.normpath(os.path.join(export_dir, safe_name))
    if not target.startswith(os.path.normpath(export_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    return JsonResponse({
        'ok': True,
        'export_dir': target,
        'message': f'Export directory prepared: {safe_name}',
    })


@require_GET
def garment_thumbnail(request, garment_path):
    """Serve garment thumbnail image (.thumb or _diffuse.png)."""
    lib_dir = str(settings.HUMANBODY_GARMENT_LIBRARY_DIR)
    # Sanitize path to prevent traversal
    safe_path = os.path.normpath(garment_path).replace('\\', '/')
    if '..' in safe_path:
        return HttpResponseNotFound('Invalid path')

    garment_dir = os.path.join(lib_dir, safe_path)
    if not os.path.normpath(garment_dir).startswith(os.path.normpath(lib_dir)):
        return HttpResponseNotFound('Invalid path')

    if not os.path.isdir(garment_dir):
        return HttpResponseNotFound('Garment not found')

    # Try .thumb first, then _diffuse.png
    for f in sorted(os.listdir(garment_dir)):
        if f.endswith('.thumb'):
            return FileResponse(
                open(os.path.join(garment_dir, f), 'rb'),
                content_type='image/png',
            )

    for f in sorted(os.listdir(garment_dir)):
        if f.endswith('_diffuse.png'):
            return FileResponse(
                open(os.path.join(garment_dir, f), 'rb'),
                content_type='image/png',
            )

    return HttpResponseNotFound('No thumbnail')


@require_GET
def garment_texture(request, garment_id, filename):
    """Serve garment texture file (PNG) from the garment cache directory."""
    cache_dir = os.path.join(str(settings.HUMANBODY_DATA_DIR), '..', 'garment_library', '.cache')
    garment_name = garment_id.split('/')[-1] if '/' in garment_id else garment_id
    safe_name = os.path.basename(filename)
    if '..' in safe_name or '..' in garment_name:
        return HttpResponseNotFound('Invalid path')
    tex_path = os.path.join(cache_dir, garment_name, safe_name)
    if not os.path.isfile(tex_path):
        return HttpResponseNotFound('Texture not found')
    content_type = 'image/png' if safe_name.endswith('.png') else 'image/jpeg'
    return FileResponse(open(tex_path, 'rb'), content_type=content_type)
