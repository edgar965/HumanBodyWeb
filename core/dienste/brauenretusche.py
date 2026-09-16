# -*- coding: utf-8 -*-
u"""Brauenretusche — die gemalten Augenbrauen aus einer MB-Lab-Hauttextur nehmen.

Edgar, 16.09.2026: „doppelte Augenbrauen". Die MB-Lab-Albedos
(`hum_f_cauc_albedo.png` …) tragen die Brauen aufgemalt; die Figur bekommt
ihre Brauen aber als Netz (`gemeinsam/augenbrauenbau.js`, mit Reglern für
Farbe, Dichte, Dicke, Lage). Mit Textur standen beide übereinander — der
gemalte Bogen dicht über dem Auge, der gebaute 16 mm über der Augenmitte.

Die Retusche kennt keine Brauenmaske (MB-Lab liefert keine). Sie findet die
Brauen selbst: ZONE = die UV-Pixel der Hautpunkte, die die MB-Lab-Einheiten
`browOutVertL/R` und `browsMidVert` bewegen, um `RAND_PX` ausgedehnt; darin
ist BRAUE, was deutlich dunkler als die Haut der Zone ist (Luminanz unter
`DUNKEL` × Median). Die Maske wird um `AUSDEHNUNG_PX` ausgedehnt und mit der
Umgebung gefüllt (Front vom Rand nach innen, dann geglättet).

Das Ergebnis liegt als `<name>_ohne_brauen.png` unter `media/hauttexturen/`
(Projekt, nicht System-Temp) und wird neu gerechnet, wenn die Quelle jünger
ist oder `FASSUNG` steigt.
"""
import logging
from pathlib import Path

import numpy as np
from django.conf import settings

logger = logging.getLogger('core')


