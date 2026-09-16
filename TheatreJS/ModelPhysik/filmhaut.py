# -*- coding: utf-8 -*-
u"""Die Materialgruppen des Koerpers im Film: Haut mit Textur und Braue,
Wimpern, Augen, Lippen, Zaehne, Naegel.

WARUM (Edgar, 17.09.2026: „baue: der pyrender-Film (er hat weder Textur
noch Augen/Wimpern)"): Der Film rendert das unterteilte Netz der Szene —
mit allen Gruppen, aber bis heute in EINER Hautfarbe: Augen, Wimpern und
Zaehne waren da, nur hautfarben. Hier bekommt jede Gruppe ihr Material wie
im Browser (`gemeinsam/koerpermaterialien.js`, `detailfarben.js`), die Haut
das fertige Bild aus `core/dienste/hautbild.py` (Albedo oder Hautfarbe,
Braue eingemischt), die Lippen ihre eigene Gruppe aus `Lippenmaske` (wie
`lippengruppe.js`).

Der gekuerzte Index der Hautmaske (`Filmmasken.gerendert`) nennt seine
Zeilen nicht — die Gruppe je Dreieck kommt ueber den Schluessel der drei
Ecken aus dem vollen Index, einmal je Index gemerkt.

Ohne Unterteiler (18K-Aussenhaut) bleibt es bei der Flaeche: Dort tragen
die Dreiecke keine Materialnummer.
"""
import logging

import numpy as np

from feinkoerper import Feinkoerper

logger = logging.getLogger(__name__)


