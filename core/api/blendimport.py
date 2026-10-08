# -*- coding: utf-8 -*-
"""Blendimportendpunkte — „Datei → Modell importieren…" mit einer .blend (Charakter-Seite, 08.10.2026).

GET  /api/character/blendimport/einstellungen/          Katalog, gemerkte Werte, letzte Importe
POST /api/character/blendimport/pruefen/                {pfad, name} → welche .blend, welcher Name (`Blendimportquelle`)
POST /api/character/blendimport/starten/                {werte} → Werte merken, Import anlegen und starten
GET  /api/character/blendimport/laufend/                {kennung|null, status, schritt, name} des Imports, der gerade rechnet
GET  /api/character/blendimport/<kennung>/zustand/      Stand des Laufs; im Schritt „figur" mit dem Fortschritt des
                                                         Auftrags „Mesh to 3D"
POST /api/character/blendimport/<kennung>/anhalten/
POST /api/character/blendimport/<kennung>/neu/          {ab} → ab diesem Schritt neu rechnen

`starten` und `neu` antworten 409, solange ein ANDERER Import läuft (`Blendimportarbeiter.laufender`).
"""

import json
import logging
import threading

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from ..daten.blendimportablage import Blendimportablage
from ..dienste.blendimportarbeiter import Blendimportarbeiter
from ..dienste.blendimporteinstellungen import Blendimporteinstellungen
from ..dienste.blendimportlauf import Blendimportlauf
from ..dienste.blendimportquelle import Blendimportquelle

logger = logging.getLogger('core')

__all__ = ['Blendimportendpunkte']


