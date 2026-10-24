# -*- coding: utf-8 -*-
"""Mesh3daipapierkorb — gewählte Jobs und Tests von `/mesh-3D-AI/` beiseitelegen (23.10.2026).

Edgar: „mach bei den Jobs die Auswahl-Checkboxen und dann die Buttons zum Löschen“ (Reiter „Jobs“ und „Test“). „Löschen“ heißt hier wie am 20.10.2026 (`Mesh3daiattrappe.BEISEITE`):
der Ordner wird VERSCHOBEN, nicht gelöscht — nach `3DObjects/mesh3dai/_beiseite/<JJJJ.MM.TT.HH.MM.SS>_geloescht/jobs|tests/<Ordner>`. Zurückholen = Ordner zurückschieben.
Danach fehlt der Job in Tabelle und Menü (`Mesh3daiattrappe.stammdaten` nimmt einen festen Job nur, wenn sein Ordner da ist; ein Tripo-Job ist nur sein Ordner mit `paar.json`),
der Test in der Liste (`Mesh3daitest.alle` liest die Ordner unter `_test/`).

Gelöscht werden nur Kennungen, die die Liste kennt — kein Pfad aus der Anfrage. Ein Ordner, den ein laufender Prozess offen hält, lässt Windows nicht verschieben: der Fehler steht im Ergebnis.
"""
import logging
import shutil
import time
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Mesh3daipapierkorb']


class Mesh3daipapierkorb:
    ARTEN = ('jobs', 'tests')

    @staticmethod
    def wurzel():
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai'

    @classmethod
    def ziel(cls, stempel, art):
        return cls.wurzel() / '_beiseite' / ('%s_geloescht' % stempel) / art

    @classmethod
    def ordner_der_jobs(cls):
        """{Kennung: Ordner} aller Jobs der Tabelle (feste Jobs und Tripo-Jobs)."""
        from .mesh3daiattrappe import Mesh3daiattrappe
        return {j['id']: cls.wurzel() / j['ordner'] for j in Mesh3daiattrappe.stammdaten()}

    @classmethod
    def ordner_der_tests(cls):
        """{Kennung: Ordner} aller Tests der Liste (mit Tripo-Jobs, wie der Reiter „Test“) — auch angelegte, noch nicht gerechnete (`anlage.json`, `Mesh3daitest.angelegt`)."""
        from .mesh3daitest import Mesh3daitest
        aus = {}
        for p in Mesh3daitest.ordner().iterdir() if Mesh3daitest.ordner().is_dir() else ():
            if ((p / 'test.json').is_file() or (p / 'anlage.json').is_file()) and '_beiseite_' not in p.name:
                aus[p.name] = p
        return aus

    @classmethod
    def loeschen(cls, art, kennungen):
        """→ {'ziel': Ordner, 'ergebnis': [{kennung, ok, fehler?}]}; `art` 'jobs' oder 'tests'."""
        if art not in cls.ARTEN:
            raise ValueError('Unbekannte Art „%s“' % art)
        bekannt = cls.ordner_der_jobs() if art == 'jobs' else cls.ordner_der_tests()
        stempel = time.strftime('%Y.%m.%d.%H.%M.%S')
        ziel = cls.ziel(stempel, art)
        ergebnis = []
        for k in kennungen:
            k = str(k)
            quelle = bekannt.get(k)
            if quelle is None or not quelle.is_dir():
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': 'nicht in der Liste'})
                continue
            try:
                ziel.mkdir(parents=True, exist_ok=True)
                shutil.move(str(quelle), str(ziel / quelle.name))
                ergebnis.append({'kennung': k, 'ok': True})
                logger.info('Mesh3D-AI: %s „%s“ beiseitegelegt: %s → %s', art, k, quelle, ziel / quelle.name)
            except OSError as fehler:
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': str(fehler)})
                logger.warning('Mesh3D-AI: %s „%s“ nicht verschoben: %s', art, k, fehler)
        return {'ziel': str(ziel), 'ergebnis': ergebnis}
