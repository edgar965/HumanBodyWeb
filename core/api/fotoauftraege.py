# -*- coding: utf-8 -*-
"""Fotoanalyse-Auftraege verwalten: anlegen, abfragen, loeschen.

Aus core/api/foto.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `doppelcode`): neun freie
Funktionen. Zwei davon — Einzel- und Sammelloeschen — raeumten dieselben vier
Dateiarten weg, in zwei wortgleichen Bloecken; das steht jetzt einmal in
`_dateien_entfernen`. Der `sys.path`-Tanz um die Wrapper (zweimal hier, sechsmal
im Projekt) liegt in `daten/wrapperpfad.py`.

`@csrf_exempt`/`@require_POST` verlangen `@staticmethod` statt `@classmethod`:
Ein Klassenmethoden-Deskriptor schoebe der umschlossenen Funktion die Klasse
als erstes Argument unter, und der Dekorator sucht dort die Anfrage.
"""

import json
import logging
import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.wrapperpfad import Wrapperpfad
from ..dienste.bildablage import Bildablage
from ..dienste.fotoanalyse import Fotoanalyse, FotoanalyseFehler
from ..dienste.fotoausrichtung import Fotoausrichtung
from ..dienste.smplx_archiv import SmplxArchiv

logger = logging.getLogger(__name__)