class Blendimportendpunkte:
    LETZTE = 5
    #: Prüfung „läuft ein anderer Import?" und Start in einem Zug (`starten`, `neu`) — der Arbeitsprozess schreibt „läuft" erst nach dem Start.
    _STARTSPERRE = threading.Lock()

    @staticmethod
    def _rumpf(request):
        try:
            daten = json.loads(request.body or b'{}')
        except ValueError:
            return {}
        return daten if isinstance(daten, dict) else {}

    @staticmethod
    def _ablage(kennung):
        try:
            return Blendimportablage(kennung)
        except ValueError:
            return None

    @staticmethod
    def _belegt(ausser=None):
        """409, solange ein anderer Import läuft (GPU und Kerne gehören ihm); sonst `None`."""
        andere = Blendimportarbeiter.laufender(ausser=ausser)
        if not andere:
            return None
        schritt = Blendimportablage(andere).stand().get('schritt') or '?'
        return JsonResponse({'error': 'Import %s läuft noch (Schritt „%s") — erst nach seinem Ende starten' % (andere, schritt)},
                            status=409)

    @staticmethod
    @require_GET
    def einstellungen(request):
        letzte = []
        for kennung in Blendimportablage.alle()[:Blendimportendpunkte.LETZTE]:
            stand = Blendimportablage(kennung).stand()
            letzte.append({'kennung': kennung, 'status': stand.get('status'), 'name': (stand.get('quelle') or {}).get('name'),
                           'modell': ((stand.get('ergebnis') or {}).get('modell') or {}).get('name')})
        return JsonResponse({**Blendimporteinstellungen.katalog(), 'schritte': list(Blendimportlauf.SCHRITTE),
                             'letzte': letzte})

    @staticmethod
    @require_POST
    def pruefen(request):
        werte = Blendimporteinstellungen.pruefen(Blendimportendpunkte._rumpf(request))
        try:
            quelle = Blendimportquelle(werte['pfad'], werte['name'], werte['eigener_name'])
            return JsonResponse({'ok': True, **quelle.steckbrief()})
        except ValueError as fehler:
            return JsonResponse({'ok': False, 'error': str(fehler)}, status=400)

    @staticmethod
    @require_GET
    def laufend(request):
        """Welcher Import rechnet gerade? Die Topbar-Leiste und der Dialog fragen es nach dem Neuladen der Seite."""
        kennung = Blendimportarbeiter.laufender()
        if not kennung:
            return JsonResponse({'kennung': None})
        stand = Blendimportablage(kennung).stand()
        return JsonResponse({'kennung': kennung, 'status': stand.get('status'), 'schritt': stand.get('schritt'),
                             'name': (stand.get('quelle') or {}).get('name')})

    @staticmethod
    @require_POST
    def starten(request):
        from ..daten.auftragskennung import Auftragskennung

        # Die Sperre hält Prüfung UND Start zusammen: zwei Klicks kurz hintereinander kommen als zwei Anfragen, und
        # solange der erste Arbeitsprozess noch nicht „läuft" im Stand steht, sähe der zweite nichts Belegtes.
        with Blendimportendpunkte._STARTSPERRE:
            belegt = Blendimportendpunkte._belegt()
            if belegt:
                return belegt
            werte = Blendimporteinstellungen.pruefen(Blendimportendpunkte._rumpf(request).get('werte'))
            try:
                quelle = Blendimportquelle(werte['pfad'], werte['name'], werte['eigener_name']).steckbrief()
            except ValueError as fehler:
                return JsonResponse({'error': str(fehler)}, status=400)
            werte = Blendimporteinstellungen.speichern(werte)
            kennung = Auftragskennung.frei(timezone.now(), lambda k: Blendimportablage(k).ordner().exists())
            ablage = Blendimportablage(kennung)
            ablage.anlegen()
            ablage.stand_schreiben({'kennung': kennung, 'status': 'neu', 'quelle': quelle, 'einstellungen': werte,
                                    'angelegt': timezone.now().isoformat()})
            Blendimportarbeiter.starten(ablage)
        return JsonResponse({'ok': True, 'kennung': kennung, 'quelle': quelle})

    @staticmethod
    @require_GET
    def zustand(request, kennung):
        ablage = Blendimportendpunkte._ablage(kennung)
        stand = ablage.stand() if ablage else {}
        if not stand:
            return JsonResponse({'error': 'Kein Import %s' % kennung}, status=404)
        if stand.get('status') == 'laeuft' and not Blendimportarbeiter.lebt(ablage):
            stand = ablage.stand()
            if stand.get('status') == 'laeuft':
                stand.update(status='gescheitert', fehler=stand.get('fehler') or 'Arbeitsprozess lebt nicht mehr (auftrag.log)')
                ablage.stand_schreiben(stand)
        stand['figur_lauf'] = Blendimportendpunkte._figurlauf(stand)
        return JsonResponse(stand, json_dumps_params={'default': str})

    @staticmethod
    def _figurlauf(stand):
        """Im Schritt „figur": Fortschritt des Auftrags „Mesh to 3D" auf das Band des Schritts umgerechnet."""
        figur = (stand.get('ergebnis') or {}).get('figur') or {}
        if stand.get('schritt') != 'figur' or not figur.get('id'):
            return None
        from ..models import Meshfigurauftrag

        job = Meshfigurauftrag.objects.filter(pk=figur['id']).first()
        if job is None:
            return None
        von, bis = Blendimportlauf.BAENDER['figur']
        return {'kennung': job.kennung, 'schritt': job.schritt, 'progress': job.progress,
                'detail': job.progress_detail, 'fortschritt': int(von + (bis - von) * (job.progress or 0) / 100.0)}

    @staticmethod
    @require_POST
    def anhalten(request, kennung):
        ablage = Blendimportendpunkte._ablage(kennung)
        if ablage is None or not ablage.stand():
            return JsonResponse({'error': 'Kein Import %s' % kennung}, status=404)
        Blendimportarbeiter.anhalten(ablage)
        return JsonResponse({'ok': True})

    @staticmethod
    @require_POST
    def neu(request, kennung):
        ablage = Blendimportendpunkte._ablage(kennung)
        if ablage is None or not ablage.stand():
            return JsonResponse({'error': 'Kein Import %s' % kennung}, status=404)
        with Blendimportendpunkte._STARTSPERRE:
            if Blendimportarbeiter.lebt(ablage):
                return JsonResponse({'error': 'Der Import läuft schon'}, status=409)
            belegt = Blendimportendpunkte._belegt(ausser=kennung)
            if belegt:
                return belegt
            ab = Blendimportendpunkte._rumpf(request).get('ab')
            ab = ab if ab in Blendimportlauf.SCHRITTE else None
            return JsonResponse({'ok': True, 'pid': Blendimportarbeiter.starten(ablage, ab=ab), 'ab': ab})
