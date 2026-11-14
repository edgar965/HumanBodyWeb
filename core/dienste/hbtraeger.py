# -*- coding: utf-8 -*-
u"""Hbtraeger — die HumanBody-Figur als Traeger fuer fremde Kleidung.

Herausgeloest aus `g9aufhumanbody.py` (19.09.2026): Netz der Figur mit ihren
Morphs (Three-Lage, m, Y oben — `GarmentcodeDienst.figurnetz` rechnet in
Projektlage Z oben), Dreiecke, weiche Normalen von MeshData, die gezeichnete
Flaeche (Catmull-Clark-Unterteiler mit seinen Normalen) und die Hautgewichte
mit DEF-Knochennamen. Die juengsten Stellungen bleiben gemerkt.

DIE NORMALEN KOMMEN NICHT AUS DEM UMLAUF DER FLAECHEN: Gemessen zeigten nur
56 % der aus den Dreiecken gerechneten nach aussen — das Hemd lag danach
8 mm IN der Haut. MeshData bringt weiche Normalen mit, der Unterteiler
rechnet seine gegen eine Referenz (`compute_quad_normals`); `nach_aussen`
richtet die Schar am Schwerpunkt aus, falls sie als Ganzes nach innen zeigt.
"""
import logging

import torch
from KoerperKI_alle.torchfeld import Torchfeld

logger = logging.getLogger('core')

__all__ = ['Hbtraeger']


