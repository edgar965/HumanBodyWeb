# -*- coding: utf-8 -*-
"""Blendermodellendpunkte — Bereich „BlenderModel": Grundfigur → Kostüm-Kreislauf → Blender (29.09.2026).

GET  /blendermodell/<kennung>/                        Auftragsseite (Lauf, Bildauswahl, 3D-Ausgabe, Optionen)
POST /api/blendermodell/anlegen/                      name, optionen (JSON), rollen (JSON), bilder[]
                                                      → startet, wenn die Grafikkarte frei ist
GET  /api/blendermodell/katalog/                      Optionen (Gruppen figur, kostuem, blender)
GET  /api/blendermodell/<id>/zustand/                 Status, Fortschritt, Bildauswahl, Ergebnis, Stellung
POST /api/blendermodell/<id>/starten/                 {optionen?, ab?, bis?} → Lauf (Schritte aus `SCHRITTE`)
POST /api/blendermodell/<id>/anhalten/
POST /api/blendermodell/<id>/modell/                  {name} → die Figur als Genesis-Modell speichern
POST /api/blendermodell/<id>/loeschen/, /api/blendermodell/loeschen/   (mehrere: {ids})
GET  /api/blendermodell/<id>/datei/<ordner>/<name>    Fotos, Netz, Bilder und Kacheln der Figur

Fotos, Rolle, Gewicht und Platz: `blendermodellfotos.py`. Optionen speichern: `blendermodelleinstellungen.py`.
Umbenennen und Duplizieren laufen über die gemeinsamen Endpunkte aller Bereiche (`auftragsname.py`,
`auftragsduplikat.py`).
"""

import json
import logging
import mimetypes

from asgiref.sync import sync_to_async
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from ..daten.auftragskennung import Auftragskennung
from ..daten.blendermodellablage import Blendermodellablage
from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.blendermodellarbeiter import Blendermodellarbeiter
from ..dienste.blendermodellgpu import Blendermodellgpu
from ..dienste.blendermodelllauf import Blendermodelllauf
from ..dienste.blendermodelloptionen import Blendermodelloptionen
from ..dienste.blendermodellspeichern import Blendermodellspeichern
from ..dienste.blendermodellvorlage import Blendermodellvorlage
from ..dienste.blendermodellzustand import Blendermodellzustand
from ..dienste.meshoptionen import Meshoptionen
from ..models import Blendermodellauftrag

logger = logging.getLogger('core')

__all__ = ['Blendermodellendpunkte']

mimetypes.add_type('model/gltf-binary', '.glb')