class Filmhaut:
    u"""Materialien und Zeichengruppen eines Koerpers, je Bild als pyrender-Netze."""

    #: Index = Materialgruppe aus `face_materials` — DER VERTRAG aus
    #: `gemeinsam/koerpermaterialien.js` (Reihenfolge!), dazu 11 = Lippen.
    #: Je Zeile: Detailfeld der Farbe (None = fest), Vorgabefarbe (sRGB),
    #: Rauheit, Deckkraft. `test_filmhaut` vergleicht mit der JS-Quelle.
    GRUPPEN = [
        ('haut', '#d4a574', 0.55, 1.0),          # 0 Haut
        ('haut', '#d4a574', 0.55, 1.0),          # 1 Censor (dieselbe Haut)
        ('wimpern', '#111111', 0.8, 1.0),        # 2 Wimpern
        (None, '#0a0a0a', 0.1, 1.0),             # 3 Pupille
        ('sklera', '#f4f0e8', 0.2, 1.0),         # 4 Sklera
        (None, '#f4f0e8', 0.05, 0.3),            # 5 Hornhaut (durchsichtig)
        ('iris', '#4a7a9b', 0.15, 1.0),          # 6 Iris
        ('zunge', '#b55a6a', 0.7, 1.0),          # 7 Zunge
        ('zaehne', '#f0ece0', 0.3, 1.0),         # 8 Zaehne
        ('naegel_hand', '#e0a88a', 0.4, 1.0),    # 9 Naegel Hand
        ('naegel_fuss', '#e0a88a', 0.4, 1.0),    # 10 Naegel Fuss
        ('lippen', '#b5707a', 0.4, 1.0),         # 11 Lippen (`lippengruppe.js`)
    ]
    HAUT = (0, 1)
    LIPPEN = 11
    #: Glanzfeld je Gruppe: Rauheit = 1 − Glanz (`Detailfarben.GLANZ`).
    GLANZ = {0: 'haut_glanz', 1: 'haut_glanz', 11: 'lippen_glanz'}

    def __init__(self, uvs, dreiecke, material, details=None, bild=None):
        self.uvs = np.ascontiguousarray(uvs, dtype=np.float32)
        self.dreiecke = np.asarray(dreiecke, dtype=np.int64)
        self.material = np.array(material, dtype=np.int64)
        self.details = dict(details or {})
        self.bild = bild
        self._werkstoffe = None
        self._zuordnung = None

    # --------------------------------------------------------------- Anlegen

    @classmethod
    def anlegen(cls, teil, details, geschlecht, body_type):
        u"""`teil['filmhaut']` fuer einen Koerper mit Unterteiler — oder None,
        dann rendert `Filmrender` die Flaeche wie bisher."""
        unterteiler = teil.get('unterteiler')
        if (unterteiler is None or unterteiler.uvs is None
                or unterteiler.triangle_materials is None):
            return None
        try:
            haut = cls(unterteiler.uvs, Feinkoerper.dreiecke(teil),
                       unterteiler.triangle_materials, details,
                       cls._hautbild(details, body_type))
            haut.lippen(cls._lippenpunkte(geschlecht, unterteiler))
        # stumm gewollt: ohne Texturen oder Maske wird der Film trotzdem fertig
        except Exception:                                       # noqa: BLE001
            logger.warning('Filmhaut: Flaeche statt Textur', exc_info=True)
            return None
        teil['filmhaut'] = haut
        return haut

    @staticmethod
    def _hautbild(details, body_type):
        from core.dienste.hautbild import Hautbild
        return Hautbild.bild(details, body_type)

    @staticmethod
    def _lippenpunkte(geschlecht, unterteiler):
        from core.dienste.lippenmaske import Lippenmaske
        return Lippenmaske.indizes(geschlecht, unterteiler.uvs, unterteiler)

    def lippen(self, punkte):
        u"""Dreiecke, deren drei Ecken Lippenpunkte sind, in die Lippengruppe."""
        ist = np.zeros(len(self.uvs), dtype=bool)
        ist[np.asarray(punkte, dtype=np.int64)] = True
        self.material[ist[self.dreiecke].all(axis=1)] = self.LIPPEN
        self._zuordnung = None

    # --------------------------------------------------------------- Gruppen

    @staticmethod
    def _schluessel(dreiecke, n):
        u"""Ein Schluessel je Dreieck, unabhaengig von der Eckenreihenfolge."""
        d = np.sort(np.asarray(dreiecke, dtype=np.int64), axis=1)
        return (d[:, 0] * n + d[:, 1]) * n + d[:, 2]

    def gruppe(self, dreiecke):
        u"""Materialgruppe je Zeile eines (gekuerzten) Index."""
        if self._zuordnung is not None and self._zuordnung[0] is dreiecke:
            return self._zuordnung[1]
        n = len(self.uvs)
        voll = self._schluessel(self.dreiecke, n)
        reihe = np.argsort(voll)
        stelle = np.clip(np.searchsorted(voll[reihe], self._schluessel(dreiecke, n)),
                         0, len(voll) - 1)
        aus = self.material[reihe[stelle]]
        self._zuordnung = (dreiecke, aus)
        return aus

    # ------------------------------------------------------------ Werkstoffe

    @classmethod
    def linear(cls, hex_farbe):
        u"""sRGB-Hex → lineares RGB, wie Three.js `color.set('#…')`."""
        aus = []
        for i in (1, 3, 5):
            c = int(hex_farbe[i:i + 2], 16) / 255.0
            aus.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
        return aus

    def _rauheit(self, nummer, vorgabe):
        glanz = self.details.get(self.GLANZ.get(nummer))
        if isinstance(glanz, (int, float)):
            return 1.0 - min(1.0, max(0.0, float(glanz)))
        return vorgabe

    def werkstoffe(self):
        u"""Ein pyrender-Material je Gruppe, einmal je Film."""
        import pyrender
        if self._werkstoffe is not None:
            return self._werkstoffe
        textur = None
        if self.bild is not None:
            textur = pyrender.Texture(source=np.ascontiguousarray(self.bild),
                                      source_channels='RGB')
        aus = []
        for nummer, (feld, vorgabe, rauheit, alpha) in enumerate(self.GRUPPEN):
            farbe = self.details.get(feld) if feld else None
            hex_farbe = farbe if isinstance(farbe, str) and len(farbe) == 7 \
                and farbe.startswith('#') else vorgabe
            mit_textur = textur is not None and nummer in self.HAUT
            aus.append(pyrender.MetallicRoughnessMaterial(
                baseColorFactor=([1.0, 1.0, 1.0] if mit_textur
                                 else self.linear(hex_farbe)) + [alpha],
                baseColorTexture=textur if mit_textur else None,
                metallicFactor=0.0, roughnessFactor=self._rauheit(nummer, rauheit),
                doubleSided=True, alphaMode='BLEND' if alpha < 1.0 else 'OPAQUE'))
        self._werkstoffe = aus
        return aus

    # ----------------------------------------------------------------- Netze

    def netze(self, punkte, normalen, dreiecke):
        u"""pyrender-Netze fuer ein Bild: ein Netz mit allen deckenden
        Gruppen, je ein eigenes fuer eine durchsichtige — pyrender zeichnet
        durchsichtige Netze nach den deckenden."""
        import pyrender
        gruppe = self.gruppe(dreiecke)
        lage = np.ascontiguousarray(punkte, dtype=np.float32)
        norm = np.ascontiguousarray(normalen, dtype=np.float32)
        deckend, durchsichtig = [], []
        for nummer, werkstoff in enumerate(self.werkstoffe()):
            zeilen = np.flatnonzero(gruppe == nummer)
            if not len(zeilen):
                continue
            teil = pyrender.Primitive(
                positions=lage, normals=norm,
                texcoord_0=self.uvs if nummer in self.HAUT else None,
                indices=np.ascontiguousarray(dreiecke[zeilen], dtype=np.uint32),
                material=werkstoff, mode=4)
            (durchsichtig if werkstoff.alphaMode == 'BLEND' else deckend).append(teil)
        aus = [pyrender.Mesh(primitives=deckend)] if deckend else []
        aus.extend(pyrender.Mesh(primitives=[t]) for t in durchsichtig)
        return aus
