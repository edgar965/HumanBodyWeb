# -*- coding: utf-8 -*-
u"""Der Weichgewebe-Zuschlag fuer Koerper und Kleider eines Films.

Aus `hbfilm.py` abgeteilt (11.09.2026, Dateigrenze). Koerper und Stoff
bekommen den Zuschlag getrennt, aber aus DERSELBEN Skelettbahn — sonst
liefe die Sekundaerbewegung auseinander, genau wie es die Grundbewegung
in den ersten Videos tat.

`ziel_mm` sind MILLIMETER, keine Kennzahl: Wieweit soll das weichste
Gewebe hoechstens nachgeben? Die Staerke dazu wird je Teil gemessen
(`Kalibrierung`). Ein fester Wert waere unbrauchbar — gemessen ergibt
`staerke = 1,0` an dieser Figur 700 mm Zuschlag.
"""
import os
import sys

import numpy as np

from feinkoerper import Feinkoerper

sys.path.insert(0, os.path.join('A:', os.sep, '3DTools',
                                'VelocitySkinning_Python'))


class Filmphysik:
    u"""Velocity Skinning als Zuschlag auf fertige LBS-Bahnen."""

    def __init__(self, teile, bahn, bildzeit, ziel_mm, melder=None):
        self.teile = teile
        self.bahn = bahn
        self.bildzeit = bildzeit
        self.physik = float(ziel_mm)
        self.melder = melder or (lambda phase, anteil: None)

    def anwenden(self):
        u"""Velocity Skinning als ZUSCHLAG auf die fertige LBS-Bahn.

        Koerper und Stoff bekommen ihn getrennt, aber aus DERSELBEN
        Skelettbahn — sonst liefe die Sekundaerbewegung auseinander,
        genau wie es die Grundbewegung frueher tat.

        `self.physik` sind MILLIMETER, nicht eine Kennzahl: Wieweit soll
        das weichste Gewebe hoechstens nachgeben? Die Staerke dazu wird je
        Teil gemessen (`Kalibrierung`). Ein fester Wert waere hier
        unbrauchbar — gemessen ergibt `staerke = 1,0` an dieser Figur
        700 mm Zuschlag, und der Stoff braucht ohnehin einen anderen Wert
        als die Haut.
        """
        from kalibrierung import Kalibrierung
        from skinning import Velocityskinning
        koerper = self.teile[0]
        # Der Koerper zuerst — die Stuecke werden gegen SEINE bereits
        # verformte Lage begrenzt, nicht gegen die rohe LBS-Lage.
        for teil in self.teile:
            haut = teil['haut']
            motor = Velocityskinning(
                haut.punkte, teil['dreiecke'], haut.gewichte, haut.namen,
                self.bahn, self.bildzeit, staerke=1.0)
            ziel = self.physik * teil.get('weichfaktor', 1.0)
            motor.staerke, _erreicht = Kalibrierung(
                motor, haut.folge).fuer(ziel)
            if teil is koerper:
                haut.folge = motor.bahn_mit_physik(haut.folge)
                teil['physik'] = motor.bilanz()
            else:
                teil['physik'] = self._stoff_mit_grenze(teil, motor, koerper)
            teil['physik']['staerke'] = motor.staerke
            teil['physik']['ziel_mm'] = ziel

    def _grenze(self, koerper, nummer):
        u"""Die Grenze eines Bildes — EINMAL je Bild fuer alle Stuecke
        (Baum und Normalen ueber 70.851 Punkte kosten je 0,2 s)."""
        from stoffgrenze import Stoffgrenze
        if not hasattr(self, '_grenzen'):
            self._grenzen = {}
        if nummer not in self._grenzen:
            # Gegen das SICHTBARE Netz — an das ist der Stoff angelegt.
            self._grenzen[nummer] = Stoffgrenze(Feinkoerper.bild(koerper, nummer),
                                                Feinkoerper.dreiecke(koerper))
        return self._grenzen[nummer]

    def _stoff_mit_grenze(self, teil, motor, koerper):
        u"""Zuschlag fuer ein Kleidungsstueck, aus dem Koerper gehalten.

        Ohne Grenze schiebt ein 28-mm-Zuschlag ein T-Shirt mit 13 mm
        Hautabstand glatt durch den Koerper (gemessen 11.09.2026, im Bild
        klaffende Loecher). Die Grenze ist keine Simulation, sondern eine
        Kuerzung je Punkt — nach aussen bleibt der Zuschlag ungekuerzt.
        """
        from stoffgrenze import Stoffgrenze
        haut = teil['haut']
        folge = np.array(haut.folge)
        gekuerzt_gesamt, vorher, nachher = 0, [], []
        motor.zuschlag = np.zeros(len(folge))
        # Der Sollabstand je Punkt aus der RUHELAGE: Eine Leggings auf 2 mm
        # bleibt auf 2 mm, auch wenn der Koerper darunter nach aussen geht.
        soll = Stoffgrenze(Feinkoerper.ruhe(koerper),
                           Feinkoerper.dreiecke(koerper)).sollabstand(haut.punkte)
        for nummer in range(len(folge)):
            grenze = self._grenze(koerper, nummer)
            versatz = motor.verschiebung(nummer, folge[nummer])
            vorher.append(grenze.durchdringung(folge[nummer] + versatz)[0])
            versatz, zahl = grenze.kuerzen(folge[nummer], versatz, soll)
            gekuerzt_gesamt += zahl
            folge[nummer] = folge[nummer] + versatz
            nachher.append(grenze.durchdringung(folge[nummer])[0])
            motor.zuschlag[nummer] = float(
                np.linalg.norm(versatz, axis=1).max())
        haut.folge = folge
        bilanz = motor.bilanz()
        bilanz['gekuerzt'] = gekuerzt_gesamt
        bilanz['durchstich_ohne_grenze'] = float(np.mean(vorher))
        bilanz['durchstich'] = float(np.mean(nachher))
        return bilanz
