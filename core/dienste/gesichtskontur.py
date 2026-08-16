# -*- coding: utf-8 -*-
"""Gesichtskontur — der Umriss des Gesichts, auf drei Wegen.

Aus `photo_silhouette_data` herausgeloest (Umbau 15.08.2026). Die drei Wege
standen dort als drei ineinander verschachtelte try-Bloecke; welcher am Ende
gewann, war nur durch Lesen der ganzen Funktion zu klaeren. Die Rangfolge steht
jetzt an einer Stelle:

    1. MediaPipe-Gesichtsumriss — der beste, wenn ein Gesicht erkannt wird.
    2. Konvexe Huelle der SMPL-X-Gesichtsvertices — nur bei passender Topologie
       (die Indexliste gilt fuer 10.475 Vertices, nicht fuer ein SMPL-Netz).
    3. Konvexe Huelle des oberen Achtels der Projektion — der Rueckfall.
"""
import logging
import os

import numpy as np
from django.conf import settings

logger = logging.getLogger('core')


class Gesichtskontur:
    """Ermittelt Gesichtsumriss und -rahmen aus Netz oder Foto."""

    #: Landmarken des Gesichtsumrisses in MediaPipes 468-Punkte-Netz, in der
    #: Reihenfolge des Umlaufs.
    OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323,
            361, 288, 397, 365, 379, 378, 400, 377, 152, 148,
            176, 149, 150, 136, 172, 58, 132, 93, 234, 127,
            162, 21, 54, 103, 67, 109]

    #: Ab so vielen Vertices gilt ein Netz als SMPL-X (10.475) und nicht als
    #: SMPL (6.890) — nur dann passen die Gesichtsindizes.
    SMPLX_AB = 10000

    #: Anteil der Bildhoehe, der beim Rueckfall als Kopf gilt.
    KOPFANTEIL = 0.12

    def __init__(self, projektion, breite, hoehe):
        self.projektion = projektion
        self.breite = breite
        self.hoehe = hoehe
        self.kontur = []
        self.rahmen_netz = None
        self.rahmen_erkannt = None
        self.aus_smplx = False

    # ------------------------------------------------------------ aus dem Netz

    def aus_smplx_vertices(self, anzahl_posiert):
        """Konvexe Huelle der Gesichtsvertices — nur bei SMPL-X-Topologie."""
        if anzahl_posiert < self.SMPLX_AB:
            return False
        pfad = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH',
                            'PyMAF-X', 'data', 'partial_mesh', 'smplx_face_vids.npz')
        if not os.path.isfile(pfad):
            return False
        indizes = np.load(pfad)['vids']
        indizes = indizes[indizes < len(self.projektion)]
        punkte = self.projektion[indizes]
        punkte = punkte[~np.isnan(punkte).any(axis=1)]
        if len(punkte) < 3:
            return False
        self.rahmen_netz = self._rahmen(punkte)
        huelle = self._huelle(punkte)
        if huelle:
            self.kontur = huelle
            self.aus_smplx = True
        return bool(huelle)

    def aus_kopfbereich(self):
        """Rueckfall: konvexe Huelle des obersten Zwoelftels der Projektion."""
        gueltig = self.projektion[~np.isnan(self.projektion).any(axis=1)]
        if len(gueltig) < 3:
            return False
        y_min, y_max = gueltig[:, 1].min(), gueltig[:, 1].max()
        grenze = y_min + (y_max - y_min) * self.KOPFANTEIL
        kopf = gueltig[gueltig[:, 1] < grenze]
        if len(kopf) < 3:
            return False
        huelle = self._huelle(kopf)
        if not huelle:
            return False
        self.kontur = huelle
        self.rahmen_netz = self._rahmen(kopf)
        return True

    # ------------------------------------------------------------- aus dem Foto

    def aus_mediapipe(self, foto, cv2):
        """Gesichtsumriss und -rahmen aus dem Foto — der genaueste Weg."""
        landmarken = self._landmarken(foto, cv2)
        if not landmarken:
            return False
        xs = [l.x * self.breite for l in landmarken]
        ys = [l.y * self.hoehe for l in landmarken]
        self.rahmen_erkannt = {'x': float(min(xs)), 'y': float(min(ys)),
                               'w': float(max(xs) - min(xs)),
                               'h': float(max(ys) - min(ys))}
        self.kontur = [[float(landmarken[i].x * self.breite),
                        float(landmarken[i].y * self.hoehe)]
                       for i in self.OVAL if i < len(landmarken)]
        if not self.aus_smplx:
            self.rahmen_netz = self.rahmen_erkannt
        return True

    def _landmarken(self, foto, cv2):
        try:
            import mediapipe as mp
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision as mp_vision
        except ImportError as e:
            logger.debug('MediaPipe nicht verfuegbar: %s', e)
            return None
        modell = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH',
                              'MocapNET_v4', 'src', 'python', 'mnet4',
                              'models', 'face_landmarker.task')
        if not os.path.isfile(modell):
            return None
        try:
            optionen = mp_vision.FaceLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=modell),
                num_faces=1)
            with mp_vision.FaceLandmarker.create_from_options(optionen) as erkenner:
                bild = mp.Image(image_format=mp.ImageFormat.SRGB,
                                data=cv2.cvtColor(foto, cv2.COLOR_BGR2RGB))
                ergebnis = erkenner.detect(bild)
            return ergebnis.face_landmarks[0] if ergebnis.face_landmarks else None
        except Exception as e:                                    # noqa: BLE001
            logger.debug('Gesichtserkennung uebersprungen: %s', e)
            return None

    # ------------------------------------------------------------------ Technik

    @staticmethod
    def _huelle(punkte):
        try:
            from scipy.spatial import ConvexHull
            huelle = ConvexHull(punkte)
            return [[float(p[0]), float(p[1])] for p in punkte[huelle.vertices]]
        except Exception:                                         # noqa: BLE001
            logger.debug('Konvexe Huelle fehlgeschlagen', exc_info=True)
            return []

    @staticmethod
    def _rahmen(punkte):
        x_min, y_min = punkte[:, 0].min(), punkte[:, 1].min()
        x_max, y_max = punkte[:, 0].max(), punkte[:, 1].max()
        return {'x': float(x_min), 'y': float(y_min),
                'w': float(x_max - x_min), 'h': float(y_max - y_min)}