class Brauenretusche:

    FASSUNG = 1
    EINHEITEN = ('browOutVertL', 'browOutVertR', 'browsMidVert')
    #: m — was eine Einheit stärker bewegt, ist Brauenhaut.
    MINDEST = 0.002
    #: Pixel (bei 2048²) um die Brauenpunkte, in denen nach Dunklem gesucht wird.
    RAND_PX = 24
    #: Pixel um die Brauenpunkte, die ein dunkler Fleck berühren muss, um Braue zu sein.
    KERN_PX = 8
    #: Luminanz unter diesem Anteil des Zonen-Medians gilt als gemalte Braue …
    DUNKEL = 0.80
    #: … und was zusammenhängend mit ihr so dunkel ist, als ihr hellerer Rand.
    RAND_DUNKEL = 0.93
    AUSDEHNUNG_PX = 2
    GLAETTUNG = 6
    ORDNER = Path(settings.MEDIA_ROOT) / 'hauttexturen'

    # --------------------------------------------------------------- Zutaten

    @classmethod
    def brauenpunkte(cls, einheiten):
        u"""Indizes der Hautpunkte, die eine der Brauen-Einheiten bewegt."""
        punkte = set()
        for name in cls.EINHEITEN:
            for richtung in ('plus', 'minus'):
                deltas = np.array(einheiten.get(name, {}).get(richtung, []),
                                  dtype=np.float64)
                if not len(deltas):
                    continue
                stark = np.linalg.norm(deltas[:, 1:], axis=1) > cls.MINDEST
                punkte.update(deltas[stark, 0].astype(int).tolist())
        return np.array(sorted(punkte), dtype=int)

    @classmethod
    def kern(cls, uvs, form, radius):
        u"""Bool-Bild (H, W): Umkreis `radius` um die UV-Pixel der Punkte."""
        from scipy import ndimage
        hoehe, breite = form
        bild = np.zeros((hoehe, breite), dtype=bool)
        u = np.clip(np.rint(uvs[:, 0] * (breite - 1)).astype(int), 0, breite - 1)
        w = np.clip(np.rint((1 - uvs[:, 1]) * (hoehe - 1)).astype(int), 0, hoehe - 1)
        bild[w, u] = True
        y, x = np.ogrid[-radius:radius + 1, -radius:radius + 1]
        return ndimage.binary_dilation(bild, structure=(x * x + y * y) <= radius ** 2)

    @classmethod
    def zone(cls, uvs, form):
        return cls.kern(uvs, form, cls.RAND_PX)

    @classmethod
    def maske(cls, bild, zone, kern):
        u"""Die gemalte Braue: das Dunkle der Zone, das die Brauenpunkte berührt
        (`kern`; Augenwinkel und Wimpernansatz liegen weiter weg), dazu die
        helleren Enden und Ränder des Bogens (`RAND_DUNKEL`, zusammenhängend
        mit dem Dunklen), etwas ausgedehnt."""
        from scipy import ndimage
        rgb = bild[..., :3].astype(np.float64)
        lum = rgb @ np.array([0.299, 0.587, 0.114])
        median = np.median(lum[zone]) if zone.any() else 0.0
        dunkel = zone & (lum < cls.DUNKEL * median)
        marken, anzahl = ndimage.label(dunkel)
        am_kern = np.zeros(anzahl + 1, dtype=bool)
        am_kern[np.unique(marken[kern & dunkel])] = True
        am_kern[0] = False
        bogen = am_kern[marken]
        # Die helleren Enden und Ränder des Bogens: zusammenhängend mit ihm.
        weich = zone & (lum < cls.RAND_DUNKEL * median)
        marken, anzahl = ndimage.label(weich)
        am_bogen = np.zeros(anzahl + 1, dtype=bool)
        am_bogen[np.unique(marken[bogen & weich])] = True
        am_bogen[0] = False
        return ndimage.binary_dilation(bogen | am_bogen[marken],
                                       iterations=cls.AUSDEHNUNG_PX)

    @classmethod
    def fuellen(cls, bild, maske):
        u"""Maskenpixel aus der Umgebung füllen — Front vom Rand nach innen,
        danach im Maskenbereich geglättet. Gibt eine Kopie zurück."""
        from scipy import ndimage
        aus = bild.astype(np.float64).copy()
        offen = maske.copy()
        kern = np.ones((3, 3))
        while offen.any():
            bekannt = ~offen
            summe = np.stack([ndimage.convolve(aus[..., k] * bekannt, kern,
                                               mode='nearest')
                              for k in range(aus.shape[-1])], axis=-1)
            anzahl = ndimage.convolve(bekannt.astype(np.float64), kern, mode='nearest')
            rand = offen & (anzahl > 0)
            if not rand.any():
                break
            aus[rand] = summe[rand] / anzahl[rand][:, None]
            offen &= ~rand
        weich = np.stack([ndimage.gaussian_filter(aus[..., k], cls.GLAETTUNG)
                          for k in range(aus.shape[-1])], axis=-1)
        aus[maske] = weich[maske]
        return np.clip(np.rint(aus), 0, 255).astype(np.uint8)

    # --------------------------------------------------------------- Zutaten

    _zutaten = {}

    @classmethod
    def zutaten(cls):
        u"""`(einheiten, uvs)` — MB-Lab-Einheiten und die UVs des Basisnetzes,
        einmal je Prozess."""
        if 'einheiten' not in cls._zutaten:
            from humanbody_core.mimik.mblab_ausdruecke import MblabAusdruecke
            mblab = Path(settings.TOOLS_ROOT) / 'tools' / 'MB-Lab' / 'data'
            cls._zutaten['einheiten'] = MblabAusdruecke(str(mblab)).einheiten()
            cls._zutaten['uvs'] = np.load(
                str(Path(settings.HUMANBODY_ROOT) / 'data' / 'humanBody' / 'uvs.npy'))
        return cls._zutaten['einheiten'], cls._zutaten['uvs']

    @classmethod
    def fuer(cls, quelle):
        u"""Die retuschierte Fassung einer Albedo — mit den Zutaten des Projekts."""
        einheiten, uvs = cls.zutaten()
        return cls.ohne_brauen(quelle, einheiten, uvs)

    @classmethod
    def brauenmaske(cls, quelle):
        u"""`(maske, zone)` der gemalten Braue einer Albedo — für `Brauenbogen`."""
        from PIL import Image
        einheiten, uvs = cls.zutaten()
        with Image.open(quelle) as bild:
            roh = np.asarray(bild.convert('RGB'))
        brauen = uvs[cls.brauenpunkte(einheiten)]
        zone = cls.zone(brauen, roh.shape[:2])
        return cls.maske(roh, zone, cls.kern(brauen, roh.shape[:2], cls.KERN_PX)), zone

    # ---------------------------------------------------------------- Datei

    @classmethod
    def ziel(cls, quelle):
        return cls.ORDNER / ('%s_ohne_brauen.png' % Path(quelle).stem)

    @classmethod
    def ohne_brauen(cls, quelle, einheiten, uvs):
        u"""Pfad der retuschierten Fassung — aus der Ablage oder frisch."""
        from PIL import Image
        quelle = Path(quelle)
        ziel = cls.ziel(quelle)
        if ziel.is_file() and ziel.stat().st_mtime >= quelle.stat().st_mtime \
                and cls._fassung(ziel) == cls.FASSUNG:
            return ziel
        with Image.open(quelle) as bild:
            roh = np.asarray(bild.convert('RGB'))
        brauen = uvs[cls.brauenpunkte(einheiten)]
        zone = cls.zone(brauen, roh.shape[:2])
        maske = cls.maske(roh, zone, cls.kern(brauen, roh.shape[:2], cls.KERN_PX))
        fertig = cls.fuellen(roh, maske)
        cls.ORDNER.mkdir(parents=True, exist_ok=True)
        Image.fromarray(fertig).save(ziel, pnginfo=cls._info())
        logger.info('Brauenretusche: %s -> %s (%d Brauenpixel in Zone %d)',
                    quelle.name, ziel.name, int(maske.sum()), int(zone.sum()))
        return ziel

    @classmethod
    def _info(cls):
        from PIL.PngImagePlugin import PngInfo
        info = PngInfo()
        info.add_text('brauenretusche', str(cls.FASSUNG))
        return info

    @staticmethod
    def _fassung(pfad):
        from PIL import Image
        with Image.open(pfad) as bild:
            return int(bild.info.get('brauenretusche', 0))