class Hbtraeger:
    u"""`laden(geschlecht, bauart, morphs, meta)` -> Woerterbuch der Figur."""

    _figuren = {}
    FIGUREN_MAX = 4


    @staticmethod
    def dreiecke(flaechen):
        u"""Vierecke in zwei Dreiecke; Dreiecke bleiben."""
        aus = []
        for f in flaechen:
            ecken = [int(i) for i in f]
            if len(ecken) >= 3:
                aus.append(ecken[:3])
            if len(ecken) == 4:
                aus.append([ecken[0], ecken[2], ecken[3]])
        return Torchfeld.feld(aus, dtype=torch.int64)

    @staticmethod
    def normalen(punkte, dreiecke):
        u"""Flaechengewichtete Punktnormalen, Laenge 1."""
        p = Torchfeld.feld(punkte, dtype=torch.float64)
        d = Torchfeld.feld(dreiecke, dtype=torch.int64)
        n = Torchfeld.cross(p[d[:, 1]] - p[d[:, 0]], p[d[:, 2]] - p[d[:, 0]])
        aus = torch.zeros_like(p)
        for k in range(3):
            Torchfeld.add_at(aus, d[:, k], n)
        laenge = Torchfeld.linalg_norm(aus, dim=1)
        laenge[laenge < 1e-12] = 1.0
        return aus / laenge[:, None]

    @staticmethod
    def three(punkte):
        u"""Projekt (m, Z oben) -> Three (m, Y oben)."""
        a = Torchfeld.feld(punkte, dtype=torch.float64)
        return Torchfeld.column_stack([a[:, 0], a[:, 2], -a[:, 1]])

    @classmethod
    def rahmen(cls, normalen):
        u"""(N, 3, 3): je Punkt die Achsen Normale, Aufwaerts (ohne Normalanteil), Quer."""
        n = Torchfeld.feld(normalen, dtype=torch.float64)
        auf = torch.tile([0.0, 1.0, 0.0], (len(n), 1))
        auf -= Torchfeld.einsum('ij,ij->i', auf, n)[:, None] * n
        laenge = Torchfeld.linalg_norm(auf, dim=1)
        flach = laenge < 1e-6
        if flach.any():
            ersatz = torch.tile([1.0, 0.0, 0.0], (int(flach.sum()), 1))
            ersatz -= Torchfeld.einsum('ij,ij->i', ersatz, n[flach])[:, None] * n[flach]
            auf[flach] = ersatz
            laenge = Torchfeld.linalg_norm(auf, dim=1)
        auf /= laenge[:, None]
        quer = Torchfeld.cross(n, auf)
        return Torchfeld.stack([n, auf, quer], axis=1)


    @classmethod
    def laden(cls, geschlecht, bauart, morphs, meta):
        u"""`{punkte, dreiecke, normalen, gewichte, knochen, fein, fein_dreiecke}`
        der HumanBody-Figur, Three-Lage — die juengsten Stellungen gemerkt."""
        from GarmentCode.dienst import GarmentcodeDienst
        from GarmentCode.webbruecke import charakterdaten
        schluessel = (geschlecht, bauart, tuple(sorted(morphs.items())),
                      tuple(sorted(meta.items())))
        figur = cls._figuren.get(schluessel)
        if figur is not None:
            return figur
        netz = charakterdaten().netzdaten(geschlecht)
        roh = GarmentcodeDienst.figurnetz(geschlecht, morphs, bauart, meta)
        if roh is None or getattr(netz, 'faces', None) is None:
            raise ValueError('HumanBody-Netz (%s) fehlt' % geschlecht)
        gewichte = getattr(netz, 'skin_weights', None) or getattr(netz, 'skin_weights_base', None)
        if not gewichte:
            raise ValueError('HumanBody-Netz ohne Hautgewichte')
        dreiecke = cls.dreiecke(netz.faces)
        punkte = cls.three(roh)
        # Die Normalen NICHT aus dem Umlauf der Flaechen (gemessen: nur 56 %
        # zeigten nach aussen — das Hemd lag danach 8 mm IN der Haut), sondern
        # die weichen Normalen von MeshData und die des Unterteilers.
        normalen = cls.nach_aussen(punkte, cls.three(netz.normals)
                                   if getattr(netz, 'normals', None) is not None
                                   else cls.normalen(punkte, dreiecke))
        fein, fein_dreiecke, fein_normalen = cls._sichtbar(geschlecht, roh, punkte, dreiecke,
                                                           normalen)
        figur = {
            'punkte': punkte, 'dreiecke': dreiecke, 'normalen': normalen,
            'gewichte': gewichte['weights'], 'knochen': list(gewichte['bone_names']),
            'fein': fein, 'fein_dreiecke': fein_dreiecke, 'fein_normalen': fein_normalen,
        }
        if len(cls._figuren) >= cls.FIGUREN_MAX:
            cls._figuren.pop(next(iter(cls._figuren)))
        cls._figuren[schluessel] = figur
        return figur

    @classmethod
    def _sichtbar(cls, geschlecht, roh, punkte, dreiecke, normalen):
        u"""(Punkte, Dreiecke, Normalen) der gezeichneten Flaeche (Catmull-Clark,
        `Charakterdaten.unterteiler`) — gegen sie kollidiert das Stueck; ohne
        Unterteiler das Steuernetz."""
        from GarmentCode.webbruecke import charakterdaten
        try:
            unterteiler = charakterdaten().unterteiler(geschlecht)
            if unterteiler is not None:
                fein = unterteiler.subdivide(Torchfeld.feld(roh))
                fein_n = cls.three(unterteiler.compute_quad_normals(fein))
                return (cls.three(fein), Torchfeld.feld(unterteiler.triangles, dtype=torch.int64),
                        cls.nach_aussen(cls.three(fein), fein_n))
        except Exception:                                 # noqa: BLE001
            logger.exception('Daz auf HumanBody: Unterteiler nicht verfuegbar')
        return punkte, dreiecke, normalen

    @staticmethod
    def nach_aussen(punkte, normalen):
        u"""Normalen so, dass die Mehrheit vom Schwerpunkt wegzeigt (Laenge 1)."""
        n = Torchfeld.kopie(Torchfeld.feld(normalen, dtype=torch.float64))
        laenge = Torchfeld.linalg_norm(n, dim=1)
        laenge[laenge < 1e-12] = 1.0
        n /= laenge[:, None]
        p = Torchfeld.feld(punkte, dtype=torch.float64)
        weg = p - p.mean(axis=0)
        if (Torchfeld.einsum('ij,ij->i', n, weg) > 0).mean() < 0.5:
            n = -n
        return n
