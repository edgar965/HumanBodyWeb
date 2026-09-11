# -*- coding: utf-8 -*-
u"""Das sichtbare Koerpernetz des Films — je Bild aus der Basis unterteilt.

Die Szene zeigt das Catmull-Clark-unterteilte Netz (70.851 Punkte); der
Film rechnete bis zum 11.09.2026 mit der 18K-Aussenhaut und zeigte deshalb
Haut durch die Leggings, die an das feine Netz angelegt ist. Die
Unterteilung ist LINEAR (`unterteiler.subdivide` = `W @ basis`): LBS und
Weichgewebe laufen weiter auf den Basispunkten (1,7 s je Bild waeren es auf
70.851), und das feine Netz folgt je Bild in Millisekunden.

Ein Teil traegt `unterteiler` und `fein_dreiecke`, wenn es so gerechnet
wird; ohne die beiden ist `haut.folge` selbst das sichtbare Netz (Stoff,
oder eine Figur ohne Unterteiler).
"""
import numpy as np


class Feinkoerper:
    u"""Feine Punkte eines Teils in Ruhe und je Bild, mit Zwischenspeicher."""

    @staticmethod
    def hat(teil):
        return teil.get('unterteiler') is not None

    @classmethod
    def ruhe(cls, teil):
        u"""Die sichtbaren Punkte in Ruhelage."""
        if not cls.hat(teil):
            return teil['haut'].punkte
        if 'fein_ruhe' not in teil:
            teil['fein_ruhe'] = np.asarray(
                teil['unterteiler'].subdivide(teil['haut'].punkte), dtype=np.float64)
        return teil['fein_ruhe']

    @classmethod
    def dreiecke(cls, teil):
        return teil['fein_dreiecke'] if cls.hat(teil) else teil['dreiecke']

    @classmethod
    def bild(cls, teil, nummer):
        u"""Die sichtbaren Punkte fuer Bild `nummer` — nach Physik, weil die
        Bahn (`haut.folge`) dann schon den Zuschlag traegt. Der Speicher
        haengt an der Bahn-Kennung: Wird die Bahn ersetzt (Physik), gilt
        der alte Eintrag nicht mehr."""
        folge = teil['haut'].folge
        if not cls.hat(teil):
            return folge[nummer]
        merker = teil.setdefault('fein_folge', {})
        schluessel = (id(folge), nummer)
        if schluessel not in merker:
            merker.clear() if any(k[0] != id(folge) for k in merker) else None
            merker[schluessel] = np.asarray(
                teil['unterteiler'].subdivide(folge[nummer]), dtype=np.float64)
        return merker[schluessel]
