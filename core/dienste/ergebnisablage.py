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

Der Ordner ist `settings.BVH_RESULTS_DIR` — seit 12.09.2026 `A_Results`
(Edgar: „das BVH soll bitte in den _AResults ordner auch kopiert werden";
er hatte `Results` umbenannt, und die Ablage legte einen leeren `Results`
neu an). Die Ergebnisseite zeigt die Kopie mit an (`kopie_von`).
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

    @staticmethod
    def pfad(videoname, pipeline):
        """Der Zielpfad einer Kopie — ohne den Ordner anzulegen."""
        stamm = videoname.rsplit('.', 1)[0]
        return Path(settings.BVH_RESULTS_DIR) / ('%s_%s.bvh' % (stamm, pipeline))

    @classmethod
    def kopieren(cls, bvh_pfad, videoname, pipeline):
        """Kopiert die BVH und gibt den Zielpfad zurueck."""
        cls.ordner()
        ziel = cls.pfad(videoname, pipeline)
        shutil.copy2(str(bvh_pfad), str(ziel))
        return str(ziel)

    @classmethod
    def kopie_von(cls, auftrag):
        """Die Ablagekopie eines Auftrags, wenn sie liegt — sonst ''."""
        if not auftrag or not getattr(auftrag, 'bvh_file', ''):
            return ''
        ziel = cls.pfad(auftrag.name, auftrag.pipeline)
        return str(ziel) if ziel.is_file() else ''
