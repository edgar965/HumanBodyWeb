# -*- coding: utf-8 -*-
"""Bildmodellendpunkte — „Modell aus Dateien": Seiten und API.

GET  /humanbody/modell-aus-dateien/                     Dashboard (Tabelle + neuer Auftrag)
GET  /humanbody/modell-aus-dateien/<kennung>/           Auftragsseite (Bilder, Optionen, 3D)
POST /api/bildmodell/anlegen/                           name, typ, bilder[] → {kennung, url}
GET  /api/bildmodell/katalog/                           Optionen je Schritt mit Verfügbarkeit
GET  /api/bildmodell/<id>/zustand/                      Status, Fortschritt, Bilder, Ergebnis
POST /api/bildmodell/<id>/bilder/                       weitere Bilder hochladen (+ `typen` JSON je Datei)
POST /api/bildmodell/<id>/bild/<datei>/                 Kategorie/Gewicht eines Bildes stellen
POST /api/bildmodell/<id>/starten/                      {optionen, ab, bis, schritte} → Arbeitsprozess
     Bilder ersetzen und löschen: `Bildmodelldateiendpunkte` (bildmodelldateien.py)
POST /api/bildmodell/<id>/anhalten/
POST /api/bildmodell/<id>/loeschen/, /api/bildmodell/loeschen/ (mehrere)
GET  /api/bildmodell/<id>/datei/<ordner>/<name>         Bilder und Vorschauen
"""

import json
import logging

from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from ..daten.auftragskennung import Auftragskennung
from ..daten.bildmodellablage import Bildmodellablage
from ..dienste.bildmodellarbeiter import Bildmodellarbeiter
from ..dienste.bildmodellbildtypen import Bildmodellbildtypen
from ..dienste.bildmodelldateien import Bildmodelldateien
from ..dienste.bildmodellfotolinien import Bildmodellfotolinien
from ..dienste.bildmodelllauf import Bildmodelllauf
from ..dienste.bildmodelloptionen import Bildmodelloptionen
from ..dienste.bildmodellpersonkatalog import Bildmodellpersonkatalog
from ..dienste.bildmodelltabelle import Bildmodelltabelle
from ..dienste.bildmodelltextur import Bildmodelltextur
from ..models import Bildmodellauftrag

logger = logging.getLogger('core')

__all__ = ['Bildmodellendpunkte']


