# -*- coding: utf-8 -*-
"""V4Neuerkennung — rohe MediaPipe-Punkte aus dem Video nachziehen.

WOZU
====
Die v4-Pipeline schreibt `2dJoints_v4.csv` mit Werten, die fürs
Seitenverhältnis korrigiert sind — MocapNET braucht das so. Für eine
Überlagerung über das echte Video sind sie damit unbrauchbar (das Skelett
sitzt daneben). Diese Klasse geht das Video deshalb noch einmal mit MediaPipe
durch und legt die ROHEN, auf 0..1 normierten Punkte als
`2dJoints_v4_raw.csv` daneben.

Herausgelöst aus `keypoints_quellen._extract_v4_keypoints` (92 Zeilen, Grenze
60). Dabei entfernt: ein `if PoseCompat: … else: …`, dessen beide Zweige
BUCHSTABENGLEICH waren (`result = pose.process(rgb)` …) — die Verzweigung war
schon beim Herausschreiben ohne Wirkung.

ABGELEITETE GELENKE
===================
MediaPipe kennt weder Hals noch Hüftmitte. Beide werden gemittelt (Schultern
bzw. Hüften), und ihre Sichtbarkeit ist das MINIMUM der beiden Quellpunkte —
nicht der Mittelwert: Sieht MediaPipe eine Schulter nicht, ist der Hals geraten,
und die Überlagerung soll das wissen.
"""

import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')


class V4Neuerkennung:
    """Liest ein Video mit MediaPipe und schreibt die rohen 2D-Punkte."""

    DATEINAME = '2dJoints_v4_raw.csv'

    #: MediaPipe-Landmarkennummer -> unser Gelenkname. Die Nummern sind der
    #: Vertrag von MediaPipe Pose (33 Landmarken) und dürfen nicht wandern.
    LANDMARKEN = {
        0: 'head', 11: 'lshoulder', 12: 'rshoulder',
        13: 'lelbow', 14: 'relbow', 15: 'lhand', 16: 'rhand',
        23: 'lhip', 24: 'rhip', 25: 'lknee', 26: 'rknee',
        27: 'lfoot', 28: 'rfoot',
    }
    #: Abgeleitet: Name -> die zwei Landmarken, deren Mitte er ist.
    MITTEN = {'neck': (11, 12), 'hip': (23, 24)}

    def __init__(self, job):
        self.job = job
        self.video = Path(settings.MEDIA_ROOT) / str(job.video_file)
        self.ziel = (Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
                     / self.DATEINAME)

    @property
    def gelenke(self):
        return sorted(set(self.LANDMARKEN.values()) | set(self.MITTEN))

    # ------------------------------------------------------------------ Ablauf

    def schreiben(self):
        """Die CSV erzeugen und ihren Pfad liefern — `None`, wenn nichts geht."""
        zeilen = self._lesen()
        if not zeilen:
            return None
        self._schreiben(zeilen)
        return self.ziel

    def _lesen(self):
        import cv2
        film = cv2.VideoCapture(str(self.video))
        if not film.isOpened():
            logger.warning('[v4] Video nicht lesbar: %s', self.video)
            return []
        erkenner = self._erkenner()
        zeilen = []
        while True:
            gelesen, bild = film.read()
            if not gelesen:
                break
            ergebnis = erkenner.process(cv2.cvtColor(bild, cv2.COLOR_BGR2RGB))
            marken = (ergebnis.pose_landmarks.landmark
                      if ergebnis.pose_landmarks else None)
            zeilen.append(self._zeile(marken) if marken else {})
        film.release()
        return zeilen

    @staticmethod
    def _erkenner():
        """`PoseCompat` aus dem Pipeline-Ordner — sonst MediaPipe direkt.

        `mp.solutions` ist ab mediapipe 0.10.30 weg; `mediapipe_compat` legt
        die Tasks-API darüber. Der Rückfall bleibt für Umgebungen mit älterem
        MediaPipe.
        """
        try:
            from mediapipe_compat import PoseCompat
            return PoseCompat()
        except ImportError:
            logger.debug('mediapipe_compat fehlt — mediapipe direkt',
                         exc_info=True)
            import mediapipe as mp
            return mp.solutions.pose.Pose(static_image_mode=False,
                                          model_complexity=1,
                                          min_detection_confidence=0.5)

    def _zeile(self, marken):
        zeile = {}
        for nummer, name in self.LANDMARKEN.items():
            marke = marken[nummer]
            zeile.update(self._werte(name, marke.x, marke.y, marke.visibility))
        for name, (links, rechts) in self.MITTEN.items():
            a, b = marken[links], marken[rechts]
            zeile.update(self._werte(name, (a.x + b.x) / 2, (a.y + b.y) / 2,
                                     min(a.visibility, b.visibility)))
        return zeile

    @staticmethod
    def _werte(name, x, y, sicht):
        return {'2DX_%s' % name: x, '2DY_%s' % name: y,
                'visible_%s' % name: sicht}

    def _schreiben(self, zeilen):
        """Die CSV schreiben — Spaltenliste EINMAL, nicht je Bild.

        `self.gelenke` rechnet `sorted(set(…))` bei jedem Zugriff. In der
        inneren Schleife gelesen wäre das bei einem Film mit 3.000 Bildern
        3.000-mal dieselbe Sortierung (gemeldet von `schleifenarbeit`).
        """
        spalten = ['frameNumber']
        for name in self.gelenke:
            # in der Schleife gewollt: `+=` auf einer Liste ist `extend` und
            # kopiert nichts — und die Kopfzeile wird EINMAL gebaut, nicht je
            # Bild (fünfzehn Durchläufe, nicht dreitausend).
            spalten += ['2DX_%s' % name, '2DY_%s' % name, 'visible_%s' % name]
        werte_spalten = spalten[1:]
        with open(self.ziel, 'w', newline='') as datei:
            datei.write(','.join(spalten) + '\n')
            for nummer, zeile in enumerate(zeilen):
                datei.write(','.join(
                    [str(nummer)]
                    + [str(zeile.get(spalte, '')) for spalte in werte_spalten])
                    + '\n')
