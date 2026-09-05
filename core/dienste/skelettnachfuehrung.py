# -*- coding: utf-8 -*-
u"""Skelettnachfuehrung — die Gelenkanpassung je Geschlecht bereithalten.

WARUM EIN DIENST (05.09.2026): `Gelenkanpassung` braucht zwei Dinge, die
sich nie aendern — das exportierte DEF-Skelett und das Grundnetz der
Koerperart ohne Morphs. Beides einmal zu laden kostet 27 ms und einen
KD-Baum ueber 18.210 Punkte; je Regleranschlag waere das die teuerste
Zeile im ganzen Ablauf. Danach kostet das Nachfuehren 2,1 ms.

Der Zwischenspeicher liegt wie bei `Charakterdaten` als Klassenattribut und
unter demselben `Ladeschloss` — es gibt einen Prozess und eine Datenlage,
und Daphne beantwortet parallel.

WOGEGEN DAS BEZUGSNETZ GEHT: `def_skeleton.json` wurde aus Blender
exportiert, als der Koerper auf ``Female_Caucasian`` ohne Morphs stand.
Genau dieses Netz ist die Ruhelage — mit ihm liefert die Anpassung bei
Morph 0 Zahl fuer Zahl die Datei zurueck (gemessen: groesste Abweichung
0,0e+00 m, 0 bewegte Knochen). Ein anderes Bezugsnetz waere ein stiller
Versatz beim ersten Seitenaufruf.
"""
import json
import logging
import os

from django.conf import settings

from humanbody_core import CharacterState, Gelenkanpassung

from ..daten.ladeschloss import Ladeschloss
from .charakterdaten import Charakterdaten

logger = logging.getLogger('core')


class Skelettnachfuehrung:
    u"""Zugriff auf die `Gelenkanpassung` — eine je Geschlecht."""

    _anpassung = {}
    _schloesser = Ladeschloss()

    #: Die Koerperart, in der das DEF-Skelett exportiert wurde. Sie ist die
    #: Ruhelage, nicht bloss eine Vorgabe: Wer hier etwas anderes einsetzt,
    #: verschiebt das Skelett schon vor dem ersten Regler.
    RUHEART = {'female': 'Female_Caucasian', 'male': 'Male_Caucasian'}

    @classmethod
    def fuer(cls, geschlecht='female'):
        u"""Die Anpassung fuer dieses Geschlecht, oder ``None``.

        ``None`` heisst: Es gibt kein exportiertes Skelett (dann laeuft die
        Seite wie bisher ohne Nachfuehrung weiter) — kein Fehler, sondern
        derselbe Zustand, den auch `Skelettdaten.def_skelett` mit 404
        beantwortet.
        """
        def bauen():
            # `False` statt `None` merken: `Ladeschloss.einmal` haelt `None`
            # fuer „noch nicht geladen" und wuerde bei fehlendem Skelett bei
            # JEDEM Regleranschlag die Datei suchen und warnen.
            gebaut = cls._bauen(geschlecht) or False
            cls._anpassung[geschlecht] = gebaut
            return gebaut
        return cls._schloesser.einmal(
            'skelett_%s' % geschlecht,
            lambda: cls._anpassung.get(geschlecht),
            bauen) or None

    @classmethod
    def _bauen(cls, geschlecht):
        knochen = cls._skelettdatei(geschlecht)
        if not knochen:
            return None
        zustand = CharacterState(Charakterdaten.morphdaten(),
                                 Charakterdaten.voreinstellungen())
        zustand.set_body_type(cls.RUHEART.get(geschlecht, 'Female_Caucasian'))
        anpassung = Gelenkanpassung(knochen, zustand.compute())
        logger.info('Gelenkanpassung %s bereit: %d Knochen, %d Netzpunkte',
                    geschlecht, len(anpassung.namen), anpassung.punktzahl)
        return anpassung

    @staticmethod
    def _skelettdatei(geschlecht):
        u"""Die ``bones``-Liste aus ``def_skeleton.json``, oder ``None``."""
        ordner = str(settings.HUMANBODY_DATA_DIR)
        if geschlecht == 'male':
            ordner += '_male'
        pfad = os.path.join(ordner, 'def_skeleton.json')
        if not os.path.isfile(pfad):
            logger.warning('Kein DEF-Skelett unter %s — keine Nachfuehrung',
                           pfad)
            return None
        with open(pfad, 'r', encoding='utf-8') as datei:
            return json.load(datei).get('bones') or None

    @classmethod
    def bewegte(cls, geschlecht, netz):
        u"""``{Knochenname: [x,y,z]}`` der bewegten Knochen — oder ``{}``.

        Leer heisst hier immer „nichts zu tun": kein Skelett vorhanden, ein
        fremdes Netz (der Testcharakter hat 17.996 statt 18.210 Punkte), oder
        schlicht ein Koerper in der Ruhelage.
        """
        anpassung = cls.fuer(geschlecht)
        if anpassung is None or not anpassung.passt_zu(netz):
            return {}
        return anpassung.bewegte(netz)
