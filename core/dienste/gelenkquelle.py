# -*- coding: utf-8 -*-
"""Gelenkquelle — 2D-Gelenkpunkte eines Auftrags lesen, egal welche Pipeline.

WARUM (17.08.2026)
=================
Es gab zwei Leser für dieselben Dateien:

    dienste/keypoints._serve_keypoints_2d_impl   für die Canvas-Überlagerung
    dienste/keypoints_quellen._get_2d_keypoints  für das gerenderte Skelettvideo

Beide wählten je Pipeline denselben Dateipfad (v4 -> `2dJoints_v4_raw.csv`,
rtmpose/vitpose/yolo11 -> `<name>_2d.csv`, sonst MediaPipe-CSV), lasen dieselben
CSV-Spalten und dieselben OpenPose-JSONs. Unterschied waren genau zwei Dinge:

    Maßstab   die Überlagerung will 0..1, der Videorenderer Pixel
    Form      dort Listen (JSON-fähig), hier Tupel

Beides sind Parameter, kein Grund für zwei Fassungen. Wer eine neue Pipeline
ergänzt, ändert jetzt EINE Stelle — vorher zwei, und beim letzten Mal ist eine
davon vergessen worden (die Überlagerung kannte `rtmpose`, das Skelettvideo
nicht).
"""

import csv
import json
import logging
from pathlib import Path

from django.conf import settings

from ..daten.gelenknamen import Gelenknamen

logger = logging.getLogger('core')


