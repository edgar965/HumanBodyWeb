# -*- coding: utf-8 -*-
"""Hautnachumfeld — `Blendimportumfeld` (die Haut-Kachel um das Scham-Stück trägt dort die Farbe des Originals) auf der Karte.

Dieselbe Rechnung wie die CPU-Fassung (`blendimportumfeld.py`, dort die Begründung, die Maße und die gemessenen Werte; Konstanten, `fuellen` und die Berichtszahlen kommen von dort — die Klasse
erbt). Auf die Karte verlegt sind die beiden Schritte, die dort Minuten brauchten:

    texel            die Texel einer Fehlstelle in und um die Figurdreiecke (UV-Raum der Kachel): je Dreieck die Texel seines Rechtecks, Schwerpunktkoordinaten in `float64` wie auf der CPU;
                     Texel IM Dreieck gehen vor Texeln nur in der Zugabe `RAND` (im Dreieck gewinnt das letzte, in der Zugabe das erste Dreieck — die Reihenfolge der CPU-Schleife, als
                     `atomicMax` bzw. `atomicMin` über die Dreiecksnummer). Die CPU rechnet je UV-Insel eigene Gitter; hier gilt EIN Gitter — nur an der Grenze zweier Inseln, wo die
                     Zugabe der einen in die andere reicht, kann ein Texel einem anderen Dreieck gehören (dort gewinnt nun immer das Innere).
    original_farbe   der nächste Punkt auf der Fläche des Originals (höchstens `ABSTAND_MAX_M`) und die Farbe aus dem Farbbild an seiner UV (bilinear).

Kerne `hn_rastern`, `hn_bary`, `hn_abtasten` (`hautnachkerne_cu/hautnachumfeld.cuh`, `Hautnachkernbau`); der nächste Punkt über GarmentCodes `Dreiecksbaum` und `fl_abfrage`
(Warps LBVH und `mesh_query_point_no_sign`, nachgebaut). Bis 21.11.2026 Warp-Kerne in dieser Datei und `wp.Mesh` (Edgar: „Warp überall raus“). Gegen sie gemessen
(`ProjektTemp/_wegwerf/physik_einheit/hautnach_vergleich.py`, `abfrage_diagnose.py`; Rig2, 200.000 Orte): `texel` bitgleich, `gefunden` bitgleich; die Farbe in 7.063 von
188.876 Treffern um höchstens 7e-4 Stufen (von 255) anders — 1.350 Orte liegen genau auf einer gemeinsamen Kante oder Ecke (Abstand der beiden Punkte ≤ 1,2e-7 m), dort
nimmt Warp 1.17 mit seinem anders gebauten BVH die andere Fläche; sonst wählt Warps Übersetzer bei UV und Bilinear andere FMA (≤ 3e-5 Stufen). Rückgabe wie die
Elternklasse: Tensoren auf der Karte.

    umfeld = Hautnachumfeld(stueck, figur, original, farbbild, 'cuda:0')
    umfeld.fuellen(kachel, farbe, leer)                          # wie `Blendimportumfeld.fuellen`
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from Assets.GarmentCode.dreiecksbaum import Dreiecksbaum
from Assets.GarmentCode.flaechenkernbau import Flaechenkernbau

from ..blendimportumfeld import Blendimportumfeld
from .hautnachkernbau import Hautnachkernbau

__all__ = ['Hautnachumfeld']

KEINE = 2 ** 31 - 1


class Hautnachumfeld(Blendimportumfeld):
    def __init__(self, stueck, figur, original, farbbild, geraet='cuda:0'):
        super().__init__(stueck, figur, original, farbbild)
        self.geraet = torch.device(geraet)
        self._netz = None

    def texel(self, dreiecke, leer):
        """`(zeile, spalte, dreieck, schwerpunkt)` der Fehlstellen-Texel in und um die Figurdreiecke `dreiecke` — wie `Blendimportumfeld.texel` (Gitter: siehe Kopf)."""
        g = self.geraet
        hoehe, breite = leer.shape
        uv = self.figur['uv'][self.figur['dreiecke'][dreiecke]]                    # (T, 3, 2)
        px = Torchfeld.stack([uv[..., 0] * breite, (1.0 - uv[..., 1]) * hoehe], axis=-1).reshape(len(dreiecke), 6)
        px = Torchfeld.feld(px, dtype=torch.float64).to(g).contiguous()
        innen = torch.full((hoehe, breite), -1, dtype=torch.int32, device=g)
        zugabe = torch.full((hoehe, breite), KEINE, dtype=torch.int32, device=g)
        with torch.cuda.device(g):
            Hautnachkernbau.rufen('hn_rastern', len(dreiecke), px, float(self.RAND), hoehe, breite, innen, zugabe)
            leer_k = Torchfeld.feld(leer).to(g) != 0
            # die Texel der Fehlstellen mit Besitzer, zeilenweise (`nonzero`) — die Ordnung der CPU-Fassung (`np.nonzero`, vorher lexsort)
            besitzer = torch.where(innen >= 0, innen, torch.where(zugabe != KEINE, zugabe, torch.full_like(innen, -1)))
            zeile, spalte = torch.nonzero(leer_k & (besitzer >= 0), as_tuple=True)
            eigner = besitzer[zeile, spalte].contiguous()
            lam = torch.zeros((len(zeile), 3), dtype=torch.float64, device=g)
            Hautnachkernbau.rufen('hn_bary', len(zeile), px, eigner, zeile.contiguous(), spalte.contiguous(), lam)
        return zeile, spalte, eigner.to(torch.int64), lam

    def original_farbe(self, orte):
        """`(farbe (n, 3) float64, gefunden (n,) bool)` auf der Karte: die Farbe des Originals am nächsten Punkt seiner Fläche zu jedem Ort — wie `Blendimportumfeld.original_farbe`."""
        g = self.geraet
        o = self.original
        with torch.cuda.device(g):
            if self._netz is None:
                baum = Dreiecksbaum(Torchfeld.feld(o['punkte'], dtype=torch.float32).to(g), Torchfeld.feld(o['dreiecke']).to(g))
                uv_ecken = Torchfeld.feld(o['uv_ecken'], dtype=torch.float32).to(g).reshape(-1, 2).contiguous()
                self._netz = (baum, uv_ecken, Torchfeld.feld(self.farbbild).to(device=g, dtype=torch.uint8).contiguous())
            baum, uv_ecken, bild = self._netz
            n = len(orte)
            q = Torchfeld.feld(orte, dtype=torch.float32).to(g).reshape(-1, 3).contiguous()
            treffer, flaeche = (torch.zeros(max(n, 1), dtype=torch.int32, device=g) for _ in range(2))
            u, v = (torch.zeros(max(n, 1), dtype=torch.float32, device=g) for _ in range(2))
            if n:
                Flaechenkernbau.rufen('fl_abfrage', n, *baum.zeiger(), q, float(self.ABSTAND_MAX_M), treffer, flaeche, u, v)
            farbe = torch.zeros((max(n, 1), 3), dtype=torch.float32, device=g)
            gefunden = torch.zeros(max(n, 1), dtype=torch.int32, device=g)
            Hautnachkernbau.rufen('hn_abtasten', n, treffer, flaeche, u, v, uv_ecken, bild, int(bild.shape[0]), int(bild.shape[1]), farbe, gefunden)
        return farbe[:n].to(torch.float64), gefunden[:n] != 0
