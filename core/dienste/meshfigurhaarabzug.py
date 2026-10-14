# -*- coding: utf-8 -*-
"""Meshfigurhaarabzug — was der Schritt „haar" als Haar ablegt, ist nicht Kleidung (14.10.2026).

Gemessen am Zauberer (Neulauf `…23.18.43`, Abnahme `doppelt`): 6.614 Flächen standen im Haar- UND im Kleidungsobjekt (graues Haar und Bart auf dem Kragen der Robe, im Band zwischen der Schnittebene des Kopfes und 4 cm unter dem Kinn),
also doppelt in der Bühne und beim Export; Edgar und die Ballerina 0. Beide Masken kamen aus verschiedenen Regeln (`Haarmaske`, `Kleidungsmaske`), keine kannte die andere. Hier gewinnt das Haar: `haar_maske.npz` (`haar`) ist die Entscheidung des
früheren Schritts. Der Hut (`kopfbedeckung`, Stück 4 „Zubehör") und der lange Bart (`Meshfigurkleidung._bart_abziehen`) sind eigene Felder und bleiben, wie sie sind.
"""

import os

import numpy as np

__all__ = ['Meshfigurhaarabzug']


class Meshfigurhaarabzug:
    #: Stück „Zubehör" (`Kleidungsmaske.ZUBEHOER`): der Hut bleibt im Kleidungsobjekt.
    ZUBEHOER = 4

    @classmethod
    def abziehen(cls, ablage, maske, regel):
        """Die Maske ohne die Flächen, die `haar_maske.npz` als Haar führt (`regel.abschliessen` rechnet `kleidung` und `haut` neu). Fehlt die Ablage, ist nichts Haar oder gehört nichts zur Kleidung: die Maske, wie sie ist."""
        pfad = ablage.arbeit('haar_maske.npz')
        if not os.path.isfile(pfad):
            return maske
        with np.load(pfad) as d:
            haar = d['haar'] if 'haar' in d.files else None
        stueck = np.asarray(maske['stueck'])
        if haar is None or len(haar) != len(stueck):
            return maske
        weg = haar & (stueck > 0) & (stueck != cls.ZUBEHOER)
        if not weg.any():
            return maske
        stueck = stueck.copy()
        stueck[weg] = 0
        return regel.abschliessen(stueck)
