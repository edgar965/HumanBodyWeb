# -*- coding: utf-8 -*-
u"""Umaformregler — UMAs Form-Regler, je Geschlecht einmal gelesen.

WARUM (05.09.2026): Die Szene-Seite zeigt zur UMA-Figur ihre 62 Regler
(Körper, Gesicht, Pose) und rechnet sie im Browser auf die Knochen der GLB.
Die Definitionen kommen aus den Text-Assets des UMA-Projekts
(`UMA_Python.Formregler`); das Lesen läuft über rund 100 kleine
YAML-Dateien und eine Kennungskarte — einmal je Prozess reicht.

Welches Geschlecht gilt, sagt der Beipackzettel der Figur (`hinweis`:
„Rasse Human Male 3.0" bzw. „Human Female 3.0").
"""
import logging
import os
import threading

from django.conf import settings

from UMA_Python import Formregler

logger = logging.getLogger('core')

__all__ = ['Umaformregler', 'UmaformreglerFehlt']


class UmaformreglerFehlt(Exception):
    u"""Kein UMA-Projekt mit Regler-Dateien am erwarteten Ort."""


class Umaformregler:
    u"""Regler-Gruppen aus `settings.UMA_UMA3_ORDNER`, zwischengespeichert."""

    _schloss = threading.Lock()
    _stand = {}

    @staticmethod
    def ordner():
        return str(settings.UMA_UMA3_ORDNER)

    @staticmethod
    def geschlecht_aus_zettel(zettel):
        u"""`rasse`, sonst der Hinweistext — beides nennt die Rasse."""
        zettel = zettel or {}
        return Formregler.geschlecht(zettel.get('rasse') or zettel.get('hinweis') or '')

    @classmethod
    def holen(cls, geschlecht):
        if geschlecht not in Formregler.GRUPPEN:
            raise ValueError('Unbekanntes Geschlecht: %r' % (geschlecht,))
        daten = cls._stand.get(geschlecht)
        if daten is not None:
            return daten
        with cls._schloss:
            daten = cls._stand.get(geschlecht)
            if daten is not None:
                return daten
            ordner = cls.ordner()
            if not os.path.isdir(os.path.join(ordner, 'DNA')):
                raise UmaformreglerFehlt('Kein UMA-Projekt mit DNA-Ordner unter %s' % ordner)
            leser = Formregler(ordner)
            gruppen = leser.gruppen(geschlecht)
            daten = {
                'geschlecht': geschlecht,
                'gruppen': gruppen,
                'anzahl': sum(len(gruppe['regler']) for gruppe in gruppen),
                'uebergangen': list(leser.uebergangen),
            }
            cls._stand = dict(cls._stand, **{geschlecht: daten})
            logger.info('Umaformregler: %s — %d Regler aus %s', geschlecht,
                        daten['anzahl'], ordner)
            return daten

    @classmethod
    def vergessen(cls):
        u"""Den Speicher leeren — für Tests und nach einem Wechsel des Ordners."""
        cls._stand = {}
