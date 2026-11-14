# -*- coding: utf-8 -*-
"""Mesh3dnetzkatalog — die Flächen des Netzes eines Mesh-3D-Auftrags, wie die Mesh-Ansicht sie sieht (13.10.2026, „Netz bearbeiten“).

Edgar: „ich möchte diesen störenden zusammenhängenden zweiten Unterarm vor dem Arm der Ballerina ausschneiden, das Mesh speichern, und dann das 3D Modell neu rechnen“ (Konzept
`Docu/konzepte/2026-10-13_mesh-3d-netz-ausschneiden-konzept.md`). Der Browser schickt nie Flächennummern, sondern ORTE (ein Klickpunkt, vier Ebenen eines Rahmens, ein Kasten); der Server übersetzt sie hier in
Flächen des ORIGINALS. Dafür braucht er je Fläche die Mitte und den zusammenhängenden Teil („Insel“), zu dem sie gehört.

Die Datei ist `arbeit/koerper.glb` des Imports — dieselbe, die die Mesh-Ansicht zeigt (bei großen Netzen als vereinfachte Kopie, deren Koordinaten unverändert sind) und die aus der Quelldatei nur durch
eine Skalierung des Wurzelknotens entsteht (`Blendimportnetz`): Flächenzahl und Flächenreihenfolge sind die der Quelle. Die Koordinaten sind die der SZENE (Knoten angewendet, `to_geometry`) — im Browser
`objekt.worldToLocal(...)` des geladenen glTF.

Teile: Flächen, die sich eine KANTE teilen (nach dem Verschmelzen der UV-Nahtkopien auf `RUNDEN` der Kastendiagonale). Gemessen an der Spiralballerina (`netz_inseln.py`): 51.096 Flächen, 16 Teile, der zweite
Unterarm samt Kugel ist einer davon. Teil 0 ist der größte. Das Ergebnis liegt neben dem Auftrag in `arbeit/netzbearbeitung/katalog.npz` (mit Stempel aus Fassung, Größe und Zeit der Datei — ein anderes Netz
gilt nie als dasselbe, `artefakte-benennen.md`) und im Speicher des Servers.
"""

import logging
import os
import threading
from pathlib import Path

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

from .mesh3dnetzdreieck import Mesh3dnetzdreieck

logger = logging.getLogger('core')

__all__ = ['Mesh3dnetzkatalog']


