# -*- coding: utf-8 -*-
"""Meshfigurendpunkte — Reiter „Mesh to 3D" auf „Modell aus Dateien": Netz → Genesis-9-Figur (27.09.2026).

GET  /modell-aus-dateien/meshfigur/<kennung>/        Auftragsseite (Fortschritt, 3D, Vergleich, Regler)
POST /api/meshfigur/anlegen/                         name, optionen (JSON), netz[] (Netz + OBJ-Beilagen)
GET  /api/meshfigur/katalog/                         Optionen
GET  /api/meshfigur/<id>/zustand/                    Status, Fortschritt, Ergebnis, Stellung
POST /api/meshfigur/<id>/starten/                    {optionen?, ab?} → Arbeitsprozess
POST /api/meshfigur/<id>/anhalten/
POST /api/meshfigur/<id>/loeschen/, /api/meshfigur/loeschen/  (mehrere: {ids})
GET  /api/meshfigur/<id>/datei/<ordner>/<name>       Netz (eingang), Bilder und Kacheln (ergebnis)
"""

import json
import logging
import mimetypes

from asgiref.sync import sync_to_async
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from ..daten.auftragskennung import Auftragskennung
from ..daten.meshfigurablage import Meshfigurablage
from ..dienste.meshfigurarbeiter import Meshfigurarbeiter
from ..dienste.meshfiguroptionen import Meshfiguroptionen
from ..models import Meshfigurauftrag

logger = logging.getLogger('core')

__all__ = ['Meshfigurendpunkte']

mimetypes.add_type('model/gltf-binary', '.glb')
mimetypes.add_type('model/obj', '.obj')