class Blendermodellendpunkte:
    #: Eine Liste, eine Stelle: die des Laufs.
    SCHRITTE = Blendermodelllauf.SCHRITTE

    @staticmethod
    def rumpf(request):
        """Der JSON-Rumpf einer Anfrage — leer, wenn keiner da ist oder er kein Objekt ist."""
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return {}
        return rumpf if isinstance(rumpf, dict) else {}

    @staticmethod
    def _json_feld(request, name, vorgabe):
        """Ein JSON-Formularfeld — der Rumpf ist nach `request.FILES` nicht mehr lesbar."""
        try:
            wert = json.loads(request.POST.get(name) or 'null')
        except ValueError:
            return vorgabe
        return vorgabe if wert is None else wert

    # ---------------------------------------------------------------- Seite

    @staticmethod
    def seite(request, kennung):
        job = get_object_or_404(Blendermodellauftrag, kennung=kennung)
        return render(
            request,
            'blendermodell_auftrag.html',
            {
                'job': job,
                'daten': {
                    'zustand': Blendermodellzustand.von(job),
                    'katalog': Blendermodelloptionen.katalog(),
                },
            },
        )

    @staticmethod
    @require_GET
    def katalog(request):
        return JsonResponse(Blendermodelloptionen.katalog())

    # --------------------------------------------------------------- Anlegen

    @staticmethod
    @require_POST
    def anlegen(request):
        name = (request.POST.get('name') or '').strip()[:200]
        dateien = [f for f in request.FILES.getlist('bilder') if Blendermodellablage.ist_bild(f.name)]
        if not name:
            return JsonResponse({'error': 'Name fehlt'}, status=400)
        if not dateien:
            return JsonResponse({'error': 'Keine Bilder (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        kennung = Auftragskennung.frei(
            timezone.now(), lambda k: Blendermodellauftrag.objects.filter(kennung=k).exists()
        )
        rollen = Blendermodellendpunkte._json_feld(request, 'rollen', {})
        ablage = Blendermodellablage(kennung)
        try:
            bilder = []
            for f in dateien:
                rolle = rollen.get(f.name) if isinstance(rollen, dict) else None
                bilder.append(
                    {
                        'datei': ablage.eingang_ablegen(f),
                        'original': f.name,
                        'gewicht': 100,
                        'bereich': None,
                        'rolle': Meshoptionen.rolle_pruefen(rolle),
                    }
                )
            job = Blendermodellauftrag.objects.create(
                kennung=kennung,
                name=name,
                bilder=bilder,
                optionen=Blendermodelloptionen.pruefen(
                    Blendermodellendpunkte._json_feld(request, 'optionen', {})
                ),
            )
        except OSError as fehler:
            # Ein halber Ordner ohne Eintrag wäre Müll, den keine Tabelle zeigt und keiner löscht.
            logger.exception('BlenderModel: Anlegen gescheitert (%s)', kennung)
            ablage.loeschen()
            return JsonResponse({'error': 'Die Fotos ließen sich nicht ablegen: %s' % fehler}, status=500)
        Blendermodellvorlage.erneuern(job)
        gestartet, hinweis = False, ''
        if request.POST.get('starten', '1') == '1':
            hinweis = Blendermodellgpu.belegt_durch(job)
            if not hinweis:
                Blendermodellarbeiter.starten(job)
                gestartet = True
        return JsonResponse(
            {
                'ok': True,
                'id': str(job.id),
                'kennung': kennung,
                'bilder': len(bilder),
                'url': reverse('blendermodell_auftrag', args=[kennung]),
                'gestartet': gestartet,
                'hinweis': hinweis,
            }
        )

    # --------------------------------------------------------------- Zustand

    @staticmethod
    @require_GET
    async def zustand(request, job_id):
        # ASYNC wie `Meshfigurendpunkte.zustand`: die Seite fragt alle zwei Sekunden; synchron stünde jede
        # Anfrage im EINEN geteilten Faden von Daphne (23.09.2026).
        daten = await sync_to_async(Blendermodellendpunkte._zustand_rechnen, thread_sensitive=False)(job_id)
        return JsonResponse(daten, json_dumps_params={'default': str})

    @staticmethod
    def _zustand_rechnen(job_id):
        job = get_object_or_404(Blendermodellauftrag, pk=job_id)
        if job.laeuft and not Blendermodellarbeiter.lebt(job):
            job.refresh_from_db()
            if job.laeuft:
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess lebt nicht mehr (auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        return Blendermodellzustand.von(job)

    # ------------------------------------------------------------------ Lauf

    @staticmethod
    @require_POST
    def starten(request, job_id):
        job = get_object_or_404(Blendermodellauftrag, pk=job_id)
        if job.laeuft and Blendermodellarbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft schon'}, status=409)
        belegt = Blendermodellgpu.belegt_durch(job)
        if belegt:
            return JsonResponse({'error': belegt}, status=409)
        rumpf = Blendermodellendpunkte.rumpf(request)
        ab = rumpf.get('ab') if rumpf.get('ab') in Blendermodellendpunkte.SCHRITTE else None
        bis = rumpf.get('bis') if rumpf.get('bis') in Blendermodellendpunkte.SCHRITTE else None
        if (
            ab
            and ab != Blendermodellendpunkte.SCHRITTE[0]
            and not Blendermodellablage(job.kennung).arbeit('grundkoerper.glb').is_file()
        ):
            return JsonResponse(
                {
                    'error': 'Es gibt noch keine Grundfigur — erst ab dem Schritt „%s" rechnen'
                    % Blendermodellendpunkte.SCHRITTE[0]
                },
                status=409,
            )
        if isinstance(rumpf.get('optionen'), dict):
            job.optionen = Blendermodelloptionen.mischen(job.optionen, rumpf['optionen'])
            job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'pid': Blendermodellarbeiter.starten(job, ab=ab, bis=bis)})

    @staticmethod
    @require_POST
    def anhalten(request, job_id):
        Blendermodellarbeiter.anhalten(get_object_or_404(Blendermodellauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def modell(request, job_id):
        """{name} → die Figur als Genesis-Modell (`data/models/<name>.json`, dasselbe Format wie „Modell
        speichern" der Szene) — erscheint unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle"."""
        job = get_object_or_404(Blendermodellauftrag, pk=job_id)
        if job.laeuft or not job.stellung():
            return JsonResponse({'error': 'Erst wenn die Figur fertig ist'}, status=409)
        try:
            name = Blendermodellspeichern.fuer(job).modell_speichern(
                Blendermodellendpunkte.rumpf(request).get('name')
            )
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'modell': name})

    # --------------------------------------------------------------- Löschen

    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        Blendermodellendpunkte._entfernen(get_object_or_404(Blendermodellauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def mehrere_loeschen(request):
        ids = Blendermodellendpunkte.rumpf(request).get('ids') or []
        n = 0
        for job in Blendermodellauftrag.objects.filter(pk__in=ids):
            Blendermodellendpunkte._entfernen(job)
            n += 1
        return JsonResponse({'ok': True, 'geloescht': n})

    @staticmethod
    def _entfernen(job):
        """Auftragsordner und Eintrag — das gespeicherte Modell und die Ablage unter
        `output/Export/BlenderModel` bleiben: sie gehören dem Nutzer, nicht dem Auftrag."""
        if job.laeuft:
            Blendermodellarbeiter.anhalten(job)
        Blendermodellablage(job.kennung).loeschen()
        job.delete()

    # --------------------------------------------------------------- Dateien

    @staticmethod
    @require_GET
    def datei(request, job_id, ordner, name):
        job = get_object_or_404(Blendermodellauftrag, pk=job_id)
        try:
            pfad = Blendermodellablage(job.kennung).datei(ordner, name)
        except ValueError:
            raise Http404('Pfad') from None
        if not pfad.is_file():
            raise Http404('Datei %s' % name)
        return Auftragsdatei.antwort(
            request, pfad, herunterladen=request.GET.get('laden') == '1', kennung=request.GET.get('v')
        )
