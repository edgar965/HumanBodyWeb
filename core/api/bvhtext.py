# -*- coding: utf-8 -*-
"""BVH als Text lesen und schreiben, glaetten, Effekte anwenden.

Aus core/api/retarget.py herausgeloest (Umbau 16.08.2026): Der Texteditor der
Bibliothek und die beiden Effekt-Endpunkte sind eine eigene Aufgabe — sie
arbeiten auf der Datei, nicht auf dem Retargeting.
"""

from ..atomic_write import AtomarSchreiber
from ..dienste.bvh_datei import BvhDatei
from ..dienste.bvhablage import Bvhablage
from ..projekt_temp import ProjektTemp
from ..safe_paths import SafePath, PfadAbgelehnt
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..dienste.retargetdaten import Retargetdaten
import json
import logging
import os


logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def retarget_bvh_text(request):
    """Server-side retarget from raw BVH text content.

    POST /api/character/retarget-bvh-text/
    Body JSON: { bvh_text: "HIERARCHY\\nROOT ...", body_height: 1.68,
                 foot_correction: false, format: null }
    """
    import tempfile

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    bvh_text = data.get('bvh_text', '')
    if not bvh_text:
        return JsonResponse({'error': 'bvh_text is required'}, status=400)

    body_height = float(data.get('body_height', 1.68))
    fmt = data.get('format', None)
    foot_correction = bool(data.get('foot_correction', False))

    # Write to temp file for parse_bvh (expects file path)
    # Ins Projekt statt nach System-Temp (Projektregel, siehe ProjektTemp).
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bvh', delete=False,
                                      dir=str(ProjektTemp.verzeichnis()),
                                      encoding='utf-8') as tmp:
        tmp.write(bvh_text)
        tmp_path = tmp.name

    try:
        return JsonResponse(Retargetdaten(tmp_path, body_height, fmt,
                                          foot_correction).holen())
    finally:
        os.unlink(tmp_path)


@csrf_exempt
@require_POST
def save_bvh_text(request):
    """Save modified BVH text to a file on disk.

    POST /api/character/save-bvh-text/
    Body JSON: { path: "/abs/path/to/file.bvh", bvh_text: "HIERARCHY\\n..." }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    save_path = data.get('path', '')
    category = data.get('category', '')
    name = data.get('name', '')
    bvh_text = data.get('bvh_text', '')
    if not bvh_text:
        return JsonResponse({'error': 'bvh_text required'}, status=400)

    from pathlib import Path

    # Resolve path: either absolute path, or category/name from library
    if not save_path and category and name:
        bvh_root = Path(str(settings.HUMANBODY_BVH_DIR)).parent
        save_path = str(bvh_root / category / f'{name}.bvh')

    if not save_path:
        return JsonResponse({'error': 'path or category+name required'}, status=400)

    # Pfadprüfung über SafePath. Vorher stand hier ein String-Präfix-Vergleich
    # (`str(sp).startswith(str(media))`) — den besteht auch `<media>_evil\x.bvh`,
    # weil "media_evil" mit "media" beginnt. SafePath vergleicht Pfade, nicht
    # Zeichenketten (`is_relative_to`, case-normalisiert).
    try:
        sp = SafePath.fuer_bvh().pruefe(save_path)
    except PfadAbgelehnt as e:
        return JsonResponse({'error': str(e)}, status=403)

    try:
        # Zeilenenden auf \n normalisieren (BVH-Dateien dürfen kein \r\n haben);
        # AtomarSchreiber schreibt mit newline='\n' und ersetzt die Datei erst,
        # wenn sie vollständig auf der Platte liegt.
        bvh_text = bvh_text.replace('\r\n', '\n').replace('\r', '\n')
        AtomarSchreiber.text_schreiben(sp, bvh_text, zeilenende='\n')
        return JsonResponse({'ok': True, 'path': str(sp)})
    except Exception as e:                                       # noqa: BLE001
        logging.getLogger('core').exception('save_bvh_text fehlgeschlagen: %s', sp)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def smooth_bvh(request):
    """Eine BVH-Datei glaetten und ueberschreiben.

    POST /api/retarget/smooth-bvh/  { category, name, sigma }
    """
    return _bvh_bearbeiten(request, nur_glaetten=True)


@csrf_exempt
@require_POST
def save_bvh_effects(request):
    """Glaettung und festgehaltene Wurzel anwenden und speichern.

    POST /api/retarget/save-bvh-effects/  { category, name, sigma?, fixed_radius? }
    """
    return _bvh_bearbeiten(request, nur_glaetten=False)


def _bvh_bearbeiten(request, nur_glaetten):
    """Gemeinsamer Weg beider Endpunkte (Umbau 15.08.2026).

    Vorher waren das zwei Funktionen mit zusammen 300 Zeilen, die sich zu neun
    Zehnteln glichen — inklusive der Pfadpruefung, die am 13.08.2026 in BEIDEN
    nachgezogen werden musste."""
    try:
        daten = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    kategorie = daten.get('category', '')
    name = daten.get('name', '')
    if not kategorie or not name:
        return JsonResponse({'error': 'category + name required'}, status=400)

    # Die Pfadpruefung ist der Grund, warum diese beiden Endpunkte am
    # 13.08.2026 auffielen: `category='../../..'` landete in den Produktivdaten,
    # und am Ende wird die Datei UEBERSCHRIEBEN.
    pfad = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / kategorie / ('%s.bvh' % name))
    if pfad is None:
        return JsonResponse({'error': 'Pfad liegt ausserhalb der BVH-Bibliothek'},
                            status=403)
    if not pfad.is_file():
        # Kein voller Pfad in der Antwort — das waere eine Auskunft ueber das
        # Dateisystem. Er steht im Protokoll.
        logger.info('BVH nicht gefunden: %s', pfad)
        return JsonResponse({'error': 'BVH not found'}, status=404)

    sigma = daten.get('sigma', 2.0) if nur_glaetten else daten.get('sigma')
    radius = None if nur_glaetten else daten.get('fixed_radius')
    try:
        bvh = BvhDatei(pfad)
        if sigma:
            bvh.glaetten(sigma)
        if radius:
            bvh.wurzel_festhalten(radius)
        if not bvh.angewandt:
            return JsonResponse({'error': 'No effects to apply'}, status=400)
        frames = bvh.speichern()
    except Exception as e:                                        # noqa: BLE001
        logger.exception('BVH-Bearbeitung fehlgeschlagen: %s/%s', kategorie, name)
        return JsonResponse({'error': str(e)}, status=500)

    logger.info('BVH bearbeitet: %s/%s — %s, %d Frames', kategorie, name,
                ', '.join(bvh.angewandt), frames)
    antwort = {'ok': True, 'frames': frames}
    if not nur_glaetten:
        antwort['applied'] = bvh.angewandt
    return JsonResponse(antwort)
