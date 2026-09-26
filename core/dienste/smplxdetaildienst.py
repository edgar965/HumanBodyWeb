# -*- coding: utf-8 -*-
"""Smplxdetaildienst — Detailmaske und Brauenbogen der SMPL-X-Haut, abgelegt.

Die Rechnung steht in `SMPL/xdetails.py` (Masken aus der 3D-Lage je Texel)
und `SMPL/xfotomerkmale.py` (Brauen und Lippen aus dem Hautfoto). Hier nur:
einmal je Geschlecht rechnen (rund 3 s), unter der Fassung ablegen, lesen.

Ablage neben der Textur (`3DObjects/Archiv/SMPL-X/texturen/`, nicht im Repo):
    details_f<F>_<geschlecht>.png        RGBA-Maske (R Lippen, G Fingernaegel,
                                         B Fussnaegel, A Augen)
    brauenbogen_f<F>_<geschlecht>.json   Brauenmittellinien fuer `Brauendecal`
Die Fotobraue wird am Bild MIT Brauen gesucht (`*_haut_mitbrauen.jpg`); die
ausgelieferte Textur traegt keine mehr (`ProjektTemp/_wegwerf/smplxuv/brauenweg.py`),
damit die gezeichnete Braue regelbar ist.
"""

import json
import logging
import os

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Smplxdetaildienst']


class Smplxdetaildienst:
    """Liefert Maske und Brauenbogen je Geschlecht (aus der Ablage oder frisch)."""

    _bogen = {}

    @staticmethod
    def _geschlecht(geschlecht):
        return 'male' if geschlecht == 'male' else 'female'

    @staticmethod
    def _fassung():
        from SMPL.xdetails import Smplxdetails

        return Smplxdetails.FASSUNG

    @classmethod
    def maske_pfad(cls, geschlecht):
        from .smplfigur import Smplfiguren

        geschlecht = cls._geschlecht(geschlecht)
        pfad = os.path.join(Smplfiguren.ordner_texturen(), 'details_f%d_%s.png' % (cls._fassung(), geschlecht))
        if not os.path.isfile(pfad):
            cls._bauen(geschlecht)
        return pfad if os.path.isfile(pfad) else None

    @classmethod
    def bogen(cls, geschlecht):
        from .smplfigur import Smplfiguren

        geschlecht = cls._geschlecht(geschlecht)
        if geschlecht in cls._bogen:
            return cls._bogen[geschlecht]
        pfad = os.path.join(Smplfiguren.ordner_texturen(),
                            'brauenbogen_f%d_%s.json' % (cls._fassung(), geschlecht))
        if not os.path.isfile(pfad):
            cls._bauen(geschlecht)
        if not os.path.isfile(pfad):
            return None
        with open(pfad, encoding='utf-8') as datei:
            cls._bogen[geschlecht] = json.load(datei)
        return cls._bogen[geschlecht]

    @classmethod
    def _foto(cls, geschlecht):
        """Das Hautfoto MIT Brauen (fuer Lippen und Brauenlinie) — oder ohne."""
        from PIL import Image

        from .smplfigur import Smplfiguren

        haupt = Smplfiguren.textur_pfad(geschlecht)
        if not haupt:
            return None
        mit = haupt.replace('_haut.jpg', '_haut_mitbrauen.jpg')
        quelle = mit if os.path.isfile(mit) else haupt
        return np.asarray(Image.open(quelle).convert('RGB'))

    @classmethod
    def _bauen(cls, geschlecht):
        from PIL import Image
        from SMPL.xdetails import Smplxdetails
        from SMPL.xkopf import SmplxKopf
        from SMPL.xuv import Smplxuv

        from .smplfigur import Smplfiguren
        from .smplxrig import Smplxrig
        from ..atomic_write import AtomarSchreiber

        foto = cls._foto(geschlecht)
        if foto is None or not Smplxuv.vorhanden():
            logger.warning('SMPL-X-Details %s: Textur oder UV fehlt', geschlecht)
            return
        modell = Smplxrig.koerper(geschlecht)
        vt, ft = Smplxuv._laden()
        details = Smplxdetails(modell, SmplxKopf.aus_modell(modell, Smplxrig.ordner()), vt, ft)
        ordner = Smplfiguren.ordner_texturen()
        fassung = cls._fassung()
        maske = os.path.join(ordner, 'details_f%d_%s.png' % (fassung, geschlecht))
        Image.fromarray(details.maske(textur=foto), 'RGBA').save(maske + '.neu.png')
        os.replace(maske + '.neu.png', maske)
        bogen = os.path.join(ordner, 'brauenbogen_f%d_%s.json' % (fassung, geschlecht))
        AtomarSchreiber.json_schreiben(bogen, details.brauenbogen(textur=foto))
        logger.info('SMPL-X-Details %s gebaut: %s', geschlecht, maske)
