# -*- coding: utf-8 -*-
"""Ai2d3dpapierkorb — gewählte Jobs oder Tests von `/2d-3d-AI/` beiseitelegen (24.10.2026, wie `Mesh3daipapierkorb` auf `/mesh-3D-AI/`).

Edgar: „Ich sagte eine Kopie der Mesh3d-Ai jobs … keine Jobauswahl zum Löschen usw“. „Löschen“ heißt wie dort NICHT löschen:
- **Tests** (echte Fotos, `Ai2d3dfotojobs`): der Ordner `3DObjects/ai2d3d/<Name>/` wird nach `3DObjects/ai2d3d/_beiseite/<JJJJ.MM.TT.HH.MM.SS>_geloescht/<Name>` verschoben (die Fotos, auf die
  `job.json` zeigt, bleiben, wo sie sind). Zurückholen = Ordner zurückschieben.
  Der Mesh3D-AI-Test des Jobs geht mit nach `3DObjects/mesh3dai/_beiseite/<Zeit>_geloescht/tests/` (`_test_mitnehmen`, 06.11.2026): Er trägt das Ergebnis des Jobs, ohne Job stünde er in der Liste von `/mesh-3D-AI/`.
- **Jobs** (Exporte unter `3DObjects/modelsExport/`): nur AUSGEBLENDET — `3DObjects/ai2d3d/_ausgeblendet.json` führt die Kennung. Der Exportordner gehört der Charakter-Seite und ist die Quelle der
  Mesh3D-AI-Paare (`paar.json`); ihn zu verschieben, nähme Mesh3D-AI seine Wahrheit. Zurückholen = Eintrag aus der Datei nehmen.
"""

import json
import logging
import shutil
import time
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Ai2d3dpapierkorb']


class Ai2d3dpapierkorb:
    ARTEN = ('jobs', 'tests')
    AUSGEBLENDET = '_ausgeblendet.json'

    @staticmethod
    def wurzel():
        return Path(settings.OBJECTS_ROOT) / 'ai2d3d'

    @classmethod
    def ausgeblendet(cls):
        """Kennungen der ausgeblendeten Exporte."""
        datei = cls.wurzel() / cls.AUSGEBLENDET
        try:
            return set(json.loads(datei.read_text(encoding='utf-8')).get('jobs', {}))
        except FileNotFoundError:
            return set()
        except (OSError, ValueError) as fehler:
            logger.warning('Ai2d3dpapierkorb: %s nicht lesbar (%s)', datei, fehler)
            return set()

    @classmethod
    def loeschen(cls, art, kennungen, jobs):
        """`jobs`: alle Jobs (`Ai2d3djobs.alle()`). → `{ziel, ergebnis: [{kennung, ok, fehler?}]}`"""
        stempel = time.strftime('%Y.%m.%d.%H.%M.%S')
        bekannt = {j['id']: j for j in jobs if (j['art'] == 'export') == (art == 'jobs')}
        if art == 'jobs':
            return cls._ausblenden([str(k) for k in kennungen], bekannt, stempel)
        ziel = cls.wurzel() / '_beiseite' / ('%s_geloescht' % stempel)
        ergebnis = []
        for k in (str(k) for k in kennungen):
            job = bekannt.get(k)
            if job is None or not job.get('ordner'):
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': 'kein Test dieses Namens'})
                continue
            try:
                ziel.mkdir(parents=True, exist_ok=True)
                shutil.move(str(job['ordner']), str(ziel / job['ordner'].name))
                logger.info('Ai2d3dpapierkorb: Test %s nach %s verschoben', k, ziel)
                ergebnis.append({'kennung': k, 'ok': True})
                cls._test_mitnehmen(job, jobs, stempel)
            except OSError as fehler:
                logger.warning('Ai2d3dpapierkorb: Test %s nicht verschoben (%s)', k, fehler)
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': str(fehler)})
        return {'ziel': str(ziel), 'ergebnis': ergebnis}

    @staticmethod
    def _test_mitnehmen(job, jobs, stempel):
        """Legt den Mesh3D-AI-Test von `job` mit weg. Nennt ein anderer Job denselben Test, bleibt er: Löschen darf keinen anderen Job berühren."""
        from .mesh3daipapierkorb import Mesh3daipapierkorb
        from .mesh3daitest import Mesh3daitest
        kennung = job.get('test')
        if not kennung or any(j is not job and j.get('test') == kennung for j in jobs):
            return
        quelle = Mesh3daitest.pfad(kennung) or Mesh3daitest.angelegt(kennung)
        if quelle is None:
            return
        ziel = Mesh3daipapierkorb.ziel(stempel, 'tests')
        ziel.mkdir(parents=True, exist_ok=True)
        shutil.move(str(quelle), str(ziel / quelle.name))
        logger.info('Ai2d3dpapierkorb: Test %s des Jobs %s nach %s verschoben', kennung, job['id'], ziel)

    @classmethod
    def _ausblenden(cls, kennungen, bekannt, stempel):
        datei = cls.wurzel() / cls.AUSGEBLENDET
        try:
            stand = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            stand = {}
        eintraege = stand.setdefault('jobs', {})
        ergebnis = []
        for k in kennungen:
            if k not in bekannt:
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': 'kein Job dieses Namens'})
                continue
            eintraege[k] = stempel
            ergebnis.append({'kennung': k, 'ok': True})
        datei.parent.mkdir(parents=True, exist_ok=True)
        datei.write_text(json.dumps(stand, ensure_ascii=False, indent=1), encoding='utf-8')
        logger.info('Ai2d3dpapierkorb: Jobs ausgeblendet %s (%s)', [e['kennung'] for e in ergebnis if e['ok']], datei)
        return {'ziel': str(datei), 'ergebnis': ergebnis}
