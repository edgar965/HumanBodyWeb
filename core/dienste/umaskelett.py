# -*- coding: utf-8 -*-
u"""Umaskelett — das Skelett der UMA-Figur aus dem Figurkatalog.

WARUM (05.09.2026)
==================
Die Vergleichsseite (Test-Animation) zeigt das UMA-Skelett neben dem
DEF-Skelett und rechnet Bewegungen darauf um. Die Quelle ist die GLB, die
Unity in `Figuren/uma/` ablegt — kein zweites Datenfile, das jemand
nachziehen muesste: Aendert sich die GLB, aendert sich das Skelett (der
Zwischenspeicher haengt an Pfad und Aenderungszeit).

Welche GLB gilt, sagt `aktuell.json` im Katalog (Feld `uma`); fehlt der
Eintrag oder zeigt er ins Leere, die juengste Datei im Ordner — dieselbe
Regel, nach der Roomguest liest (`Figuren/VERTRAG.md`).

WAS GELIEFERT WIRD: die Knotenpose (nicht die Bindpose, siehe
`Gltfskelett`), nach +Z ausgerichtet wie das DEF-Skelett
(`Skelettausrichtung`), in Three.js-Form. Einmal als Knochenliste fuer
den Browser, einmal als `SkeletonGeometry` fuer den Retarget-Motor —
beide aus demselben Lesevorgang.
"""
import json
import logging
import os
import threading
import time

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Umaskelett', 'UmaskelettFehlt']


class UmaskelettFehlt(Exception):
    u"""Keine UMA-GLB im Katalog."""


class Umaskelett:
    u"""UMA-Skelett aus `Figuren/uma/`, je Datei einmal gelesen."""

    QUELLE = 'uma'
    ZEIGER = 'aktuell.json'
    #: glTF-Knochen zeigen entlang +Y (siehe `Gltfskelett`).
    RICHTUNGSACHSE = (0.0, 1.0, 0.0)
    ZEITFORMAT = '%Y-%m-%d %H:%M:%S'

    _schloss = threading.Lock()
    #: Je GLB-Pfad `(mtime, knochen, geometrie)` — seit dem 06.09.2026 je
    #: Datei, nicht nur die aus `aktuell.json`: Der Retarget-Motor braucht
    #: das Skelett DER Figur, die in der Szene steht (`Retargetwahl.figur`).
    _bestand = {}

    # -------------------------------------------------------------- Datei

    @classmethod
    def glb_pfad(cls, name=None):
        u"""Die gueltige GLB — `name` aus dem Katalog, sonst aus dem Zeiger, sonst
        die juengste."""
        katalog = str(settings.FIGUREN_KATALOG)
        ordner = os.path.join(katalog, cls.QUELLE)
        if name:
            pfad = os.path.join(ordner, os.path.basename(name))
            if not os.path.isfile(pfad):
                raise UmaskelettFehlt('Keine UMA-Figur %s unter %s' % (name, ordner))
            return pfad
        name = cls._zeiger(katalog)
        if name and os.path.isfile(os.path.join(ordner, name)):
            return os.path.join(ordner, name)
        juengste = cls._juengste(ordner)
        if juengste is None:
            raise UmaskelettFehlt('Keine UMA-Figur unter %s' % ordner)
        if name:
            logger.warning('Umaskelett: %s nennt %s, die Datei fehlt — '
                           'nehme %s', cls.ZEIGER, name,
                           os.path.basename(juengste))
        return juengste

    @classmethod
    def _zeiger(cls, katalog):
        pfad = os.path.join(katalog, cls.ZEIGER)
        if not os.path.isfile(pfad):
            return None        # kein Zeiger: die juengste Datei zaehlt (Vertrag)
        try:
            with open(pfad, encoding='utf-8') as datei:
                return json.load(datei).get(cls.QUELLE)
        except (OSError, ValueError):
            # Ein Zeiger, der da ist und nicht lesbar: nachlesbar halten,
            # aber nicht abbrechen — die juengste Datei zaehlt trotzdem.
            logger.warning('Umaskelett: %s unlesbar', pfad, exc_info=True)
            return None

    @staticmethod
    def _juengste(ordner):
        if not os.path.isdir(ordner):
            return None
        dateien = [os.path.join(ordner, n) for n in os.listdir(ordner)
                   if n.lower().endswith('.glb')]
        return max(dateien, key=os.path.getmtime) if dateien else None

    # ----------------------------------------------------------- Ergebnis

    @classmethod
    def knochen(cls, name=None):
        u"""Die Knochen in Three.js-Form — siehe `Gltfskelett.knochen`."""
        return cls._laden(name)[1]

    @classmethod
    def geometrie(cls, name=None):
        u"""`SkeletonGeometry` fuer den Retarget-Motor, Achse +Y — der Figur `name`,
        sonst der gueltigen."""
        return cls._laden(name)[2]

    @classmethod
    def beschreibung(cls):
        u"""Quelle, Dateiname und Stand — fuer die Antwort an den Browser."""
        pfad = cls.glb_pfad()
        return {
            'quelle': cls.QUELLE,
            'datei': os.path.basename(pfad),
            'stand': time.strftime(cls.ZEITFORMAT,
                                   time.localtime(os.path.getmtime(pfad))),
        }

    @classmethod
    def _laden(cls, name=None):
        u"""`(mtime, knochen, geometrie)` der Datei — aus dem Bestand oder frisch
        gelesen."""
        pfad = cls.glb_pfad(name)
        mtime = os.path.getmtime(pfad)
        eintrag = cls._bestand.get(pfad)
        if eintrag is not None and eintrag[0] == mtime:
            return eintrag
        with cls._schloss:
            eintrag = cls._bestand.get(pfad)
            if eintrag is not None and eintrag[0] == mtime:
                return eintrag
            from humanbody_core.skeleton import SkeletonGeometry
            from humanbody_core.skeleton.gltfskelett import Gltfskelett
            from humanbody_core.skeleton.skelettausrichtung import Skelettausrichtung
            from humanbody_core.skeleton.formats.uma_knochen import Umazuordnung
            roh = Gltfskelett(pfad).knochen()
            knochen = Skelettausrichtung(roh, Umazuordnung.LINKS,
                                         Umazuordnung.RECHTS).ausgerichtet()
            geometrie = SkeletonGeometry.from_three(knochen, cls.RICHTUNGSACHSE)
            # Erst wenn beides steht, wird es sichtbar — sonst saehe ein
            # zweiter Faden die Knochen ohne die Geometrie.
            eintrag = cls._bestand[pfad] = (mtime, knochen, geometrie)
            logger.info('Umaskelett: %s gelesen, %d Knochen', pfad, len(knochen))
            return eintrag

    @classmethod
    def vergessen(cls):
        u"""Den Speicher leeren — fuer Tests und nach einem Katalogwechsel."""
        cls._bestand = {}
