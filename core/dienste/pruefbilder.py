# -*- coding: utf-8 -*-
"""Pruefbilder — die Bilder, an denen Fable jede Runde von „2D3D Kleider" prüft (02.10.2026).

Edgars Vorgabe: „jede iteration wird von dir begutachtet, und dann neuer Code erzeugt" — „Vorgabe ist, du überprüfst
und optimierst den Code". Die Vergleichstafel der Note (`Iterationstafel` auf 128 × 192 je Blickwinkel) reicht dafür
nicht: Unterlippe, Säume, ein ausgefranster Ausschnitt sind darauf ein bis drei Pixel groß (Tafel von Runde 11:
384 × 404 für drei Ansichten). Deshalb zwei eigene Bilder je Runde, unabhängig von der Note:

    runde_NNN_vergleich.png   wie bisher oben Foto, unten Render, aber `breite` × 1,5·`breite` je Ansicht (Option
                              `iterationen.tafelbreite`, Vorgabe 384) — die Renders der Runde entstehen dafür in
                              dieser Breite, die Note rechnet sie weiter auf 128 × 192 herunter.
    runde_NNN_kopf.png        je Blickwinkel der Kopf: oben aus dem Foto, unten `Genesishaarrender.bild_kopf` MIT
                              Texturen (Haut, Haar, Kragen) — derselbe Ausschnitt: 0,34 m im Quadrat, Mitte 0,13 m
                              unter dem Scheitel. Das Foto wird über die Modellhöhe in Meter umgerechnet (Figur im
                              Foto vom Scheitel bis zu den Füßen = `modell_hoehe`).

Ein Fehler hier hält die Runde nicht auf (Log); die Note hängt nicht an diesen Bildern.
"""

import logging

import numpy as np
from PIL import Image, ImageDraw

from .iterationsbild import Iterationsbild
from .iterationsreferenz import Iterationsreferenz
from .iterationstafel import Iterationstafel

logger = logging.getLogger('core')

__all__ = ['Pruefbilder']


