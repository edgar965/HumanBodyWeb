# -*- coding: utf-8 -*-
"""Fotoanalyse-Auftraege verwalten: anlegen, abfragen, loeschen.

Aus core/api/foto.py herausgeloest (Umbau 16.08.2026).
"""

from ..dienste.fotoanalyse import Fotoanalyse, FotoanalyseFehler
from ..dienste.fotoausrichtung import Fotoausrichtung
from ..dienste.smplx_archiv import SmplxArchiv
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import os


import logging

logger = logging.getLogger(__name__)


@require_GET
def photo_analysis_job_data(request, job_id):
    """Return saved analysis result JSON for a specific job.

    Re-computes morph mapping from stored betas for latest mapping quality.
    """
    from ..models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)
    try:
        data = json.loads(job.result_json)
    except (json.JSONDecodeError, TypeError):
        logger.exception('photo_analysis_job_data: JSONDecodeError/TypeError')
        return JsonResponse({'ok': False, 'error': 'Invalid result data'}, status=500)

    # Re-compute morph mapping from stored betas for latest mapping quality
    if data.get('betas'):
        import sys
        wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
        sys.path.insert(0, wrappers_dir)
        try:
            from smplest_x_wrapper import betas_to_morph_sliders
            mapping = betas_to_morph_sliders(
                data['betas'], data.get('gender', 'female'),
                expression=data.get('expression'))
            data['morphs'] = mapping['morphs']
            data['meta_sliders'] = mapping['meta_sliders']
            data['body_type'] = mapping['body_type']
        except Exception:
            # Kein `stumm gewollt`: Hier faellt der Aufruf des SMPL-Wrappers
            # aus, und die Seite zeigt danach die ALTEN Morphs — das sieht wie
            # ein Rechenfehler aus, nicht wie ein fehlendes Modul.
            logger.warning('[foto] Morph-Zuordnung aus Betas fehlgeschlagen, '
                           'gespeicherte Werte bleiben stehen', exc_info=True)
        finally:
            if wrappers_dir in sys.path:
                sys.path.remove(wrappers_dir)

    # Add convenient URLs for frontend
    data['ok'] = True
    data['photo_url'] = f'/{job.photo_file}' if job.photo_file else None
    if data.get('texture_path'):
        data['texture_url'] = f'/{data["texture_path"]}'
    if data.get('silhouette_path'):
        data['silhouette_url'] = f'/{data["silhouette_path"]}'
    if job.result_image:
        data['result_image_url'] = f'/{job.result_image}'

    return JsonResponse(data)


@csrf_exempt
@require_POST
def photo_analysis_save_screenshot(request, job_id):
    """Save a rendered 3D screenshot for a photo analysis job."""
    from ..models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    import base64
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    img_data = body.get('image', '')
    if not img_data:
        return JsonResponse({'ok': False, 'error': 'No image data'}, status=400)

    # Strip data URL prefix (e.g. "data:image/jpeg;base64,...")
    if ',' in img_data:
        img_data = img_data.split(',', 1)[1]

    try:
        raw = base64.b64decode(img_data)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid base64'}, status=400)

    # Save as JPEG
    screenshot_dir = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis', 'screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)
    fname = f'{job_id}.jpg'
    fpath = os.path.join(screenshot_dir, fname)
    with open(fpath, 'wb') as f:
        f.write(raw)

    rel_path = f'media/photo_analysis/screenshots/{fname}'
    job.result_image = rel_path
    job.save(update_fields=['result_image'])
    return JsonResponse({'ok': True, 'path': f'/{rel_path}'})


def photo_analysis_reprocess(request, job_id):
    """Redirect to photo-to-3d page with the job's photo pre-loaded for re-analysis."""
    from django.shortcuts import redirect
    return redirect(f'/humanbody/photo-to-3d/?job={job_id}')


@csrf_exempt
@require_POST
def photo_analysis_delete(request, job_id):
    """Delete a photo analysis job."""
    from ..models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)
    # Delete photo file
    photo_path = os.path.join(str(settings.BASE_DIR), job.photo_file)
    if os.path.isfile(photo_path):
        os.remove(photo_path)
    # Delete result screenshot
    if job.result_image:
        img_path = os.path.join(str(settings.BASE_DIR), job.result_image)
        if os.path.isfile(img_path):
            os.remove(img_path)
    # Delete SMPL-X output files
    smplx_dir = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody',
                             'data', 'photoTo3D', 'SMPLX')
    for ext in ('.json', '.npz'):
        p = os.path.join(smplx_dir, f'{job.id}{ext}')
        if os.path.isfile(p):
            os.remove(p)
    job.delete()
    from django.shortcuts import redirect
    return redirect('photo_analysis_jobs')


