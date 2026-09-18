# -*- coding: utf-8 -*-
"""Koerperfeinheit — was im Film ueber die 18K-Aussenhaut hinausgeht.

MB-Lab (`tools/MB-Lab/humanoid.py`) haengt an die Figur drei Modifier, in
dieser Reihenfolge: Corrective Smooth (alles ausser Kopf), SubSurf (Render
3) und Displace (Textur aus Alter/Tonus/Masse, Staerke 0,01). Bis zum
17.09.2026 rechnete der Film nur die Unterteilung (eine Stufe); Edgar:
„implementiere alles, was fehlt". Hier laufen die drei je Bild hintereinander:

    Basis (LBS + Physik, 18.210)
      → Korrekturglaettung           (`humanbody_core/korrekturglaettung.py`)
      → Unterteilung  W @ basis      (`CatmullClarkSubdivider`, Stufe aus Einstellung)
      → Hautverschiebung entlang der Normale  (`humanbody_core/hautverschiebung.py`)

Die Normalen der feinen Punkte fuer die Verschiebung kommen NICHT aus den
2,2 Mio. feinen Dreiecken (893 ms je Bild bei drei Stufen), sondern aus den
Basisdreiecken durch dieselbe Matrix: `normalize(W @ n_basis)` — fuer eine
glatte Unterteilung dieselbe Richtung, in 80 ms.

`Kopfmaske`: MB-Lab nimmt die Vertexgruppe `head` invertiert; hier ist das
1 − (Summe der Gewichte der Kopf- und Gesichtsknochen).
"""

import os
import re
import sys

import numpy as np

# `humanbody_core` liegt neben HumanBodyWeb — wie in `bvh_nach_anim.py`, aber
# ohne festen Laufwerksbuchstaben (Regel `projektpfade`).
_HUMANBODY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'HumanBody'
)
if _HUMANBODY not in sys.path:
    sys.path.insert(0, _HUMANBODY)

from humanbody_core.hautverschiebung import Hautverschiebung  # noqa: E402
from humanbody_core.korrekturglaettung import Korrekturglaettung  # noqa: E402
from maskengeometrie import Geometrie  # noqa: E402


class Koerperfeinheit:
    """Unterteiler, Korrekturglaettung und Hautverschiebung EINES Koerpers."""

    #: Knochen, die zum Kopf gehoeren (Corrective Smooth laesst ihn aus).
    KOPF = re.compile(
        r'^(DEF|MCH|ORG)-(brow|cheek|chin|ear|forehead|jaw|lid|lip|'
        r'nose|temple|tongue|eye|teeth|spine\.006)(\.|$)'
    )

    def __init__(self, unterteiler, vierecke, verschiebung=None, korrektur=True):
        """`verschiebung` = (H, W)-Textur in 0..1 oder None; `korrektur`
        False laesst die Glaettung aus (Vergleich, Tests)."""
        self.unterteiler = unterteiler
        self.vierecke = np.asarray(vierecke, dtype=np.int64)
        self.textur = None if verschiebung is None else np.asarray(verschiebung, dtype=np.float32)
        self.mit_korrektur = bool(korrektur)
        self.korrektur = None

    # ---------------------------------------------------------------- Aufbau

    @classmethod
    def kopfmaske(cls, gewichte, namen):
        """Je Basispunkt der Anteil, der am Kopf haengt (0..1)."""
        spalten = [i for i, name in enumerate(namen) if cls.KOPF.match(name)]
        if not spalten:
            return np.zeros(len(gewichte))
        return np.clip(np.asarray(gewichte)[:, spalten].sum(axis=1), 0.0, 1.0)

    def anlegen(self, punkte_ruhe, gewichte, namen):
        """Die Korrekturglaettung an der Ruhelage — mit MB-Labs Ausnahme
        des Kopfes. Muss vor dem ersten `punkte()` laufen."""
        if not self.mit_korrektur:
            return self
        maske = 1.0 - self.kopfmaske(gewichte, namen)
        self.korrektur = Korrekturglaettung(self.vierecke, gewichte=maske)
        self.korrektur.ruhelage(np.asarray(punkte_ruhe, dtype=np.float64))
        return self

    # -------------------------------------------------------------- Rechnung

    def glaetten(self, basis):
        if self.korrektur is None:
            return np.asarray(basis, dtype=np.float64)
        return self.korrektur.anwenden(basis)

    def verschieben(self, fein, basis, basis_dreiecke):
        if self.textur is None:
            return fein
        cc = self.unterteiler
        normalen = cc.subdivide(Geometrie.normalen(basis, basis_dreiecke))
        laenge = np.linalg.norm(normalen, axis=1, keepdims=True)
        normalen = normalen / np.maximum(laenge, 1e-12)
        return Hautverschiebung.anwenden(
            fein,
            normalen,
            cc.uvs,
            self.textur,
            staerke=Hautverschiebung.STAERKE,
            kopien_eltern=cc.kopien_eltern,
            geo_punkte=cc.geo_vertex_count,
        )

    def punkte(self, basis, basis_dreiecke):
        """Die sichtbaren Punkte zu einem Basisstand (Ruhe oder ein Bild)."""
        geglaettet = self.glaetten(basis)
        fein = self.unterteiler.subdivide(geglaettet)
        return np.asarray(self.verschieben(fein, geglaettet, basis_dreiecke), dtype=np.float64)

    @property
    def dreiecke(self):
        return np.asarray(self.unterteiler.triangles, dtype=np.int64)

    def beschreibung(self):
        return '%d Stufe(n), Korrekturglaettung %s, Hautverschiebung %s' % (
            self.unterteiler.levels,
            'an' if self.korrektur is not None else 'aus',
            'an' if self.textur is not None else 'aus',
        )
