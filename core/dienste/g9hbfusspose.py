# -*- coding: utf-8 -*-
u"""G9hbfusspose — die Fusspose eines Daz-Schuhs auf der HumanBody-Figur.

WARUM (19.09.2026, Edgar mit Bild: „Die Sandalen fitten nicht" — der flache
Fuss stand vor und ueber der Sandale): Ein Genesis-8-Schuh mit `!FootPose`
(Bardot Sandals: `l_foot` x 25,7 Grad, `l_toes` x -34,4) ist so modelliert,
wie er am GEBEUGTEN Fuss sitzt — Sohle eben, Ferse oben. Auf Genesis 9
bekommt die FIGUR die Pose als Griff (`genesis9-inhalte.md`, Schuhe). Auf
HumanBody gibt es dafuer den Absatz (`core/dienste/absatzpose.py`): Fuss um
die Querachse um `winkel_grad` gebeugt, Zehen um `winkel + sprengung` zurueck,
die Figur um `hebung_cm` gehoben. Aus der Daz-Pose wird also

    winkel_grad    = l_foot x                      (25,7)
    sprengung_grad = -(l_toes x + l_foot x)        (8,7: die Zehenspitze steigt)
    hebung_cm      = -tiefster Punkt des Stuecks   (die Sohle steht auf dem Boden)

RUHELAGE: Der Browser haeutet das Stueck an DEF-foot/DEF-toe und dreht es
mit dem Fuss — ein Stueck, das schon die gebeugte Form hat, wuerde doppelt
gedreht (Daz gleicht genau das mit JCMs aus, die es hier nicht gibt). Darum
wird das uebertragene Stueck VOR dem Haeuten in die Ruhelage zurueckgedreht:
`ruhelage` sucht je Punkt die Lage, die unter dem Absatz (lineares Blend-
Skinning ueber seine Gewichte) wieder auf die uebertragene faellt — Fixpunkt-
Iteration, die Drehungen sind klein. Die Knochenkoepfe stammen vom
Grundskelett des Geschlechts (`def_skeleton.json`), nicht von der Figur mit
Morphs: ein Zentimeter am Drehpunkt macht bei 26 Grad 4 mm am Zeh.
"""
import math

import numpy as np

from Genesis9.garderobe import G9garderobe

__all__ = ['G9hbfusspose']


class G9hbfusspose:
    u"""Absatzwerte aus der Daz-Fusspose und das Stueck in die Ruhelage."""

    FUSS = ('DEF-foot.L', 'DEF-foot.R')
    ZEHEN = ('DEF-toe.L', 'DEF-toe.R')
    DURCHGAENGE = 25
    _koepfe = {}

    # --------------------------------------------------------------- Absatz

    @classmethod
    def absatz(cls, kennung, kaefige):
        u"""`{winkel_grad, sprengung_grad, hebung_cm, plateau_cm, quelle}` fuer
        einen Schuh mit Fusspose — sonst None. `kaefige`: die uebertragenen
        Teile (M, 3), fuer den Hub."""
        griff = G9garderobe.griff(kennung) or {}
        fuss = griff.get('l_foot') or griff.get('r_foot')
        if not fuss:
            return None
        winkel = float(fuss.get('rotation/x', 0.0))
        zehen = griff.get('l_toes') or griff.get('r_toes') or {}
        zehen_x = float(zehen.get('rotation/x', -winkel))
        tiefster = min((float(np.asarray(k)[:, 1].min()) for k in kaefige if len(k)), default=0.0)
        return {'winkel_grad': round(winkel, 2), 'sprengung_grad': round(-(zehen_x + winkel), 2),
                'hebung_cm': round(max(0.0, -tiefster * 100.0), 2), 'plateau_cm': 0.0,
                'quelle': 'schuh:%s' % kennung}

    # ------------------------------------------------------------- Ruhelage

    @classmethod
    def koepfe(cls, geschlecht):
        u"""{DEF-Knochen: Kopf (Three, m)} des Grundskeletts — einmal je Geschlecht."""
        if geschlecht not in cls._koepfe:
            from .absatzpose import Absatzpose
            from .skelettgeometrie import Skelettgeometrie
            if geschlecht == 'male':
                from humanbody_core.skeleton import SkeletonGeometry
                from django.conf import settings
                ordner = settings.HUMANBODY_DATA_DIR.parent / (settings.HUMANBODY_DATA_DIR.name + '_male')
                welt = SkeletonGeometry.from_json(str(ordner / 'def_skeleton.json'),
                                                  str(ordner / 'skin_weights_base.json')).compute_world_transforms()
            else:
                welt = Skelettgeometrie.holen().compute_world_transforms()
            cls._koepfe[geschlecht] = {n: np.asarray(welt[n]['world_pos'], dtype=np.float64)
                                       for n in Absatzpose.FUSS + Absatzpose.ZEHEN if n in welt}
        return cls._koepfe[geschlecht]

    @staticmethod
    def um_x(grad):
        u"""Drehmatrix um die Querachse x (Three: y oben, z vorn) — positiv senkt die Zehen."""
        c, s = math.cos(math.radians(grad)), math.sin(math.radians(grad))
        return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])

    @classmethod
    def gebeugt(cls, punkte, haut, absatz, koepfe):
        u"""(M, 3) Punkte unter dem Absatz — lineares Blend-Skinning ueber Fuss- und
        Zehenknochen, alle anderen Knochen stehen still."""
        p = np.asarray(punkte, dtype=np.float64)
        namen = list(haut['knochen'])
        index = np.asarray(haut['index'], dtype=np.int64)
        gewicht = np.asarray(haut['gewicht'], dtype=np.float64)
        r_fuss = cls.um_x(absatz['winkel_grad'])
        r_zeh = cls.um_x(-(absatz['winkel_grad'] + absatz['sprengung_grad']))
        bewegt = {}
        for seite in ('L', 'R'):
            fuss, zeh = 'DEF-foot.%s' % seite, 'DEF-toe.%s' % seite
            if fuss in koepfe:
                bewegt[fuss] = lambda q, hf=koepfe[fuss]: (q - hf) @ r_fuss.T + hf
            if fuss in koepfe and zeh in koepfe:
                bewegt[zeh] = lambda q, hf=koepfe[fuss], hz=koepfe[zeh]: (
                    ((q - hz) @ r_zeh.T + hz - hf) @ r_fuss.T + hf)
        aus = p.copy()
        for spalte in range(index.shape[1]):
            for nr, name in enumerate(namen):
                if name not in bewegt:
                    continue
                m = (index[:, spalte] == nr) & (gewicht[:, spalte] > 0)
                if m.any():
                    aus[m] += gewicht[m, spalte][:, None] * (bewegt[name](p[m]) - p[m])
        return aus

    @classmethod
    def ruhelage(cls, punkte, haut, absatz, geschlecht='female'):
        u"""Die Lage, die unter dem Absatz auf `punkte` faellt (Fixpunkt, DURCHGAENGE)."""
        ziel = np.asarray(punkte, dtype=np.float64)
        koepfe = cls.koepfe(geschlecht)
        if not koepfe:
            return ziel
        ruhe = ziel.copy()
        for _ in range(cls.DURCHGAENGE):
            rest = cls.gebeugt(ruhe, haut, absatz, koepfe) - ziel
            ruhe -= rest
            if np.abs(rest).max() < 1e-5:
                break
        return ruhe
