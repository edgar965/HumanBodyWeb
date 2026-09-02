# -*- coding: utf-8 -*-
"""Auslieferung von BVH-, Video- und Erkennungsdateien EINES Auftrags.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.

UMBAU 18.08.2026 (Befund `freie-funktionen`, Kriterium 1): Die Arbeit steht in

    dienste/videoauslieferung.py  Video finden und mit `Range` ausliefern
    dienste/videoablage.py        fertige Videos in den Ausgabeordner
    daten/dateigroessen.py        Groessenangabe fuer die Auftragsliste

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `klassenreif` Frage 2): Es blieben
dreizehn freie Funktionen, und NEUN davon begannen mit derselben Zeile —
`get_object_or_404(BVHJob, id=job_id)`. Genau das meint „dieselben Werte durch
mehrere Funktionen faedeln": Der Auftrag ist der Zustand, den alle teilen. Er
wird jetzt EINMAL im Konstruktor aufgeloest; die Endpunkte sind Methoden.

DABEI GEFUNDEN (18.08.2026): `_serve_retarget_job_impl` holte
`retarget_bvh_data` aus `core.character_api` -- die Datei ist beim Umbau am
15.08.2026 in `core/api/` aufgegangen und existiert nicht mehr. Damit war
`/api/bvh/<auftrag>/?mode=retarget` tot. Ein Import IN einer Funktion faellt
weder beim Start noch dem Werkzeug `tote-importe` auf -- nur beim Aufruf.
"""

import logging
import os
from pathlib import Path

from django.conf import settings
from django.http import (
    FileResponse, HttpResponse, HttpResponseNotFound, JsonResponse,
)
from django.shortcuts import get_object_or_404

from ..dienste.keypoints import Ueberlagerungspunkte
from ..dienste.retargetdaten import Retargetdaten
from ..dienste.skelettvideo import Skelettfilm
from ..dienste.videoablage import Videoablage
from ..dienste.videoauslieferung import Videoauslieferung
from ..models import BVHJob

logger = logging.getLogger('core')


