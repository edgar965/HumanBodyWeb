# -*- coding: utf-8 -*-
u"""Mhzielbaum — welche Ziele es gibt und wovon ihr Gewicht abhaengt.

Portiert aus `MakeHuman/makehuman/lib/targets.py` (AGPL 3, siehe
`MakeHuman/HERKUNFT.md`). Der Kern ist eine Idee, die man kennen muss:

DER DATEINAME IST DIE FORMEL
============================
MakeHuman legt keine Zuordnungstabelle an. Der PFAD eines Ziels sagt, wann es
wirkt. `macrodetails/universal-female-young-maxmuscle-minweight.target` wird
zerlegt in Woerter (`/`, `-` und `.` trennen). Jedes Wort, das ein bekannter
WERT ist (`female`, `young`, `maxmuscle`, `minweight`), traegt sich in seine
Kategorie ein; alles Uebrige (`macrodetails`, `universal`) wird zum
Gruppenschluessel.

    Gewicht = Produkt aller Faktoren der eingetragenen Werte
              mal dem Faktor des Gruppenschluessels

Fuer dieses Ziel also `femaleVal · youngVal · maxmuscleVal · minweightVal · 1`.
Steht der Regler „Muskeln" bei 0,5, ist `maxmuscleVal` = 0 — das Ziel faellt
weg, ohne dass es jemand ausschliessen muesste.

DIE NEUN KATEGORIEN sind fest (`_cat_data` im Upstream) und stehen unten. Was
nicht darin vorkommt, ist Teil des Gruppennamens: So haengen die rund 250
Detailregler (`head-age-decr`, `l-foot-scale-incr`) an ihrem eigenen
Gruppenschluessel, den der Regler selbst auf 0..1 setzt.
"""

import logging
import os
import threading
from collections import OrderedDict

logger = logging.getLogger('core')

__all__ = ['Mhzielbaum', 'Mhziel']


class Mhziel:
    u"""Ein Ziel: Dateiname, Gruppenschluessel und die Werte, die es waehlen."""

    __slots__ = ('pfad', 'schluessel', 'werte')

    def __init__(self, pfad, schluessel, werte):
        #: Pfad relativ zum Zielordner, mit `/`, ohne `.target`.
        self.pfad = pfad
        #: Gruppenname (`macrodetails-universal`, `head-age-decr`).
        self.schluessel = schluessel
        #: Die eingetragenen Kategoriewerte (`['female', 'young']`).
        self.werte = werte

    @property
    def faktoren(self):
        u"""Alle Namen, deren Faktoren multipliziert das Gewicht ergeben."""
        return self.werte + [self.schluessel]

    def __repr__(self):
        return '<Mhziel %s %s>' % (self.pfad, self.werte)


class Mhzielbaum:
    u"""Alle Ziele des Upstreams, nach Gruppenschluessel geordnet."""

    #: Kategorie -> Werte. Wortgleich aus `lib/targets.py` `_cat_data`; die
    #: Reihenfolge ist dort ohne Bedeutung, die Namen sind es nicht.
    KATEGORIEN = OrderedDict((
        ('gender', ['male', 'female']),
        ('age', ['baby', 'child', 'young', 'old']),
        ('race', ['caucasian', 'asian', 'african']),
        ('muscle', ['maxmuscle', 'averagemuscle', 'minmuscle']),
        ('weight', ['minweight', 'averageweight', 'maxweight']),
        ('height', ['minheight', 'averageheight', 'maxheight']),
        ('breastsize', ['mincup', 'averagecup', 'maxcup']),
        ('breastfirmness', ['minfirmness', 'averagefirmness', 'maxfirmness']),
        ('bodyproportions', ['uncommonproportions', 'regularproportions',
                             'idealproportions']),
    ))

    #: Wert -> Kategorie (`_value_cat` im Upstream).
    WERTKATEGORIE = {wert: kat for kat, werte in KATEGORIEN.items()
                     for wert in werte}

    _baum = None
    _schloss = threading.Lock()

    def __init__(self, gruppen, ziele):
        #: Gruppenschluessel -> Liste von `Mhziel`.
        self.gruppen = gruppen
        #: Alle Ziele, in Lesereihenfolge.
        self.ziele = ziele

    # ------------------------------------------------------------------ laden

    @classmethod
    def wurzel(cls):
        from django.conf import settings
        return str(settings.MAKEHUMAN_ZIELE_DIR)

    @classmethod
    def vorhanden(cls):
        return os.path.isdir(cls.wurzel())

    @classmethod
    def holen(cls):
        if cls._baum is not None:
            return cls._baum
        with cls._schloss:
            if cls._baum is None:
                cls._baum = cls._einlesen()
        return cls._baum

    @classmethod
    def _einlesen(cls):
        gruppen = {}
        ziele = []
        wurzel = cls.wurzel()
        for ordner, _, namen in os.walk(wurzel):
            for name in sorted(namen):
                if not name.endswith('.target'):
                    continue
                pfad = os.path.relpath(os.path.join(ordner, name),
                                       wurzel).replace(os.sep, '/')
                ziel = cls.zerlegen(pfad[:-len('.target')])
                ziele.append(ziel)
                gruppen.setdefault(ziel.schluessel, []).append(ziel)
        logger.info('MakeHuman-Ziele gelesen: %d Dateien, %d Gruppen',
                    len(ziele), len(gruppen))
        return cls(gruppen, ziele)

    # --------------------------------------------------------------- zerlegen

    @classmethod
    def zerlegen(cls, pfad):
        u"""Einen Zielpfad in Gruppenschluessel und Kategoriewerte trennen.

        `macrodetails/universal-female-young-maxmuscle-minweight`
        -> Schluessel `macrodetails-universal`, Werte `['female', 'young',
        'maxmuscle', 'minweight']`.

        Die Werte kommen in der Reihenfolge der KATEGORIEN heraus, nicht in
        der des Dateinamens — sonst haengt das Ergebnis daran, wie jemand die
        Datei benannt hat.
        """
        eingetragen = {}
        teile = []
        for wort in pfad.replace('/', '-').split('-'):
            if not wort:
                continue
            kategorie = cls.WERTKATEGORIE.get(wort)
            if kategorie is None:
                teile.append(wort)
            elif kategorie not in eingetragen:
                eingetragen[kategorie] = wort
            else:
                # Zweimal dieselbe Kategorie kommt im Bestand nicht vor; wenn
                # doch, gilt das erste Wort und das zweite ist Namensteil.
                teile.append(wort)
        werte = [eingetragen[k] for k in cls.KATEGORIEN if k in eingetragen]
        return Mhziel(pfad, '-'.join(teile), werte)

    # -------------------------------------------------------- nachschlagen

    def in_gruppe(self, schluessel):
        u"""Die Ziele dieser Gruppe — leer, wenn es sie nicht gibt."""
        if not schluessel:
            return []
        return self.gruppen.get(schluessel, [])

    def abhaengigkeiten(self, schluessel):
        u"""Welche Kategorien die Gewichte dieser Gruppe beeinflussen."""
        kategorien = set()
        for ziel in self.in_gruppe(schluessel):
            kategorien.update(self.WERTKATEGORIE[w] for w in ziel.werte)
        return kategorien
