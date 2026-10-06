# -*- coding: utf-8 -*-
"""Haarwuchs — Richtung, Länge und Locken des Kurzhaars eines Herrenschnitts als Felder über dem Kopf (05.10.2026).

Zu `Herrenhaar` (Edgar, 05.10.2026: „Vielleicht machst du dir ein Haarmodell als eigenes Modell … ein Haar für einen normalen mittelalten Mann mit normalem Haarschnitt"). Die Richtung, in die ein Haar wächst und liegt,
hängt nur davon ab, WO am Kopf es steht — nicht von einem Netz einer Frisur. Das Feld hier ist das einfachste, das wie ein Herrenschnitt aussieht:

  * die Haare wachsen vom Haarwirbel am Hinterkopf (`WIRBEL`) strahlenförmig nach außen,
  * je tiefer am Kopf, desto mehr zieht die Schwerkraft sie nach unten (`SCHWERKRAFT`: ab dem oberen Höhenwinkel anteilig, ab dem unteren ganz),
  * auf der Stirnseite oben sind sie nach hinten gekämmt (`NACH_HINTEN`), wie bei einem kurzen Schnitt, der ohne Scheitel zurückgenommen wird,
  * jedes Haar weicht um einen kleinen Winkel ab (`ABWEICHUNG`), und ein glattes Rauschfeld (`Haarwuchs.rauschen`, Wellenlänge `WELLE_M`) lässt benachbarte Haare dieselbe Richtung und Länge nehmen — Strähnen statt einer
    gleichmäßigen Bürste.

Alles sind Annahmen über „normales" Haar, nicht Messungen an diesem Auftrag. Die Größen (Dicke, Haarlinie, Farbe) kommen aus den Fotos (`Haarkappe`, `Herrenhaar`); hier steht nur die Form des Wuchses. Reine NumPy-Funktionen, kein Django.
"""

import numpy as np

__all__ = ['Haarwuchs']


class Haarwuchs:
    #: Haarwirbel (Azimut von vorn, Höhenwinkel) — am Hinterkopf oben, Annahme.
    WIRBEL = (172.0, 74.0)
    #: Höhenwinkel, unter dem die Schwerkraft anteilig (obere Zahl) bzw. ganz (untere) die Richtung bestimmt.
    SCHWERKRAFT = (62.0, 18.0)
    #: Stirnseite oben: so viel Anteil der Richtung zeigt nach hinten (zum Wirbel).
    NACH_HINTEN = 0.95
    #: Streuung der Richtung je Haar (Grad) und Stärke der gemeinsamen Drehung benachbarter Haare (Grad).
    ABWEICHUNG = 5.0
    DREHUNG = 12.0
    #: Wellenlänge des Rauschfelds (m) — so groß sind Strähnen.
    WELLE_M = 0.018
    KANAELE = 14

    @staticmethod
    def einheit(az, el):
        """Einheitsvektor (…, 3) aus Azimut (von +z nach +x) und Höhenwinkel, beide in Grad."""
        a, e = np.radians(az), np.radians(el)
        return np.stack([np.cos(e) * np.sin(a), np.sin(e), np.cos(e) * np.cos(a)], axis=-1)

    @staticmethod
    def _norm(v):
        return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)

    @staticmethod
    def _weich(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    @classmethod
    def _zu(cls, u, ziel):
        """Tangente an `u` (Kugel um den Kopfmittelpunkt) in Richtung des Punkts `ziel` (3,) — am Punkt selbst und gegenüber die Nullrichtung."""
        return cls._norm(ziel[None, :] - (u @ ziel)[:, None] * u)

    @classmethod
    def rauschen(cls, u, samen, kanaele=None):
        """Glattes Rauschen in [−1, 1] je Richtung `u` (N, 3): Summe von Kosinuswellen der Wellenlänge `WELLE_M` bei einem Kopfradius von rund 0,1 m — gleiche Richtung, gleicher Wert, benachbarte Punkte ähnlich."""
        zufall = np.random.default_rng(int(samen))
        n = int(kanaele or cls.KANAELE)
        richtung = cls._norm(zufall.standard_normal((n, 3)))
        frequenz = (2.0 * np.pi / cls.WELLE_M) * 0.1 * (0.6 + 0.8 * zufall.random(n))          # Radius der Einheitskugel 0,1 m
        phase = 2.0 * np.pi * zufall.random(n)
        return np.clip((np.cos((u @ richtung.T) * frequenz + phase)).sum(axis=1) * np.sqrt(2.0 / n) / 1.4, -1.0, 1.0)

    @classmethod
    def laufrichtung(cls, u, samen=0):
        """Wuchsrichtung (N, 3, Einheit, tangential an der Kugel) je Wurzelrichtung `u` (N, 3, Einheit) vom Kopfmittelpunkt."""
        wirbel = cls.einheit(*cls.WIRBEL)
        el = np.degrees(np.arcsin(np.clip(u[:, 1], -1.0, 1.0)))
        weg = -cls._zu(u, wirbel)                                    # vom Wirbel fort
        zum = cls._zu(u, wirbel)                                     # zum Wirbel hin (nach hinten gekämmt)
        runter = cls._norm(np.array([0.0, -1.0, 0.0]) + u[:, 1:2] * u)       # g − (g·u)·u mit g = (0, −1, 0)
        runter[np.linalg.norm(runter, axis=1) < 0.5] = (0.0, 0.0, -1.0)    # am Scheitelpol gibt es kein „unten": nach hinten
        schwer = cls._weich((cls.SCHWERKRAFT[0] - el) / (cls.SCHWERKRAFT[0] - cls.SCHWERKRAFT[1]))[:, None]
        vorn = (cls._weich((u[:, 2] - 0.15) / 0.5) * cls._weich((el - 28.0) / 25.0) * cls.NACH_HINTEN)[:, None]
        t = cls._norm((1.0 - vorn) * ((1.0 - schwer) * weg + schwer * runter) + vorn * zum)
        leer = np.linalg.norm(t, axis=1) < 0.5                       # am Wirbel (und an den Polen) gibt es keine Richtung „vom Wirbel fort": dort nach unten
        t[leer] = runter[leer]
        winkel = np.radians(cls.DREHUNG * cls.rauschen(u, samen + 11) + cls.ABWEICHUNG * np.random.default_rng(samen + 12).standard_normal(len(u)))[:, None]
        drehen = np.cross(u, t)
        return cls._norm(t * np.cos(winkel) + drehen * np.sin(winkel))
