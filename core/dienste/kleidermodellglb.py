# -*- coding: utf-8 -*-
"""Kleidermodellglb — die Teile eines `Kleidermodellbau` als GLB für die Bühne (30.09.2026, aus `Kleidermodellbau.glb`
herausgelöst, als die Texturen dazukamen).

Ein Teil ohne Textur wird ein Knoten mit flacher Farbe (Vertexfarben). Ein Teil mit Texturen (`teil['textur']`,
Gruppen mit Albedo) wird je Materialgruppe ein eigener Knoten mit UV und Bild (`trimesh.visual.TextureVisuals`, PBR mit
Farbfaktor = Daz-Farbe × Tönung); der Knotenname behält den Vorsatz `<art>__<sorte>__<n>` (die Bühne schaltet daran Haar und
Kleider, `Haarenginebuehnenmodell.art` liest den Anfang) und hängt `_g<k>` an. Dreiecke ohne Bild bleiben flach.
"""

import numpy as np

__all__ = ['Kleidermodellglb']


class Kleidermodellglb:
    #: Längste Kante eines Bildes in der GLB (die Runden-GLB soll klein bleiben; die Bühne lädt sie je Runde).
    KANTE = 1024

    @staticmethod
    def _flach(trimesh, punkte, dreiecke, farbe):
        netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64),
                               faces=np.asarray(dreiecke, dtype=np.int64), process=False)
        rgb = [int(round(float(c) * 255)) for c in np.asarray(farbe)[:3]]
        netz.visual = trimesh.visual.ColorVisuals(
            netz, vertex_colors=np.tile(np.array([*rgb, 255], dtype=np.uint8), (len(netz.vertices), 1)))
        return netz

    @classmethod
    def _bild(cls, pfad):
        from PIL import Image
        with Image.open(pfad) as roh:
            bild = roh.convert('RGB')
            if max(bild.size) > cls.KANTE:
                bild.thumbnail((cls.KANTE, cls.KANTE))
            return bild.copy()

    @classmethod
    def _gruppe(cls, trimesh, punkte, dreiecke, uv, gruppe):
        """Ein Knoten je Materialgruppe: die Dreiecke der Gruppe auf den Punkten, die sie brauchen."""
        wahl = np.asarray(dreiecke, dtype=np.int64)[gruppe['ab']:gruppe['ab'] + gruppe['anzahl']]
        if not len(wahl):
            return None
        nummern, neu = np.unique(wahl.ravel(), return_inverse=True)
        netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64)[nummern],
                               faces=neu.reshape(-1, 3), process=False)
        material = trimesh.visual.material.PBRMaterial(
            baseColorTexture=cls._bild(gruppe['albedo']),
            baseColorFactor=[int(round(float(c) * 255)) for c in gruppe['faktor']] + [255],
            metallicFactor=0.0, roughnessFactor=0.85, doubleSided=True)
        if gruppe.get('normalen') is not None:
            material.normalTexture = cls._bild(gruppe['normalen'])
        netz.visual = trimesh.visual.TextureVisuals(uv=np.asarray(uv, dtype=np.float64)[nummern], material=material)
        return netz

    @classmethod
    def schreiben(cls, teile, pfad, punkte_je_teil=None):
        import trimesh
        szene = trimesh.Scene()
        for i, t in enumerate(teile):
            punkte = t['punkte'] if punkte_je_teil is None else punkte_je_teil[i]
            name = '%s__%s__%d' % (t.get('art'), t.get('sorte') or t.get('art'), i)
            textur = t.get('textur') or []
            uv = t.get('uv')
            mit_bild = [g for g in textur if g.get('albedo') is not None] if uv is not None else []
            if not mit_bild:
                szene.add_geometry(cls._flach(trimesh, punkte, t['dreiecke'], t['farbe']), node_name=name)
                continue
            belegt = np.zeros(len(t['dreiecke']), dtype=bool)
            for k, g in enumerate(mit_bild):
                netz = cls._gruppe(trimesh, punkte, t['dreiecke'], uv, g)
                if netz is not None:
                    belegt[g['ab']:g['ab'] + g['anzahl']] = True
                    szene.add_geometry(netz, node_name='%s_g%d' % (name, k))
            if not belegt.all():
                szene.add_geometry(cls._flach(trimesh, punkte, np.asarray(t['dreiecke'])[~belegt], t['farbe']),
                                   node_name=name + '_flach')
        pfad.parent.mkdir(parents=True, exist_ok=True)
        szene.export(str(pfad))
        return pfad
