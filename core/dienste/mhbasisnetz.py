# -*- coding: utf-8 -*-
u"""Mhbasisnetz — das MakeHuman-Basisnetz (hm08), einmal gelesen.

WARUM ES DIESE FIGUR GIBT (Edgar, 06.09.2026: „Implementiere auch das
Hinzufuegen eines MakeHuman Modells … unter anderem gibt es garments fuer
MakeHuman, die sollten dann perfekt funktionieren")
=====================================================================
Die 181 Kleidungsstuecke in `HumanBody/data/garment_library/` sind
MakeHuman-Stuecke: eine `.mhclo`-Zuordnung, in der JEDER Stoffpunkt an drei
Punkten des MakeHuman-Basiskoerpers haengt (Gewichte + Versatz). Auf einem
anderen Koerper ist das eine Naeherung — `MhProxyAnpassung` schiebt, glaettet
und rueckt deshalb nach. Auf DIESEM Koerper ist es die Rechnung selbst.

Gemessen (06.09.2026, `MHCLOProxy.fit_full` gegen `base_vertices.npy`):

    tops/female_casualsuit01   2.197 Punkte   Abstand zur Haut  8,2 mm Median
    pants/cortu_cargo_pants      211 Punkte                    15,3 mm
    shoes/toigo_mj_cloth_shoes   556 Punkte                     7,5 mm
    dresses/toigo_shift_dress  6.892 Punkte                    13,5 mm

Zum Einordnen: die Messlatte des GarmentCode-Wegs liegt bei 13,2 mm Median
(CLAUDE.md, 06.09.2026). Entscheidend ist eine zweite Zahl: 6.591 der
Zuordnungen des Anzugs zeigen auf Punkte mit Index >= 13.380 — die
HELFERGEOMETRIE. Nur weil hier alle 19.158 Punkte der Datei da sind, ist keine
einzige Zuordnung ungueltig; sonst faengt `MHCLOProxy` sie mit
Nachbarschaftsmittelung ab.

WAS IN DER DATEI STEHT
======================
`MakeHuman/base.obj` (CC0, MakeHuman-Community) — 19.158 Punkte,
18.486 VIERECKE, 139 Gruppen:

    body            13.378 Vierecke, Punkte 0..13.379, 1,666 m hoch
    helper-*         4.358 Vierecke   Helfergeometrie (Strumpf, Rock, Haar …),
                                      Traeger der .mhclo-Zuordnungen
    joint-*            750 Vierecke   125 Gelenkwuerfel, je sechs Flaechen

Einheiten: MakeHuman rechnet in DEZIMETERN mit Y oben. Three.js rechnet in
Metern mit Y oben — es wird also nur skaliert, nicht gedreht.
`base_vertices.npy` ist Punkt fuer Punkt dieselbe Datei (geprueft mit
`np.allclose`); den Fit rechnet `Mhkleidnetz` weiter darauf, weil die
Zuordnungen in der `.mhclo` genau diese Nummerierung meinen.

DER UMLAUFSINN IST GEMESSEN, NICHT GERATEN
==========================================
`[a,b,c] + [a,c,d]` ergibt ein Volumen von **+0,0549 m3** (ein Mensch von
1,67 m hat rund 60-70 Liter), die umgekehrte Folge dasselbe negativ. Positiv
heisst: Normalen nach aussen, und genau so zeichnet Three.js die Vorderseite.
`CatmullClarkSubdivider._triangulieren` dreht den Umlaufsinn um — fuer die
geglaettete Fassung wird er deshalb zurueckgedreht (`Mhglaettung`). Gerechnet
wird das in `Mhnetzformen`; hier stehen nur Punkte und Gruppen.
"""

import logging
import os
import threading
from collections import OrderedDict

import numpy as np
from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Mhbasisnetz']


