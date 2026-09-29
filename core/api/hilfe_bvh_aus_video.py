# -*- coding: utf-8 -*-
"""Hilfe -> BVH aus Video: die eigene SMPL-X-Pipeline, eigenständig statt als
Abschnitt der Vergleichsseite, mit einem herunterladbaren Startskript.

Auftrag Edgar (29.09.2026): „mach eine Seite Hilfe - BVH aus Video wo du die
aktuelle Pipeline SMPL-X (eigen) beschreibst … und ein Skript erstellst
(downloadbar) wie man aus einem Video ein SMPLX Modell mit Animation
erstellt."

Die Beschreibung kommt aus `core.dienste.eigenepipeline.Eigenepipeline` —
derselben Quelle wie der Abschnitt auf „Hilfe -> Video to BVH" (12.09.2026),
nicht verdoppelt. Das Startskript liegt echt auf der Platte
(`Docu/downloads/bvh_aus_video_starten.py`) und wird nur ausgeliefert, nicht
hier erzeugt — was heruntergeladen wird, ist dasselbe, was im Repo steht und
getestet ist.
"""
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound

from ..dienste.eigenepipeline import Eigenepipeline
from ..pipelines.smplbefehl import Smplbefehl
from .hilfeseite import Hilfeseite

#: Wo das Startskript liegt — eine Konstante, damit Seite und Download
#: denselben Pfad kennen und keiner ihn zweimal tippt.
SKRIPT_PFAD = Path(settings.BASE_DIR) / 'Docu' / 'downloads' / 'bvh_aus_video_starten.py'


class BvhAusVideo(Hilfeseite):
    """Beschreibung der SMPL-X-Pipeline plus Anleitung/Download zum Selbermachen."""

    template_name = 'hilfe/bvh_aus_video.html'
    AKTIV = 'hilfe_bvh_aus_video'

    def kontext(self):
        return {
            'eigene': Eigenepipeline.kontext(),
            'quellen_vorgabe': Smplbefehl.SMPLX_QUELLEN,
            'skript_name': SKRIPT_PFAD.name,
        }


def skript_download(request):
    """Das Startskript als Datei — echte Datei, kein Text aus der Vorlage."""
    if not SKRIPT_PFAD.is_file():
        return HttpResponseNotFound('Skript nicht gefunden: %s' % SKRIPT_PFAD)
    return FileResponse(
        open(SKRIPT_PFAD, 'rb'), content_type='text/x-python',
        as_attachment=True, filename=SKRIPT_PFAD.name,
    )
