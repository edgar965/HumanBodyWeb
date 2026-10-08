# -*- coding: utf-8 -*-
"""Blendimporthaut — die Originalhaut der .blend auf die vier Haut-Kacheln von Genesis (Farbe, Normalen, Rauheit).

Kachel 1005 (Nägel) wird nicht gebacken (`Blendimportlage.NICHT_GEBACKEN`): Genesis' Nägel und der Nagellack-Preset gelten.
Die gebackenen Normalen werden von falschen Treffern gesäubert (`Blendimportnormalen`, Bericht `normalen_flach`).

„Mesh to 3D" überträgt die Netzfarbe über rund 2 Mio. Proben (`meshfigur.md`, Schritt „textur") — für ein Scan-Netz
genug, für eine 8K-Haut zu grob, und Normalen und Rauheit kennt es nicht. Hier backt Blender aus dem Original
(`blendbacken.py`): Der Körper wird dafür in die Ruhelage der Figur gerechnet (`Blendimportlage.ruhelage`), die Figur
selbst (Regler + Eigenmorph, Stufe 1) liegt je Kachel als OBJ daneben.

NACHARBEIT: Wo kein Strahl das Original trifft, ist die gebackene Farbe schwarz. Dort gilt die Kachel von „Mesh to 3D"
(Daz-Haut auf den Hautton getönt, darüber die Netzfarbe), die Normale wird flach (128, 128, 255), die Rauheit der Median
der getroffenen Texel. Der Anteil getroffener Texel steht je Kachel im Bericht, dazu der Abstand der Körperpunkte zur
FLÄCHE der Figur in Ruhe (Median, p95, Maximum, RMS, Anteil über 8 mm) — er sagt, wie gut beide Flächen beim Backen
übereinanderliegen. Gemessen am ersten Lauf (08.10.2026): Median 0,99 mm, p95 14,4 mm, 12,3 % über 8 mm — die großen
Abstände sitzen an Fingern, Brustwarzen, Lippen, Schritt und Zehen (Wärmekarte). Deutung, nicht geprüft: Dort trifft
der Strahl (Auszug 15 mm, Reichweite 35 mm) nicht oder die falsche Stelle.
"""

import logging

import numpy as np

from .blendimportblender import Blendimportblender
from .blendimportlage import Blendimportlage

logger = logging.getLogger('core')

__all__ = ['Blendimporthaut']