class Fotoauftraege:
    """Alles, was mit einem Fotoanalyse-Auftrag geschieht."""

    #: Dateiendungen der SMPL-X-Ausgabe je Auftrag.
    SMPLX_ENDUNGEN = ('.json', '.npz')

    # ----------------------------------------------------------- Nachschlagen

    @staticmethod
    def _auftrag(job_id):
        """Der Auftrag — oder None, wenn es ihn nicht (mehr) gibt."""
        from ..models import PhotoAnalysisJob
        try:
            return PhotoAnalysisJob.objects.get(id=job_id)
        except PhotoAnalysisJob.DoesNotExist:
            return None

    @staticmethod
    def _nicht_gefunden():
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    @staticmethod
    @require_GET
    def daten(request, job_id):
        """Das gespeicherte Analyseergebnis eines Auftrags.

        Die Morph-Zuordnung wird aus den gespeicherten Betas NEU gerechnet —
        damit eine verbesserte Zuordnung auch alte Auftraege erreicht.
        """
        job = Fotoauftraege._auftrag(job_id)
        if job is None:
            return Fotoauftraege._nicht_gefunden()
        try:
            daten = json.loads(job.result_json)
        except (json.JSONDecodeError, TypeError):
            logger.exception('photo_analysis_job_data: JSONDecodeError/TypeError')
            return JsonResponse({'ok': False, 'error': 'Invalid result data'},
                                status=500)
        Fotoauftraege._morphs_nachrechnen(daten)
        return JsonResponse(Fotoauftraege._mit_adressen(daten, job))

    @staticmethod
    def _morphs_nachrechnen(daten):
        if not daten.get('betas'):
            return
        try:
            with Wrapperpfad():
                from smplest_x_wrapper import betas_to_morph_sliders
                zuordnung = betas_to_morph_sliders(
                    daten['betas'], daten.get('gender', 'female'),
                    expression=daten.get('expression'))
            daten['morphs'] = zuordnung['morphs']
            daten['meta_sliders'] = zuordnung['meta_sliders']
            daten['body_type'] = zuordnung['body_type']
        except Exception:
            # Kein `stumm gewollt`: Hier faellt der Aufruf des SMPL-Wrappers
            # aus, und die Seite zeigt danach die ALTEN Morphs — das sieht wie
            # ein Rechenfehler aus, nicht wie ein fehlendes Modul.
            logger.warning('[foto] Morph-Zuordnung aus Betas fehlgeschlagen, '
                           'gespeicherte Werte bleiben stehen', exc_info=True)

    @staticmethod
    def _mit_adressen(daten, job):
        """Die Adressen, die das Frontend zum Anzeigen braucht."""
        daten['ok'] = True
        daten['photo_url'] = '/%s' % job.photo_file if job.photo_file else None
        if daten.get('texture_path'):
            daten['texture_url'] = '/%s' % daten['texture_path']
        if daten.get('silhouette_path'):
            daten['silhouette_url'] = '/%s' % daten['silhouette_path']
        if job.result_image:
            daten['result_image_url'] = '/%s' % job.result_image
        return daten

    # ------------------------------------------------------------ Bildsichern

    @staticmethod
    @csrf_exempt
    @require_POST
    def bild_sichern(request, job_id):
        """Ein im Browser gerendertes 3D-Bild beim Auftrag ablegen."""
        job = Fotoauftraege._auftrag(job_id)
        if job is None:
            return Fotoauftraege._nicht_gefunden()
        try:
            rumpf = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'},
                                status=400)
        roh = Bildablage.bytes_aus_dataurl(rumpf.get('image', ''))
        if roh is None:
            return JsonResponse({'ok': False, 'error': 'Invalid base64'},
                                status=400)
        if not roh:
            return JsonResponse({'ok': False, 'error': 'No image data'},
                                status=400)
        relativ = Bildablage('screenshots').sichern(job_id, roh)
        job.result_image = relativ
        job.save(update_fields=['result_image'])
        return JsonResponse({'ok': True, 'path': '/%s' % relativ})

    # ---------------------------------------------------------------- Loeschen

    @staticmethod
    def _dateien_entfernen(job):
        """Foto, Ergebnisbild und die SMPL-X-Ausgabe EINES Auftrags.

        Stand bis zum 27.08.2026 zweimal wortgleich da — einmal fuer das
        Einzel-, einmal fuer das Sammelloeschen. Zwei Kopien derselben
        Aufraeumliste vergessen frueher oder spaeter verschiedene Dateien.
        """
        basis = str(settings.BASE_DIR)
        foto = os.path.join(basis, job.photo_file)
        if os.path.isfile(foto):
            os.remove(foto)
        if job.result_image:
            bild = os.path.join(basis, job.result_image)
            if os.path.isfile(bild):
                os.remove(bild)
        smplx = os.path.join(basis, '..', 'HumanBody', 'data', 'photoTo3D',
                             'SMPLX')
        for endung in Fotoauftraege.SMPLX_ENDUNGEN:
            pfad = os.path.join(smplx, '%s%s' % (job.id, endung))
            if os.path.isfile(pfad):
                os.remove(pfad)

    @staticmethod
    @csrf_exempt
    @require_POST
    def loeschen(request, job_id):
        """Einen Fotoanalyse-Auftrag samt Dateien loeschen."""
        job = Fotoauftraege._auftrag(job_id)
        if job is None:
            return Fotoauftraege._nicht_gefunden()
        Fotoauftraege._dateien_entfernen(job)
        job.delete()
        return redirect('photo_analysis_jobs')

    @staticmethod
    @csrf_exempt
    @require_POST
    def mehrere_loeschen(request):
        """Mehrere Fotoanalyse-Auftraege auf einmal loeschen."""
        try:
            kennungen = json.loads(request.body).get('ids', [])
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'},
                                status=400)
        if not kennungen:
            return JsonResponse({'ok': False, 'error': 'No job IDs provided'},
                                status=400)
        geloescht = 0
        for kennung in kennungen:
            job = Fotoauftraege._auftrag(kennung)
            # stumm gewollt: Ein Auftrag, den ein anderer Tab schon geloescht
            # hat, ist genau das gewuenschte Ergebnis — die Zahl unten nennt
            # die echte Menge.
            if job is None:
                continue
            Fotoauftraege._dateien_entfernen(job)
            job.delete()
            geloescht += 1
        return JsonResponse({'ok': True, 'deleted': geloescht})

    @staticmethod
    def erneut_analysieren(request, job_id):
        """Zur Foto-zu-3D-Seite mit vorgeladenem Foto des Auftrags."""
        return redirect('/humanbody/photo-to-3d/?job=%s' % job_id)

    # ---------------------------------------------------------------- Analyse

    @staticmethod
    @csrf_exempt
    @require_POST
    def analysieren(request):
        """Ein hochgeladenes Foto zu Koerperparametern machen.

        Bis zum Umbau am 15.08.2026 standen hier 205 Zeilen: Datei ablegen,
        Backend rufen, ein Dict ueber 150 Zeilen wachsen lassen, Auftrag
        anlegen, Netz und Parameter archivieren, Ausrichtung rechnen. Das liegt
        jetzt in Fotoanalyse, SmplxArchiv und der Datenklasse Analyseergebnis.
        """
        hochgeladen = request.FILES.get('photo')
        if not hochgeladen:
            return JsonResponse({'ok': False, 'error': 'No photo uploaded'},
                                status=400)
        try:
            ergebnis, pfad, _name = Fotoanalyse.ausfuehren(
                hochgeladen, request.POST.get('backend'))
        except FotoanalyseFehler as fehler:
            return JsonResponse({'ok': False, 'error': str(fehler)},
                                status=fehler.status)
        job = Fotoauftraege._anlegen(ergebnis, hochgeladen.name)
        if job is not None:
            ergebnis.job_id = job.id
            SmplxArchiv.ablegen(ergebnis, job, hochgeladen.name)
            Fotoauftraege._ausrichtung_nachtragen(ergebnis, job, pfad)
        return JsonResponse(ergebnis.als_dict())

    @staticmethod
    def _anlegen(ergebnis, dateiname):
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
        except Exception:                                         # noqa: BLE001
            logger.error('Fotoauftrag nicht speicherbar', exc_info=True)
            return None

    @staticmethod
    def _ausrichtung_nachtragen(ergebnis, job, foto_pfad):
        """Automatische Ausrichtung rechnen und beim Auftrag hinterlegen."""
        if not ergebnis.hat_kamera:
            return
        try:
            ausrichtung = Fotoausrichtung.automatisch(
                ergebnis.kameradaten, ergebnis.betas, ergebnis.geschlecht,
                photo_path=foto_pfad)
        except Exception as fehler:                               # noqa: BLE001
            logger.error('Automatische Ausrichtung fehlgeschlagen: %s', fehler)
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

    @staticmethod
    @require_GET
    def backendzustand(request):
        """Welche Analyse-Backends stehen bereit?"""
        try:
            with Wrapperpfad():
                from photo_analyzer import get_all_status
                backends = get_all_status()
        except ImportError:
            logger.warning('photo_analyzer nicht importierbar — keine Backends',
                           exc_info=True)
            backends = {}
        return JsonResponse({'backends': backends})