class Pruefbilder:
    KOPF = 'kopf_%+04d.png'
    KOPF_GROESSE = 384
    HINTERGRUND = (255, 255, 255)
    SCHRIFT = 14

    def __init__(self, ablage, breite):
        self.ablage = ablage
        self.breite = int(breite)

    @property
    def groesse(self):
        return self.breite, int(self.breite * 1.5)

    # ------------------------------------------------------------------ Tafel

    def tafel(self, ansichten, ziel):
        """`ansichten`: [(winkel, datei der Vorlage, Pfad des Renders, iou)] → `ziel` (PNG) oder None."""
        paare = []
        for winkel, datei, render, iou in ansichten:
            if not render.is_file():
                continue
            vorlage = Iterationsreferenz.bild(self.ablage, datei, self.groesse)
            paare.append((winkel, vorlage, Iterationsbild.aus_render(render, self.groesse), {'iou': iou}))
        return Iterationstafel.bauen(paare, ziel) if paare else None

    # ------------------------------------------------------------------- Kopf

    def kopf(self, render, teile, referenzen, modell_hoehe, aus, ziel):
        """Die Kopftafel: je Referenz Foto- und Render-Kopf. `render` ist der offene `Genesishaarrender` der Runde,
        `teile` die gehäuteten Teile (Haltung der Fotos). → `ziel` oder None."""
        from .genesishaarrender import Genesishaarrender
        k = self.KOPF_GROESSE
        paare = []
        for r in referenzen:
            try:
                foto = self._fotokopf(r.datei, float(modell_hoehe), render)
                pfad = aus / (self.KOPF % int(round(r.winkel)))
                render.bild_kopf([(t['punkte'], t['dreiecke'], t['farbe'], Genesishaarrender.extra(t)) for t in teile],
                                 r.winkel, pfad, groesse=(k, k))
                with Image.open(pfad) as bild:
                    paare.append((r.winkel, foto, bild.convert('RGB').copy()))
            except (OSError, ValueError, RuntimeError) as fehler:
                logger.warning('Prüfbilder: Kopf %+d° nicht gebaut (%s)', round(r.winkel), fehler)
        if not paare:
            return None
        tafel = Image.new('RGB', (k * len(paare), 2 * k + self.SCHRIFT + 6), self.HINTERGRUND)
        zeichnen = ImageDraw.Draw(tafel)
        for i, (winkel, foto, kopf) in enumerate(paare):
            tafel.paste(foto, (i * k, 0))
            tafel.paste(kopf, (i * k, k))
            zeichnen.line([(i * k, 0), (i * k, 2 * k)], fill=Iterationstafel.TRENNER)
            zeichnen.text((i * k + 4, 2 * k + 3), '%+d°  Kopf' % round(winkel), fill=(40, 40, 40))
        zeichnen.line([(0, k), (tafel.width, k)], fill=Iterationstafel.TRENNER)
        tafel.save(ziel)
        return ziel

    def _fotokopf(self, datei, modell_hoehe, render):
        return Image.fromarray(self.kopfausschnitt(datei, modell_hoehe, render, self.KOPF_GROESSE)[0])

    def kopfausschnitt(self, datei, modell_hoehe, render, k):
        """(rgb uint8 auf Weiß, maske bool) des Fotokopfs im Ausschnitt von `bild_kopf`, `k` Pixel im Quadrat — Pixel je
        Meter aus der Figurhöhe im Foto, waagerecht auf die Mitte des Kopfes gestellt."""
        rgb, maske = self._foto(datei)
        abbildung = Iterationsbild.abbildung(maske)
        if abbildung is None or modell_hoehe <= 0:
            raise ValueError('keine Figur im Foto %s' % datei)
        _cx, y0, y1 = abbildung
        je_m = (y1 - y0) / modell_hoehe
        halb = 0.5 * render.KOPF_HOEHE * je_m
        mitte_y = y0 + render.KOPF_UNTER_SCHEITEL * je_m
        oben = maske[y0:int(y0 + 2 * render.KOPF_UNTER_SCHEITEL * je_m)]
        spalten = np.flatnonzero(oben.sum(axis=0) > 0)
        if not len(spalten):
            raise ValueError('kein Kopf im Foto %s' % datei)
        mitte_x = float(np.average(spalten, weights=oben.sum(axis=0)[spalten]))
        grund = np.full_like(rgb, 255)
        frei = np.where(maske[..., None], rgb, grund).astype(np.uint8)
        kasten = (mitte_x - halb, mitte_y - halb, mitte_x + halb, mitte_y + halb)
        bild = Image.fromarray(frei).transform((k, k), Image.EXTENT, kasten, resample=Image.BICUBIC,
                                               fillcolor=self.HINTERGRUND)
        figur = Image.fromarray(maske.astype(np.uint8) * 255).transform((k, k), Image.EXTENT, kasten,
                                                                        resample=Image.BILINEAR, fillcolor=0)
        return np.asarray(bild.convert('RGB')), np.asarray(figur) > 127

    def _foto(self, datei):
        """(rgb uint8, maske bool) in voller Auflösung — freigestellt aus „netz", sonst das Foto auf Weiß."""
        from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        vorbereitet = self.ablage.unter(Engine2d3dKleiderablage.VORBEREITET) / (datei.rsplit('.', 1)[0] + '.png')
        if vorbereitet.is_file():
            with Image.open(vorbereitet) as bild:
                rgba = np.asarray(bild.convert('RGBA'))
            return rgba[..., :3], rgba[..., 3] > 127
        with Image.open(self.ablage.unter(Engine2d3dKleiderablage.EINGANG) / datei) as bild:
            rgb = np.asarray(bild.convert('RGB'))
        return rgb, (765 - rgb.astype(np.int32).sum(axis=2)) > Iterationsbild.WEISS_SCHWELLE
