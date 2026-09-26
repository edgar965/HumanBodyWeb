# -*- coding: utf-8 -*-
"""Smplxbedlamdienst — die BEDLAM-Hauttexturen fuer SMPL-X: Liste, Bau, Ablage.

Rechnung in `SMPL/xbedlamhaut.py` (Liste, Augapfel-Insel) und
`SMPL/xbrauenweg.py` (Fotobraue weg) — hier nur: einmal je Textur bauen
(Braue weg + eigenes Auge hinein, ~3 s), unter der Fassung ablegen, lesen.
Wie `smplxdetaildienst.py`, derselbe Aufbau.

Ablage neben der eigenen Textur (`3DObjects/Archiv/SMPL-X/texturen/bedlam/`,
nicht im Repo): `f<FASSUNG>_<geschlecht>_<schluessel>.jpg`.
"""

import logging
import os

logger = logging.getLogger('core')

__all__ = ['Smplxbedlamdienst']


class Smplxbedlamdienst:
    """Liest die BEDLAM-Rohtexturen, baut die SMPL-X-taugliche Fassung, cacht sie."""

    FASSUNG = 1

    @staticmethod
    def _basis():
        from django.conf import settings

        return str(settings.SMPLX_BEDLAM_DIR)

    @staticmethod
    def _geschlecht(geschlecht):
        return 'male' if geschlecht == 'male' else 'female'

    @classmethod
    def verfuegbar(cls, geschlecht):
        """`[{schluessel, name}]` — leer, wenn der Ordner (noch) fehlt."""
        from SMPL.xbedlamhaut import Smplxbedlamhaut

        return Smplxbedlamhaut.liste(cls._basis(), cls._geschlecht(geschlecht))

    @classmethod
    def _ablageordner(cls):
        from .smplfigur import Smplfiguren

        ordner = os.path.join(Smplfiguren.ordner_texturen(), 'bedlam')
        os.makedirs(ordner, exist_ok=True)
        return ordner

    @classmethod
    def textur_pfad(cls, geschlecht, schluessel):
        """Pfad zur fertigen Textur — baut sie beim ersten Abruf, `None` bei
        unbekanntem Schlüssel oder fehlendem Ordner."""
        geschlecht = cls._geschlecht(geschlecht)
        pfad = os.path.join(cls._ablageordner(), 'f%d_%s_%s.jpg' % (cls.FASSUNG, geschlecht, schluessel))
        if os.path.isfile(pfad):
            return pfad
        if not cls._bauen(geschlecht, schluessel, pfad):
            return None
        return pfad if os.path.isfile(pfad) else None

    @classmethod
    def _bauen(cls, geschlecht, schluessel, ziel):
        import numpy as np
        from PIL import Image
        from SMPL.xbedlamhaut import Smplxbedlamhaut
        from SMPL.xbrauenweg import Smplxbrauenweg
        from SMPL.xdetails import Smplxdetails
        from SMPL.xkopf import SmplxKopf
        from SMPL.xuv import Smplxuv

        from .smplfigur import Smplfiguren
        from .smplxrig import Smplxrig

        quelle = Smplxbedlamhaut.pfad(cls._basis(), geschlecht, schluessel)
        eigene_textur = Smplfiguren.textur_pfad(geschlecht)
        if not quelle or not eigene_textur or not Smplxuv.vorhanden():
            logger.warning('BEDLAM-Textur %s/%s: Quelle, eigenes Foto oder UV fehlt', geschlecht, schluessel)
            return False
        modell = Smplxrig.koerper(geschlecht)
        vt, ft = Smplxuv._laden()
        kopf = SmplxKopf.aus_modell(modell, Smplxrig.ordner())
        details = Smplxdetails(modell, kopf, vt, ft)

        haut = np.array(Image.open(quelle).convert('RGB'))
        n = haut.shape[0]
        eigen = np.array(Image.open(eigene_textur).convert('RGB'))
        if eigen.shape[0] != n:
            eigen = np.array(Image.fromarray(eigen).resize((n, n)))

        ohne_brauen_bgr = Smplxbrauenweg.entfernen(haut[:, :, ::-1].copy(), details)
        ohne_brauen = ohne_brauen_bgr[:, :, ::-1]
        augen = Smplxbedlamhaut.augenmaske(vt, ft, modell.faces, n)
        fertig = Smplxbedlamhaut.komponieren(ohne_brauen, eigen, augen)

        neu = ziel + '.neu.jpg'
        Image.fromarray(fertig).save(neu, quality=90)
        os.replace(neu, ziel)
        logger.info('BEDLAM-Textur gebaut: %s', ziel)
        return True
