# -*- coding: utf-8 -*-
"""Texturbacken — ein Foto auf die UV-Karte eines SMPL-X-Netzes bringen.

Aus `smplx_texture` herausgeloest (Umbau 15.08.2026, 179 Zeilen Endpunkt).
Die Reihenfolge der Vorzuege beim Projizieren steht jetzt an einer Stelle:

    1. vollstaendige posierte SMPL-X-Projektion (Topologie passt),
    2. orthographisch mit gespeicherter Ausrichtung,
    3. orthographisch mit einer aus der Pose abgeleiteten Ausrichtung.

Der zweite Fall ist der haeufige: Die Foto-Pipeline liefert oft nur einen
SMPL-Koerper mit 6.890 Vertices, waehrend SMPL-X 10.475 hat. Von rund 13.000
Dreiecken sind nur 268 gemeinsam — mit SMPL-Vertices auf SMPL-X-Dreiecken wird
die Textur zu Konfetti.
"""
import logging
import os
import sys

import numpy as np
from django.conf import settings

from .fotoausrichtung import Fotoausrichtung

logger = logging.getLogger('core')


class Texturbacken:
    """Backt eine Textur und legt sie ab."""

    GROESSE = 1024
    VORGABE_HINTERGRUND = (136, 170, 204)      # BGR
    REGIONEN = ('all', 'body', 'face')

    def __init__(self, job_id, daten, foto):
        self.job_id = job_id
        self.daten = daten
        self.foto = foto
        self.hoehe, self.breite = foto.shape[:2]

    # ------------------------------------------------------------------ Farbe

    @classmethod
    def hintergrundfarbe(cls, hexwert):
        """'#ccaa88' -> (b, g, r) fuer OpenCV."""
        try:
            r = int(hexwert[1:3], 16)
            g = int(hexwert[3:5], 16)
            b = int(hexwert[5:7], 16)
            return (b, g, r)
        except (ValueError, IndexError, TypeError):
            return cls.VORGABE_HINTERGRUND

    # ------------------------------------------------------------- Projektion

    def posierte_projektion(self, anzahl_vertices):
        """(projektion, projektion_fuer_ausrichtung) — je nach Topologie.

        Passt die Vertexzahl, wird direkt projiziert. Passt sie nicht, taugt die
        Projektion immer noch, um die orthographische Lage zu bestimmen."""
        kamera = self.daten.get('cam_data')
        pfad = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody', 'data',
                            'photoTo3D', 'SMPLX', '%s.npz' % self.job_id)
        if not (kamera and os.path.isfile(pfad)):
            return None, None
        try:
            npz = np.load(pfad)
            if 'posed_vertices' not in npz:
                return None, None
            posiert = npz['posed_vertices']
            projektion = Fotoausrichtung.vertices_projizieren(
                posiert, kamera, self.breite, self.hoehe)
        except Exception:                                         # noqa: BLE001
            logger.error('Posierte Vertices fuer %s nicht ladbar', self.job_id,
                         exc_info=True)
            return None, None
        if len(posiert) >= anzahl_vertices:
            return projektion, None
        logger.info('Nur SMPL-Koerper (%d < %d) — orthographisch backen, '
                    'Lage aus der Pose', len(posiert), anzahl_vertices)
        return None, projektion

    @staticmethod
    def versatz_anwenden(projektion, versatz):
        """Feinkorrektur des Assistenten auf eine fertige Projektion."""
        if not versatz:
            return projektion
        gueltig = ~np.isnan(projektion).any(axis=1)
        mx = projektion[gueltig, 0].mean()
        my = projektion[gueltig, 1].mean()
        s = versatz.get('scale', 1.0)
        projektion[gueltig, 0] = ((projektion[gueltig, 0] - mx) * s + mx
                                  + versatz.get('dx', 0))
        projektion[gueltig, 1] = ((projektion[gueltig, 1] - my) * s + my
                                  + versatz.get('dy', 0))
        return projektion

    def lage_bestimmen(self, vertices, projektion_aus_pose):
        """Koerperlage fuer den orthographischen Weg."""
        ausrichtung = self.daten.get('alignment_data') or {}
        lage = ausrichtung.get('body_transform')
        if lage:
            return lage
        if projektion_aus_pose is None:
            return None
        lage = Fotoausrichtung.koerper_verschiebung(
            vertices, projektion_aus_pose, self.breite, self.hoehe, margin=0.05)
        versatz = ausrichtung.get('proj_2d_offset')
        if lage and versatz:
            lage['center_x'] += versatz.get('dx', 0)
            lage['center_y'] += versatz.get('dy', 0)
            lage['scale'] *= versatz.get('scale', 1.0)
        return lage

    # ------------------------------------------------------------------ backen

    def backen(self, backend, vertices, faces, region, hintergrund):
        """Textur erzeugen — wirft die Ausnahme des Backends weiter."""
        projektion, aus_pose = self.posierte_projektion(len(vertices))
        ausrichtung = self.daten.get('alignment_data') or {}
        argumente = dict(job_data=self.daten, texture_size=self.GROESSE,
                         bg_color=hintergrund, region=region)
        if projektion is not None:
            argumente['proj_2d'] = self.versatz_anwenden(
                projektion, ausrichtung.get('proj_2d_offset'))
        else:
            lage = self.lage_bestimmen(vertices, aus_pose)
            if lage:
                argumente['body_transform'] = lage
            if ausrichtung.get('face_transform'):
                argumente['face_transform'] = ausrichtung['face_transform']

        verzeichnis = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody',
                                   'PhotoToTexture')
        sys.path.insert(0, verzeichnis)
        try:
            from bake_texture import bake_with_backend
            return bake_with_backend(backend, vertices, faces, self.foto,
                                     **argumente)
        finally:
            if verzeichnis in sys.path:
                sys.path.remove(verzeichnis)

    # ----------------------------------------------------------------- ablegen

    @staticmethod
    def verzeichnis():
        pfad = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis',
                            'textures')
        os.makedirs(pfad, exist_ok=True)
        return pfad

    def zusammensetzen(self, cv2, textur, region, hintergrund):
        """Koerper- und Gesichtstextur uebereinanderlegen, wenn beide da sind."""
        if region not in ('body', 'face'):
            return textur
        ordner = self.verzeichnis()
        cv2.imwrite(os.path.join(ordner, '%s_%s.png' % (self.job_id, region)),
                    textur)
        koerper = os.path.join(ordner, '%s_body.png' % self.job_id)
        gesicht = os.path.join(ordner, '%s_face.png' % self.job_id)
        if not (os.path.isfile(koerper) and os.path.isfile(gesicht)):
            return textur
        unten = cv2.imread(koerper, cv2.IMREAD_UNCHANGED)
        oben = cv2.imread(gesicht, cv2.IMREAD_UNCHANGED)
        if oben.shape[2] == 4:
            maske = oben[:, :, 3] > 0
        else:
            maske = np.any(oben != np.array(hintergrund, dtype=np.uint8), axis=2)
        zusammen = unten.copy()
        zusammen[maske] = oben[maske]
        return zusammen

    def speichern(self, cv2, textur):
        """Fertige Textur ablegen und den Pfad relativ zum Projekt liefern."""
        name = '%s.png' % self.job_id
        cv2.imwrite(os.path.join(self.verzeichnis(), name), textur)
        return 'media/photo_analysis/textures/%s' % name
