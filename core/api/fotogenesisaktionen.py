# -*- coding: utf-8 -*-
"""Fotogenesisaktionsendpunkte — Löschen und Neuanlage auf `/foto-genesis/` (24.10.2026), wie `Meshgenesispapierkorbendpunkt` und „Neuer Test aus einem Mesh“ auf `/mesh-genesis/`.

    POST /api/fotogenesis/loeschen/    {art: 'jobs'|'tests', ids: [...]}            → {ok, ziel, ergebnis: [{kennung, ok, fehler?}]}   (`Fotogenesispapierkorb`: verschieben bzw. ausblenden)
    POST /api/fotogenesis/test-neu/    Formular: fotos (mehrere), name               → {ok, kennung, adresse}                           (`Fotogenesisfotoneu`, ohne Rechnen)
    POST /api/fotogenesis/<job>/koerpergroesse/   {koerpergroesse_m: 1.85 | null}  → {ok, koerpergroesse_m}                          (`Fotogenesiskoerpergroesse`, nur Tests)
    POST /api/fotogenesis/<job>/name/             {name}                            → {ok, name}                                      (`Meshgenesisname`, nur Tests)
    POST /api/fotogenesis/<job>/normalen/         {engine, foto, zusammen}          → {ok, normalen}                                  (`Fotogenesisnormalen`, nur Tests)
    POST /api/fotogenesis/<job>/pshuman/          {zeile1, drehteller}   → {ok, pshuman}   (`Fotogenesispshuman`, nur Tests)
    POST /api/fotogenesis/<job>/geschlecht/       {geschlecht}           → {ok, geschlecht}   (`Fotogenesisgeschlecht`, nur Tests)
    POST /api/fotogenesis/<job>/job-rechnen/                             → {ok, stand}   (`Fotogenesisjoblauf`: PSHuman, Foto-Kette, Genesis)
    GET  /api/fotogenesis/<job>/job-stand/                               → {stand}
    POST /api/fotogenesis/<job>/genesis-rechnen/                         → {ok, kennung, adresse}   (`Fotogenesisgenesisstart`, nur Tests)
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.fotogenesisadresse import Fotogenesisadresse
from ..dienste.fotogenesisform import Fotogenesisform
from ..dienste.fotogenesisfotoneu import Fotogenesisfotoneu
from ..dienste.fotogenesisgenesisstart import Fotogenesisgenesisstart
from ..dienste.fotogenesisgeschlecht import Fotogenesisgeschlecht
from ..dienste.fotogenesisjoblauf import Fotogenesisjoblauf
from ..dienste.fotogenesisjobs import Fotogenesisjobs
from ..dienste.fotogenesiskoerpergroesse import Fotogenesiskoerpergroesse
from ..dienste.fotogenesisnormalen import Fotogenesisnormalen
from ..dienste.fotogenesispapierkorb import Fotogenesispapierkorb
from ..dienste.fotogenesispshuman import Fotogenesispshuman
from ..dienste.meshgenesisrechenschlange import Meshgenesisrechenschlange
from ..dienste.fotogenesistextur import Fotogenesistextur
from ..dienste.meshgenesisname import Meshgenesisname

logger = logging.getLogger('core')

__all__ = ['Fotogenesisaktionsendpunkte']


class Fotogenesisaktionsendpunkte:
    @staticmethod
    @require_POST
    def loeschen(request):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON'}, status=400)
        art, ids = (rumpf.get('art'), rumpf.get('ids')) if isinstance(rumpf, dict) else (None, None)
        if art not in Fotogenesispapierkorb.ARTEN or not isinstance(ids, list) or not ids:
            return JsonResponse({'error': 'Erwartet {art: jobs|tests, ids: [...]}'}, status=400)
        aus = Fotogenesispapierkorb.loeschen(art, ids, Fotogenesisjobs.alle())
        return JsonResponse(dict(aus, ok=all(e['ok'] for e in aus['ergebnis'])))

    @staticmethod
    @require_POST
    def genesis_rechnen(request, job):
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None or gefunden.get('art') != 'foto':
            return JsonResponse({'error': 'Kein Test aus Fotos: %s' % job}, status=404)
        try:
            kennung = Fotogenesisgenesisstart.starten(gefunden)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'kennung': kennung, 'adresse': '/mesh-genesis/test/%s/' % kennung})

    @staticmethod
    @require_POST
    def job_rechnen(request, job):
        """Knopf „Job rechnen“: PSHuman, Foto-Kette (mit Häkchen) und Genesis nacheinander (`Fotogenesisjoblauf`)."""
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None or gefunden.get('art') != 'foto':
            return JsonResponse({'error': 'Kein Test aus Fotos: %s' % job}, status=404)
        try:
            return JsonResponse({'ok': True, 'stand': Meshgenesisrechenschlange.job_starten(gefunden)})
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)

    @staticmethod
    @require_GET
    def job_stand(request, job):
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None or gefunden.get('art') != 'foto':
            return JsonResponse({'error': 'Kein Test aus Fotos: %s' % job}, status=404)
        return JsonResponse({'stand': Fotogenesisjoblauf(gefunden).stand_fuer_seite()})

    @staticmethod
    @require_POST
    def neu(request):
        try:
            kennung = Fotogenesisfotoneu.anlegen(request.POST.get('name'), request.FILES.getlist('fotos'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'kennung': kennung, 'adresse': '/foto-genesis/test/%s/' % kennung})

    @staticmethod
    @require_POST
    def koerpergroesse(request, job):
        """Die Körpergröße der Person eines Tests in seine job.json (`Fotogenesiskoerpergroesse`), Feld oben auf der Testseite."""
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict) or Fotogenesiskoerpergroesse.FELD not in rumpf:
                raise ValueError('Erwartet {%s: Meter | null}' % Fotogenesiskoerpergroesse.FELD)
            meter = Fotogenesiskoerpergroesse.setzen(gefunden, rumpf[Fotogenesiskoerpergroesse.FELD])
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Fotogenesiskoerpergroesse.FELD: meter})

    @staticmethod
    @require_POST
    def normalen(request, job):
        """Normalen-Engine eines Tests in seine job.json (`Fotogenesisnormalen`), Combo-Boxen oben auf der Testseite."""
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict):
                raise ValueError('Erwartet {engine, foto, zusammen}')
            wahl = Fotogenesisnormalen.setzen(gefunden, rumpf)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Fotogenesisnormalen.FELD: wahl})

    @staticmethod
    @require_POST
    def textur(request, job):
        """Textur-Engine eines Tests in seine job.json (`Fotogenesistextur`, Combo-Box „Textur“)."""
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict):
                raise ValueError('Erwartet {engine}')
            wahl = Fotogenesistextur.setzen(gefunden, rumpf)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Fotogenesistextur.FELD: wahl})

    @staticmethod
    @require_POST
    def form(request, job):
        """Form-Engine eines Tests in seine job.json (`Fotogenesisform`, Combo-Box „Form“ mit Checkboxen)."""
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict):
                raise ValueError('Erwartet {engine, bilder, finger}')
            wahl = Fotogenesisform.setzen(gefunden, rumpf)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Fotogenesisform.FELD: wahl})

    @staticmethod
    @require_POST
    def pshuman(request, job):
        """PSHuman-Weg eines Tests in seine job.json (`Fotogenesispshuman`, Combo-Box „PSHuman“)."""
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict):
                raise ValueError('Erwartet {zeile1, drehteller}')
            wahl = Fotogenesispshuman.setzen(gefunden, rumpf)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Fotogenesispshuman.FELD: wahl})

    @staticmethod
    @require_POST
    def geschlecht(request, job):
        """Genesis-Grundfigur eines Tests in seine job.json und seinen Mesh-Genesis-Test (`Fotogenesisgeschlecht`, Auswahl „Genesis“)."""
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict) or Fotogenesisgeschlecht.FELD not in rumpf:
                raise ValueError('Erwartet {%s}' % Fotogenesisgeschlecht.FELD)
            wert = Fotogenesisgeschlecht.setzen(gefunden, rumpf[Fotogenesisgeschlecht.FELD])
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Fotogenesisgeschlecht.FELD: wert})

    @staticmethod
    @require_POST
    def name(request, job):
        """Den Namen eines Tests ändern (24.10.2026, Edgar: „hast den Stift wieder vergessen, mit dem ich den Job umbenennen kann. das war drin bei mesh3d-AI job!“) — derselbe Stift
        (`gemeinsam/auftragname.js`) und dieselbe Ablage wie Mesh-Genesis: `name.json` im Testordner (`Meshgenesisname`), die job.json bleibt; die Kennung bleibt, die Adresse folgt dem Namen (`Fotogenesisadresse`)."""
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None or gefunden.get('art') != 'foto':
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON mit name'}, status=400)
        try:
            name = Meshgenesisname.setzen(gefunden['ordner'], rumpf.get('name') if isinstance(rumpf, dict) else None, gefunden['name_vorgabe'])
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        logger.info('Foto-Genesis Test %s umbenannt: „%s“ → „%s“ (ursprünglich „%s“)', gefunden['id'], gefunden['name'], name, gefunden['name_vorgabe'])
        return JsonResponse({'ok': True, 'name': name, 'adresse': Fotogenesisadresse.seite(Fotogenesisjobs.job(gefunden['id']))})
