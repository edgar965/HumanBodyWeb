# -*- coding: utf-8 -*-
u"""Mhformung — aus Reglerstellungen ein verformtes MakeHuman-Netz.

Der Kern ist eine Zeile aus `core/algos3d.Target.apply`::

    coord[nummern] += verschiebungen * gewicht

Mehr passiert beim Modellieren in MakeHuman nicht: Jedes Ziel, dessen Gewicht
nicht 0 ist, verschiebt seine Punkte. Die ganze Kunst steckt davor — in der
Frage, WELCHE Ziele mit welchem Gewicht gelten (`Mhmodifikatoren`).

Gerechnet wird auf dem ROHNETZ in MakeHuman-Dezimetern, weil die
Verschiebungen in derselben Einheit und denselben Achsen stehen. Umgerechnet
wird erst danach (`Mhbasisnetz.punkte_three`).

WAS DIE KLEIDUNG DAVON HAT: `MHCLOProxy.fit_vectorized` bekommt genau diesen
verformten Koerper. Eine `.mhclo` haengt jeden Stoffpunkt an drei
Koerperpunkte — verschieben sich die, wandert der Stoff mit. Genau so folgt
Kleidung in MakeHuman dem Modellieren, und deshalb braucht es hier keinen
zweiten Anpassungsschritt.
"""

import hashlib
import json
import logging
import threading
from collections import OrderedDict

import numpy as np

from .mhbasisnetz import Mhbasisnetz
from .mhmakrowerte import Mhmakrowerte
from .mhmodifikatoren import Mhmodifikatoren
from .mhzielablage import Mhzielablage

logger = logging.getLogger('core')

__all__ = ['Mhformung']


class Mhformung:
    u"""Ein Satz Reglerstellungen und das Netz, das daraus wird."""

    #: Zuletzt gerechnete Netze, nach Fingerabdruck. Eine Anfrage holt den
    #: Koerper UND je Kleidungsstueck denselben Traeger — ohne diesen
    #: Speicher waere dieselbe Verformung dreimal gerechnet. Klein gehalten:
    #: ein Netz sind 19.158 x 3 float64 = 460 KB.
    _gerechnet = OrderedDict()
    _HOECHSTENS = 8
    _schloss = threading.Lock()

    def __init__(self, makro=None, regler=None):
        #: Die Makroregler (Geschlecht, Alter, Rasse, Muskeln, …).
        self.makro = Mhmakrowerte(makro)
        #: Die Detailregler, `{'head/head-age-decr|incr': 0.4}`.
        self.regler = dict(regler or {})

    # ---------------------------------------------------------------- rechnen

    def punkte(self):
        u"""Das verformte Rohnetz (N, 3) in MakeHuman-Dezimetern — gepuffert."""
        schluessel = self.fingerabdruck()
        with Mhformung._schloss:
            fertig = Mhformung._gerechnet.get(schluessel)
        if fertig is not None:
            return fertig
        punkte = self._rechnen()
        with Mhformung._schloss:
            Mhformung._gerechnet[schluessel] = punkte
            while len(Mhformung._gerechnet) > Mhformung._HOECHSTENS:
                Mhformung._gerechnet.popitem(last=False)
        return punkte

    def _rechnen(self):
        u"""Das verformte Rohnetz (N, 3) in MakeHuman-Dezimetern.

        AUCH IN DER VORGABESTELLUNG WIRD GERECHNET, und das ist der Punkt, an
        dem eine naheliegende Abkuerzung falsch waere: `base.obj` ist NICHT
        MakeHumans Vorgabefigur. Bei mittigen Reglern haben die
        Makro-Zielgruppen zusammen das Gewicht 1,0 —

            macrodetails            6 Ziele je 1/6   (3 Rassen x 2 Geschlechter,
                                                      Alter „young" = 1)
            macrodetails-universal  2 Ziele je 0,5   (Geschlecht, sonst Mitte)

        — und erst mit ihnen entsteht der Mensch, den MakeHuman beim Start
        zeigt. Wer bei Vorgabe das nackte Basisnetz zurueckgibt, bekommt eine
        Figur, die es in MakeHuman nirgends gibt.

        Ohne Ziele auf der Platte kommt das Basisnetz unveraendert zurueck —
        die Figur bleibt benutzbar, nur ohne Modellierregler.
        """
        basis = Mhbasisnetz.holen()
        punkte = basis.punkte.copy()
        if not Mhzielablage.bereit():
            return punkte
        if not Mhmodifikatoren.vorhanden():
            logger.warning('Keine MakeHuman-Modifier-Datei — Regler wirken nicht')
            return punkte
        gewichte = Mhmodifikatoren.holen().gewichte(self.regler, self.makro)
        angewandt = 0
        for pfad, gewicht in gewichte.items():
            nummern, verschiebungen = Mhzielablage.ziel(pfad)
            if not len(nummern):
                continue
            # Ziele koennen Punkte nennen, die es im Netz nicht gibt (der
            # Upstream mischt Netzfassungen); die fallen weg statt zu werfen.
            gueltig = nummern < len(punkte)
            np.add.at(punkte, nummern[gueltig],
                      verschiebungen[gueltig] * gewicht)
            angewandt += 1
        logger.debug('MakeHuman geformt: %d von %d Zielen mit Gewicht',
                     angewandt, len(gewichte))
        return punkte

    # ------------------------------------------------------------ uebernehmen

    @classmethod
    def aus_abfrage(cls, makro_roh, regler_roh):
        u"""Aus zwei JSON-Woerterbuechern der Seite."""
        return cls(makro_roh if isinstance(makro_roh, dict) else None,
                   regler_roh if isinstance(regler_roh, dict) else None)

    def als_dict(self):
        return {'makro': dict(self.makro.werte), 'regler': dict(self.regler)}

    def fingerabdruck(self):
        u"""Ein kurzer Name fuer diese Stellung — Schluessel im Zwischenspeicher.

        Aus den Werten selbst, nicht aus einer laufenden Nummer: Zwei gleiche
        Stellungen sollen dasselbe Netz bekommen, auch aus zwei Sitzungen.
        Reglerwerte von 0 fallen heraus — sonst haetten „nie angefasst" und
        „auf 0 zurueckgestellt" verschiedene Abdruecke und derselbe Koerper
        laege zweimal im Speicher.
        """
        stand = {'makro': dict(self.makro.werte),
                 'regler': {k: v for k, v in self.regler.items() if v}}
        text = json.dumps(stand, sort_keys=True)
        return hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]
