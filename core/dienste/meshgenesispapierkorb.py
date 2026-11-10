# -*- coding: utf-8 -*-
"""Meshgenesispapierkorb — gewählte Jobs und Tests von `/mesh-genesis/` beiseitelegen (23.10.2026).

Edgar: „mach bei den Jobs die Auswahl-Checkboxen und dann die Buttons zum Löschen“ (Reiter „Jobs“ und „Test“). „Löschen“ heißt hier wie am 20.10.2026 (`Meshgenesisattrappe.BEISEITE`):
der Ordner wird VERSCHOBEN, nicht gelöscht — nach `3DObjects/meshgenesis/_beiseite/<JJJJ.MM.TT.HH.MM.SS>_geloescht/jobs|tests/<Ordner>`. Zurückholen = Ordner zurückschieben.
Danach fehlt der Job in Tabelle und Menü (`Meshgenesisattrappe.stammdaten` nimmt einen festen Job nur, wenn sein Ordner da ist; ein Tripo-Job ist nur sein Ordner mit `paar.json`),
der Test in der Liste (`Meshgenesistest.alle` liest die Ordner unter `_test/`).

Der Test eines Foto-Genesis-Jobs bleibt (06.11.2026, Edgar: „die jobs sollten immer unabhängig voneinander sein“): Er trägt das Ergebnis des Jobs (`Meshgenesisjobtest`), löschen geht nur am Job (`Fotogenesispapierkorb`).

Gelöscht werden nur Kennungen, die die Liste kennt — kein Pfad aus der Anfrage. Ein Ordner, den ein laufender Prozess offen hält, lässt Windows nicht verschieben: der Fehler steht im Ergebnis.
"""
import logging
import shutil
import time
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Meshgenesispapierkorb']


class Meshgenesispapierkorb:
    ARTEN = ('jobs', 'tests')

    @staticmethod
    def wurzel():
        return Path(settings.OBJECTS_ROOT) / 'meshgenesis'

    @classmethod
    def ziel(cls, stempel, art):
        return cls.wurzel() / '_beiseite' / ('%s_geloescht' % stempel) / art

    @classmethod
    def ordner_der_jobs(cls):
        """{Kennung: Ordner} aller Jobs der Tabelle (feste Jobs und Tripo-Jobs)."""
        from .meshgenesisattrappe import Meshgenesisattrappe
        return {j['id']: cls.wurzel() / j['ordner'] for j in Meshgenesisattrappe.stammdaten()}

    @classmethod
    def ordner_der_tests(cls):
        """{Kennung: Ordner} aller Tests der Liste (mit Tripo-Jobs, wie der Reiter „Test“) — auch angelegte, noch nicht gerechnete (`anlage.json`, `Meshgenesistest.angelegt`)."""
        from .meshgenesistest import Meshgenesistest
        aus = {}
        for p in Meshgenesistest.ordner().iterdir() if Meshgenesistest.ordner().is_dir() else ():
            if ((p / 'test.json').is_file() or (p / 'anlage.json').is_file()) and '_beiseite_' not in p.name:
                aus[p.name] = p
        return aus

    @classmethod
    def loeschen(cls, art, kennungen):
        """→ {'ziel': Ordner, 'ergebnis': [{kennung, ok, fehler?}]}; `art` 'jobs' oder 'tests'."""
        if art not in cls.ARTEN:
            raise ValueError('Unbekannte Art „%s“' % art)
        from .meshgenesisjobtest import Meshgenesisjobtest
        bekannt = cls.ordner_der_jobs() if art == 'jobs' else cls.ordner_der_tests()
        zum_job = Meshgenesisjobtest.kennungen() if art == 'tests' else set()
        stempel = time.strftime('%Y.%m.%d.%H.%M.%S')
        ziel = cls.ziel(stempel, art)
        ergebnis = []
        for k in kennungen:
            k = str(k)
            quelle = bekannt.get(k)
            if quelle is None or not quelle.is_dir():
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': 'nicht in der Liste'})
                continue
            if k in zum_job:
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': 'gehört zu einem Job von Foto-Genesis, dort löschen'})
                continue
            try:
                ziel.mkdir(parents=True, exist_ok=True)
                shutil.move(str(quelle), str(ziel / quelle.name))
                ergebnis.append({'kennung': k, 'ok': True})
                logger.info('Mesh-Genesis: %s „%s“ beiseitegelegt: %s → %s', art, k, quelle, ziel / quelle.name)
            except OSError as fehler:
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': str(fehler)})
                logger.warning('Mesh-Genesis: %s „%s“ nicht verschoben: %s', art, k, fehler)
        return {'ziel': str(ziel), 'ergebnis': ergebnis}
