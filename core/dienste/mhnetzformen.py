# -*- coding: utf-8 -*-
u"""Mhnetzformen — Netzarithmetik ohne Kenntnis von MakeHuman.

Vier Schritte, die zwischen Datei und Browser immer dieselben sind:
umschluesseln, Vierecke teilen, verdichten, Normalen. Sie standen in
`Mhbasisnetz`, hatten dort aber nichts mit dem BASISNETZ zu tun — und die
Datei war ueber 300 Zeilen. `Mhkleidnetz` braucht zwei davon ebenfalls.

DER UMLAUFSINN IST GEMESSEN: `[a,b,c] + [a,c,d]` ergibt fuer den geschlossenen
MakeHuman-Koerper ein Volumen von **+0,0549 m3** (ein Mensch von 1,67 m hat
rund 60-70 Liter), die umgekehrte Folge dasselbe negativ. Positiv heisst
Normalen nach aussen, und so zeichnet Three.js die Vorderseite. Der Fall
`test_umlaufsinn_zeigt_nach_aussen` haelt das fest; mit gedrehter Folge wird
er rot (gegengeprueft am 06.09.2026).
"""

import numpy as np

__all__ = ['Mhnetzformen']


class Mhnetzformen:
    u"""Reine Umformungen auf Punkten, Vierecken und Dreiecken."""

    @staticmethod
    def umschluesseln(vierecke):
        u"""`(benutzte Punktnummern, dieselben Vierecke mit lokalen Nummern)`.

        Nur die tatsaechlich benutzten Punkte gehen an den Browser: Die
        Gelenkwuerfel allein sind 750 Flaechen, aber der Puffer haette sonst
        immer alle 19.158 Punkte. Die lueckenlose Nummerierung ist ausserdem
        das, was `CatmullClarkSubdivider` erwartet.
        """
        if not len(vierecke):
            return (np.zeros((0,), dtype=np.int64),
                    np.zeros((0, 4), dtype=np.int64))
        return Mhnetzformen._neu_nummerieren(vierecke)

    @staticmethod
    def verdichten(punkte, dreiecke):
        u"""Punkte wegwerfen, auf die kein Dreieck mehr zeigt.

        Nach dem Ausblenden der verdeckten Haut (`Mhloeschmaske`) bleiben sonst
        tausende Punkte im Puffer, die nichts zeichnen — und die Zahl im Panel
        („13.380 Punkte") saegte am Vertrauen: Sie stimmte nicht mehr mit dem
        ueberein, was zu sehen ist.
        """
        if not len(dreiecke):
            return (np.zeros((0, 3), dtype=np.float32),
                    np.zeros((0, 3), dtype=np.uint32))
        nummern, neu = Mhnetzformen._neu_nummerieren(dreiecke)
        return punkte[nummern], neu.astype(np.uint32)

    @staticmethod
    def _neu_nummerieren(flaechen):
        nummern = np.unique(flaechen)
        umschluessel = np.zeros(int(nummern.max()) + 1, dtype=np.int64)
        umschluessel[nummern] = np.arange(len(nummern))
        return nummern, umschluessel[flaechen]

    @staticmethod
    def dreiecke(vierecke):
        u"""`[a,b,c,d]` -> `[a,b,c]` und `[a,c,d]` — siehe Kopf der Datei."""
        vierecke = np.asarray(vierecke)
        return np.concatenate([vierecke[:, [0, 1, 2]],
                               vierecke[:, [0, 2, 3]]],
                              axis=0).astype(np.uint32)

    @staticmethod
    def normalen(punkte, dreiecke):
        u"""Punktnormalen aus den Flaechen — gemittelt und normiert."""
        normalen = np.zeros((len(punkte), 3), dtype=np.float64)
        if not len(dreiecke):
            return normalen.astype(np.float32)
        ecke = [punkte[dreiecke[:, i]].astype(np.float64) for i in range(3)]
        flaeche = np.cross(ecke[1] - ecke[0], ecke[2] - ecke[0])
        for i in range(3):
            np.add.at(normalen, dreiecke[:, i], flaeche)
        laenge = np.linalg.norm(normalen, axis=1, keepdims=True)
        laenge[laenge < 1e-12] = 1.0
        return (normalen / laenge).astype(np.float32)