class Mhbasisnetz:
    u"""Punkte und Flaechengruppen des MakeHuman-Basisnetzes."""

    DATEI = 'base.obj'
    #: MakeHuman rechnet in Dezimetern; Y ist schon oben.
    MASSSTAB = 0.1

    KOERPERGRUPPE = 'body'
    HELFERVORSATZ = 'helper-'
    GELENKVORSATZ = 'joint-'

    #: Schluessel -> (Anzeigename, Erklaerung). Reihenfolge = die im Panel.
    TEILE = OrderedDict((
        ('koerper', (u'Körper', u'Die Haut — was MakeHuman anzeigt.')),
        ('helfer', (u'Helfergeometrie',
                    u'Strumpf, Rock, Haar, Zunge: unsichtbare Hilfsflächen, '
                    u'an denen die Kleidungszuordnungen hängen.')),
        ('gelenke', (u'Gelenkwürfel',
                     u'Je sechs Flächen an jeder Knochenstelle — MakeHumans '
                     u'Marker für das Skelett.')),
    ))

    _eines = None
    _schloss = threading.Lock()

    def __init__(self, punkte, gruppen):
        #: (N, 3) float64 in MakeHuman-Dezimetern, Y oben.
        self.punkte = punkte
        #: Gruppenname -> (F, 4) int32.
        self.gruppen = gruppen
        koerper = self._punktnummern(('koerper',))
        self._boden = (float(self.punkte_three()[koerper][:, 1].min())
                       if len(koerper) else 0.0)

    # ------------------------------------------------------------------ laden

    @classmethod
    def holen(cls):
        u"""Das eine Basisnetz — beim ersten Aufruf gelesen.

        Ein Schloss, doppelt geprueft, wie bei `Kleiderbibliothek`: Daphne
        beantwortet nebenlaeufig, und zwei Anfragen wuerden die Datei sonst
        beide lesen.
        """
        if cls._eines is not None:
            return cls._eines
        with cls._schloss:
            if cls._eines is None:
                cls._eines = cls._einlesen()
        return cls._eines

    @classmethod
    def pfad(cls):
        return os.path.join(str(settings.MAKEHUMAN_ROOT), cls.DATEI)

    @classmethod
    def vorhanden(cls):
        return os.path.isfile(cls.pfad())

    @classmethod
    def _einlesen(cls):
        u"""Punkte und Gruppen aus der OBJ.

        Ein eigener Leser, weil `GarmentFitter.obj_io` die Gruppen NICHT
        mitliest — und ohne sie stuenden Helfergeometrie und Gelenkwuerfel
        untrennbar im selben Netz wie die Haut.
        """
        punkte = []
        gruppen = OrderedDict()
        laufend = 'standard'
        with open(cls.pfad(), encoding='utf-8', errors='replace') as datei:
            for zeile in datei:
                if zeile.startswith('v '):
                    teile = zeile.split()
                    punkte.append((float(teile[1]), float(teile[2]),
                                   float(teile[3])))
                elif zeile.startswith('g '):
                    laufend = zeile[2:].strip()
                elif zeile.startswith('f '):
                    ecken = [int(p.split('/')[0]) - 1
                             for p in zeile.split()[1:]]
                    if len(ecken) == 4:
                        gruppen.setdefault(laufend, []).append(ecken)
        netz = cls(np.array(punkte, dtype=np.float64),
                   OrderedDict((name, np.array(flaechen, dtype=np.int32))
                               for name, flaechen in gruppen.items()))
        logger.info('MakeHuman-Basisnetz gelesen: %d Punkte, %d Gruppen',
                    len(netz.punkte), len(netz.gruppen))
        return netz

    # ----------------------------------------------------------- Gliederung

    @classmethod
    def teilname(cls, gruppe):
        u"""Zu welchem der drei Teile gehoert diese OBJ-Gruppe?"""
        if gruppe == cls.KOERPERGRUPPE:
            return 'koerper'
        if gruppe.startswith(cls.GELENKVORSATZ):
            return 'gelenke'
        return 'helfer'

    def steckbrief(self):
        u"""Der Eintrag, den der Dialog „Charakter hinzufügen" anzeigt.

        Eine Liste mit EINEM Eintrag — MakeHuman hat genau ein Basisnetz, und
        alles Weitere waeren dort Modellierregler (`.target`-Dateien), die
        dieses Projekt nicht mitbringt. Es bleibt eine Liste, weil eine zweite
        Topologie (MakeHumans „Proxy"-Netze) genau hier stuende.
        """
        vierecke = self.vierecke(('koerper',))
        punkte = self.punkte_three()[self._punktnummern(('koerper',))]
        return {
            'name': 'basis',
            'anzeige': u'MakeHuman-Basiskörper (hm08)',
            'punkte': int(len(punkte)),
            'flaechen': int(len(vierecke)),
            'hoehe': float(punkte[:, 1].max() - punkte[:, 1].min()),
            'teile': self.uebersicht(),
        }

    def uebersicht(self):
        u"""Je Teil: Anzeigename, Erklaerung, Flaechen- und Punktzahl."""
        aus = []
        for schluessel, (anzeige, erklaerung) in self.TEILE.items():
            vierecke = self.vierecke((schluessel,))
            aus.append({
                'schluessel': schluessel,
                'name': anzeige,
                'erklaerung': erklaerung,
                'flaechen': int(len(vierecke)),
                'punkte': int(len(np.unique(vierecke))) if len(vierecke) else 0,
            })
        return aus

    def vierecke(self, teile):
        u"""Alle Vierecke der genannten Teile, aneinandergehaengt."""
        gewaehlt = [flaechen for name, flaechen in self.gruppen.items()
                    if self.teilname(name) in teile]
        if not gewaehlt:
            return np.zeros((0, 4), dtype=np.int32)
        return np.concatenate(gewaehlt, axis=0)

    def _punktnummern(self, teile):
        vierecke = self.vierecke(teile)
        if not len(vierecke):
            return np.zeros((0,), dtype=np.int32)
        return np.unique(vierecke)

    # -------------------------------------------------------------- Punkte

    def punkte_three(self, roh=None):
        u"""(N, 3) in Metern mit Y oben — der Raum von Three.js.

        `roh` ist das VERFORMTE Netz aus `Mhformung`; ohne Angabe gilt das
        Basisnetz. Alle drei Umrechnungen nehmen es entgegen, damit die
        Modellierregler nicht an einer davon vorbeilaufen.
        """
        return (self.punkte if roh is None else roh) * self.MASSSTAB

    def punkte_blender(self, roh=None):
        u"""(N, 3) in Metern mit Z oben — der Raum, in dem `MHCLOProxy` rechnet."""
        roh = self.punkte if roh is None else roh
        return np.column_stack([roh[:, 0] * self.MASSSTAB,
                                -roh[:, 2] * self.MASSSTAB,
                                roh[:, 1] * self.MASSSTAB])

    @property
    def boden(self):
        u"""Die y-Lage der Fusssohlen des BASISNETZES (Meter, Three-Achsen)."""
        return self._boden

    def boden_von(self, roh=None):
        u"""Die Fusssohlen eines (verformten) Netzes.

        Sie kommen IMMER aus der Koerpergruppe, nie aus der sichtbaren
        Auswahl: Sonst huepfte die Figur, sobald jemand die Gelenkwuerfel
        dazuschaltet. Und sie kommen aus dem VERFORMTEN Netz — ein Kind ist
        kleiner, seine Fuesse stehen woanders, und ohne diese Zeile schwebte
        es ueber dem Boden.
        """
        if roh is None:
            return self._boden
        koerper = self._punktnummern(('koerper',))
        if not len(koerper):
            return 0.0
        return float(self.punkte_three(roh)[koerper][:, 1].min())

    def punkte_am_boden(self, nummern, roh=None):
        u"""Diese Punkte in Metern, Y oben, Fuesse auf 0."""
        punkte = self.punkte_three(roh)[nummern]
        punkte[:, 1] -= self.boden_von(roh)
        return punkte.astype(np.float32)
