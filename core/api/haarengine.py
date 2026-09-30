# -*- coding: utf-8 -*-
"""Haarengineendpunkte — Bereich „Haar Engine": Grundfigur → Iterationen → Film.

GET  /haarengine/<kennung>/                        Auftragsseite (Lauf, Bildauswahl, 3D-Ausgabe, Optionen, Iterationen)
POST /api/haarengine/anlegen/                      name, optionen (JSON), rollen (JSON), bilder[], starten (0/1)
                                                      → startet nur bei starten=1 und freier Grafikkarte
GET  /api/haarengine/katalog/                      Optionen (Gruppen figur, iterationen, film)
GET  /api/haarengine/<id>/zustand/                 Status, Fortschritt, Bildauswahl, Ergebnis, Stellung
POST /api/haarengine/<id>/starten/                 {optionen?, ab?, bis?} → Lauf (Schritte aus `SCHRITTE`)
POST /api/haarengine/<id>/anhalten/
POST /api/haarengine/<id>/modell/                  {name} → die Figur als Genesis-Modell speichern
POST /api/haarengine/<id>/loeschen/, /api/haarengine/loeschen/   (mehrere: {ids})
GET  /api/haarengine/<id>/datei/<ordner>/<name>    Fotos, Bilder der Runden, Ergebnisdateien

Fotos, Rolle, Gewicht und Platz: `haarenginefotos.py`. Optionen speichern:
`haarengineeinstellungen.py`. Runden löschen: `haarengineiterationen.py`. Umbenennen und Duplizieren
laufen über die gemeinsamen Endpunkte aller Bereiche (`auftragsname.py`, `auftragsduplikat.py`).
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
from ..daten.haarengineablage import Haarengineablage
from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.haarenginearbeiter import Haarenginearbeiter
from ..dienste.haarenginegpu import Haarenginegpu
from ..dienste.haarenginelauf import Haarenginelauf
from ..dienste.haarengineoptionen import Haarengineoptionen
from ..dienste.haarenginespeichern import Haarenginespeichern
from ..dienste.haarenginevorlage import Haarenginevorlage
from ..dienste.haarenginezustand import Haarenginezustand
from ..dienste.meshoptionen import Meshoptionen
from ..models import Haarengineauftrag

logger = logging.getLogger('core')

__all__ = ['Haarengineendpunkte']

mimetypes.add_type('model/gltf-binary', '.glb')


class Haarengineendpunkte:
    #: Eine Liste, eine Stelle: die des Laufs.
    SCHRITTE = Haarenginelauf.SCHRITTE

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
        job = get_object_or_404(Haarengineauftrag, kennung=kennung)
        return render(
            request,
            'haarengine_auftrag.html',
            {
                'job': job,
                'daten': {
                    'zustand': Haarenginezustand.von(job),
                    'katalog': Haarengineoptionen.katalog(),
                },
            },
        )

    @staticmethod
    @require_GET
    def katalog(request):
        return JsonResponse(Haarengineoptionen.katalog())

    # --------------------------------------------------------------- Anlegen

    @staticmethod
    @require_POST
    def anlegen(request):
        name = (request.POST.get('name') or '').strip()[:200]
        dateien = [f for f in request.FILES.getlist('bilder') if Haarengineablage.ist_bild(f.name)]
        # Fotos und Körper aus einem Auftrag „Mesh to 3D" (Edgar, 30.09.2026: „erstelle einen neuen Job, der die
        # Bilder aus …/meshfigur/2026.09.29.15.42.36/ nimmt") — `Haarengineauftragsquelle`.
        meshfigur = (request.POST.get('meshfigur') or '').strip()[:19]
        if not name:
            return JsonResponse({'error': 'Name fehlt'}, status=400)
        if not dateien and not meshfigur:
            return JsonResponse({'error': 'Keine Bilder (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        kennung = Auftragskennung.frei(
            timezone.now(), lambda k: Haarengineauftrag.objects.filter(kennung=k).exists()
        )
        rollen = Haarengineendpunkte._json_feld(request, 'rollen', {})
        optionen = Haarengineendpunkte._json_feld(request, 'optionen', {})
        ablage = Haarengineablage(kennung)
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
            if meshfigur:
                from ..dienste.haarengineauftragsquelle import Haarengineauftragsquelle
                bilder += Haarengineauftragsquelle.fotos(meshfigur, ablage)
                optionen = Haarengineauftragsquelle.optionen(meshfigur, optionen)
            if not bilder:
                ablage.loeschen()
                return JsonResponse({'error': 'Der Auftrag „Mesh to 3D" %s hat keine Fotos' % meshfigur}, status=400)
            job = Haarengineauftrag.objects.create(
                kennung=kennung,
                name=name,
                bilder=bilder,
                optionen=Haarengineoptionen.pruefen(optionen),
            )
        except ValueError as fehler:
            ablage.loeschen()
            return JsonResponse({'error': str(fehler)}, status=400)
        except OSError as fehler:
            # Ein halber Ordner ohne Eintrag wäre Müll, den keine Tabelle zeigt und keiner löscht.
            logger.exception('Haar Engine: Anlegen gescheitert (%s)', kennung)
            ablage.loeschen()
            return JsonResponse({'error': 'Die Fotos ließen sich nicht ablegen: %s' % fehler}, status=500)
        Haarenginevorlage.erneuern(job)
        gestartet, hinweis = False, ''
        if request.POST.get('starten', '1') == '1':
            hinweis = Haarenginegpu.belegt_durch(job)
            if not hinweis:
                Haarenginearbeiter.starten(job)
                gestartet = True
        return JsonResponse(
            {
                'ok': True,
                'id': str(job.id),
                'kennung': kennung,
                'bilder': len(bilder),
                'url': reverse('haarengine_auftrag', args=[kennung]),
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
        daten = await sync_to_async(Haarengineendpunkte._zustand_rechnen, thread_sensitive=False)(job_id)
        return JsonResponse(daten, json_dumps_params={'default': str})

    @staticmethod
    def _zustand_rechnen(job_id):
        job = get_object_or_404(Haarengineauftrag, pk=job_id)
        if job.laeuft and not Haarenginearbeiter.lebt(job):
            job.refresh_from_db()
            if job.laeuft:
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess lebt nicht mehr (auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        return Haarenginezustand.von(job)

    # ------------------------------------------------------------------ Lauf

    @staticmethod
    @require_POST
    def starten(request, job_id):
        job = get_object_or_404(Haarengineauftrag, pk=job_id)
        if job.laeuft and Haarenginearbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft schon'}, status=409)
        belegt = Haarenginegpu.belegt_durch(job)
        if belegt:
            return JsonResponse({'error': belegt}, status=409)
        rumpf = Haarengineendpunkte.rumpf(request)
        ab = rumpf.get('ab') if rumpf.get('ab') in Haarengineendpunkte.SCHRITTE else None
        bis = rumpf.get('bis') if rumpf.get('bis') in Haarengineendpunkte.SCHRITTE else None
        if (
            ab
            and ab != Haarengineendpunkte.SCHRITTE[0]
            and not Haarengineablage(job.kennung).arbeit('grundkoerper.glb').is_file()
        ):
            return JsonResponse(
                {
                    'error': 'Es gibt noch keine Grundfigur — erst ab dem Schritt „%s" rechnen'
                    % Haarengineendpunkte.SCHRITTE[0]
                },
                status=409,
            )
        if isinstance(rumpf.get('optionen'), dict):
            job.optionen = Haarengineoptionen.mischen(job.optionen, rumpf['optionen'])
            job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'pid': Haarenginearbeiter.starten(job, ab=ab, bis=bis)})

    @staticmethod
    @require_POST
    def anhalten(request, job_id):
        Haarenginearbeiter.anhalten(get_object_or_404(Haarengineauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def modell(request, job_id):
        """{name} → die Figur als Genesis-Modell (`data/models/<name>.json`, dasselbe Format wie „Modell
        speichern" der Szene) — erscheint unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle"."""
        job = get_object_or_404(Haarengineauftrag, pk=job_id)
        if job.laeuft or not job.stellung():
            return JsonResponse({'error': 'Erst wenn die Figur fertig ist'}, status=409)
        try:
            name = Haarenginespeichern.fuer(job).modell_speichern(
                Haarengineendpunkte.rumpf(request).get('name')
            )
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'modell': name})

    # --------------------------------------------------------------- Löschen

    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        Haarengineendpunkte._entfernen(get_object_or_404(Haarengineauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def mehrere_loeschen(request):
        ids = Haarengineendpunkte.rumpf(request).get('ids') or []
        n = 0
        for job in Haarengineauftrag.objects.filter(pk__in=ids):
            Haarengineendpunkte._entfernen(job)
            n += 1
        return JsonResponse({'ok': True, 'geloescht': n})

    @staticmethod
    def _entfernen(job):
        """Auftragsordner und Eintrag — das gespeicherte Modell und die Ablage unter
        `output/Export/HaarEngine` bleiben: sie gehören dem Nutzer, nicht dem Auftrag."""
        if job.laeuft:
            Haarenginearbeiter.anhalten(job)
        Haarengineablage(job.kennung).loeschen()
        job.delete()

    # --------------------------------------------------------------- Dateien

    @staticmethod
    @require_GET
    def datei(request, job_id, ordner, name):
        job = get_object_or_404(Haarengineauftrag, pk=job_id)
        try:
            pfad = Haarengineablage(job.kennung).datei(ordner, name)
        except ValueError:
            raise Http404('Pfad') from None
        if not pfad.is_file():
            raise Http404('Datei %s' % name)
        return Auftragsdatei.antwort(
            request, pfad, herunterladen=request.GET.get('laden') == '1', kennung=request.GET.get('v')
        )
