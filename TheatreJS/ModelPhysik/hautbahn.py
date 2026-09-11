# -*- coding: utf-8 -*-
u"""Ein Netz entlang einer Skelettbahn haeuten — Koerper wie Stoff.

Dieselbe Klasse fuer beides. Das ist der Punkt: Solange Koerper und
Kleidung durch DENSELBEN Code mit DENSELBEN Matrizen laufen, koennen sie
nicht auseinanderlaufen. Zwei getrennte Wege waren die Ursache der
„Zombie-Videos" vom 10.09.2026.

DIE RUHEPROBE IST DAS SCHARFE INSTRUMENT: Mit der Ruhelage gefuettert muss
LBS das Grundnetz Punkt fuer Punkt reproduzieren. Faellt sie durch, stimmt
eine Konvention nicht — und in Bewegung sieht auch ein falsches Skinning
plausibel aus.
"""
import numpy as np


class Hautbahn:
    u"""Lineares Blend-Skinning eines Netzes ueber eine Bildfolge."""

    def __init__(self, punkte, gewichte, namen, bahn):
        u"""`gewichte` ist n x b, `namen` nennt die Spalten."""
        self.punkte = np.asarray(punkte, dtype=np.float64)
        self.gewichte = np.asarray(gewichte, dtype=np.float64)
        self.namen = list(namen)
        self.bahn = bahn
        self._pruefen()

    def _pruefen(self):
        u"""Kein Knochen darf fehlen — sonst verschwindet Gewicht stumm.

        LBS teilt am Ende durch die Gewichtssumme. Faellt ein Knochen aus
        der Rechnung, wird sein Gewicht auf die uebrigen umverteilt, und
        der Punkt wandert mit dem falschen Knochen davon. Genau so sind
        3.670 von 7.290 Stoffpunkten zerfasert.
        """
        self.fehlend = [n for n in self.namen if n not in self.bahn.ruhe]
        if self.fehlend:
            raise ValueError(
                u'%d Knochen des Netzes fehlen im Skelett, darunter %s. '
                u'LBS wuerde ihr Gewicht stumm umverteilen.'
                % (len(self.fehlend), u', '.join(self.fehlend[:4])))
        summe = self.gewichte.sum(axis=1)
        self.ohne_gewicht = int((summe <= 1e-9).sum())

    # ----------------------------------------------------------- Rechnung

    def _lbs(self, lage):
        u"""Ein Bild: jeder Punkt gewichtet ueber seine Knochen."""
        ziel = np.zeros_like(self.punkte)
        summe = np.zeros((len(self.punkte), 1))
        for spalte, name in enumerate(self.namen):
            w = self.gewichte[:, spalte:spalte + 1]
            if not w.any():
                continue
            punkt, quat = lage[name]
            dreh = self.bahn.dreh(quat)
            rum, tum = self.bahn.ruhe_um[name]
            ziel += w * ((self.punkte @ rum.T + tum) @ dreh.T
                         + np.asarray(punkt))
            summe += w
        return ziel / np.maximum(summe, 1e-9)

    def ruheprobe(self):
        u"""Groesste Abweichung, wenn die Ruhelage eingesetzt wird."""
        return float(np.abs(self._lbs(self.bahn.ruhe) - self.punkte).max())

    def rechnen(self):
        u"""Die ganze Bahn: (Bilder, n, 3)."""
        self.folge = np.array([self._lbs(lage) for lage in self.bahn.lagen])
        return self.folge

    # -------------------------------------------------------------- Masse

    def bewegung(self):
        u"""Mittlerer und groesster Weg eines Punktes ueber die Bahn."""
        weg = np.linalg.norm(self.folge - self.folge[0], axis=2)
        return float(weg.mean()), float(weg.max())

    def spanne(self, auswahl=None):
        u"""Groesste Ausdehnung der Bahn, ueber alle oder eine Auswahl.

        Mit `auswahl` laesst sich ein Koerperteil pruefen: Der Aermel MUSS
        sich so weit bewegen wie der Arm darunter. Eine Gesamtzahl mittelt
        genau das weg — der stehende Rumpf ueberdeckt den bewegten Arm.
        """
        teil = self.folge if auswahl is None else self.folge[:, auswahl]
        mitte = teil.mean(axis=1)
        return float(np.linalg.norm(mitte.max(axis=0) - mitte.min(axis=0)))
