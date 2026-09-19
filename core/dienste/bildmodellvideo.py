# -*- coding: utf-8 -*-
"""Bildmodellvideo — Drehvideos im Auftrag: Standbild, Eintrag, GVHMR-Form.

Edgar (19.09.2026): „Kannst du das GVHMR einbinden?" — GVHMR ist ein
Videoverfahren und schätzt EINE SMPL-X-Form je Sequenz (Betas je Bild
dupliziert, Streuung 0). Ein Drehvideo ist damit ein Eingang wie ein
Hauptbild: ein Eintrag der Kategorie `video`, ein Gewicht, eine Schätzung
im Feld `schaetzung` — die Mischung nimmt es wie ein Körperbild.

Sichtung: je Video ein Standbild aus der Mitte als `zuschnitt/<stamm>_video.jpg`
(die Kachel der Seite), Bildzahl und Bildrate aus der Datei. Kein Rig.
Schätzung: `_run_gvhmr_betas.py <video> <schaetzung/gvhmr>` in python10;
GVHMR legt Vorstufe und `hmr4d_results.pt` unter `gvhmr/<stamm>/` ab,
ein zweiter Lauf liest nur.
"""

import logging
import os

from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellmehrbild import Bildmodellmehrbild

logger = logging.getLogger('core')

__all__ = ['Bildmodellvideo']


class Bildmodellvideo:
    RUNNER = '_run_gvhmr_betas.py'
    ENDUNG = '_video.jpg'
    WARTEZEIT = 7200

    def __init__(self, ablage):
        self.ablage = ablage

    # ------------------------------------------------------------ Sichtung

    def sichten(self, vorhandene):
        """Ein Eintrag je Video im Original-Ordner; Kategorie und Gewicht
        eines vorhandenen Eintrags bleiben, ebenso seine Schätzung."""
        alt = {e.get('datei'): e for e in vorhandene if e.get('video')}
        aus = []
        for video in self.ablage.videos():
            datei = video.stem + self.ENDUNG
            eintrag = {
                'datei': datei,
                'quelle': video.name,
                'video': True,
                'kategorie': 'video',
                'gewicht': 1.0,
                'ansicht': 'drehung',
                'haltung': 'video',
            }
            try:
                eintrag.update(self.standbild(video, self.ablage.zuschnitt() / datei))
            except Exception as fehler:  # noqa: BLE001
                eintrag['fehler'] = 'Standbild: %s' % fehler
                eintrag['gewicht'] = 0.0
            vorher = alt.get(datei)
            if vorher:
                for k in ('kategorie', 'gewicht', 'manuell', 'schaetzung'):
                    if k in vorher:
                        eintrag[k] = vorher[k]
            aus.append(eintrag)
        return aus

    @staticmethod
    def standbild(video, ziel):
        """Das mittlere Bild als JPG; `{bilder, fps, breite, hoehe}`."""
        import cv2

        quelle = cv2.VideoCapture(str(video))
        try:
            bilder = int(quelle.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            fps = float(quelle.get(cv2.CAP_PROP_FPS) or 0)
            quelle.set(cv2.CAP_PROP_POS_FRAMES, max(0, bilder // 2))
            ok, bild = quelle.read()
            if not ok or bild is None:
                quelle.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, bild = quelle.read()
            if not ok or bild is None:
                raise RuntimeError('kein Bild lesbar')
            hoehe, breite = bild.shape[:2]
            cv2.imwrite(str(ziel), bild, [cv2.IMWRITE_JPEG_QUALITY, 90])
        finally:
            quelle.release()
        return {'bilder': bilder, 'fps': round(fps, 3), 'breite': int(breite), 'hoehe': int(hoehe)}

    # ----------------------------------------------------------- Schätzung

    def schaetzen(self, eintrag, melder=None):
        """GVHMR über das Video; Rohantwort des Runners oder `{'error': …}`."""
        import subprocess

        video = self.ablage.original() / eintrag['quelle']
        ordner = self.ablage.videoordner(video)
        ordner.mkdir(parents=True, exist_ok=True)
        runner = os.path.join(Wrapperpfad.pfad(), self.RUNNER)
        if melder:
            melder(0.1, 'GVHMR: %s (%s Bilder)' % (eintrag['quelle'], eintrag.get('bilder', '?')))
        prozess = subprocess.Popen(
            [settings.PIPELINE_PYTHON, runner, str(video), str(ordner)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=Wrapperpfad.pfad(),
        )
        try:
            aus, fehler = prozess.communicate(timeout=self.WARTEZEIT)
        except subprocess.TimeoutExpired:
            prozess.kill()
            return {'error': 'GVHMR: keine Antwort nach %d s' % self.WARTEZEIT}
        antwort = Bildmodellmehrbild.antwort(aus)
        if not antwort:
            return {'error': 'GVHMR ohne Antwort: %s' % (fehler or '')[-400:]}
        return antwort
