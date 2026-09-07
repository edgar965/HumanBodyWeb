# -*- coding: utf-8 -*-
u"""Mhloeschmaske — welche Koerperpunkte ein Kleidungsstueck verdeckt.

DER BEFUND, DER DAZU GEFUEHRT HAT (06.09.2026)
==============================================
Der erste Lauf mit `female_casualsuit01` auf dem MakeHuman-Basiskoerper sah
falsch aus: helle Flecken auf Brust, Bauch und Oberschenkeln. Gemessen statt
geraten — Vorzeichen des Abstands jedes Stoffpunktes zur naechsten Hautstelle,
entlang deren Normale:

    tops/female_casualsuit01     2.197 Punkte   23,5 % INNERHALB der Haut,
                                                tiefster Durchstich 21,1 mm
    dresses/toigo_shift_dress    6.892 Punkte    2,1 %, 16,0 mm
    underwear/elvs_bow_front_bra 5.339 Punkte    5,6 %, 14,4 mm
    pants/cortu_cargo_pants        211 Punkte    0,0 %

Das ist KEIN Fehler der Anpassung. MakeHuman legt Kleidung bewusst dicht an
und blendet die Haut darunter aus — jede `.mhclo` bringt dafuer einen Abschnitt
`delete_verts` mit, eine Liste von Punktnummern des Basisnetzes. 224 der
Dateien in der Bibliothek haben ihn. Ohne ihn steht die Haut durch den Stoff,
und zwar genau dort, wo der Stoff eng anliegt.

DAS FORMAT
==========
Zahlen und Bereiche, durch Leerzeichen getrennt, ueber viele Zeilen. Der
Bindestrich ist ein EIGENES Wort:

    1355 - 1413 1420 - 1423 1430 - 1455 1502 1506 - 1509

heisst 1355..1413, 1420..1423, 1430..1455, 1502, 1506..1509. Wer den
Bindestrich als Teil der Zahl liest, bekommt negative Nummern und verliert
jeden Bereich — das faellt nicht auf, weil die Maske dann nur kleiner wird.
"""

import glob
import logging
import os
import threading

logger = logging.getLogger('core')

__all__ = ['Mhloeschmaske']


class Mhloeschmaske:
    u"""Die `delete_verts`-Liste einer `.mhclo`, einmal je Stueck gelesen."""

    ABSCHNITT = 'delete_verts'

    _gelesen = {}
    _schloss = threading.Lock()

    @classmethod
    def punkte(cls, kennung):
        u"""Die verdeckten Punktnummern als `frozenset` — leer, wenn keine da."""
        if kennung in cls._gelesen:
            return cls._gelesen[kennung]
        with cls._schloss:
            if kennung not in cls._gelesen:
                cls._gelesen[kennung] = cls._lesen(kennung)
        return cls._gelesen[kennung]

    @classmethod
    def vereinigt(cls, kennungen):
        u"""Alles, was diese Stuecke zusammen verdecken."""
        alle = set()
        for kennung in kennungen:
            alle |= cls.punkte(kennung)
        return alle

    # ------------------------------------------------------------------ lesen

    @classmethod
    def _lesen(cls, kennung):
        from .mhgarderobe import Mhgarderobe
        ordner = Mhgarderobe.verzeichnis(kennung)
        if not ordner:
            return frozenset()
        dateien = glob.glob(os.path.join(ordner, '*.mhclo'))
        if not dateien:
            return frozenset()
        try:
            with open(dateien[0], encoding='utf-8', errors='replace') as datei:
                punkte = cls._abschnitt(datei)
        except OSError as fehler:
            logger.debug('Löschmaske nicht lesbar (%s): %s', kennung, fehler)
            return frozenset()
        logger.debug('Löschmaske %s: %d Punkte', kennung, len(punkte))
        return frozenset(punkte)

    @classmethod
    def _abschnitt(cls, zeilen):
        u"""Alles hinter `delete_verts` einsammeln."""
        gefunden = False
        woerter = []
        for zeile in zeilen:
            wort = zeile.strip()
            if not gefunden:
                gefunden = wort == cls.ABSCHNITT
                continue
            woerter.extend(wort.split())
        return cls.nummern(woerter)

    @staticmethod
    def nummern(woerter):
        u"""`['1', '-', '4', '9']` -> `{1, 2, 3, 4, 9}`."""
        punkte = set()
        vorher = None
        bereich = False
        for wort in woerter:
            if wort == '-':
                bereich = True
                continue
            try:
                zahl = int(wort)
            except ValueError:
                bereich = False
                continue
            if bereich and vorher is not None:
                punkte.update(range(min(vorher, zahl), max(vorher, zahl) + 1))
                bereich = False
            else:
                punkte.add(zahl)
            vorher = zahl
        return punkte
