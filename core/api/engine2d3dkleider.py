# -*- coding: utf-8 -*-
"""Engine2d3dKleiderendpunkte — Bereich „Haar Engine": Grundfigur → Iterationen → Film.

GET  /engine2d3dkleider/<kennung>/                        Auftragsseite (Lauf, Bildauswahl, 3D-Ausgabe, Optionen, Iterationen)
POST /api/engine2d3dkleider/anlegen/                      name, optionen (JSON), rollen (JSON), bilder[], starten (0/1)
                                                      → startet nur bei starten=1 und freier Grafikkarte
GET  /api/engine2d3dkleider/katalog/                      Optionen (Gruppen figur, iterationen, film)
GET  /api/engine2d3dkleider/<id>/zustand/                 Status, Fortschritt, Bildauswahl, Ergebnis, Stellung
POST /api/engine2d3dkleider/<id>/starten/                 {optionen?, ab?, bis?} → Lauf (Schritte aus `SCHRITTE`)
POST /api/engine2d3dkleider/<id>/anhalten/
POST /api/engine2d3dkleider/<id>/modell/                  {name} → die Figur als Genesis-Modell speichern
POST /api/engine2d3dkleider/<id>/loeschen/, /api/engine2d3dkleider/loeschen/   (mehrere: {ids})
GET  /api/engine2d3dkleider/<id>/datei/<ordner>/<name>    Fotos, Bilder der Runden, Ergebnisdateien

Fotos, Rolle, Gewicht und Platz: `engine2d3dkleiderfotos.py`. Optionen speichern:
`engine2d3dkleidereinstellungen.py`. Runden löschen: `engine2d3dkleideriterationen.py`. Umbenennen und Duplizieren
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
from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from ..dienste.engine2d3dkleidergpu import Engine2d3dKleidergpu
from ..dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from ..dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from ..dienste.engine2d3dkleiderspeichern import Engine2d3dKleiderspeichern
from ..dienste.engine2d3dkleidervorlage import Engine2d3dKleidervorlage
from ..dienste.engine2d3dkleiderzustand import Engine2d3dKleiderzustand
from ..dienste.meshoptionen import Meshoptionen
from ..models import Engine2d3dKleiderauftrag

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderendpunkte']

mimetypes.add_type('model/gltf-binary', '.glb')


class Engine2d3dKleiderendpunkte:
    #: Eine Liste, eine Stelle: die des Laufs.
    SCHRITTE = Engine2d3dKleiderlauf.SCHRITTE

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
        job = get_object_or_404(Engine2d3dKleiderauftrag, kennung=kennung)
        return render(
            request,
            'engine2d3dkleider_auftrag.html',
            {
                'job': job,
                'daten': {
                    'zustand': Engine2d3dKleiderzustand.von(job),
                    'katalog': Engine2d3dKleideroptionen.katalog(),
                },
            },
        )

    @staticmethod
    @require_GET
    def katalog(request):
        return JsonResponse(Engine2d3dKleideroptionen.katalog())

    # --------------------------------------------------------------- Anlegen

    @staticmethod
    @require_POST
    def anlegen(request):
        name = (request.POST.get('name') or '').strip()[:200]
        dateien = [f for f in request.FILES.getlist('bilder') if Engine2d3dKleiderablage.ist_bild(f.name)]
        # Fotos und Körper aus einem Auftrag „Mesh to 3D" (Edgar, 30.09.2026: „erstelle einen neuen Job, der die
        # Bilder aus …/meshfigur/2026.09.29.15.42.36/ nimmt") — `Engine2d3dKleiderauftragsquelle`.
        meshfigur = (request.POST.get('meshfigur') or '').strip()[:19]
        if not name:
            return JsonResponse({'error': 'Name fehlt'}, status=400)
        if not dateien and not meshfigur:
            return JsonResponse({'error': 'Keine Bilder (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        kennung = Auftragskennung.frei(
            timezone.now(), lambda k: Engine2d3dKleiderauftrag.objects.filter(kennung=k).exists()
        )
        rollen = Engine2d3dKleiderendpunkte._json_feld(request, 'rollen', {})
        optionen = Engine2d3dKleiderendpunkte._json_feld(request, 'optionen', {})
        ablage = Engine2d3dKleiderablage(kennung)
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
                from ..dienste.engine2d3dkleiderauftragsquelle import Engine2d3dKleiderauftragsquelle
                bilder += Engine2d3dKleiderauftragsquelle.fotos(meshfigur, ablage)
                optionen = Engine2d3dKleiderauftragsquelle.optionen(meshfigur, optionen)
            if not bilder:
                ablage.loeschen()
                return JsonResponse({'error': 'Der Auftrag „Mesh to 3D" %s hat keine Fotos' % meshfigur}, status=400)
            job = Engine2d3dKleiderauftrag.objects.create(
                kennung=kennung,
                name=name,
                bilder=bilder,
                optionen=Engine2d3dKleideroptionen.pruefen(optionen),
            )
        except ValueError as fehler:
            ablage.loeschen()
            return JsonResponse({'error': str(fehler)}, status=400)
        except OSError as fehler:
            # Ein halber Ordner ohne Eintrag wäre Müll, den keine Tabelle zeigt und keiner löscht.
            logger.exception('Haar Engine: Anlegen gescheitert (%s)', kennung)
            ablage.loeschen()
            return JsonResponse({'error': 'Die Fotos ließen sich nicht ablegen: %s' % fehler}, status=500)
        Engine2d3dKleidervorlage.erneuern(job)
        gestartet, hinweis = False, ''
        if request.POST.get('starten', '1') == '1':
            hinweis = Engine2d3dKleidergpu.belegt_durch(job)
            if not hinweis:
                Engine2d3dKleiderarbeiter.starten(job)
                gestartet = True
        return JsonResponse(
            {
                'ok': True,
                'id': str(job.id),
                'kennung': kennung,
                'bilder': len(bilder),
                'url': reverse('engine2d3dkleider_auftrag', args=[kennung]),
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
        daten = await sync_to_async(Engine2d3dKleiderendpunkte._zustand_rechnen, thread_sensitive=False)(job_id)
        return JsonResponse(daten, json_dumps_params={'default': str})

    @staticmethod
    def _zustand_rechnen(job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        if job.laeuft and not Engine2d3dKleiderarbeiter.lebt(job):
            job.refresh_from_db()
            if job.laeuft:
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess lebt nicht mehr (auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        return Engine2d3dKleiderzustand.von(job)

    # ------------------------------------------------------------------ Lauf

    @staticmethod
    @require_POST
    def starten(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        if job.laeuft and Engine2d3dKleiderarbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft schon'}, status=409)
        belegt = Engine2d3dKleidergpu.belegt_durch(job)
        if belegt:
            return JsonResponse({'error': belegt}, status=409)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        ab = rumpf.get('ab') if rumpf.get('ab') in Engine2d3dKleiderendpunkte.SCHRITTE else None
        bis = rumpf.get('bis') if rumpf.get('bis') in Engine2d3dKleiderendpunkte.SCHRITTE else None
        # Wie `Engine2d3dKleiderlauf.ausfuehren`: die Grundfigur braucht erst, wer NACH „grundfigur" beginnt — „koerper"
        # und „grundfigur" bauen sie ja erst (vorher verlangte die API sie für alles außer „netz").
        schritte = Engine2d3dKleiderendpunkte.SCHRITTE
        if (
            ab
            and 'grundfigur' in schritte
            and schritte.index(ab) > schritte.index('grundfigur')
            and not Engine2d3dKleiderablage(job.kennung).arbeit('grundkoerper.glb').is_file()
        ):
            return JsonResponse(
                {
                    'error': 'Es gibt noch keine Grundfigur — erst ab dem Schritt „%s" rechnen'
                    % Engine2d3dKleiderendpunkte.SCHRITTE[0]
                },
                status=409,
            )
        if isinstance(rumpf.get('optionen'), dict):
            job.optionen = Engine2d3dKleideroptionen.mischen(job.optionen, rumpf['optionen'])
            job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'pid': Engine2d3dKleiderarbeiter.starten(job, ab=ab, bis=bis)})

    @staticmethod
    @require_POST
    def anhalten(request, job_id):
        Engine2d3dKleiderarbeiter.anhalten(get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def modell(request, job_id):
        """{name} → die Figur als Genesis-Modell (`data/models/<name>.json`, dasselbe Format wie „Modell
        speichern" der Szene) — erscheint unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle"."""
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        if job.laeuft or not job.stellung():
            return JsonResponse({'error': 'Erst wenn die Figur fertig ist'}, status=409)
        try:
            name = Engine2d3dKleiderspeichern.fuer(job).modell_speichern(
                Engine2d3dKleiderendpunkte.rumpf(request).get('name')
            )
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'modell': name})

    # --------------------------------------------------------------- Löschen

    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        Engine2d3dKleiderendpunkte._entfernen(get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id))
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def mehrere_loeschen(request):
        ids = Engine2d3dKleiderendpunkte.rumpf(request).get('ids') or []
        n = 0
        for job in Engine2d3dKleiderauftrag.objects.filter(pk__in=ids):
            Engine2d3dKleiderendpunkte._entfernen(job)
            n += 1
        return JsonResponse({'ok': True, 'geloescht': n})

    @staticmethod
    def _entfernen(job):
        """Auftragsordner und Eintrag — das gespeicherte Modell und die Ablage unter
        `output/Export/Engine2d3dKleider` bleiben: sie gehören dem Nutzer, nicht dem Auftrag."""
        if job.laeuft:
            Engine2d3dKleiderarbeiter.anhalten(job)
        Engine2d3dKleiderablage(job.kennung).loeschen()
        job.delete()

    # --------------------------------------------------------------- Dateien

    @staticmethod
    @require_GET
    def datei(request, job_id, ordner, name):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        try:
            pfad = Engine2d3dKleiderablage(job.kennung).datei(ordner, name)
        except ValueError:
            raise Http404('Pfad') from None
        if not pfad.is_file():
            raise Http404('Datei %s' % name)
        return Auftragsdatei.antwort(
            request, pfad, herunterladen=request.GET.get('laden') == '1', kennung=request.GET.get('v')
        )
