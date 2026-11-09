# -*- coding: utf-8 -*-
"""Ai2d3daktionsendpunkte — Löschen und Neuanlage auf `/2d-3d-AI/` (24.10.2026), wie `Mesh3daipapierkorbendpunkt` und „Neuer Test aus einem Mesh“ auf `/mesh-3D-AI/`.

    POST /api/2d3dai/loeschen/    {art: 'jobs'|'tests', ids: [...]}            → {ok, ziel, ergebnis: [{kennung, ok, fehler?}]}   (`Ai2d3dpapierkorb`: verschieben bzw. ausblenden)
    POST /api/2d3dai/test-neu/    Formular: fotos (mehrere), name               → {ok, kennung, adresse}                           (`Ai2d3dfotoneu`, ohne Rechnen)
    POST /api/2d3dai/<job>/koerpergroesse/   {koerpergroesse_m: 1.85 | null}  → {ok, koerpergroesse_m}                          (`Ai2d3dkoerpergroesse`, nur Tests)
    POST /api/2d3dai/<job>/name/             {name}                            → {ok, name}                                      (`Mesh3dainame`, nur Tests)
    POST /api/2d3dai/<job>/normalen/         {engine, foto, zusammen}          → {ok, normalen}                                  (`Ai2d3dnormalen`, nur Tests)
    POST /api/2d3dai/<job>/pshuman/          {zeile1, drehteller}   → {ok, pshuman}   (`Ai2d3dpshuman`, nur Tests)
    POST /api/2d3dai/<job>/geschlecht/       {geschlecht}           → {ok, geschlecht}   (`Ai2d3dgeschlecht`, nur Tests)
    POST /api/2d3dai/<job>/job-rechnen/                             → {ok, stand}   (`Ai2d3djoblauf`: PSHuman, Foto-Kette, Genesis)
    GET  /api/2d3dai/<job>/job-stand/                               → {stand}
    POST /api/2d3dai/<job>/genesis-rechnen/                         → {ok, kennung, adresse}   (`Ai2d3dgenesisstart`, nur Tests)
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.ai2d3dadresse import Ai2d3dadresse
from ..dienste.ai2d3dform import Ai2d3dform
from ..dienste.ai2d3dfotoneu import Ai2d3dfotoneu
from ..dienste.ai2d3dgenesisstart import Ai2d3dgenesisstart
from ..dienste.ai2d3dgeschlecht import Ai2d3dgeschlecht
from ..dienste.ai2d3djoblauf import Ai2d3djoblauf
from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.ai2d3dkoerpergroesse import Ai2d3dkoerpergroesse
from ..dienste.ai2d3dnormalen import Ai2d3dnormalen
from ..dienste.ai2d3dpapierkorb import Ai2d3dpapierkorb
from ..dienste.ai2d3dpshuman import Ai2d3dpshuman
from ..dienste.mesh3dairechenschlange import Mesh3dairechenschlange
from ..dienste.ai2d3dtextur import Ai2d3dtextur
from ..dienste.mesh3dainame import Mesh3dainame

logger = logging.getLogger('core')

__all__ = ['Ai2d3daktionsendpunkte']


class Ai2d3daktionsendpunkte:
    @staticmethod
    @require_POST
    def loeschen(request):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON'}, status=400)
        art, ids = (rumpf.get('art'), rumpf.get('ids')) if isinstance(rumpf, dict) else (None, None)
        if art not in Ai2d3dpapierkorb.ARTEN or not isinstance(ids, list) or not ids:
            return JsonResponse({'error': 'Erwartet {art: jobs|tests, ids: [...]}'}, status=400)
        aus = Ai2d3dpapierkorb.loeschen(art, ids, Ai2d3djobs.alle())
        return JsonResponse(dict(aus, ok=all(e['ok'] for e in aus['ergebnis'])))

    @staticmethod
    @require_POST
    def genesis_rechnen(request, job):
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None or gefunden.get('art') != 'foto':
            return JsonResponse({'error': 'Kein Test aus Fotos: %s' % job}, status=404)
        try:
            kennung = Ai2d3dgenesisstart.starten(gefunden)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'kennung': kennung, 'adresse': '/mesh-3D-AI/test/%s/' % kennung})

    @staticmethod
    @require_POST
    def job_rechnen(request, job):
        """Knopf „Job rechnen“: PSHuman, Foto-Kette (mit Häkchen) und Genesis nacheinander (`Ai2d3djoblauf`)."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None or gefunden.get('art') != 'foto':
            return JsonResponse({'error': 'Kein Test aus Fotos: %s' % job}, status=404)
        try:
            return JsonResponse({'ok': True, 'stand': Mesh3dairechenschlange.job_starten(gefunden)})
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)

    @staticmethod
    @require_GET
    def job_stand(request, job):
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None or gefunden.get('art') != 'foto':
            return JsonResponse({'error': 'Kein Test aus Fotos: %s' % job}, status=404)
        return JsonResponse({'stand': Ai2d3djoblauf(gefunden).stand_fuer_seite()})

    @staticmethod
    @require_POST
    def neu(request):
        try:
            kennung = Ai2d3dfotoneu.anlegen(request.POST.get('name'), request.FILES.getlist('fotos'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'kennung': kennung, 'adresse': '/2d-3d-AI/test/%s/' % kennung})

    @staticmethod
    @require_POST
    def koerpergroesse(request, job):
        """Die Körpergröße der Person eines Tests in seine job.json (`Ai2d3dkoerpergroesse`), Feld oben auf der Testseite."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict) or Ai2d3dkoerpergroesse.FELD not in rumpf:
                raise ValueError('Erwartet {%s: Meter | null}' % Ai2d3dkoerpergroesse.FELD)
            meter = Ai2d3dkoerpergroesse.setzen(gefunden, rumpf[Ai2d3dkoerpergroesse.FELD])
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Ai2d3dkoerpergroesse.FELD: meter})

    @staticmethod
    @require_POST
    def normalen(request, job):
        """Normalen-Engine eines Tests in seine job.json (`Ai2d3dnormalen`), Combo-Boxen oben auf der Testseite."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict):
                raise ValueError('Erwartet {engine, foto, zusammen}')
            wahl = Ai2d3dnormalen.setzen(gefunden, rumpf)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Ai2d3dnormalen.FELD: wahl})

    @staticmethod
    @require_POST
    def textur(request, job):
        """Textur-Engine eines Tests in seine job.json (`Ai2d3dtextur`, Combo-Box „Textur“)."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict):
                raise ValueError('Erwartet {engine}')
            wahl = Ai2d3dtextur.setzen(gefunden, rumpf)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Ai2d3dtextur.FELD: wahl})

    @staticmethod
    @require_POST
    def form(request, job):
        """Form-Engine eines Tests in seine job.json (`Ai2d3dform`, Combo-Box „Form“ mit Checkboxen)."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict):
                raise ValueError('Erwartet {engine, bilder, finger}')
            wahl = Ai2d3dform.setzen(gefunden, rumpf)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Ai2d3dform.FELD: wahl})

    @staticmethod
    @require_POST
    def pshuman(request, job):
        """PSHuman-Weg eines Tests in seine job.json (`Ai2d3dpshuman`, Combo-Box „PSHuman“)."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict):
                raise ValueError('Erwartet {zeile1, drehteller}')
            wahl = Ai2d3dpshuman.setzen(gefunden, rumpf)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Ai2d3dpshuman.FELD: wahl})

    @staticmethod
    @require_POST
    def geschlecht(request, job):
        """Genesis-Grundfigur eines Tests in seine job.json und seinen Mesh3D-AI-Test (`Ai2d3dgeschlecht`, Auswahl „Genesis“)."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict) or Ai2d3dgeschlecht.FELD not in rumpf:
                raise ValueError('Erwartet {%s}' % Ai2d3dgeschlecht.FELD)
            wert = Ai2d3dgeschlecht.setzen(gefunden, rumpf[Ai2d3dgeschlecht.FELD])
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Ai2d3dgeschlecht.FELD: wert})

    @staticmethod
    @require_POST
    def name(request, job):
        """Den Namen eines Tests ändern (24.10.2026, Edgar: „hast den Stift wieder vergessen, mit dem ich den Job umbenennen kann. das war drin bei mesh3d-AI job!“) — derselbe Stift
        (`gemeinsam/auftragname.js`) und dieselbe Ablage wie Mesh3D-AI: `name.json` im Testordner (`Mesh3dainame`), die job.json bleibt; die Kennung bleibt, die Adresse folgt dem Namen (`Ai2d3dadresse`)."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None or gefunden.get('art') != 'foto':
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON mit name'}, status=400)
        try:
            name = Mesh3dainame.setzen(gefunden['ordner'], rumpf.get('name') if isinstance(rumpf, dict) else None, gefunden['name_vorgabe'])
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        logger.info('2d-3d-AI Test %s umbenannt: „%s“ → „%s“ (ursprünglich „%s“)', gefunden['id'], gefunden['name'], name, gefunden['name_vorgabe'])
        return JsonResponse({'ok': True, 'name': name, 'adresse': Ai2d3dadresse.seite(Ai2d3djobs.job(gefunden['id']))})