class Bildmodellendpunkte:
    # -------------------------------------------------------------- Seiten

    @staticmethod
    def _eingaenge(ablage):
        """Bilder und Drehvideos des Auftrags, wie hochgeladen."""
        return [p.name for p in ablage.originale() + ablage.videos()]

    @staticmethod
    def dashboard(request):
        auftraege = Bildmodellauftrag.objects.all()
        return render(
            request,
            'bildmodell.html',
            {
                'tabelle': Bildmodelltabelle(auftraege).tabelle(),
                'typen': Bildmodellauftrag.TYP_CHOICES,
                'testfiguren': Bildmodellpersonkatalog.testfiguren(),
            },
        )

    @staticmethod
    def auftragsseite(request, kennung):
        job = get_object_or_404(Bildmodellauftrag, kennung=kennung)
        return render(
            request,
            'bildmodell_auftrag.html',
            {
                'job': job,
                'kategorien': Bildmodellauftrag.KATEGORIEN,
                'katalog_json': json.dumps(Bildmodelloptionen.katalog(), ensure_ascii=False),
                'zustand_json': json.dumps(Bildmodellendpunkte._zustand(job), ensure_ascii=False),
            },
        )

    # ------------------------------------------------------------- Anlegen

    @staticmethod
    @require_POST
    def anlegen(request):
        name = (request.POST.get('name') or '').strip()
        typ = request.POST.get('typ') or 'genesis9'
        dateien = [f for f in request.FILES.getlist('bilder') if Bildmodellablage.ist_eingang(f.name)]
        if not name:
            return JsonResponse({'error': 'Name fehlt'}, status=400)
        if typ not in dict(Bildmodellauftrag.TYP_CHOICES):
            return JsonResponse({'error': 'Unbekannter Typ %s' % typ}, status=400)
        kennung = Auftragskennung.frei(
            timezone.now(), lambda k: Bildmodellauftrag.objects.filter(kennung=k).exists()
        )
        job = Bildmodellauftrag.objects.create(
            kennung=kennung,
            name=name,
            typ=typ,
            optionen=Bildmodelloptionen.pruefen(Bildmodellendpunkte._optionen_aus(request)),
        )
        ablage = Bildmodellablage(kennung)
        for f in dateien:
            ablage.original_ablegen(f)
        return JsonResponse(
            {
                'ok': True,
                'id': str(job.id),
                'kennung': kennung,
                'url': reverse('bildmodell_auftrag', args=[kennung]),
                'bilder': len(dateien),
            }
        )

    @staticmethod
    def _optionen_aus(request):
        """Optionen aus dem Formularfeld `optionen` (JSON) — der Rumpf ist
        nach `request.FILES` nicht mehr lesbar (`RawPostDataException`)."""
        roh = request.POST.get('optionen')
        if not roh:
            return {}
        try:
            return json.loads(roh)
        except ValueError:
            return {}

    @staticmethod
    @require_GET
    def katalog(request):
        return JsonResponse(Bildmodelloptionen.katalog())

    # ------------------------------------------------------------- Zustand

    @staticmethod
    def _zustand(job):
        return {
            'id': str(job.id),
            'kennung': job.kennung,
            'name': job.name,
            'typ': job.typ,
            'status': job.status,
            'schritt': job.schritt,
            'progress': job.progress,
            'progress_detail': job.progress_detail,
            'lauf': Bildmodelllauf.relativ(job),
            'error': job.error_message,
            'optionen': job.optionen,
            'bilder': job.bilder,
            'ergebnis': job.ergebnis,
            'textur': Bildmodelltextur.hautton(job.bilder),
            'texturbilder': Bildmodelltextur.liste(job.bilder),
            'fotolinien': Bildmodellfotolinien(job).alle(),
            'modell': job.modell,
            'laeuft': job.laeuft,
            'originale': Bildmodellendpunkte._eingaenge(Bildmodellablage(job.kennung)),
            'neue': Bildmodelldateien(job, Bildmodellablage(job.kennung)).ohne_befund(),
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
        }

    @staticmethod
    @require_GET
    def zustand(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        if job.laeuft and not Bildmodellarbeiter.lebt(job):
            job.refresh_from_db()
            if job.laeuft:
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess lebt nicht mehr (auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        return JsonResponse(Bildmodellendpunkte._zustand(job))

    # -------------------------------------------------------------- Bilder

    @staticmethod
    @require_POST
    def bilder(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        ablage = Bildmodellablage(job.kennung)
        n = 0
        namen = []
        for f in request.FILES.getlist('bilder'):
            if Bildmodellablage.ist_eingang(f.name):
                ablage.original_ablegen(f)
                namen.append(Bildmodellablage.sauber(f.name))
                n += 1
        # Bildtypen-Vorgaben je Datei (`{name: {haupt, neben, nutzung}}`, 19.09.2026): die
        # Testfallbilder und „Bild für die Textur" kennen ihren Typ, die Sichtung übernimmt ihn.
        typen = Bildmodellbildtypen.vorgaben_pruefen(request.POST.get('typen'), namen)
        if typen:
            optionen = dict(job.optionen or {})
            optionen['bildtypen'] = {**(optionen.get('bildtypen') or {}), **typen}
            job.optionen = optionen
            job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'neu': n, 'originale': Bildmodellendpunkte._eingaenge(ablage)})

    @staticmethod
    @require_POST
    def bild(request, job_id, datei):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        eintrag = job.bild(datei)
        if eintrag is None:
            raise Http404('Kein Bild %s' % datei)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Kein JSON'}, status=400)
        # Hauptbild-/Nebenbild-Typ, Nutzung, Kategorie, Gewicht, Textur-Häkchen (19.09.2026).
        Bildmodellbildtypen.stellen(eintrag, rumpf)
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'bild': eintrag, 'textur': Bildmodelltextur.hautton(job.bilder),
                             'texturbilder': Bildmodelltextur.liste(job.bilder)})

    # ------------------------------------------------------------- Starten

    @staticmethod
    @require_POST
    def starten(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        if job.laeuft and Bildmodellarbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft schon'}, status=409)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            rumpf = {}
        optionen = Bildmodelloptionen.pruefen(rumpf.get('optionen') or job.optionen)
        for feld in Bildmodelloptionen.BLEIBEN:
            # Ohne eigene Angabe bleiben Proportionen (Popup), Testfall, gezogene Linien und
            # Bildtypen-Vorgaben erhalten — `pruefen` kennt sie nicht.
            if feld not in (rumpf.get('optionen') or {}):
                optionen[feld] = (job.optionen or {}).get(feld) or {}
        if isinstance(rumpf.get('fest'), dict):
            optionen['fest'] = rumpf['fest']
        ab = rumpf.get('ab') or 'sichtung'
        if ab not in Bildmodelloptionen.REIHENFOLGE:
            ab = 'sichtung'
        # `bis`: nur bis zu diesem Schritt (die Sichtung neuer Dateien, 19.09.2026).
        bis = rumpf.get('bis') if rumpf.get('bis') in Bildmodelloptionen.REIHENFOLGE else None
        # `schritte`: genau diese Schritte — „Textur anpassen" = [sichtung,] textur (19.09.2026).
        schritte = [s for s in (rumpf.get('schritte') or []) if s in Bildmodelloptionen.REIHENFOLGE]
        if schritte:
            ab, bis = schritte[0], schritte[-1]
        optionen['ab'] = ab  # für `Bildmodelllauf.relativ`: Balken ab dem Startschritt
        job.optionen = optionen
        job.progress = 0
        job.schritt = ab
        job.save(update_fields=['optionen', 'progress', 'schritt', 'updated_at'])
        pid = Bildmodellarbeiter.starten(job, ab, bis, schritte or None)
        return JsonResponse({'ok': True, 'pid': pid, 'ab': ab, 'bis': bis, 'schritte': schritte})

    @staticmethod
    @require_POST
    def anhalten(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        Bildmodellarbeiter.anhalten(job)
        return JsonResponse({'ok': True})

    # ------------------------------------------------------------ Löschen

    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        Bildmodellendpunkte._entfernen(job)
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def mehrere_loeschen(request):
        try:
            kennungen = json.loads(request.body or b'{}').get('ids') or []
        except ValueError:
            kennungen = []
        n = 0
        for job in Bildmodellauftrag.objects.filter(pk__in=kennungen):
            Bildmodellendpunkte._entfernen(job)
            n += 1
        return JsonResponse({'ok': True, 'geloescht': n})

    @staticmethod
    def _entfernen(job):
        if job.laeuft:
            Bildmodellarbeiter.anhalten(job)
        Bildmodellablage(job.kennung).loeschen()
        job.delete()

    # -------------------------------------------------------------- Dateien

    @staticmethod
    @require_GET
    def datei(request, job_id, ordner, name):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        if ordner not in (Bildmodellablage.ORIGINAL, Bildmodellablage.ZUSCHNITT, Bildmodellablage.ERGEBNIS):
            raise Http404('Kein solcher Ordner')
        try:
            pfad = Bildmodellablage(job.kennung).datei(ordner, name)
        except ValueError:
            raise Http404('Pfad') from None
        if not pfad.is_file():
            raise Http404('Datei %s' % name)
        return FileResponse(open(pfad, 'rb'))
