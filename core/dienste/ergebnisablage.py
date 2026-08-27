# -*- coding: utf-8 -*-
"""Ergebnisablage — die fertige BVH in den gemeinsamen Ergebnisordner.

Stand bis zum 27.08.2026 als `_copy_bvh_to_results` in
`core/api/bibliothek.py` — also in einem ENDPUNKT-Modul, obwohl kein Endpunkt
sie ruft: Die vier Aufrufstellen liegen alle in `pipelines/auftragslauf.py`
und holen sie mit einem Import IN der Funktion. Genau deshalb sah sie beim
Umbau tot aus.

Der Name der Zieldatei ist `<videoname ohne Endung>_<pipeline>.bvh`; eine
vorhandene Datei wird ueberschrieben. Das ist gewollt: Ein zweiter Lauf
derselben Pipeline auf demselben Video ersetzt sein eigenes Ergebnis.
"""

import shutil
from pathlib import Path

from django.conf import settings


class Ergebnisablage:
    """Der gemeinsame Ergebnisordner aller Pipelines."""

    @staticmethod
    def ordner():
        pfad = Path(settings.BVH_RESULTS_DIR)
        pfad.mkdir(parents=True, exist_ok=True)
        return pfad

    @classmethod
    def kopieren(cls, bvh_pfad, videoname, pipeline):
        """Kopiert die BVH und gibt den Zielpfad zurueck."""
        stamm = videoname.rsplit('.', 1)[0]
        ziel = cls.ordner() / ('%s_%s.bvh' % (stamm, pipeline))
        shutil.copy2(str(bvh_pfad), str(ziel))
        return str(ziel)