class Auftragsdateien:
    """Alles, was zu EINEM Auftrag heruntergeladen werden kann.

    Jeder Einstieg ist eine Klassenmethode mit der Signatur, die Django
    erwartet (`request, job_id`); sie baut die Instanz und arbeitet damit.
    Der Auftrag wird dabei genau einmal aufgeloest.
    """

    def __init__(self, request, job_id):
        self.request = request
        self.job = get_object_or_404(BVHJob, id=job_id)

    # ------------------------------------------------------------ Bewegung

    @classmethod
    def bvh(cls, request, job_id):
        """Vereinheitlichter Bewegungsendpunkt.

        GET /api/bvh/<job_id>/                  -> BVH-Datei im Klartext
        GET /api/bvh/<job_id>/?mode=retarget    -> Rigify/DEF-Quaternionen
        GET /api/bvh/<job_id>/?mode=keypoints2d -> 2D-Punkte zum Ueberlagern

        Fuer `mode=retarget`: `body_height` (Vorgabe 1.68), `format` (sonst
        erkannt), `foot_correction` (Vorgabe aus).
        """
        selbst = cls(request, job_id)
        art = request.GET.get('mode', 'bvh')
        if art == 'keypoints2d':
            return JsonResponse(Ueberlagerungspunkte(selbst.job).daten())
        if art == 'retarget':
            return selbst._retarget()
        return selbst._bewegungsdatei()

    def _bewegungsdatei(self):
        pfad = self.job.bvh_file
        # Rueckfall: Beim Hybridlauf kann der Koerper scheitern und das Gesicht
        # gelingen — dann ist die Gesichtsdatei alles, was es gibt.
        if (not pfad or not os.path.exists(pfad)) and self.job.bvh_file_face \
                and os.path.exists(self.job.bvh_file_face):
            pfad = self.job.bvh_file_face
        if not pfad or not os.path.exists(pfad):
            return HttpResponseNotFound('BVH file not found')
        return self.textantwort(pfad)

    def _retarget(self):
        """Die BVH des Auftrags auf das Rigify/DEF-Skelett uebertragen."""
        if not self.job.bvh_file:
            return HttpResponseNotFound('Job has no BVH file')
        if not os.path.isfile(self.job.bvh_file):
            return HttpResponseNotFound('BVH file not found: %s'
                                        % self.job.bvh_file)
        werte = self.request.GET
        return JsonResponse(Retargetdaten(
            self.job.bvh_file,
            float(werte.get('body_height', 1.68)),
            werte.get('format', None),
            werte.get('foot_correction', '').lower() in ('1', 'true'),
        ).holen().als_dict())

    @classmethod
    def bvh_gesicht(cls, request, job_id):
        """Die Gesicht+Haende-BVH der Hybrid-Pipeline."""
        selbst = cls(request, job_id)
        gesicht = selbst.job.bvh_file_face
        if not gesicht or not os.path.exists(gesicht):
            return HttpResponseNotFound('Face BVH file not found')
        return selbst.textantwort(gesicht)

    @classmethod
    def punkte_2d(cls, request, job_id):
        """Aeltere Adresse — dasselbe wie `bvh(?mode=keypoints2d)`."""
        return JsonResponse(
            Ueberlagerungspunkte(cls(request, job_id).job).daten())

    # --------------------------------------------------------------- Video

    @classmethod
    def video(cls, request, job_id):
        """Das hochgeladene Video, ersatzweise das aus dem Ausgabeordner."""
        return Videoauslieferung(cls(request, job_id).job).antwort(request)

    #: Kantenlängen des Vorschaubilds.
    VORSCHAU_BREITE = 160
    VORSCHAU_HOEHE = 90
    #: JPEG-Güte — Vorschaubilder sind 160 Pixel breit, mehr bringt nichts.
    VORSCHAU_GUETE = 75

    @classmethod
    def vorschaubild(cls, request, job_id):
        """Bild 0 des Videos als JPEG.

        JEDER FEHLSCHLAG WIRD PROTOKOLLIERT (28.08.2026): Hier stand
        `except Exception: return 404` ohne eine einzige Logzeile. Auf
        `/process/list/` liefen dadurch drei Anfragen ins Leere, und im Log
        stand nichts — weder „Video weg" noch „cv2 fehlt". Die Browserprobe
        hat es gefunden, nicht das Fehlerlog.

        Der häufigste Fall ist harmlos: Das Video wurde verschoben oder
        gelöscht, der Auftrag zeigt noch auf den alten Pfad. Er wird deshalb
        als Warnung gemeldet, nicht als Fehler — aber gemeldet.
        """
        selbst = cls(request, job_id)
        pfad = Path(settings.MEDIA_ROOT) / str(selbst.job.video_file)
        if not pfad.is_file():
            logger.warning('Vorschaubild %s: Video liegt nicht (mehr) '
                           'unter %s', job_id, pfad)
            return HttpResponseNotFound('Video file missing')
        try:
            return cls._vorschau_aus(pfad)
        except ImportError:
            logger.warning('Vorschaubild %s: cv2 fehlt in dieser Umgebung',
                           job_id, exc_info=True)
            return HttpResponseNotFound('Thumbnail generation failed')
        except Exception:                                    # noqa: BLE001
            logger.warning('Vorschaubild %s aus %s nicht erzeugbar',
                           job_id, pfad, exc_info=True)
            return HttpResponseNotFound('Thumbnail generation failed')

    @classmethod
    def _vorschau_aus(cls, pfad):
        """Erstes Bild lesen, verkleinern, als JPEG zurückgeben."""
        import cv2
        aufnahme = cv2.VideoCapture(str(pfad))
        try:
            gelesen, bild = aufnahme.read()
        finally:
            aufnahme.release()
        if not gelesen:
            logger.warning('Vorschaubild: %s hat kein lesbares erstes Bild',
                           pfad)
            return HttpResponseNotFound('Could not read video frame')
        hoehe, breite = bild.shape[:2]
        faktor = min(cls.VORSCHAU_BREITE / breite, cls.VORSCHAU_HOEHE / hoehe)
        bild = cv2.resize(bild, (int(breite * faktor), int(hoehe * faktor)))
        _, jpeg = cv2.imencode('.jpg', bild,
                               [cv2.IMWRITE_JPEG_QUALITY, cls.VORSCHAU_GUETE])
        return HttpResponse(jpeg.tobytes(), content_type='image/jpeg')

    @classmethod
    def erkennungsdaten(cls, request, job_id):
        """Erkennungs-Flags je Bild als JSON fuer den BVH-Spieler."""
        selbst = cls(request, job_id)
        datei = (Path(settings.MEDIA_ROOT) / 'output' / str(selbst.job.id)
                 / 'detection.json')
        if not datei.exists():
            # Alte Auftraege haben keine Erkennungsdaten — leere Liste statt
            # 404, damit der Spieler nicht in den Fehlerzweig laeuft.
            return JsonResponse([], safe=False)
        antwort = FileResponse(open(datei, 'rb'),
                               content_type='application/json')
        antwort['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return antwort

    # ------------------------------------------------------- Skelettvideos

    @classmethod
    def skelettvideo(cls, request, job_id):
        """Nur das Skelett: weiss auf schwarz."""
        selbst = cls(request, job_id)
        return selbst._rendern(False, '%s_%s_rig_only.mp4'
                               % (selbst.job.pipeline,
                                  Path(selbst.job.name).stem))

    @classmethod
    def ueberlagerungsvideo(cls, request, job_id):
        """Das Video mit dem Skelett darueber."""
        selbst = cls(request, job_id)
        return selbst._rendern(True, '%s_skeleton.mp4'
                               % Path(selbst.job.name).stem)

    def _rendern(self, ueberlagern, dateiname):
        """Video rendern, in den Ausgabeordner legen und herunterladen."""
        pfad = Skelettfilm(self.job, ueberlagern=ueberlagern).erzeugen()
        if not pfad or not pfad.exists():
            art = 'overlay' if ueberlagern else 'rig'
            return HttpResponseNotFound('Could not render %s video' % art)
        Videoablage.kopieren(pfad, dateiname)
        return FileResponse(open(pfad, 'rb'), content_type='video/mp4',
                            filename=dateiname)

    @classmethod
    def video3d_sichern(cls, request, job_id):
        """Das im Browser aufgezeichnete 3D-Video in den Ausgabeordner."""
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required'}, status=405)
        selbst = cls(request, job_id)
        hochgeladen = request.FILES.get('video')
        if not hochgeladen:
            return JsonResponse({'error': 'No video file'}, status=400)
        ziel = Videoablage.schreiben(
            hochgeladen, '%s_3d_character.webm' % Path(selbst.job.name).stem)
        return JsonResponse({'ok': True, 'path': str(ziel)})

    # ---------------------------------------------------------------- Hilfe

    @staticmethod
    def textantwort(pfad):
        """BVH-Text ohne Zwischenspeicher -- er aendert sich beim Bearbeiten."""
        antwort = FileResponse(open(pfad, 'rb'), content_type='text/plain',
                               filename=os.path.basename(pfad))
        antwort['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return antwort