class Meshfigurendpunkte:
    SCHRITTE = ('erkennung', 'kalibrierung', 'koerper', 'gesicht', 'rest', 'textur', 'vorschau', 'speichern')

    @staticmethod
    def seite(request, kennung):
        job = get_object_or_404(Meshfigurauftrag, kennung=kennung)
        return render(
            request,
            'meshfigur_auftrag.html',
            {
                'job': job,
                'katalog_json': json.dumps(Meshfiguroptionen.katalog(), ensure_ascii=False),
                'zustand_json': json.dumps(Meshfigurendpunkte._zustand(job), ensure_ascii=False, default=str),
            },
        )

    @staticmethod
    def _json_feld(request, name, vorgabe):
        try:
            wert = json.loads(request.POST.get(name) or 'null')
        except ValueError:
            return vorgabe
        return vorgabe if wert is None else wert

    @staticmethod
    @require_POST
    def anlegen(request):
        name = (request.POST.get('name') or '').strip()[:200]
        dateien = request.FILES.getlist('netz')
        netze = [f for f in dateien if Meshfigurablage.ist_netz(f.name)]
        if not name:
            return JsonResponse({'error': 'Name fehlt'}, status=400)
        if len(netze) != 1:
            return JsonResponse(
                {'error': 'Genau ein Netz (GLB, GLTF, OBJ, PLY, STL, OFF) — gefunden: %d' % len(netze)},
                status=400,
            )
        kennung = Auftragskennung.frei(
            timezone.now(), lambda k: Meshfigurauftrag.objects.filter(kennung=k).exists()
        )
        ablage = Meshfigurablage(kennung)
        netz = ablage.ablegen(netze[0])
        beilagen = [ablage.ablegen(f) for f in dateien if Meshfigurablage.ist_beilage(f.name)]
        eingang = {
            'datei': netz,
            'original': netze[0].name,
            'bytes': int(netze[0].size),
            'beilagen': beilagen,
        }
        job = Meshfigurauftrag.objects.create(
            kennung=kennung,
            name=name,
            eingang=eingang,
            optionen=Meshfiguroptionen.pruefen(Meshfigurendpunkte._json_feld(request, 'optionen', {})),
        )
        if request.POST.get('starten', '1') == '1':
            Meshfigurarbeiter.starten(job)
        return JsonResponse(
            {
                'ok': True,
                'id': str(job.id),
                'kennung': kennung,
                'url': reverse('meshfigur_auftrag', args=[kennung]),
            }
        )

    @staticmethod
    @require_GET
    def katalog(request):
        return JsonResponse(Meshfiguroptionen.katalog())

    # --------------------------------------------------------------- Zustand

    @staticmethod
    def _zustand(job):
        from ..dienste.meshfigurspeichern import Meshfigurspeichern

        return {
            'id': str(job.id),
            'kennung': job.kennung,
            'name': job.name,
            'status': job.status,
            'schritt': job.schritt,
            'progress': job.progress,
            'progress_detail': job.progress_detail,
            'error': job.error_message,
            'optionen': Meshfiguroptionen.pruefen(job.optionen),
            'eingang': job.eingang,
            'ergebnis': job.ergebnis,
            'stellung': job.stellung(),
            'modell': job.modell,
            'laeuft': job.laeuft,
            'schritte': list(Meshfigurendpunkte.SCHRITTE),
            'exportordner': str(Meshfigurspeichern.zielordner_fuer(job)),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'finished_at': job.finished_at.isoformat() if job.finished_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
        }

    @staticmethod
    @require_GET
    async def zustand(request, job_id):
        # ASYNC wie `Meshendpunkte.zustand`: die Seite fragt jede Sekunde.
        daten = await sync_to_async(Meshfigurendpunkte._zustand_rechnen, thread_sensitive=False)(job_id)
        return JsonResponse(daten, json_dumps_params={'default': str})

    @staticmethod
    def _zustand_rechnen(job_id):
        job = get_object_or_404(Meshfigurauftrag, pk=job_id)
        if job.laeuft and not Meshfigurarbeiter.lebt(job):
            job.refresh_from_db()
            if job.laeuft:
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess lebt nicht mehr (auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        return Meshfigurendpunkte._zustand(job)

    # ------------------------------------------------------------------ Lauf

    @staticmethod
    def _rumpf(request):
        try:
            return json.loads(request.body or b'{}')
        except ValueError:
            return {}

    @staticmethod
    @require_POST
    def starten(request, job_id):
        job = get_object_or_404(Meshfigurauftrag, pk=job_id)
        if job.laeuft and Meshfigurarbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft schon'}, status=409)
        rumpf = Meshfigurendpunkte._rumpf(request)
        if isinstance(rumpf.get('optionen'), dict):
            job.optionen = Meshfiguroptionen.pruefen({**(job.optionen or {}), **rumpf['optionen']})
            job.save(update_fields=['optionen', 'updated_at'])
        ab = rumpf.get('ab') if rumpf.get('ab') in Meshfigurendpunkte.SCHRITTE else None
        return JsonResponse({'ok': True, 'pid': Meshfigurarbeiter.starten(job, ab=ab)})

    @staticmethod
    @require_POST
    def anhalten(request, job_id):
        Meshfigurarbeiter.anhalten(get_object_or_404(Meshfigurauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    # --------------------------------------------------------------- Löschen

    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        Meshfigurendpunkte._entfernen(get_object_or_404(Meshfigurauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def mehrere_loeschen(request):
        ids = Meshfigurendpunkte._rumpf(request).get('ids') or []
        n = 0
        for job in Meshfigurauftrag.objects.filter(pk__in=ids):
            Meshfigurendpunkte._entfernen(job)
            n += 1
        return JsonResponse({'ok': True, 'geloescht': n})

    @staticmethod
    def _entfernen(job):
        """Auftragsordner und Eintrag — das gespeicherte Modell und die Ablage unter
        `output/Export/MeshTo3D` bleiben: sie gehören dem Nutzer, nicht dem Auftrag."""
        if job.laeuft:
            Meshfigurarbeiter.anhalten(job)
        Meshfigurablage(job.kennung).loeschen()
        job.delete()

    # --------------------------------------------------------------- Dateien

    @staticmethod
    @require_GET
    def datei(request, job_id, ordner, name):
        job = get_object_or_404(Meshfigurauftrag, pk=job_id)
        try:
            pfad = Meshfigurablage(job.kennung).datei(ordner, name)
        except ValueError:
            raise Http404('Pfad') from None
        if not pfad.is_file():
            raise Http404('Datei %s' % name)
        return FileResponse(
            open(pfad, 'rb'),
            as_attachment=request.GET.get('laden') == '1',
            filename=pfad.name,
            content_type=mimetypes.guess_type(pfad.name)[0] or 'application/octet-stream',
        )