@csrf_exempt
@require_POST
def photo_analysis_bulk_delete(request):
    """Delete multiple photo analysis jobs at once."""
    from ..models import PhotoAnalysisJob
    try:
        data = json.loads(request.body)
        job_ids = data.get('ids', [])
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    if not job_ids:
        return JsonResponse({'ok': False, 'error': 'No job IDs provided'}, status=400)

    deleted = 0
    for jid in job_ids:
        try:
            job = PhotoAnalysisJob.objects.get(id=jid)
            photo_path = os.path.join(str(settings.BASE_DIR), job.photo_file)
            if os.path.isfile(photo_path):
                os.remove(photo_path)
            if job.result_image:
                img_path = os.path.join(str(settings.BASE_DIR), job.result_image)
                if os.path.isfile(img_path):
                    os.remove(img_path)
            # Delete SMPL-X output files
            smplx_dir = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody',
                                     'data', 'photoTo3D', 'SMPLX')
            for ext in ('.json', '.npz'):
                p = os.path.join(smplx_dir, f'{job.id}{ext}')
                if os.path.isfile(p):
                    os.remove(p)
            job.delete()
            deleted += 1
        # stumm gewollt: Massenloeschen ueber eine Liste von Kennungen. Ein
        # Auftrag, den ein anderer Tab schon geloescht hat, ist genau das
        # gewuenschte Ergebnis — die Zaehlung unten nennt die echte Zahl.
        except PhotoAnalysisJob.DoesNotExist:
            continue
    return JsonResponse({'ok': True, 'deleted': deleted})


@csrf_exempt
@require_POST
def analyze_photo(request):
    """Ein hochgeladenes Foto zu Koerperparametern machen.

    Bis zum Umbau am 15.08.2026 standen hier 205 Zeilen: Datei ablegen, Backend
    rufen, ein Dict ueber 150 Zeilen wachsen lassen, Auftrag anlegen, Netz und
    Parameter archivieren, Ausrichtung rechnen. Das liegt jetzt in Fotoanalyse,
    SmplxArchiv und der Datenklasse Analyseergebnis.
    """
    hochgeladen = request.FILES.get('photo')
    if not hochgeladen:
        return JsonResponse({'ok': False, 'error': 'No photo uploaded'}, status=400)

    try:
        ergebnis, pfad, _name = Fotoanalyse.ausfuehren(
            hochgeladen, request.POST.get('backend'))
    except FotoanalyseFehler as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=e.status)

    job = _analyse_auftrag_anlegen(ergebnis, hochgeladen.name)
    if job is not None:
        ergebnis.job_id = job.id
        SmplxArchiv.ablegen(ergebnis, job, hochgeladen.name)
        _ausrichtung_nachtragen(ergebnis, job, pfad)
    return JsonResponse(ergebnis.als_dict())


def _analyse_auftrag_anlegen(ergebnis, dateiname):
    """Auftrag in der Datenbank — ohne ihn geht die Antwort trotzdem raus."""
    try:
        from ..models import PhotoAnalysisJob
        return PhotoAnalysisJob.objects.create(
            original_filename=dateiname,
            photo_file=ergebnis.foto_url.lstrip('/'),
            backend=ergebnis.backend,
            gender=ergebnis.geschlecht,
            body_type=ergebnis.koerpertyp,
            result_json=json.dumps(ergebnis.als_dict(), default=str),
            duration_seconds=ergebnis.dauer,
        )
    except Exception:                                             # noqa: BLE001
        logger.error('Fotoauftrag nicht speicherbar', exc_info=True)
        return None


def _ausrichtung_nachtragen(ergebnis, job, foto_pfad):
    """Automatische Ausrichtung rechnen und beim Auftrag hinterlegen."""
    if not ergebnis.hat_kamera:
        return
    try:
        ausrichtung = Fotoausrichtung.automatisch(
            ergebnis.kameradaten, ergebnis.betas, ergebnis.geschlecht,
            photo_path=foto_pfad)
    except Exception as e:                                        # noqa: BLE001
        logger.error('Automatische Ausrichtung fehlgeschlagen: %s', e)
        return
    if not ausrichtung:
        return
    ergebnis.ausrichtung = ausrichtung
    job.result_json = json.dumps(ergebnis.als_dict(), default=str)
    job.save(update_fields=['result_json'])
    logger.info('Ausrichtung fuer %s: Massstab %.3f, Mitte (%.1f, %.1f)',
                job.id, ausrichtung['body_transform']['scale'],
                ausrichtung['body_transform']['center_x'],
                ausrichtung['body_transform']['center_y'])


@require_GET
def analyze_photo_status(request):
    """Return status of all photo analysis backends."""
    import sys
    wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
    sys.path.insert(0, wrappers_dir)
    try:
        from photo_analyzer import get_all_status
        backends = get_all_status()
    except ImportError:
        logger.warning('photo_analyzer nicht importierbar — keine Backends', exc_info=True)
        backends = {}
    finally:
        if wrappers_dir in sys.path:
            sys.path.remove(wrappers_dir)

    return JsonResponse({'backends': backends})
