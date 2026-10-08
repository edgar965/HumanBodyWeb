# -*- coding: utf-8 -*-
"""Blendimportaugen — die Originalaugen einer .blend als Augenbild der Genesis-Figur.

Edgar (08.10.2026): „Die Originalaugen auf Genesis übertragen, aber einstellbar / ersetzbar". Die Figur behält die
Genesis-Augäpfel; ihr Bild (`G9_Eyes01_D.jpg`) legt beide Augen in die obere Bildhälfte, Mitten (¼, ¼) und (¾, ¼), Iris
bis Radius 48/512, Limbus bis 56/512 (gemessen, `Meshfiguraugenbild`). Das Augenbild der .blend ist eine Frontalansicht:
Mitte = UV des vordersten Augenpunkts (Blick −Y in Blender), Irisrand = wo die mittlere Helligkeit je Ring über die
Hälfte zwischen Iris und Lederhaut steigt („cute girl": Mitte nahe der Bildmitte, Iris ~0,12 der Kante — am Bild
gesehen 08.10.2026). Je Ausgabepunkt im Kreis um eine Daz-Mitte wird radial so abgebildet, dass Irisrand auf Irisrand
fällt; außerhalb der Kreise bleibt das Daz-Bild.

Ersetzbar: Das Bild liegt als `fototextur.augen` beim Modell (`Genesis9fototextur.anhang`); wer andere Augen will,
nimmt den Eintrag heraus oder wählt beim Import „Genesis-Augen" — dann gilt das Daz-Bild in der Irisfarbe des Modells,
das „Mesh to 3D" schon geschrieben hat (`Meshfiguraugenbild`).
"""

import logging

import numpy as np

from .meshfiguraugenbild import Meshfiguraugenbild

logger = logging.getLogger('core')

__all__ = ['Blendimportaugen']


class Blendimportaugen:
    DATEI = 'augen_original.jpg'
    KANTE = 2048
    #: Daz-Kreis je Auge (Anteil der Kante): bis zur Mitte zwischen den Augen.
    KREIS = 0.25
    #: Bis hierher (Anteil der Kante des Originals) reicht die Lederhaut im Augenbild von „cute girl" (am Bild
    #: gesehen: weißer Fleck bis etwa 0,27, danach der rote Hintergrund) — Näherung, kein Messwert.
    LEDERHAUT = 0.26
    #: Anteil des Radius, über den zum Daz-Bild übergeblendet wird.
    UEBERBLENDUNG = 0.2
    IRIS_DAZ = Meshfiguraugenbild.IRIS[1]

    def __init__(self, ablage, inventar, rollen):
        self.ablage = ablage
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.augen = [r for r in rollen if r['rolle'] == 'auge']

    def mitte_uv(self):
        """UV des vordersten Punkts (kleinstes y in Blender) des ersten Auges."""
        netz = self.inventar[self.augen[0]['name']]
        with np.load(self.ablage.export(netz['datei'])) as d:
            punkte, dreiecke, uv = d['punkte'], d['dreiecke'], d['uv_ecken']
        vorn = int(np.argmin(punkte[:, 1]))
        treffer = dreiecke.reshape(-1) == vorn
        return uv.reshape(-1, 2)[treffer].mean(axis=0)

    @staticmethod
    def irisradius(bild, mitte_px):
        """Irisrand in Anteilen der Kante aus der Helligkeit je Ring (Ringe von 0,5 % der Kante)."""
        hell = bild.astype(np.float64).mean(axis=2)
        yy, xx = np.mgrid[:hell.shape[0], :hell.shape[1]]
        r = np.hypot(xx - mitte_px[0], yy - mitte_px[1]) / hell.shape[1]
        ringe = np.arange(0.0, 0.3, 0.005)
        mittel = np.array([hell[(r >= a) & (r < a + 0.005)].mean() for a in ringe])
        lederhaut = float(mittel.max())
        iris = float(np.median(mittel[(ringe > 0.02) & (ringe < ringe[int(np.argmax(mittel))])][:8]))
        schwelle = 0.5 * (iris + lederhaut)
        ab = int(np.argmax(ringe > 0.02))
        ueber = np.flatnonzero(mittel[ab:] > schwelle)
        return float(ringe[ab + ueber[0]]) if len(ueber) else 0.12

    def schreiben(self):
        """`{datei, mitte_uv, iris}` oder None ohne Augen in der .blend."""
        from PIL import Image

        if not self.augen:
            return None
        quelle = ((self.inventar[self.augen[0]['name']].get('materialien') or [{}])[0] or {}).get('farbe')
        vorlage = Meshfiguraugenbild.vorlage()
        if not quelle or vorlage is None:
            logger.warning('Blender-Import %s: Augenbild nicht übertragen (Bild %s, Vorlage %s)',
                           self.ablage.kennung, quelle, vorlage)
            return None
        with Image.open(quelle) as b:
            her = np.asarray(b.convert('RGB'), dtype=np.uint8)
        mitte = self.mitte_uv()
        mitte_px = (mitte[0] * her.shape[1], (1.0 - mitte[1]) * her.shape[0])
        iris = self.irisradius(her, mitte_px)
        with Image.open(vorlage) as b:
            aus = np.asarray(b.convert('RGB').resize((self.KANTE, self.KANTE), Image.LANCZOS)).copy()
        yy, xx = np.mgrid[:self.KANTE, :self.KANTE].astype(np.float64) + 0.5
        faktor = iris / self.IRIS_DAZ
        # Nur so weit, wie das Original Lederhaut hat (`LEDERHAUT`, Anteil der Kante); dahinter ist sein Hintergrund
        # (bei „cute girl" dunkelrot, gesehen 08.10.2026) — dort bleibt das Daz-Bild, weich überblendet.
        grenze = min(self.KREIS, self.LEDERHAUT / faktor)
        for mx, my in Meshfiguraugenbild.MITTEN:
            dx, dy = xx / self.KANTE - mx, yy / self.KANTE - my
            r = np.hypot(dx, dy)
            innen = r < grenze
            sx = np.clip(mitte_px[0] + dx[innen] * faktor * her.shape[1], 0, her.shape[1] - 1).astype(np.int64)
            sy = np.clip(mitte_px[1] + dy[innen] * faktor * her.shape[0], 0, her.shape[0] - 1).astype(np.int64)
            w = np.clip((grenze - r[innen]) / (self.UEBERBLENDUNG * grenze), 0.0, 1.0)[:, None]
            aus[innen] = np.round(w * her[sy, sx] + (1.0 - w) * aus[innen]).astype(np.uint8)
        Image.fromarray(aus).save(self.ablage.ergebnis(self.DATEI), quality=92)
        return {'datei': self.DATEI, 'mitte_uv': [round(float(v), 4) for v in mitte], 'iris': round(iris, 4)}