class Mesh3dnetzkatalog:
    ORDNER = 'netzbearbeitung'
    DATEI = 'katalog.npz'
    NETZ = 'koerper.glb'
    #: Fassung des Verfahrens — eine Ablage anderer Fassung wird neu gerechnet.
    FASSUNG = 1
    #: Punkte, die näher als dieser Anteil der Kastendiagonale liegen, sind derselbe Punkt (UV-Nahtkopien liegen exakt aufeinander).
    RUNDEN = 5e-5
    #: Im Speicher bleiben höchstens so viele Kataloge (ein Netz mit 2 Mio. Flächen: ~50 MB).
    SPEICHER_MAX = 2
    #: Suche der Fläche unter einem Punkt (`naechste_flaeche_genau`): so viele Kandidaten höchstens, und Dreiecke größer als dieser Radius (Szeneneinheiten) werden nicht gesucht.
    KANDIDATEN_MAX = 20000
    RADIUS_MAX = 0.6
    _speicher = {}
    _sperre = threading.Lock()

    def __init__(self, flaechen, mitte, insel, stempel):
        self.flaechen = int(flaechen)
        #: (F, 3) float32 Mitte jeder Fläche, Koordinaten der Szene.
        self.mitte = mitte
        #: (F,) int32 Nummer des Teils je Fläche; 0 = der größte.
        self.insel = insel
        self.groessen = Torchfeld.astype(Torchfeld.bincount(insel), torch.int64)
        self.stempel = stempel
        self._baum = None
        #: Punkte (float32) und Flächen (int32) der Datei und der größte Abstand einer Ecke zur Mitte ihrer Fläche — `dreiecke` liest sie erst, wenn ein Klick die Dreiecke braucht.
        self._eck = None
        self._flaechenradius = 0.0
        #: Die Datei, aus der der Katalog stammt (`fuer` setzt sie) — `farben_lab` liest die Textur daraus, erst wenn eine Auswahl nach Farbe sie braucht.
        self.pfad = None
        self._lab = None

    # ------------------------------------------------------------------ Zugriff

    @classmethod
    def datei(cls, ablage):
        return ablage.arbeit(cls.NETZ)

    @classmethod
    def stempel_von(cls, pfad):
        stand = Path(pfad).stat()
        return [cls.FASSUNG, stand.st_size, stand.st_mtime_ns]

    @classmethod
    def fuer(cls, ablage):
        """Der Katalog zum Netz des Imports: aus dem Speicher, aus der Ablage oder frisch gerechnet. `ValueError` mit dem Grund (kein Netz, mehrere Netze in der Datei)."""
        pfad = cls.datei(ablage)
        if not pfad.is_file():
            raise ValueError('Das Netz dieses Auftrags ist noch nicht da (Schritt „Netz“ hat nicht gerechnet)')
        stempel = cls.stempel_von(pfad)
        schluessel = (ablage.kennung, tuple(stempel))
        with cls._sperre:
            gefunden = cls._speicher.get(schluessel)
            if gefunden is None:
                gefunden = cls._lesen(ablage, stempel) or cls._rechnen(ablage, pfad, stempel)
                gefunden.pfad = pfad
                while len(cls._speicher) >= cls.SPEICHER_MAX:
                    cls._speicher.pop(next(iter(cls._speicher)))
                cls._speicher[schluessel] = gefunden
            return gefunden

    def naechste_flaeche(self, punkt):
        """Nummer der Fläche, deren Mitte dem Punkt am nächsten liegt."""
        return int(self._mittenbaum().query(Torchfeld.feld(punkt, dtype=torch.float64))[1])

    def _mittenbaum(self):
        if self._baum is None:
            from KoerperKI_alle.kartenbaum import Kartenbaum as cKDTree

            self._baum = cKDTree(self.mitte)
        return self._baum

    def dreiecke(self, nummern):
        """(N, 3, 3) die Eckpunkte der Flächen `nummern` in den Koordinaten der Szene — aus der Datei gelesen, beim ersten Gebrauch; `None`, wenn der Katalog keine Datei hat (Prüfkatalog)."""
        if self.pfad is None:
            return None
        if self._eck is None:
            punkte, flaechen = self.geometrie(self.pfad)
            eck = Torchfeld.astype(punkte, torch.float32), Torchfeld.astype(flaechen, torch.int32)
            self._flaechenradius = float(Torchfeld.linalg_norm(eck[0][eck[1]] - self.mitte[:, None, :], dim=2).max())
            self._eck = eck
        punkte, flaechen = self._eck
        return Torchfeld.astype(punkte[flaechen[Torchfeld.feld(nummern, dtype=torch.int64)]], torch.float64)

    def abstand_zu_flaechen(self, punkt, nummern):
        """(N,) Abstand des Punkts zu den DREIECKEN `nummern` (nicht zu ihren Mitten: ein Flügel mit 0,4 m langen Kanten hat die Mitte 4 cm neben dem Klick, der Klick liegt auf ihm); `None` ohne Datei."""
        eck = self.dreiecke(nummern)
        return None if eck is None else Mesh3dnetzdreieck.abstand(punkt, eck)

    def naechste_flaeche_genau(self, punkt):
        """Nummer der Fläche, auf der der Punkt liegt (oder die ihm am nächsten ist), gemessen am Dreieck. Kandidaten sind alle Flächen, deren Mitte höchstens so weit entfernt ist wie das größte Dreieck des Netzes reicht
        (`KANDIDATEN_MAX` nächste Mitten, `RADIUS_MAX` Szeneneinheiten); ohne Datei oder ohne Kandidaten gilt die nächste Mitte."""
        p = Torchfeld.feld(punkt, dtype=torch.float64)
        if self.dreiecke([0]) is None:
            return self.naechste_flaeche(p)
        baum = self._mittenbaum()
        kandidaten = Torchfeld.feld(baum.query_ball_point(p, min(self._flaechenradius, self.RADIUS_MAX)), dtype=torch.int64)
        if len(kandidaten) == 0:
            return self.naechste_flaeche(p)
        if len(kandidaten) > self.KANDIDATEN_MAX:
            kandidaten = kandidaten[torch.argsort(Torchfeld.linalg_norm(self.mitte[kandidaten] - p, dim=1), stable=True)[:self.KANDIDATEN_MAX]]
        return int(kandidaten[int(Mesh3dnetzdreieck.abstand(p, self.dreiecke(kandidaten)).argmin())])

    def farben_lab(self):
        """(F, 3) float32 — die Farbe jeder Fläche (Textur an der UV der Flächenmitte) als CIE-Lab; einmal gelesen und gemerkt. `ValueError`, wenn das Netz keine Farbtextur hat."""
        if self._lab is None:
            self._lab = self.lab_von(self.farben(self.pfad))
        return self._lab

    @staticmethod
    def farben(pfad):
        """(F, 3) sRGB 0…255 je Fläche aus der Basisfarbtextur der Datei (UV der Flächenmitte), Reihenfolge der Flächen wie in `geometrie`."""
        import trimesh

        szene = trimesh.load(str(pfad), force='scene', process=False)
        netz = szene.to_geometry() if hasattr(szene, 'to_geometry') else szene.dump(concatenate=True)
        visuell = netz.visual
        material = getattr(visuell, 'material', None)
        bild = getattr(material, 'baseColorTexture', None) or getattr(material, 'image', None)
        uv = getattr(visuell, 'uv', None)
        if bild is None or uv is None:
            # Ohne Textur die Farbe an den Ecken (ein Netz aus einem Foto-Scan trägt Vertexfarben): das Mittel der drei Eckfarben, wie die Ansicht im Browser (`Mesh3dnetzfarbe._vertexfarben`)
            ecken = getattr(visuell, 'vertex_colors', None) if getattr(visuell, 'kind', None) == 'vertex' else None
            if ecken is None or len(ecken) != len(netz.vertices):
                raise ValueError('Das Netz hat weder Farbtextur noch Vertexfarben — die Auswahl nach Farbe braucht eine von beiden')
            return Torchfeld.feld(ecken, dtype=torch.float32)[Torchfeld.feld(netz.faces)][:, :, :3].mean(axis=1)
        pixel = Torchfeld.feld(bild.convert('RGB'))
        h, b = pixel.shape[:2]
        uvm = Torchfeld.feld(uv)[Torchfeld.feld(netz.faces)].mean(axis=1)
        x = Torchfeld.clip(Torchfeld.astype(uvm[:, 0] * (b - 1), torch.int64), 0, b - 1)
        y = Torchfeld.clip(Torchfeld.astype((1.0 - uvm[:, 1]) * (h - 1), torch.int64), 0, h - 1)
        return Torchfeld.astype(pixel[y, x], torch.float32)

    @staticmethod
    def lab_von(rgb):
        """sRGB (0…255) → CIE-Lab (D65), für den Farbabstand ΔE."""
        c = Torchfeld.feld(rgb, dtype=torch.float64) / 255.0
        lin = torch.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        xyz = lin @ Torchfeld.feld([[0.4124, 0.2126, 0.0193], [0.3576, 0.7152, 0.1192], [0.1805, 0.0722, 0.9505]], copy=True) / Torchfeld.feld([0.95047, 1.0, 1.08883], copy=True)
        f = torch.where(xyz > 0.008856, Torchfeld.cbrt(xyz), 7.787 * xyz + 16.0 / 116.0)
        return Torchfeld.astype(Torchfeld.stack([116.0 * f[:, 1] - 16.0, 500.0 * (f[:, 0] - f[:, 1]), 200.0 * (f[:, 1] - f[:, 2])], axis=1), torch.float32)

    # ------------------------------------------------------------------ Ablage

    @classmethod
    def _ablagedatei(cls, ablage):
        return ablage.arbeit(cls.ORDNER) / cls.DATEI

    @classmethod
    def _lesen(cls, ablage, stempel):
        datei = cls._ablagedatei(ablage)
        if not Npztorch.da(datei):
            return None
        try:
            with Npztorch.lesen(datei) as d:
                if list(d['stempel']) != stempel:
                    return None
                return cls(len(d['insel']), d['mitte'], d['insel'], stempel)
        except (OSError, ValueError, KeyError):
            logger.warning('Mesh-3D %s: Katalog des Netzes nicht lesbar — wird neu gerechnet', ablage.kennung, exc_info=True)
            return None

    @classmethod
    def _schreiben(cls, ablage, katalog):
        datei = cls._ablagedatei(ablage)
        datei.parent.mkdir(parents=True, exist_ok=True)
        teil = Path(str(datei) + '.teil')
        Npztorch.speichern(teil, stempel=Torchfeld.feld(katalog.stempel, dtype=torch.int64), mitte=katalog.mitte, insel=katalog.insel, komprimiert=False)
        Npztorch.ersetzen(teil, datei)

    # ------------------------------------------------------------------ Rechnen

    @classmethod
    def _rechnen(cls, ablage, pfad, stempel):
        punkte, flaechen = cls.geometrie(pfad)
        insel = cls.teile(punkte, flaechen)
        katalog = cls(len(flaechen), Torchfeld.astype(punkte[flaechen].mean(axis=1), torch.float32), insel, stempel)
        cls._schreiben(ablage, katalog)
        logger.info('Mesh-3D %s: Netzkatalog %d Flächen, %d Teile', ablage.kennung, katalog.flaechen, len(katalog.groessen))
        return katalog

    @staticmethod
    def geometrie(pfad):
        """Punkte und Flächen der Datei in den Koordinaten der Szene, Reihenfolge wie in der Datei. `ValueError` bei mehr als einem Netz (die Reihenfolge nach `to_geometry` wäre nicht die der Datei)."""
        import trimesh

        szene = trimesh.load(str(pfad), force='scene', process=False)
        if len(szene.geometry) != 1:
            raise ValueError('Die Datei enthält %d Netze — Ausschneiden geht nur bei einer Datei mit einem Netz' % len(szene.geometry))
        netz = szene.to_geometry() if hasattr(szene, 'to_geometry') else szene.dump(concatenate=True)
        if not isinstance(netz, trimesh.Trimesh) or len(netz.faces) == 0:
            raise ValueError('Kein Dreiecksnetz in %s' % Path(pfad).name)
        return Torchfeld.feld(netz.vertices, dtype=torch.float64), Torchfeld.feld(netz.faces, dtype=torch.int64)

    @classmethod
    def teile(cls, punkte, flaechen):
        """Teil je Fläche (0 = der größte): Flächen, die eine Kante teilen, gehören zusammen; Punkte gleicher Lage (UV-Nähte) zählen als einer."""
        from KoerperKI_alle.kartenduenn import coo_matrix
        from KoerperKI_alle.kartengraph import connected_components

        anzahl = len(flaechen)
        diagonale = float(Torchfeld.linalg_norm(Torchfeld.amax(punkte, dim=0) - Torchfeld.amin(punkte, dim=0))) or 1.0
        schluessel = Torchfeld.astype(Torchfeld.round(punkte / (diagonale * cls.RUNDEN)), torch.int64)
        _, neu = Torchfeld.unique(schluessel, axis=0, return_inverse=True)
        f = neu.reshape(-1)[flaechen]
        kanten = torch.sort(Torchfeld.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), dim=1, stable=True).values
        je_kante = torch.tile(Torchfeld.arange(anzahl), (3,))
        ordnung = Torchfeld.lexsort((kanten[:, 1], kanten[:, 0]))
        k, fl = kanten[ordnung], je_kante[ordnung]
        gleich = (k[1:] == k[:-1]).all(axis=1)
        graph = coo_matrix((torch.ones(int(gleich.sum()), dtype=torch.float64, device='cuda'), (fl[:-1][gleich], fl[1:][gleich])), shape=(anzahl, anzahl))
        _, marke = connected_components(graph, directed=False)
        reihenfolge = torch.argsort(-Torchfeld.bincount(marke), stable=True)
        neue_nummer = torch.empty(len(reihenfolge), dtype=torch.int32, device='cuda')
        neue_nummer[reihenfolge] = torch.arange(len(reihenfolge), dtype=torch.int32, device='cuda')
        return neue_nummer[marke]
