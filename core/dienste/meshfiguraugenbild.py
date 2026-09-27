# -*- coding: utf-8 -*-
"""Meshfiguraugenbild — das Daz-Augenbild mit der Irisfarbe des Netzes.

Edgar, 27.09.2026: „mach das mit der Iris". Die Figur trägt die Daz-Augäpfel; ihr Bild
(`G9_Eyes01_D.jpg`, 4096², Iris grau-braun, Median (108, 85, 66)) wirkte neben dem bernsteinfarbenen
gemalten Auge des Kopfnetzes blass. `Meshfiguriris` (Runner, Schritt „textur") misst die Irisfarbe des
Netzes; hier wird die Iris des Daz-Bilds darauf gefärbt und als `meshfigur_augen.jpg` neben die Kacheln
gelegt (`ergebnis.fototextur.augen`). Die Figur setzt es als Albedo der Augäpfel (`Genesis9fototextur`).

LAGE (gemessen am Bild, Maß auf 512 px): beide Augen im oberen Viertel, Mitten (128, 128) und
(384, 128); Pupille bis Radius 20 (Median (3, 3, 4)), Iris 20–52, Limbus 48–56, dann Lederhaut
(Median ~(175, 169, 163)). Gefärbt wird je Kanal LINEAR mit dem Faktor Ziel / Median der Iris
(24–48) — die Zeichnung der Iris bleibt, nur ihr Ton wandert; an Pupille und Limbus weich
ausgeblendet, damit kein Ring entsteht. Die Lederhaut bleibt, wie Daz sie malt.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfiguraugenbild']


class Meshfiguraugenbild:
    DATEI = 'meshfigur_augen.jpg'
    VORLAGE = '01'
    #: Ausgabe (Kante in px): 2048 reicht für den Augapfel und hält die Datei klein.
    KANTE = 2048
    #: Anteile der Bildkante (aus den px-Maßen auf 512).
    MITTEN = ((0.25, 0.25), (0.75, 0.25))
    PUPILLE = (20 / 512, 24 / 512)
    IRIS = (24 / 512, 48 / 512)
    LIMBUS = (48 / 512, 56 / 512)
    GRENZEN = (0.2, 5.0)

    # --------------------------------------------------------------- Farbe

    @staticmethod
    def linear(srgb):
        c = np.asarray(srgb, dtype=np.float64) / 255.0
        return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def srgb(linear):
        c = np.clip(linear, 0.0, 1.0)
        return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255.0

    @classmethod
    def gewicht(cls, kante):
        """(kante, kante) 0..1 — 1 in der Iris, weich zu Pupille und Limbus, 0 sonst."""
        yy, xx = np.mgrid[:kante, :kante].astype(np.float64) + 0.5
        aus = np.zeros((kante, kante))
        for mx, my in cls.MITTEN:
            r = np.hypot(xx - mx * kante, yy - my * kante) / kante
            ein = np.clip((r - cls.PUPILLE[0]) / (cls.PUPILLE[1] - cls.PUPILLE[0]), 0, 1)
            aus_ = np.clip((cls.LIMBUS[1] - r) / (cls.LIMBUS[1] - cls.LIMBUS[0]), 0, 1)
            aus = np.maximum(aus, ein * aus_)
        return aus

    @classmethod
    def irismaske(cls, kante):
        yy, xx = np.mgrid[:kante, :kante].astype(np.float64) + 0.5
        aus = np.zeros((kante, kante), dtype=bool)
        for mx, my in cls.MITTEN:
            r = np.hypot(xx - mx * kante, yy - my * kante) / kante
            aus |= (r >= cls.IRIS[0]) & (r < cls.IRIS[1])
        return aus

    @classmethod
    def faerben_bild(cls, bild, ziel):
        """(H, W, 3) uint8 → gefärbt; `ziel` sRGB. Gibt (Bild, Faktoren je Kanal)."""
        bild = np.asarray(bild, dtype=np.uint8)
        kante = bild.shape[0]
        lin = cls.linear(bild)
        quelle = np.median(lin[cls.irismaske(kante)], axis=0)
        faktor = np.clip(cls.linear(ziel) / np.maximum(quelle, 1e-6), *cls.GRENZEN)
        w = cls.gewicht(kante)[..., None]
        aus = cls.srgb(lin * (1.0 + w * (faktor - 1.0)))
        return np.round(aus).astype(np.uint8), faktor

    # ---------------------------------------------------------------- Datei

    @classmethod
    def vorlage(cls):
        """Pfad des Daz-Augenbilds (`G9_Eyes01_D.jpg`) — oder None."""
        from Genesis9.hautpresets import G9hautpresets
        from Genesis9.material import G9material

        albedo = (G9hautpresets.augenbilder(cls.VORLAGE).get('Eye Left') or {}).get('albedo')
        pfad = G9material.datei(albedo) if albedo else None
        return pfad if pfad and pfad.is_file() else None

    @classmethod
    def schreiben(cls, ordner, ziel):
        """Das gefärbte Bild nach `ordner/DATEI`; gibt `{datei, ziel, faktor}` oder None."""
        from PIL import Image

        quelle = cls.vorlage()
        if quelle is None or not ziel:
            logger.warning('Mesh to 3D: Augenbild nicht gefärbt (Vorlage %s, Ziel %s)', quelle, ziel)
            return None
        bild = Image.open(quelle).convert('RGB').resize((cls.KANTE, cls.KANTE), Image.LANCZOS)
        gefaerbt, faktor = cls.faerben_bild(np.asarray(bild), ziel)
        Image.fromarray(gefaerbt).save(ordner / cls.DATEI, quality=92)
        return {
            'datei': cls.DATEI,
            'ziel': [int(v) for v in ziel],
            'faktor': [round(float(v), 3) for v in faktor],
        }
