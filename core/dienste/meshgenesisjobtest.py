# -*- coding: utf-8 -*-
"""Meshgenesisjobtest — welche Mesh-Genesis-Tests zu einem Foto-Genesis-Job gehören.

Edgar, 06.11.2026: „warum die neuen Jobs 2d-3d-ai auch hier erscheinen“, „das ist ein bug“.
Das Genesis-Ergebnis eines Jobs ist ein Test unter `_test/` (job.json `meshgenesis_test`, `Fotogenesisgenesiszeile`).
Er gehört zur Jobseite, nicht in den Reiter „Test“ von `/mesh-genesis/`: Dort wurden am 06.11.2026 zwischen
14:24 und 14:26 solche Tests in den Papierkorb gelegt, und den Jobs fehlte danach ihre Genesis-Zeile.
Dasselbe am 25.10.2026 mit `edgar_foto` (`Fotogenesisfigur`).

Ein Test gehört zum Job, wenn die job.json ihn nennt oder seine `anlage.json` den Namen `<Job>-mesh-genesis`
trägt (so heißt er schon, solange die Kette rechnet und die job.json ihn noch nicht nennt). Dieselbe
Zuordnung wie `Hautohneki.job_wahl` in der Kette. Die Seite des Tests bleibt über die Adresse erreichbar.

    Meshgenesisjobtest.kennungen()      # {'edgar2010_mesh_genesis', …}
"""
import json
from pathlib import Path

from django.conf import settings

from .meshgenesistest import Meshgenesistest

__all__ = ['Meshgenesisjobtest']


class Meshgenesisjobtest:
    TESTNAME = '%s-mesh-genesis'

    @staticmethod
    def _json(datei):
        """Inhalt als dict, bei fehlender oder kaputter Datei {}."""
        try:
            wert = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}
        return wert if isinstance(wert, dict) else {}

    @classmethod
    def kennungen(cls):
        """Die Kennungen aller Tests, die zu einem Job unter `3DObjects/fotogenesis/` gehören."""
        genannt, namen = set(), set()
        for datei in (Path(settings.OBJECTS_ROOT) / 'fotogenesis').glob('*/job.json'):
            test = cls._json(datei).get('meshgenesis_test')
            if test:
                genannt.add(str(test))
            namen.add(cls.TESTNAME % datei.parent.name)
        ordner = Meshgenesistest.ordner()
        if not ordner.is_dir():
            return genannt
        benannt = {p.name for p in ordner.iterdir() if cls._json(p / 'anlage.json').get('name') in namen}
        return genannt | benannt
