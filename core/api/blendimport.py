# -*- coding: utf-8 -*-
"""Blendimportendpunkte — „Datei → Modell importieren…" mit einer .blend, OBJ oder FBX (Charakter-Seite, 08.10.2026).

Ein Satz Endpunkte für alle Formate (10.10.2026): `format` (`blend` Vorgabe, `obj`, `fbx` — `Blendimportformate`) kommt als
`?format=` beim GET und als Feld `format` im Rumpf der POSTs; er wählt Katalog, gemerkte Werte, Endung der Quelle und die Schritte.

GET  /api/character/blendimport/einstellungen/          Katalog, gemerkte Werte, Schritte, letzte Importe [?format=]
POST /api/character/blendimport/pruefen/                {pfad, name, format} → welche Datei, welcher Name (`Blendimportquelle`)
POST /api/character/blendimport/starten/                {werte, format} → Werte merken, Import anlegen und starten
GET  /api/character/blendimport/laufend/                {kennung|null, status, schritt, name} des Imports, der gerade rechnet
GET  /api/character/blendimport/<kennung>/zustand/      Stand des Laufs; im Schritt „figur" mit dem Fortschritt des
                                                         Auftrags „Mesh to 3D"
POST /api/character/blendimport/<kennung>/anhalten/
POST /api/character/blendimport/<kennung>/neu/          {ab} → ab diesem Schritt neu rechnen

`starten` und `neu` reihen den Import ein, solange ein ANDERER Import rechnet oder wartet (`Blendimportarbeiter.laufender`, `Blendimportwarteschlange`): Antwort `{ok, wartet: true, meldung, hinter}`, der
Arbeitsprozess startet sofort und wartet, bis er an der Reihe ist (bis 14.10.2026 gab es hier ein 409 mit „erst nach seinem Ende starten"). 409 bleibt nur für „derselbe Import läuft schon".
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
from ..dienste.blendimportformate import Blendimportformate
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
    def _einstellungen(format):
        """Die Einstellungs-Klasse des Formats. Die der .blend steht hier im Modul (`Blendimporteinstellungen`), nicht über
        `Blendimportformate` — so bleibt sie für die Tests austauschbar; OBJ und FBX kommen aus `Blendimportformate`."""
        return Blendimporteinstellungen if format == 'blend' else Blendimportformate.einstellungen(format)

    @staticmethod
    def _quelle(werte, format):
        return Blendimportquelle(werte['pfad'], werte['name'], werte['eigener_name'], Blendimportformate.endung(format))

    @staticmethod
    def _hinter(ausser=None):
        """Kennung des Imports, hinter dem ein neuer Start sich einreihen muss (er rechnet, oder es stehen schon Wartende davor — GPU und Kerne gehören immer nur einem); sonst `None`."""
        from ..dienste.blendimportwarteschlange import Blendimportwarteschlange

        if not Blendimportarbeiter.laufender(ausser=ausser):
            return None
        return Blendimportwarteschlange.hinter(ausser=ausser)

    @staticmethod
    def _eingereiht(ablage, ab, hinter):
        """Den Import starten — hinter `hinter` eingereiht, wenn ein anderer rechnet oder wartet — und die Antwort bauen: `wartet` und die Meldung für die Anzeige (keine Fehlermeldung, kein 409)."""
        pid = Blendimportarbeiter.starten(ablage, ab=ab, einreihen=bool(hinter), hinter=hinter)
        antwort = {'ok': True, 'pid': pid, 'ab': ab, 'wartet': bool(hinter)}
        if hinter:
            antwort['meldung'] = ablage.stand().get('detail') or 'In der Warteschlange'
            antwort['hinter'] = hinter
        return antwort

    @staticmethod
    @require_GET
    def einstellungen(request):
        format = Blendimportformate.pruefen(request.GET.get('format'))
        letzte = []
        for kennung in Blendimportablage.alle()[:Blendimportendpunkte.LETZTE]:
            stand = Blendimportablage(kennung).stand()
            letzte.append({'kennung': kennung, 'status': stand.get('status'), 'name': (stand.get('quelle') or {}).get('name'),
                           'modell': ((stand.get('ergebnis') or {}).get('modell') or {}).get('name')})
        return JsonResponse({**Blendimportendpunkte._einstellungen(format).katalog(), 'format': format,
                             'schritte': list(Blendimportlauf.schritte_fuer(format)), 'letzte': letzte})

    @staticmethod
    @require_POST
    def pruefen(request):
        rumpf = Blendimportendpunkte._rumpf(request)
        format = Blendimportformate.pruefen(rumpf.get('format'))
        werte = Blendimportendpunkte._einstellungen(format).pruefen(rumpf)
        try:
            return JsonResponse({'ok': True, **Blendimportendpunkte._quelle(werte, format).steckbrief()})
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
            hinter = Blendimportendpunkte._hinter()
            rumpf = Blendimportendpunkte._rumpf(request)
            format = Blendimportformate.pruefen(rumpf.get('format'))
            einstellungen = Blendimportendpunkte._einstellungen(format)
            werte = einstellungen.pruefen(rumpf.get('werte'))
            try:
                quelle = Blendimportendpunkte._quelle(werte, format).steckbrief()
            except ValueError as fehler:
                return JsonResponse({'error': str(fehler)}, status=400)
            werte = einstellungen.speichern(werte)
            kennung = Auftragskennung.frei(timezone.now(), lambda k: Blendimportablage(k).ordner().exists())
            ablage = Blendimportablage(kennung)
            ablage.anlegen()
            # `modell_speichern`: der Import aus der Charakter-Seite IST der Auftrag, ein Modell zu bauen (der Dialog lädt es danach) — ein Mesh-3D-Auftrag speichert nur auf Klick
            # der Jobseite (`Mesh3dmodellspeichern`, 15.10.2026).
            ablage.stand_schreiben({'kennung': kennung, 'status': 'neu', 'quelle': quelle, 'einstellungen': werte,
                                    'angelegt': timezone.now().isoformat(), 'modell_speichern': True})
            antwort = Blendimportendpunkte._eingereiht(ablage, None, hinter)
        return JsonResponse({**antwort, 'kennung': kennung, 'quelle': quelle})

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
        # Die Schritte dieses Imports (ein Stand von vor dem 10.10.2026 kennt sie nicht): eine .blend hat kein „umwandeln".
        stand.setdefault('schritte', list(Blendimportlauf.schritte_fuer((stand.get('quelle') or {}).get('format'), stand.get('weg'))))
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
        von, bis = Blendimportlauf.baender_fuer(stand.get('weg'))['figur']
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
                # Steht er schon in der Schlange, ist das keine Fehlermeldung wert: er startet, sobald er an der Reihe ist.
                if ablage.stand().get('wartet'):
                    return JsonResponse({'ok': True, 'wartet': True, 'meldung': ablage.stand().get('detail') or 'In der Warteschlange'})
                return JsonResponse({'error': 'Der Import läuft schon'}, status=409)
            if not (ablage.stand().get('quelle') or {}).get('datei'):
                # Die Kopie ohne Daten (`Mesh3dkopie.ohne_daten`) bringt kein Netz mit: ohne Datei würde der Lauf erst im Schritt „koerper“ mit einem unverständlichen Fehler enden.
                return JsonResponse({'error': 'Dem Auftrag fehlt das Netz — „Datei wählen …“ lädt eines hoch, „Quelle übernehmen“ setzt es (die Kopie ohne Daten bringt keines mit).'}, status=400)
            hinter = Blendimportendpunkte._hinter(ausser=kennung)
            rumpf = Blendimportendpunkte._rumpf(request)
            stand = ablage.stand()
            if stand.get('modell_speichern') and not rumpf.get('modell_speichern'):
                # „Neu berechnen“ der Mesh-3D-Jobseite: auch ein Auftrag aus der Charakter-Seite speichert dann nur noch auf Klick (`Mesh3dmodellspeichern`).
                stand['modell_speichern'] = False
                ablage.stand_schreiben(stand)
            ab = rumpf.get('ab')
            ab = ab if ab in Blendimportlauf.SCHRITTE else None
            return JsonResponse(Blendimportendpunkte._eingereiht(ablage, ab, hinter))
