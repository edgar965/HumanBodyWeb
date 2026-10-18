# -*- coding: utf-8 -*-
u"""Mhkopfausrichtung — MakeHumans Kopf im Klon auf Genesis' Kopf legen (17.10.2026).

Eine Affinabbildung `p' = A·p + t`, aus den Ankern (`Mhkopfanker`: Nase, Kinn, Scheitel, Hinterkopf, Ohren) und den Augengelenken beider Rigs gerechnet, mit
leichter Bindung an die Einheit (Ridge), damit wenige Anker keine Scherung erzwingen. Sie gilt voll von der Kinnhoehe aufwaerts und laeuft zum Hals hin weich
auf null (Smoothstep zwischen dem Halsgelenk `neck01` und dem Kinn) — der Hals bleibt, wo der Rumpf ihn hinlegt.

DIE VERSCHIEBUNGEN gehen mit: ein Morph-Delta am Kopf wird mit dem LINEAREN Teil `A` gedreht und gestreckt (`linear`), gewichtet wie die Punkte. Sonst bliebe die
Lage richtig und die Richtung/Groesse falsch (Kopf Genesis 14 % hoeher als MakeHumans bei gleicher Koerpergroesse).
"""
import numpy as np

from .mhkopfanker import Mhkopfanker

__all__ = ['Mhkopfausrichtung']


class Mhkopfausrichtung:
    u"""Affinabbildung des Kopfes samt Hoehengewicht."""

    #: Bindung an die Einheit, als Anteil der mittleren Streuung der Anker.
    RIDGE = 0.05

    def __init__(self, matrix, versatz, y_null, y_voll, anker=None):
        self.matrix = np.asarray(matrix, dtype=np.float64)
        self.versatz = np.asarray(versatz, dtype=np.float64)
        self.y_null = float(y_null)
        self.y_voll = float(y_voll)
        self.anker = anker or {}

    # ------------------------------------------------------------ Berechnen

    @classmethod
    def berechnen(cls, quelle, ziel, quelle_augen, ziel_augen, y_null):
        u"""`quelle`/`ziel`: Netzpunkte des Kopfes (Meter), `*_augen`: `[links, rechts]` Augengelenke, `y_null`: Hoehe, ab der die Wirkung beginnt."""
        q, z = Mhkopfanker.finden(quelle), Mhkopfanker.finden(ziel)
        s = [q[n] for n in Mhkopfanker.NAMEN] + [np.asarray(a, dtype=np.float64) for a in quelle_augen]
        t = [z[n] for n in Mhkopfanker.NAMEN] + [np.asarray(a, dtype=np.float64) for a in ziel_augen]
        s, t = np.array(s), np.array(t)
        cs, ct = s.mean(axis=0), t.mean(axis=0)
        x, y = s - cs, t - ct
        lam = cls.RIDGE * float((x ** 2).sum()) / 3.0
        matrix = (y.T @ x + lam * np.eye(3)) @ np.linalg.inv(x.T @ x + lam * np.eye(3))
        versatz = ct - matrix @ cs
        return cls(matrix, versatz, y_null, q['kinn'][1], {n: (q[n], z[n]) for n in Mhkopfanker.NAMEN})

    # --------------------------------------------------------------- Anwenden

    def gewicht(self, y):
        u"""0 am Hals (`y_null`) … 1 ab Kinnhoehe, glatt dazwischen."""
        x = np.clip((np.asarray(y, dtype=np.float64) - self.y_null) / max(self.y_voll - self.y_null, 1e-6), 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    def anwenden(self, punkte):
        p = np.asarray(punkte, dtype=np.float64)
        neu = p @ self.matrix.T + self.versatz
        return p + self.gewicht(p[:, 1])[:, None] * (neu - p)

    def linear(self, delta, y):
        u"""Verschiebungen mit dem linearen Teil mitnehmen; `y` ist die Hoehe der Punkte VOR der Ausrichtung."""
        d = np.asarray(delta, dtype=np.float64)
        return d + self.gewicht(y)[:, None] * (d @ (self.matrix - np.eye(3)).T)

    def rest_mm(self):
        u"""Abstand der Anker nach der Abbildung zu ihren Zielen, mm (Mass fuer die Guete der Anpassung)."""
        return {n: round(float(np.linalg.norm(self.matrix @ q + self.versatz - z)) * 1000, 1) for n, (q, z) in self.anker.items()}