class Gelenkquelle:
    """Findet und liest die 2D-Gelenkdatei eines Auftrags."""

    #: Pipelines, die eine MocapNET-taugliche CSV `<pipeline>_2d.csv` schreiben.
    EIGENE_CSV = ('rtmpose', 'vitpose', 'yolo11')
    #: Pipelines, die über SMPL laufen — dort ist die MediaPipe-CSV die bessere
    #: Quelle als die Kameraprojektion (die kann versetzt sein).
    SMPL = ('gvhmr', 'wham', 'prompthmr', 'hybrid_gvhmr', 'hybrid_prompthmr')
    #: Rohe MediaPipe-Koordinaten. `2dJoints_v4.csv` ist fürs
    #: Seitenverhältnis korrigiert (MocapNET-Eingabe) und taugt NICHT zur
    #: Überlagerung.
    V4_ROH = '2dJoints_v4_raw.csv'

    def __init__(self, job):
        self.job = job
        self.ordner = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)

    # ------------------------------------------------------------ Dateiwahl

    def csv_pfad(self, neu_erkennen=True):
        """Die CSV zu dieser Pipeline — oder `None`.

        `neu_erkennen`: Fehlt die rohe v4-CSV, wird sie aus dem Video neu
        gewonnen (MediaPipe). Das kostet den ganzen Film und ist deshalb
        abschaltbar.
        """
        pipeline = self.job.pipeline
        if pipeline == 'v4' or pipeline in self.SMPL:
            pfad = self.ordner / self.V4_ROH
            if pfad.exists():
                return pfad
            return self._v4_neu() if neu_erkennen else None
        if pipeline in self.EIGENE_CSV:
            return self.ordner / ('%s_2d.csv' % pipeline)
        return self.ordner / 'frames-mpdata' / '2dJoints_mediapipe.csv'

    def _v4_neu(self):
        """Rohe MediaPipe-Punkte nachträglich gewinnen — Fehlschlag = `None`.

        Direkt auf `V4Neuerkennung` und NICHT über den alten Namen in
        `keypoints_quellen`: Der ruft seinerseits diese Klasse hier, und das
        Werkzeug `abhaengigkeiten` hat den Ring sofort gemeldet
        (`gelenkquelle -> keypoints_quellen -> gelenkquelle`). Dass beide Importe
        in Funktionen stehen und deshalb nicht knallen, macht ihn nicht besser.
        """
        from .v4_neuerkennung import V4Neuerkennung
        try:
            return V4Neuerkennung(self.job).schreiben()
        except Exception as fehler:                                # noqa: BLE001
            # Kein Abbruch: Ohne Punkte zeigt die Seite das Video ohne Skelett.
            logger.warning('MediaPipe extraction failed: %s', fehler)
            return None

    def bildmasse(self):
        """Breite und Höhe des Videos — mindestens 1, damit nie durch 0 geteilt
        wird (`cv2` liefert 0, wenn die Datei fehlt)."""
        import cv2
        pfad = Path(settings.MEDIA_ROOT) / str(self.job.video_file)
        film = cv2.VideoCapture(str(pfad))
        masse = (int(film.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1,
                 int(film.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1)
        film.release()
        return masse

    # --------------------------------------------------------------- Lesen

    def aus_csv(self, pfad, breite=1, hoehe=1, tupel=False):
        """Die CSV in eine Liste je Bild — `{gelenk: [x, y, sicht]}`.

        `breite`/`hoehe` skalieren: 1 lässt die normalisierten Werte stehen, die
        Bildmaße rechnen in Pixel um.
        """
        if not pfad or not Path(pfad).exists():
            return []
        bilder = []
        with open(pfad) as datei:
            for zeile in csv.DictReader(datei):
                bilder.append(self._punkte(zeile, breite, hoehe, tupel))
        return bilder

    def _punkte(self, zeile, breite, hoehe, tupel):
        punkte = {}
        for name in Gelenknamen.GELENKE:
            x, y, sicht = ('2DX_%s' % name, '2DY_%s' % name, 'visible_%s' % name)
            if x not in zeile or not zeile[x]:
                continue
            try:
                werte = (float(zeile[x]) * breite, float(zeile[y]) * hoehe,
                         float(zeile[sicht]) if zeile.get(sicht) else 0)
            except (ValueError, KeyError):
                # stumm gewollt: Eine leere Zelle je Gelenk ist der Normalfall,
                # wenn MediaPipe ein Gelenk nicht gesehen hat.
                logger.debug('uebergangen', exc_info=True)
                continue
            punkte[name] = werte if tupel else list(werte)
        return punkte

    def aus_openpose(self, breite=1, hoehe=1, tupel=False, alle=False):
        """Die OpenPose-JSONs eines Laufs — eines je Bild, in Dateinamensfolge.

        `alle=False` liest nur die 15 Körpergelenke der Überlagerung, `True` die
        vollen BODY_25 (Füße, Augen, Ohren) für das Skelettvideo.
        """
        ordner = self.ordner / 'openpose_json'
        if not ordner.exists():
            return []
        namen = (Gelenknamen.OPENPOSE_BODY25 if alle
                 else Gelenknamen.OPENPOSE_BODY25[:15])
        bilder = []
        for datei in sorted(ordner.glob('*_keypoints.json')):
            with open(datei) as offen:
                bilder.append(self._openpose_bild(json.load(offen), namen,
                                                  breite, hoehe, tupel))
        return bilder

    def _openpose_bild(self, daten, namen, breite, hoehe, tupel):
        """Ein Bild: flache Liste `[x, y, conf, …]` -> `{gelenk: …}`.

        Der Maßstab ist hier umgekehrt zur CSV: OpenPose schreibt PIXEL, die
        Überlagerung will 0..1. Deshalb wird geteilt, nicht multipliziert.
        """
        leute = daten.get('people') or []
        if not leute:
            return {}
        werte = leute[0].get('pose_keypoints_2d', [])
        punkte = {}
        for stelle, name in enumerate(namen):
            i = stelle * 3
            if i + 2 >= len(werte):
                continue
            eintrag = (werte[i] / breite, werte[i + 1] / hoehe, werte[i + 2])
            punkte[name] = eintrag if tupel else list(eintrag)
        return Gelenknamen.umbenannt(punkte)
