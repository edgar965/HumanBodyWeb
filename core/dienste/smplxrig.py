# -*- coding: utf-8 -*-
u"""Smplxrig — Skelett und Hautgewichte des SMPL-X-Modells fuer einen Koerper.

WARUM (Edgar, 15.09.2026: „kannst du die SMPL Modelle auf SMPL-X umstellen
(also inkl. Gesichtsknochen)?"): Die SMPL-Figur der Szene trug das
24-Gelenke-Skelett von SMPL — ohne Kiefer, Augen und Finger. Seither
kommen Skelett und Haut aus SMPL-X (55 Gelenke, `SMPL/xskelett.py`); die
Modelldateien liegen unter `settings.SMPLX_MODELS_DIR`.

Herausgeloest aus `Smplfiguren` (276 Zeilen): Dort bleiben Katalog, Netz
und Masse; hier steht, was aus dem Modell kommt.

ZWEI RICHTUNGEN DES UEBERTRAGS — nicht verwechseln (07.09.2026):

    Skelett   je SMPL-X-Punkt der naechste fremde Punkt (10.475 Eintraege,
              Eingabe des Regressors)
    Haut      je fremdem Punkt der naechste SMPL-X-Punkt (ein Gewicht je
              Punkt des angezeigten Netzes)

Beide auf einem SMPL-X-Referenzkoerper in der HALTUNG des fremden Netzes
(`arm_pose_angle` aus dessen YAML). Ein SMPL-X-Netz (10.475 Punkte) braucht
keinen Uebertrag; die alten SMPL-Koerper (6.890) und GarmentCodes eigene
(23.752) laufen ueber ihn.
"""

import logging

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Smplxrig']


class Smplxrig:
    u"""Lesender Zugang zum SMPL-X-Modell, je Geschlecht einmal geladen."""

    _gelenke = {}
    _haut = {}
    _koerper = {}

    @staticmethod
    def ordner():
        return str(settings.SMPLX_MODELS_DIR)

    @classmethod
    def vorhanden(cls, geschlecht='female'):
        from SMPL.xkoerper import Smplxkoerper
        return Smplxkoerper.vorhanden(geschlecht, cls.ordner())

    # ----------------------------------------------------------------- Modell

    @classmethod
    def koerper(cls, geschlecht):
        u"""Das formbare Modell (`Smplxkoerper`) — 75 MB, deshalb einmal."""
        from SMPL.xkoerper import Smplxkoerper
        if geschlecht not in cls._koerper:
            cls._koerper[geschlecht] = Smplxkoerper.laden(geschlecht, cls.ordner())
        return cls._koerper[geschlecht]

    @classmethod
    def gelenke(cls, geschlecht):
        from SMPL.xgelenke import Smplxgelenke
        if geschlecht not in cls._gelenke:
            cls._gelenke[geschlecht] = Smplxgelenke.aus_modell(geschlecht, cls.ordner())
        return cls._gelenke[geschlecht]

    @classmethod
    def haut(cls, geschlecht):
        from SMPL.xhaut import Smplxhaut
        if geschlecht not in cls._haut:
            cls._haut[geschlecht] = Smplxhaut.aus_modell(geschlecht, cls.ordner())
        return cls._haut[geschlecht]

    @classmethod
    def vergessen(cls):
        u"""Den Speicher leeren — fuer Tests."""
        cls._gelenke, cls._haut, cls._koerper = {}, {}, {}

    # ---------------------------------------------------------------- Skelett

    @classmethod
    def kette(cls, name, punkte, geschlecht, armwinkel):
        u"""Das `Gelenkskelett` zu diesem Netz — oder `None`, wenn das Modell
        fehlt. `None` ist eine Antwort: Die Figur bleibt dann ein Netz."""
        try:
            gelenke = cls.gelenke(geschlecht)
            if gelenke.passt(punkte):
                return gelenke.kette(punkte)
            referenz = cls.referenz(geschlecht, armwinkel)
            uebertrag = gelenke.uebertragen(punkte, referenz)
            cls._melden('Skelett', name, punkte, armwinkel, uebertrag)
            return gelenke.kette_uebertragen(punkte, uebertrag)
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('SMPL-X-Skelett fuer %s nicht baubar: %s', name, fehler)
            return None

    @classmethod
    def skelett(cls, name, punkte, geschlecht, armwinkel):
        u"""`{name, knochen}` — die Antwort an den Browser, oder `None`."""
        from SMPL.xgelenke import Smplxgelenke
        kette = cls.kette(name, punkte, geschlecht, armwinkel)
        if kette is None:
            return None
        bezeichnung = Smplxgelenke.BEZEICHNUNG
        if not cls.gelenke(geschlecht).passt(punkte):
            bezeichnung += ', uebertragen'
        return {'name': bezeichnung, 'knochen': kette.bauplan()}

    # ------------------------------------------------------------------- Haut

    @classmethod
    def hautgewichte(cls, name, punkte, geschlecht, armwinkel):
        u"""`{knochen, index, gewicht}` (numpy) — oder `None`."""
        from SMPL.uebertrag import Netzuebertrag
        try:
            haut = cls.haut(geschlecht)
            zuordnung = None
            if not cls.gelenke(geschlecht).passt(punkte):
                referenz = cls.referenz(geschlecht, armwinkel)
                uebertrag = Netzuebertrag.bauen(punkte, referenz)
                cls._melden('Hautgewichte', name, punkte, armwinkel, uebertrag)
                zuordnung = uebertrag.zuordnung
            index, anteil = haut.fuer_punkte(len(punkte), zuordnung)
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('SMPL-X-Hautgewichte fuer %s nicht baubar: %s',
                           name, fehler)
            return None
        return {'knochen': haut.knochennamen(), 'index': index, 'gewicht': anteil}

    # ---------------------------------------------------------------- Helfer

    @classmethod
    def referenz(cls, geschlecht, armwinkel):
        u"""Der SMPL-X-Durchschnittskoerper in der Haltung des fremden Netzes."""
        return cls.koerper(geschlecht).a40(None, grad=armwinkel)

    @staticmethod
    def _melden(was, name, punkte, armwinkel, uebertrag):
        guete = uebertrag.guete
        logger.info('SMPL-X-%s uebertragen auf %s (%d Punkte, %.1f Grad): '
                    'Zuordnung Median %.4f, p90 %.4f der Koerperhoehe',
                    was, name, len(punkte), armwinkel, guete['median'],
                    guete['p90'])
