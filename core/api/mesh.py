# -*- coding: utf-8 -*-
"""Meshendpunkte — Reiter „Mesh" auf „Modell aus Dateien": Fotos → Netz (26.09.2026).

GET  /modell-aus-dateien/mesh/<kennung>/            Auftragsseite (Fortschritt, 3D, Downloads)
POST /api/mesh/anlegen/                             name, optionen (JSON), rollen (JSON), bilder[]
GET  /api/mesh/katalog/                             Optionen mit Verfügbarkeit je Formmodell
GET  /api/mesh/<id>/zustand/                        Status, Fortschritt, Bilder, Ergebnis
POST /api/mesh/<id>/starten/                        {optionen?, ab?} → Arbeitsprozess
POST /api/mesh/<id>/anhalten/
POST /api/mesh/<id>/bilder/                         weitere Fotos
POST /api/mesh/<id>/rolle/<datei>/                  {rolle} je Foto
POST /api/mesh/<id>/gewicht/<datei>/                {gewicht, bereich?} je Foto (26.09.2026 abends)
POST /api/mesh/<id>/retexturieren/                  nur Textur neu (Form aus Cache, `ab='textur'`)
POST /api/mesh/<id>/loeschen/, /api/mesh/loeschen/  (mehrere: {ids})
GET  /api/mesh/<id>/datei/<ordner>/<name>           Fotos, Freisteller, GLB/OBJ/PLY, Vorschauen
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
from ..daten.meshablage import Meshablage
from ..dienste.mesharbeiter import Mesharbeiter
from ..dienste.meshoptionen import Meshoptionen
from ..models import Meshauftrag

logger = logging.getLogger('core')

__all__ = ['Meshendpunkte']

#: GLB hat keinen Eintrag in Pythons Tabelle — der Browser (GLTFLoader) nimmt aber jeden Typ.
mimetypes.add_type('model/gltf-binary', '.glb')
mimetypes.add_type('model/obj', '.obj')


class Meshendpunkte:
    # ---------------------------------------------------------------- Seite

    @staticmethod
    def seite(request, kennung):
        job = get_object_or_404(Meshauftrag, kennung=kennung)
        return render(request, 'mesh_auftrag.html', {
            'job': job,
            'katalog_json': json.dumps(Meshoptionen.katalog(), ensure_ascii=False),
            'zustand_json': json.dumps(Meshendpunkte._zustand(job), ensure_ascii=False),
        })

    # --------------------------------------------------------------- Anlegen

    @staticmethod
    def _json_feld(request, name, vorgabe):
        """Ein JSON-Formularfeld — der Rumpf ist nach `request.FILES` nicht mehr lesbar."""
        try:
            wert = json.loads(request.POST.get(name) or 'null')
        except ValueError:
            return vorgabe
        return vorgabe if wert is None else wert

    @staticmethod
    @require_POST
    def anlegen(request):
        name = (request.POST.get('name') or '').strip()[:200]
        dateien = [f for f in request.FILES.getlist('bilder') if Meshablage.ist_bild(f.name)]
        if not name:
            return JsonResponse({'error': 'Name fehlt'}, status=400)
        if not dateien:
            return JsonResponse({'error': 'Keine Bilder (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        kennung = Auftragskennung.frei(timezone.now(), lambda k: Meshauftrag.objects.filter(kennung=k).exists())
        rollen = Meshendpunkte._json_feld(request, 'rollen', {})
        ablage = Meshablage(kennung)
        bilder = []
        for f in dateien:
            gespeichert = ablage.eingang_ablegen(f)
            rolle = rollen.get(f.name) if isinstance(rollen, dict) else None
            bilder.append({'datei': gespeichert, 'original': f.name, 'gewicht': 100, 'bereich': None,
                           'rolle': Meshoptionen.rolle_pruefen(rolle)})
        job = Meshauftrag.objects.create(kennung=kennung, name=name, bilder=bilder,
                                         optionen=Meshoptionen.pruefen(Meshendpunkte._json_feld(request, 'optionen', {})))
        if request.POST.get('starten', '1') == '1':
            Mesharbeiter.starten(job)
        return JsonResponse({'ok': True, 'id': str(job.id), 'kennung': kennung,
                             'url': reverse('mesh_auftrag', args=[kennung]), 'bilder': len(bilder)})

    @staticmethod
    @require_GET
    def katalog(request):
        return JsonResponse(Meshoptionen.katalog())

    # --------------------------------------------------------------- Zustand

    @staticmethod
    def _zustand(job):
        return {
            'id': str(job.id), 'kennung': job.kennung, 'name': job.name, 'status': job.status,
            'schritt': job.schritt, 'progress': job.progress, 'progress_detail': job.progress_detail,
            'error': job.error_message, 'optionen': Meshoptionen.pruefen(job.optionen), 'bilder': job.bilder,
            'ergebnis': job.ergebnis, 'laeuft': job.laeuft,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'finished_at': job.finished_at.isoformat() if job.finished_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
        }

    @staticmethod
    @require_GET
    async def zustand(request, job_id):
        # ASYNC wie `Bildmodellendpunkte.zustand`: die Seite fragt jede Sekunde; synchron
        # stünde jede Anfrage im EINEN geteilten Faden von Daphne (23.09.2026).
        daten = await sync_to_async(Meshendpunkte._zustand_rechnen, thread_sensitive=False)(job_id)
        return JsonResponse(daten)

    @staticmethod
    def _zustand_rechnen(job_id):
        job = get_object_or_404(Meshauftrag, pk=job_id)
        if job.laeuft and not Mesharbeiter.lebt(job):
            job.refresh_from_db()
            if job.laeuft:
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess lebt nicht mehr (auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        return Meshendpunkte._zustand(job)

    # ---------------------------------------------------------------- Lauf

    @staticmethod
    def _rumpf(request):
        try:
            return json.loads(request.body or b'{}')
        except ValueError:
            return {}

    @staticmethod
    @require_POST
    def starten(request, job_id):
        job = get_object_or_404(Meshauftrag, pk=job_id)
        if job.laeuft and Mesharbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft schon'}, status=409)
        rumpf = Meshendpunkte._rumpf(request)
        if isinstance(rumpf.get('optionen'), dict):
            job.optionen = Meshoptionen.pruefen({**(job.optionen or {}), **rumpf['optionen']})
            job.save(update_fields=['optionen', 'updated_at'])
        ab = rumpf.get('ab') if rumpf.get('ab') in ('vorbereitung', 'form', 'gesicht', 'textur', 'export') else None
        return JsonResponse({'ok': True, 'pid': Mesharbeiter.starten(job, ab=ab)})

    @staticmethod
    @require_POST
    def anhalten(request, job_id):
        Mesharbeiter.anhalten(get_object_or_404(Meshauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    # --------------------------------------------------------------- Bilder

    @staticmethod
    @require_POST
    def bilder(request, job_id):
        job = get_object_or_404(Meshauftrag, pk=job_id)
        ablage = Meshablage(job.kennung)
        neu = []
        for f in request.FILES.getlist('bilder'):
            if Meshablage.ist_bild(f.name):
                neu.append({'datei': ablage.eingang_ablegen(f), 'original': f.name, 'rolle': 'auto',
                           'gewicht': 100, 'bereich': None})
        job.bilder = list(job.bilder or []) + neu
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'neu': len(neu), 'bilder': job.bilder})

    @staticmethod
    @require_POST
    def rolle(request, job_id, datei):
        job = get_object_or_404(Meshauftrag, pk=job_id)
        eintrag = job.bild(datei)
        if eintrag is None:
            raise Http404('Kein Bild %s' % datei)
        eintrag['rolle'] = Meshoptionen.rolle_pruefen(Meshendpunkte._rumpf(request).get('rolle'))
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'bild': eintrag})

    @staticmethod
    @require_POST
    def gewicht(request, job_id, datei):
        """Fotogewicht (0..100) und optionaler Bereichsausschnitt — wirkt erst nach
        `retexturieren`/einem neuen Lauf, hier nur Ablage (wie `rolle`)."""
        job = get_object_or_404(Meshauftrag, pk=job_id)
        eintrag = job.bild(datei)
        if eintrag is None:
            raise Http404('Kein Bild %s' % datei)
        rumpf = Meshendpunkte._rumpf(request)
        eintrag['gewicht'] = Meshoptionen.gewicht_pruefen(rumpf.get('gewicht'))
        if 'bereich' in rumpf:
            eintrag['bereich'] = Meshoptionen.bereich_pruefen(rumpf.get('bereich'))
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'bild': eintrag})

    @staticmethod
    @require_POST
    def retexturieren(request, job_id):
        """Nur die Textur neu — Form kommt aus `form_cache.npz` (`Meshlauf`/`_run_mesh.py`),
        kein neuer Formlauf. Braucht einen vorherigen fertigen Lauf (sonst kein Cache)."""
        job = get_object_or_404(Meshauftrag, pk=job_id)
        if job.laeuft and Mesharbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft schon'}, status=409)
        if job.status != 'fertig':
            return JsonResponse({'error': 'Erst einen Lauf abschließen, dann nachschärfen'}, status=409)
        return JsonResponse({'ok': True, 'pid': Mesharbeiter.starten(job, ab='textur')})

    # -------------------------------------------------------------- Löschen

    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        Meshendpunkte._entfernen(get_object_or_404(Meshauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def mehrere_loeschen(request):
        ids = Meshendpunkte._rumpf(request).get('ids') or []
        n = 0
        for job in Meshauftrag.objects.filter(pk__in=ids):
            Meshendpunkte._entfernen(job)
            n += 1
        return JsonResponse({'ok': True, 'geloescht': n})

    @staticmethod
    def _entfernen(job):
        if job.laeuft:
            Mesharbeiter.anhalten(job)
        Meshablage(job.kennung).loeschen()
        job.delete()

    # -------------------------------------------------------------- Dateien

    @staticmethod
    @require_GET
    def datei(request, job_id, ordner, name):
        job = get_object_or_404(Meshauftrag, pk=job_id)
        try:
            pfad = Meshablage(job.kennung).datei(ordner, name)
        except ValueError:
            raise Http404('Pfad') from None
        if not pfad.is_file():
            raise Http404('Datei %s' % name)
        herunterladen = request.GET.get('laden') == '1'
        return FileResponse(open(pfad, 'rb'), as_attachment=herunterladen, filename=pfad.name,
                            content_type=mimetypes.guess_type(pfad.name)[0] or 'application/octet-stream')
