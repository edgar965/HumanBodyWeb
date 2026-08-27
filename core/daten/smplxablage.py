# -*- coding: utf-8 -*-
"""Smplxablage — wo die SMPL-X-Ergebnisse eines Fotoauftrags liegen.

`HumanBody/data/photoTo3D/SMPLX/<auftrag>.npz` (und `.json`) wurde an VIER
Stellen einzeln zusammengesetzt (`api/fotoabgleich`, `api/fotoauftraege`,
`dienste/smplx_archiv`, `dienste/texturbacken`). Beim Loeschen eines Auftrags
raeumt die eine Stelle, beim Lesen sucht die naechste — laufen sie auseinander,
bleiben Dateien liegen, die niemand mehr findet.

DER ORDNERNAME IST GEMISCHT GESCHRIEBEN, UND DAS BLEIBT SO
==========================================================
`photoTo3D` ist ein Verzeichnis auf der Platte, `photo_to_3d` die Adresse der
Seite. Das Werkzeug `namensvarianten` meldet beide als „dasselbe Ding, zwei
Schreibweisen" — hier ist es das nicht: Der Ordner traegt seinen Namen seit dem
ersten Lauf und enthaelt Produktivdaten. Umbenennen hiesse, die Ergebnisse aller
bisherigen Auftraege wegzuwerfen. Der Name steht deshalb GENAU EINMAL, hier.
"""

import os

from django.conf import settings


class Smplxablage:
    """Der Ordner mit den SMPL-X-Ergebnissen und die Dateien darin."""

    #: Verzeichnisname auf der Platte. Gemischte Schreibweise — siehe oben.
    ORDNER = 'photoTo3D'
    #: Unterordner der SMPL-X-Ausgabe.
    UNTERORDNER = 'SMPLX'
    #: Dateiendungen, die je Auftrag entstehen.
    ENDUNGEN = ('.json', '.npz')

    @classmethod
    def verzeichnis(cls):
        return os.path.join(str(settings.BASE_DIR), '..', 'HumanBody', 'data',
                            cls.ORDNER, cls.UNTERORDNER)

    @classmethod
    def datei(cls, job_id, endung='.npz'):
        return os.path.join(cls.verzeichnis(), '%s%s' % (job_id, endung))

    @classmethod
    def dateien(cls, job_id):
        """Alle Dateien EINES Auftrags — zum Aufraeumen."""
        return [cls.datei(job_id, endung) for endung in cls.ENDUNGEN]