class Blendimporthaut:
    FLACH = (128, 128, 255)

    def __init__(self, ablage, job, inventar, rollen, px, melden=None):
        self.ablage = ablage
        self.job = job
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen
        self.px = int(px)
        self.melden = melden or (lambda anteil, text: None)
        self.normalen_flach = {}

    def _koerper(self):
        name = next(r['name'] for r in self.rollen if r['rolle'] == 'koerper')
        with np.load(self.ablage.export(self.inventar[name]['datei'])) as d:
            return name, np.asarray(d['punkte'], dtype=np.float64)

    def abstand(self, ruhe, figur, dreiecke):
        """Abstand jedes Körperpunkts zur FLÄCHE der Figur (mm) — Median, p95, Maximum, RMS und Anteil über 8 mm.
        Nicht zum nächsten Punkt: bei 104.480 Figurpunkten und 5–10 mm Punktabstand maß das den Punktabstand mit
        (Import 2026.10.08.11.28.06: Median 2,62 mm zum Punkt gegen 0,99 mm zur Fläche)."""
        import trimesh

        _, d, _ = trimesh.proximity.closest_point(trimesh.Trimesh(figur, dreiecke, process=False), ruhe)
        d = d * 1000.0
        return {'median_mm': round(float(np.median(d)), 2), 'p95_mm': round(float(np.percentile(d, 95)), 2),
                'max_mm': round(float(d.max()), 1), 'rms_mm': round(float(np.sqrt((d ** 2).mean())), 2),
                'ueber_8mm': round(float((d > 8.0).mean()), 4)}

    def backen(self, blend):
        lage = Blendimportlage(self.job)
        name, punkte = self._koerper()
        ruhe = lage.ruhelage(punkte)
        np.save(self.ablage.arbeit('koerper_ruhe.npy'), Blendimportlage.blender(ruhe))
        ordner = self.ablage.arbeit('genesis')
        ordner.mkdir(parents=True, exist_ok=True)
        objs = lage.genesis_objs(ordner)
        figur = lage.genesis()
        # `nummern`, nicht `kacheln`: der Lauf legt unter `kacheln` die Dateien ab (`{**bericht}` überschrieb sie mit der Liste).
        bericht = {'abstand': self.abstand(ruhe, figur['punkte'], figur['dreiecke']), 'nummern': sorted(objs)}
        logger.info('Blender-Import %s: Körper in Ruhe, Abstand zur Figur %s', self.ablage.kennung, bericht['abstand'])
        Blendimportblender(self.ablage, self.melden).laufen(
            'blendbacken.py', blend,
            ['--koerper', name, '--lage', self.ablage.arbeit('koerper_ruhe.npy'), '--genesis', ordner,
             '--ziel', self.ablage.ergebnis(), '--px', self.px],
            self.ablage.ergebnis('gebacken.txt'))
        bericht['deckung'] = self.nacharbeiten(sorted(objs))
        bericht['normalen_flach'] = self.normalen_flach
        return self.kacheln(sorted(objs)), bericht

    # ------------------------------------------------------------ Nacharbeit

    def _meshfigur_kachel(self, kachel):
        from ..daten.meshfigurablage import Meshfigurablage

        name = ((self.job.ergebnis or {}).get('fototextur') or {}).get('kacheln', {}).get(str(kachel))
        pfad = Meshfigurablage(self.job.kennung).ergebnis(name) if name else None
        return pfad if pfad and pfad.is_file() else None

    def nacharbeiten(self, kacheln):
        """Fehlstellen füllen; `{kachel: Anteil getroffener Texel in %}`."""
        from PIL import Image

        from .blendimportnormalen import Blendimportnormalen

        Image.MAX_IMAGE_PIXELS = None
        deckung = {}
        self.normalen_flach = {}
        for k in kacheln:
            farbe_pfad = self.ablage.ergebnis('haut_%d_farbe.jpg' % k)
            farbe = np.asarray(Image.open(farbe_pfad).convert('RGB'))
            # JPEG verwischt das reine Schwarz der Fehlstellen um wenige Stufen.
            leer = farbe.max(axis=2) <= 6
            deckung[str(k)] = round(100.0 * (1.0 - leer.mean()), 1)
            ersatz = self._meshfigur_kachel(k)
            if leer.any() and ersatz is not None:
                hinten = np.asarray(Image.open(ersatz).convert('RGB').resize(farbe.shape[1::-1], Image.LANCZOS))
                farbe = np.where(leer[..., None], hinten, farbe)
                Image.fromarray(farbe).save(farbe_pfad, quality=95)
            normal_pfad = self.ablage.ergebnis('haut_%d_normalen.png' % k)
            normal = np.asarray(Image.open(normal_pfad).convert('RGB')).copy()
            # Die rohe Karte bleibt in `arbeit/` — die Grenze der Säuberung lässt sich so ohne neues Backen (17 Minuten) ändern.
            Image.fromarray(normal).save(self.ablage.arbeit('normalen_roh_%d.png' % k))
            normal[leer] = self.FLACH
            normal, self.normalen_flach[str(k)] = Blendimportnormalen.saeubern(normal, leer)
            Image.fromarray(normal).save(normal_pfad)
            rauh_pfad = self.ablage.ergebnis('haut_%d_rauheit.jpg' % k)
            rauh = np.asarray(Image.open(rauh_pfad).convert('L')).copy()
            if (~leer).any():
                rauh[leer] = int(np.median(rauh[~leer]))
            Image.fromarray(rauh).save(rauh_pfad, quality=95)
            self.melden(0.95, 'Kachel %d nachgearbeitet (%.1f %% getroffen)' % (k, deckung[str(k)]))
        return deckung

    def kacheln(self, kacheln):
        """`{1001: Datei, '1001:normalen': Datei, '1001:rauheit': Datei, …}` (Namen in `ergebnis/`)."""
        aus = {}
        for k in kacheln:
            aus[str(k)] = 'haut_%d_farbe.jpg' % k
            aus['%d:normalen' % k] = 'haut_%d_normalen.png' % k
            aus['%d:rauheit' % k] = 'haut_%d_rauheit.jpg' % k
        return aus
